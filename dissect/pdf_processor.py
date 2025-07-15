"""
PDF Processor Module
Handles PDF content extraction using PyMuPDF
"""

import fitz  # PyMuPDF
import json
import base64
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

class PDFProcessor:
    """PDF content processor using PyMuPDF"""
    
    def __init__(self, pdf_path: str, output_dir: Path):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.images_dir = output_dir / "images"
        self.images_dir.mkdir(exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def extract_content(self) -> Dict[str, Any]:
        """Extract all content from PDF"""
        result = {
            'text': '',
            'images': [],
            'pages': 0,
            'errors': [],
            'metadata': {},
            'pages_data': []
        }
        
        try:
            # Open PDF document
            pdf_document = fitz.open(self.pdf_path)
            result['pages'] = len(pdf_document)
            result['metadata'] = self._extract_metadata(pdf_document)
            
            all_text = []
            
            # Process each page
            for page_num in range(result['pages']):
                page_data = self._process_page(pdf_document, page_num)
                result['pages_data'].append(page_data)
                
                # Collect page text
                if page_data['text']:
                    all_text.append(f"--- Page {page_num + 1} ---\n{page_data['text']}")
                
                # Collect page images
                result['images'].extend(page_data['images'])
                
                # Collect page errors
                result['errors'].extend(page_data['errors'])
                
                self.logger.info(f"Processed page {page_num + 1}/{result['pages']}")
            
            # Combine all text
            result['text'] = '\n\n'.join(all_text)
            
            # Save extraction results
            self._save_results(result)
            
            pdf_document.close()
            
        except Exception as e:
            error_msg = f"PDF processing error: {str(e)}"
            result['errors'].append(error_msg)
            self.logger.error(error_msg)
        
        return result
    
    def _process_page(self, pdf_document: fitz.Document, page_num: int) -> Dict[str, Any]:
        """Process a single page"""
        page_data = {
            'page_number': page_num + 1,
            'text': '',
            'images': [],
            'errors': [],
            'text_blocks': [],
            'dimensions': {}
        }
        
        try:
            page = pdf_document[page_num]
            
            # Get page dimensions
            page_data['dimensions'] = {
                'width': page.rect.width,
                'height': page.rect.height
            }
            
            # Extract text
            page_data['text'] = page.get_text()
            
            # Extract text blocks with positioning
            text_blocks = page.get_text("dict")
            page_data['text_blocks'] = self._process_text_blocks(text_blocks)
            
            # Extract images
            page_data['images'] = self._extract_images(pdf_document, page, page_num)
            
            # Extract page screenshot
            page_data['screenshot'] = self._extract_page_screenshot(page, page_num)

        except Exception as e:
            error_msg = f"Page {page_num + 1} processing error: {str(e)}"
            page_data['errors'].append(error_msg)
            self.logger.error(error_msg)
        
        return page_data
    
    def _extract_page_screenshot(self, page: fitz.Page, page_num: int) -> Optional[str]:
        """Extract a screenshot of the page"""
        try:
            # Render page to a pixmap
            pix = page.get_pixmap()

            # Generate filename
            screenshot_filename = f"page_{page_num + 1}_screenshot.png"
            screenshot_path = self.images_dir / screenshot_filename

            # Save screenshot
            pix.save(str(screenshot_path))

            return screenshot_filename

        except Exception as e:
            self.logger.error(f"Page {page_num + 1} screenshot error: {str(e)}")
            return None

    def _process_text_blocks(self, text_dict: Dict) -> List[Dict]:
        """Process text blocks with positioning and formatting"""
        blocks = []
        
        for block in text_dict.get('blocks', []):
            if 'lines' in block:  # Text block
                block_data = {
                    'bbox': block['bbox'],
                    'lines': []
                }
                
                for line in block['lines']:
                    line_data = {
                        'bbox': line['bbox'],
                        'spans': []
                    }
                    
                    for span in line['spans']:
                        span_data = {
                            'text': span['text'],
                            'bbox': span['bbox'],
                            'font': span['font'],
                            'size': span['size'],
                            'color': span['color']
                        }
                        line_data['spans'].append(span_data)
                    
                    block_data['lines'].append(line_data)
                
                blocks.append(block_data)
        
        return blocks
    
    def _extract_images(self, pdf_document: fitz.Document, page: fitz.Page, page_num: int) -> List[Dict]:
        """Extract images from a page"""
        images = []
        
        try:
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                try:
                    # Get image reference
                    xref = img[0]
                    
                    # Extract image data
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Generate filename
                    image_filename = f"page_{page_num + 1}_img_{img_index + 1}.{image_ext}"
                    image_path = self.images_dir / image_filename
                    
                    # Save image
                    with open(image_path, 'wb') as f:
                        f.write(image_bytes)
                    
                    # Get image coordinates
                    img_rects = page.get_image_rects(xref)
                    bbox = list(img_rects[0]) if img_rects else []
                    
                    image_data = {
                        'page': page_num + 1,
                        'index': img_index + 1,
                        'filename': image_filename,
                        'path': str(image_path),
                        'bbox': bbox,
                        'width': img[2],
                        'height': img[3],
                        'format': image_ext,
                        'size_bytes': len(image_bytes),
                        'xref': xref
                    }
                    
                    images.append(image_data)
                    
                except Exception as e:
                    error_msg = f"Failed to extract image {img_index + 1} on page {page_num + 1}: {str(e)}"
                    self.logger.error(error_msg)
                    
                    # Add placeholder for failed image
                    images.append({
                        'page': page_num + 1,
                        'index': img_index + 1,
                        'filename': None,
                        'path': None,
                        'bbox': [],
                        'width': img[2] if len(img) > 2 else 0,
                        'height': img[3] if len(img) > 3 else 0,
                        'format': 'unknown',
                        'error': str(e)
                    })
        
        except Exception as e:
            error_msg = f"Image extraction error on page {page_num + 1}: {str(e)}"
            self.logger.error(error_msg)
        
        return images
    
    def _extract_metadata(self, pdf_document: fitz.Document) -> Dict[str, Any]:
        """Extract PDF metadata"""
        metadata = {}
        
        try:
            pdf_metadata = pdf_document.metadata
            metadata.update(pdf_metadata)
            
            # Additional metadata
            metadata['page_count'] = len(pdf_document)
            metadata['encrypted'] = pdf_document.is_encrypted
            metadata['pdf_version'] = pdf_document.pdf_version()
            
        except Exception as e:
            self.logger.error(f"Metadata extraction error: {e}")
        
        return metadata
    
    def _save_results(self, result: Dict[str, Any]):
        """Save extraction results to JSON file"""
        try:
            results_file = self.output_dir / "extraction_results.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            
            # Save just the text
            text_file = self.output_dir / "extracted_text.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(result['text'])
            
            # Save image metadata
            if result['images']:
                images_file = self.output_dir / "images_metadata.json"
                with open(images_file, 'w', encoding='utf-8') as f:
                    json.dump(result['images'], f, indent=2, default=str)
            
        except Exception as e:
            self.logger.error(f"Failed to save results: {e}")
