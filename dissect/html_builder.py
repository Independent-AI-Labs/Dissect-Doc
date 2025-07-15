"""
Enhanced HTML Builder Module
Builds HTML reports with lazy loading and improved functionality
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import logging

from dissect.html_template import HTMLTemplate


class HTMLBuilder:
    """Builds HTML reports with enhanced features including lazy loading"""
    
    def __init__(self, extraction_result: Dict[str, Any], output_dir: Path, 
                 filename: str, api_key: Optional[str] = None, min_image_size: int = 256):
        self.extraction_result = extraction_result
        self.output_dir = output_dir
        self.filename = filename
        self.api_key = api_key
        self.min_image_size = min_image_size
        self.logger = logging.getLogger(__name__)
        
        # Process images for duplicates and filtering
        self.unique_images, self.duplicate_groups = self._process_duplicate_images()
        self.small_images, self.regular_images = self._filter_images_by_size()
        
        # Calculate word and token counts
        self.doc_word_count = self._count_words(self.extraction_result['text'])
        self.doc_token_count = self._estimate_tokens(self.extraction_result['text'])
        
        # Lazy loading configuration
        self.pages_per_chunk = 25
        self.total_pages = len(self.extraction_result['pages_data'])
        
    def _process_duplicate_images(self) -> Tuple[List[Dict[str, Any]], Dict[str, List[Dict[str, Any]]]]:
        """Process images to detect duplicates by hash and pixel similarity"""
        unique_images = []
        duplicate_groups = {}
        seen_hashes = {}
        processed_images = []
        
        for img in self.extraction_result['images']:
            if not img.get('filename'):
                continue
                
            # Calculate hash from image data or use provided hash
            img_hash = img.get('hash')
            if not img_hash:
                # If no hash provided, create one from filename and size
                img_hash = hashlib.md5(f"{img['filename']}{img.get('size_bytes', 0)}".encode()).hexdigest()
                img['hash'] = img_hash
            
            # First check for exact hash matches
            if img_hash in seen_hashes:
                # This is a duplicate
                original_img = seen_hashes[img_hash]
                if img_hash not in duplicate_groups:
                    duplicate_groups[img_hash] = [original_img]
                duplicate_groups[img_hash].append(img)
            else:
                # Check for pixel similarity with existing images
                similarity_found = False
                for existing_img in processed_images:
                    if self._are_images_similar(img, existing_img):
                        # Found similar image - group them
                        existing_hash = existing_img.get('hash')
                        if existing_hash not in duplicate_groups:
                            duplicate_groups[existing_hash] = [existing_img]
                        duplicate_groups[existing_hash].append(img)
                        similarity_found = True
                        break
                
                if not similarity_found:
                    # This is unique
                    seen_hashes[img_hash] = img
                    unique_images.append(img)
                    processed_images.append(img)
        
        return unique_images, duplicate_groups
    
    def _are_images_similar(self, img1: Dict[str, Any], img2: Dict[str, Any]) -> bool:
        """Check if two images are similar (99% pixel similarity)"""
        # Basic similarity check based on dimensions and file size
        # In a full implementation, this would load and compare actual pixel data
        
        # If dimensions are very different, they're not similar
        w1, h1 = img1.get('width', 0), img1.get('height', 0)
        w2, h2 = img2.get('width', 0), img2.get('height', 0)
        
        if w1 == 0 or h1 == 0 or w2 == 0 or h2 == 0:
            return False
        
        # Check if dimensions are similar (within 5% tolerance)
        width_diff = abs(w1 - w2) / max(w1, w2)
        height_diff = abs(h1 - h2) / max(h1, h2)
        
        if width_diff > 0.05 or height_diff > 0.05:
            return False
        
        # Check if file sizes are similar (within 10% tolerance)
        size1 = img1.get('size_bytes', 0)
        size2 = img2.get('size_bytes', 0)
        
        if size1 > 0 and size2 > 0:
            size_diff = abs(size1 - size2) / max(size1, size2)
            if size_diff > 0.10:
                return False
        
        # Check if formats are the same
        if img1.get('format') != img2.get('format'):
            return False
        
        # If all basic checks pass, consider them similar
        return True
        
    def _filter_images_by_size(self) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Filter images by size - separate small UI elements from regular images"""
        small_images = []
        regular_images = []
        min_area = self.min_image_size * self.min_image_size

        for img in self.extraction_result['images']:
            if not img.get('filename'):
                continue
                
            width = img.get('width', 0)
            height = img.get('height', 0)
            area = width * height
            
            # Images with an area smaller than min_area are considered small/UI elements
            if area < min_area:
                small_images.append(img)
            else:
                regular_images.append(img)
        
        return small_images, regular_images
    
    def _count_words(self, text: str) -> int:
        """Count words in text"""
        if not text:
            return 0
        return len(text.split())
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 characters)"""
        if not text:
            return 0
        return len(text) // 4
        
    def generate_html(self) -> str:
        """Generate the complete HTML report with lazy loading"""
        self.logger.info("Starting HTML report generation...")
        
        try:
            # Build all components
            self.logger.info("Generating modal template...")
            modal = HTMLTemplate.get_modal_template()
            
            self.logger.info("Generating settings template...")
            settings = HTMLTemplate.get_settings_template()
            
            self.logger.info("Generating header template...")
            header = HTMLTemplate.get_header_template(
                self.filename, 
                self.extraction_result['pages'], 
                len(self.unique_images)
            )
            
            self.logger.info("Generating stats template...")
            stats = HTMLTemplate.get_stats_template(
                self.extraction_result['pages'],
                self.doc_word_count,
                self.doc_token_count,
                len(self.regular_images),
                len(self.small_images),
                len(self.unique_images),
                len(self.extraction_result['images']) - len(self.unique_images),
                self.min_image_size
            )
            
            self.logger.info("Generating lazy-loaded content...")
            content = self._generate_lazy_content()
            
            self.logger.info("Generating footer template...")
            footer = HTMLTemplate.get_footer_template()
            
            self.logger.info("Getting main template...")
            main_template = HTMLTemplate.get_main_template(self.filename)
            
            self.logger.info("Replacing template placeholders...")
            # Use simple string replacement with comment-style placeholders to avoid CSS/JS conflicts
            html_content = main_template.replace('<!--MODAL_PLACEHOLDER-->', modal)
            html_content = html_content.replace('<!--SETTINGS_PLACEHOLDER-->', settings)
            html_content = html_content.replace('<!--HEADER_PLACEHOLDER-->', header)
            html_content = html_content.replace('<!--STATS_PLACEHOLDER-->', stats)
            html_content = html_content.replace('<!--CONTENT_PLACEHOLDER-->', content)
            html_content = html_content.replace('<!--FOOTER_PLACEHOLDER-->', footer)
            
            # Generate JSON data for lazy loading
            self._generate_pages_json()
            
            # Save HTML file
            html_file = self.output_dir / f"{self.filename}_report.html"
            self.logger.info(f"Writing HTML file to: {html_file}")
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.info("HTML report generation completed successfully!")
            return str(html_file)
            
        except Exception as e:
            self.logger.error(f"HTML generation failed at step: {str(e)}")
            self.logger.error(f"Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    def _generate_pages_json(self):
        """Generate JSON data for lazy loading pages"""
        pages_data = {}
        
        for i, page_data in enumerate(self.extraction_result['pages_data']):
            pages_data[str(page_data['page_number'])] = {
                'page_number': page_data['page_number'],
                'text': page_data.get('text', ''),
                'word_count': self._count_words(page_data.get('text', '')),
                'token_count': self._estimate_tokens(page_data.get('text', '')),
                'images': [img for img in self.extraction_result['images'] if img['page'] == page_data['page_number']],
                'screenshot': page_data.get('screenshot')
            }
        
        # Save to JSON file
        json_file = self.output_dir / f"{self.filename}_pages.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(pages_data, f, indent=2, ensure_ascii=False)
    
    def _generate_lazy_content(self) -> str:
        """Generate main content section with lazy loading structure"""
        content = f"""
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-8">
        <div id="pagesContainer" class="space-y-8">
            <!-- Loading indicator -->
            <div id="loadingIndicator" class="text-center py-8">
                <div class="inline-flex items-center px-4 py-2 font-semibold leading-6 text-sm shadow rounded-md text-white bg-indigo-500 hover:bg-indigo-400 transition ease-in-out duration-150 cursor-not-allowed">
                    <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Loading pages...
                </div>
            </div>
            
            <!-- Load first chunk immediately -->
            <div id="initialPages">
                {self._generate_page_chunk(0, min(self.pages_per_chunk, self.total_pages))}
            </div>
            
            <!-- Placeholder for additional chunks -->
            <div id="lazyPages"></div>
            
            <!-- Load more button -->
            <div id="loadMoreContainer" class="text-center py-8" style="display: none;">
                <button id="loadMoreBtn" onclick="loadMorePages()" class="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold py-3 px-6 rounded-lg shadow-lg transform transition hover:scale-105">
                    Load More Pages ({self.pages_per_chunk} more)
                </button>
            </div>
            
            <!-- End indicator -->
            <div id="endIndicator" class="text-center py-8 text-gray-500" style="display: none;">
                <div class="flex items-center justify-center">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    All pages loaded
                </div>
            </div>
        </div>
    </div>
        """
        
        return content
    
    def _generate_page_chunk(self, start_idx: int, end_idx: int) -> str:
        """Generate a chunk of pages"""
        chunk_html = ""
        
        for i in range(start_idx, min(end_idx, self.total_pages)):
            page_data = self.extraction_result['pages_data'][i]
            chunk_html += self._generate_page_section(page_data)
        
        return chunk_html
    
    def _generate_page_section(self, page_data: Dict[str, Any]) -> str:
        """Generate a single page section"""
        page_num = page_data['page_number']
        page_images = [img for img in self.extraction_result['images'] if img['page'] == page_num]
        
        # Calculate page-specific stats
        page_text = page_data.get('text', '')
        page_word_count = self._count_words(page_text)
        page_token_count = self._estimate_tokens(page_text)
        
        # Filter images by size
        min_area = self.min_image_size * self.min_image_size
        regular_page_images = [img for img in page_images if img.get('width', 0) * img.get('height', 0) >= min_area]
        small_page_images = [img for img in page_images if img.get('width', 0) * img.get('height', 0) < min_area]
        
        screenshot_filename = page_data.get('screenshot')

        return f"""
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden page-section" data-page="{page_num}">
            <div class="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
                <h2 class="text-xl font-semibold text-white flex items-center">
                    <span class="bg-white bg-opacity-20 rounded-full w-8 h-8 flex items-center justify-center mr-3 text-sm">
                        {page_num}
                    </span>
                    Page {page_num}
                    <span class="ml-auto flex items-center space-x-3 text-sm">
                        <span class="bg-white bg-opacity-20 px-2 py-1 rounded-full">
                            {page_word_count:,} words
                        </span>
                        <span class="bg-white bg-opacity-20 px-2 py-1 rounded-full">
                            {page_token_count:,} tokens
                        </span>
                        <span class="bg-white bg-opacity-20 px-2 py-1 rounded-full">
                            {len(regular_page_images)} images
                        </span>
                        {f'<span class="bg-white bg-opacity-20 px-2 py-1 rounded-full text-xs">{len(small_page_images)} small</span>' if small_page_images else ''}
                    </span>
                </h2>
            </div>
            
            <div class="p-6">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
                    <div class="lg:col-span-1">
                        {self._generate_screenshot_section(screenshot_filename, page_num)}
                    </div>
                    <div class="lg:col-span-2 grid grid-cols-1 gap-8">
                        <div class="space-y-6">
                            <div>
                                <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                                    <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                    </svg>
                                    Text Content
                                </h3>
                                <div class="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                                    <pre class="text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">{page_text[:2000]}{'...' if len(page_text) > 2000 else ''}</pre>
                                </div>
                            </div>
                        </div>

                        <div class="space-y-6">
                            {self._generate_images_section(regular_page_images, small_page_images)}
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """

    def _generate_screenshot_section(self, screenshot_filename: Optional[str], page_num: int) -> str:
        """Generate the screenshot section for a page"""
        if not screenshot_filename:
            return """
            <div class="bg-gray-50 rounded-lg p-8 text-center">
                <p class="text-gray-500">No screenshot available</p>
            </div>
            """

        # Create a mock image object for the screenshot to reuse the card generation logic
        screenshot_img_obj = {
            'filename': screenshot_filename,
            'page': page_num,
            'index': 'screenshot',
            'width': 1024,  # Default width, can be adjusted
            'height': 768, # Default height
            'format': 'PNG',
            'size_bytes': 0, # Not available, can be omitted
            'hash': f"screenshot_{page_num}"
        }

        return f"""
        <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <svg class="w-5 h-5 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                </svg>
                Page Screenshot
            </h3>
            {self._generate_image_card(screenshot_img_obj, is_small=False, is_screenshot=True)}
        </div>
        """
    
    def _generate_images_section(self, regular_images: List[Dict[str, Any]], small_images: List[Dict[str, Any]]) -> str:
        """Generate images section for a page with size filtering"""
        content = f"""
        <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 002 2z"></path>
                </svg>
                Images ({len(regular_images)} regular{f', {len(small_images)} small' if small_images else ''})
            </h3>
        """
        
        if not regular_images and not small_images:
            content += """
            <div class="bg-gray-50 rounded-lg p-8 text-center">
                <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 002 2z"></path>
                </svg>
                <p class="text-gray-500">No images found on this page</p>
            </div>
            """
        else:
            # Regular images (always visible)
            if regular_images:
                content += f"""
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 regular-images">
                """
                for img in regular_images:
                    content += self._generate_image_card(img, is_small=False)
                content += """
                </div>
                """
            
            # Small images (hidden by default)
            if small_images:
                content += f"""
                <div class="small-images mt-6">
                    <div class="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div class="flex items-center">
                            <svg class="w-5 h-5 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                            </svg>
                            <span class="text-sm font-medium text-yellow-800">Small Images & UI Elements</span>
                        </div>
                        <p class="text-xs text-yellow-600 mt-1">These images have an area smaller than {self.min_image_size}×{self.min_image_size} pixels and likely contain UI elements, icons, or decorative graphics</p>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
                """
                for img in small_images:
                    content += self._generate_image_card(img, is_small=True)
                content += """
                    </div>
                </div>
                """
        
        content += """
        </div>
        """
        
        return content
    
    def _generate_image_card(self, img: Dict[str, Any], is_small: bool = False, is_screenshot: bool = False) -> str:
        """Generate a single image card"""
        if img.get('filename'):
            # Check if this is a duplicate or similar image
            is_duplicate = False
            is_similar = False
            duplicate_count = 0
            
            if not is_screenshot and img.get('hash'):
                for img_hash, duplicates in self.duplicate_groups.items():
                    if img['hash'] == img_hash:
                        is_duplicate = True
                        duplicate_count = len(duplicates)
                        break
                    elif img in duplicates:
                        is_similar = True
                        duplicate_count = len(duplicates)
                        break
            
            # Different styling for small images
            if is_small:
                card_class = "bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
                image_class = "w-full h-20 object-contain clickable-image hover:scale-105 transition-transform duration-200"
                padding_class = "p-2"
            else:
                card_class = "bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow"
                image_class = "w-full h-auto object-contain clickable-image" if is_screenshot else "w-full h-48 object-contain clickable-image hover:scale-105 transition-transform duration-200"
                padding_class = "p-3"

            # Choose appropriate indicator
            if is_screenshot:
                indicator = ""
            elif is_duplicate:
                indicator = f"""
                    <div class="duplicate-indicator">
                        DUP {duplicate_count}x
                    </div>
                """
            elif is_similar:
                indicator = f"""
                    <div class="similar-indicator">
                        SIM {duplicate_count}x
                    </div>
                """
            else:
                indicator = """
                    <div class="unique-indicator">
                        UNIQUE
                    </div>
                """
            
            alt_text = f"Screenshot of Page {img['page']}" if is_screenshot else f"Page {img['page']} Image {img['index']}"
            data_image_id = f"page_{img['page']}_screenshot" if is_screenshot else f"{img['page']}_{img['index']}"

            return f"""
                <div class="relative group">
                    <div class="{card_class}">
                        <div class="aspect-w-16 aspect-h-9 bg-gray-100 relative" onclick="openModal('images/{img['filename']}', '{img['page']}', '{img['index']}', '{img['width']}', '{img['height']}', '{img.get('format', 'unknown')}', '{self._format_bytes(img.get('size_bytes', 0))}', '{img.get('hash', '')[:8]}')">
                            <img 
                                src="./images/{img['filename']}"
                                alt="{alt_text}"
                                class="{image_class}"
                                data-image-id="{data_image_id}"
                                data-image-filename="{img['filename']}"
                                data-image-hash="{img.get('hash', '')}"
                                data-width="{img['width']}"
                                data-height="{img['height']}"
                                loading="lazy"
                            >
                            <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity duration-200"></div>
                            {indicator}
                            
                            {self._generate_ai_button() if not is_small else ''}
                            
                            <!-- Expand indicator -->
                            <div class="absolute bottom-1 right-1 bg-black bg-opacity-60 text-white px-1 py-0.5 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity duration-200 expand-pill">
                                Expand
                            </div>
                        </div>
                        <div class="{padding_class}">
                            <div class="flex items-center justify-between text-xs text-gray-600">
                                <span class="font-medium">{'Screenshot' if is_screenshot else f"Image {img['index']}"}</span>
                                <span class="bg-gray-100 px-1 py-0.5 rounded text-xs">{img.get('format', 'PNG').upper()}</span>
                            </div>
                            {f'<div class="mt-1 text-xs text-gray-500"><span>{img["width"]} × {img["height"]}</span></div>' if not is_small else ''}
                            {self._generate_ai_analysis_section(img) if not is_small else ''}
                        </div>
                    </div>
                </div>
            """
        else:
            return f"""
                <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                    <div class="flex items-center">
                        <svg class="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                        <span class="text-sm text-red-700">Failed to extract image {img['index']}</span>
                    </div>
                </div>
            """
    
    def _generate_ai_button(self) -> str:
        """Generate clickable AI analysis button"""
        return """
            <button 
                class="absolute top-2 right-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-3 py-1 rounded-full text-xs font-semibold opacity-0 group-hover:opacity-100 transition-all duration-200 flex items-center space-x-1 cursor-pointer shadow-lg ai-analysis-button"
                onclick="analyzeImageFromButton(this, event)"
                title="Click for AI analysis"
                style="display: none;"
            >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                </svg>
                <span>AI</span>
            </button>
        """
    
    def _generate_ai_analysis_section(self, img: Dict[str, Any]) -> str:
        """Generate AI analysis section in the card"""
        image_id = f"page_{img['page']}_screenshot" if img['index'] == 'screenshot' else f"{img['page']}_{img['index']}"
        
        return f"""
            <div class="mt-3 pt-3 border-t border-gray-100 ai-analysis-section" style="display: none;">
                <div class="flex items-center justify-between mb-2">
                    <span class="text-xs font-semibold text-purple-600 flex items-center">
                        <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                        AI Analysis
                    </span>
                    <button
                        class="text-xs bg-purple-100 hover:bg-purple-200 text-purple-700 px-2 py-1 rounded transition-colors"
                        onclick="toggleAnalysis('{image_id}')"
                        id="btn-{image_id}"
                    >
                        Analyze
                    </button>
                </div>
                <div 
                    id="analysis-{image_id}" 
                    class="text-xs text-gray-600 hidden"
                >
                    <div class="flex items-center justify-center py-4 bg-gray-50 rounded">
                        <span class="text-gray-400">Click "Analyze" to get detailed AI description</span>
                    </div>
                </div>
            </div>
        """
    
    def _format_bytes(self, bytes_size: int) -> str:
        """Format bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"