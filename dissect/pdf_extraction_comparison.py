#!/usr/bin/env python3
"""
PDF Extraction Library Comparison Script
Tests multiple PDF extraction libraries for performance and capabilities
"""

import os
import time
import json
import sys
from pathlib import Path
from datetime import datetime
import traceback
from typing import Dict, List, Any, Optional
import base64
import hashlib
import io

# Check and install required packages
required_packages = [
    'pdfplumber',
    'fitz',  # PyMuPDF
    'pdfminer.six',
    'pdf2image',  # for fallback image extraction
    'Pillow',
    'tabulate'
]

def install_package(package):
    """Install a package using pip"""
    import subprocess
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_and_install_dependencies():
    """Check and install required dependencies"""
    missing_packages = []
    for package in required_packages:
        try:
            if package == 'fitz':
                import fitz
            elif package == 'pdfplumber':
                import pdfplumber
            elif package == 'pdfminer.six':
                import pdfminer
            elif package == 'pdf2image':
                import pdf2image
            elif package == 'Pillow':
                import PIL
            elif package == 'tabulate':
                import tabulate
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"Installing missing packages: {missing_packages}")
        for package in missing_packages:
            if package == 'fitz':
                success = install_package('PyMuPDF')
            else:
                success = install_package(package)
            if not success:
                print(f"Failed to install {package}")

    # Import after installation
    global pdfplumber, fitz, tabulate, Image, pdfminer
    try:
        import pdfplumber
        import fitz
        from tabulate import tabulate
        from PIL import Image
        import pdfminer
    except ImportError as e:
        print(f"Import error after installation: {e}")
        sys.exit(1)

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.results = {}
        self.base_output_dir = Path("extraction_results")
        self.base_output_dir.mkdir(exist_ok=True)

    def create_library_output_dir(self, library_name: str) -> Path:
        """Create separate output directory for each library"""
        lib_dir = self.base_output_dir / library_name.lower().replace(' ', '_')
        lib_dir.mkdir(exist_ok=True)
        (lib_dir / "images").mkdir(exist_ok=True)
        return lib_dir

    def save_image(self, image_data: bytes, image_name: str, output_dir: Path) -> str:
        """Save image data to file and return relative path"""
        try:
            image_path = output_dir / "images" / f"{image_name}.png"
            with open(image_path, 'wb') as f:
                f.write(image_data)
            return f"images/{image_name}.png"
        except Exception as e:
            print(f"Error saving image {image_name}: {e}")
            return None

    def extract_with_pdfplumber(self) -> Dict[str, Any]:
        """Extract using PDFPlumber"""
        start_time = time.time()
        result = {
            'library': 'PDFPlumber',
            'text': '',
            'images': [],
            'pages': 0,
            'errors': [],
            'execution_time': 0,
            'memory_usage': 'N/A',
            'features': []
        }

        output_dir = self.create_library_output_dir('PDFPlumber')

        try:
            # Suppress PDFPlumber warnings by redirecting stderr temporarily
            import io
            import sys
            old_stderr = sys.stderr
            sys.stderr = io.StringIO()

            with pdfplumber.open(self.pdf_path) as pdf:
                result['pages'] = len(pdf.pages)
                all_text = []
                image_count = 0

                for page_num, page in enumerate(pdf.pages):
                    try:
                        # Extract text with coordinates
                        text = page.extract_text()
                        if text:
                            all_text.append(f"--- Page {page_num + 1} ---\n{text}")
                    except Exception as text_error:
                        result['errors'].append(f"Text extraction error on page {page_num + 1}: {str(text_error)}")

                    # Extract images - PDFPlumber has limited image extraction
                    try:
                        # Try to get image objects from page
                        if hasattr(page, 'images') and page.images:
                            for img_idx, img in enumerate(page.images):
                                image_count += 1
                                result['images'].append({
                                    'page': page_num + 1,
                                    'bbox': img.get('bbox', []),
                                    'width': img.get('width', 0),
                                    'height': img.get('height', 0),
                                    'image_file': None  # PDFPlumber doesn't easily extract image data
                                })

                        # Alternative: try to access the underlying page object safely
                        if hasattr(page, 'page_obj') and page.page_obj:
                            page_obj = page.page_obj
                            if (hasattr(page_obj, 'get') and
                                page_obj.get('/Resources') and
                                '/XObject' in page_obj.get('/Resources', {})):

                                xobjects = page_obj['/Resources']['/XObject']
                                if hasattr(xobjects, 'keys'):  # Check if it's iterable
                                    for obj_name in xobjects:
                                        try:
                                            obj = xobjects[obj_name]
                                            if hasattr(obj, 'get') and obj.get('/Subtype') == '/Image':
                                                image_count += 1
                                                result['images'].append({
                                                    'page': page_num + 1,
                                                    'name': str(obj_name),
                                                    'subtype': 'Image',
                                                    'image_file': None
                                                })
                                        except Exception as obj_error:
                                            # Skip problematic objects silently
                                            pass
                    except Exception as img_error:
                        result['errors'].append(f"Image extraction error on page {page_num + 1}: {str(img_error)}")

                    # Extract tables if any
                    try:
                        tables = page.extract_tables()
                        if tables:
                            result['features'].append(f"Page {page_num + 1}: {len(tables)} tables")
                    except Exception as table_error:
                        result['errors'].append(f"Table extraction error on page {page_num + 1}: {str(table_error)}")

            # Restore stderr
            sys.stderr = old_stderr

            result['text'] = '\n\n'.join(all_text)
            result['features'].extend([
                f"Text extraction with coordinates",
                f"Image detection: {image_count} images",
                f"Table extraction supported"
            ])

        except Exception as e:
            result['errors'].append(f"PDFPlumber error: {str(e)}")
            # Restore stderr in case of error
            sys.stderr = old_stderr

        result['execution_time'] = time.time() - start_time
        return result

    def extract_with_pymupdf(self) -> Dict[str, Any]:
        """Extract using PyMuPDF (fitz)"""
        start_time = time.time()
        result = {
            'library': 'PyMuPDF',
            'text': '',
            'images': [],
            'pages': 0,
            'errors': [],
            'execution_time': 0,
            'memory_usage': 'N/A',
            'features': []
        }

        output_dir = self.create_library_output_dir('PyMuPDF')

        try:
            pdf_document = fitz.open(self.pdf_path)
            result['pages'] = len(pdf_document)
            all_text = []
            image_count = 0

            for page_num in range(result['pages']):
                page = pdf_document[page_num]

                try:
                    # Extract text with coordinates
                    text = page.get_text()
                    if text:
                        all_text.append(f"--- Page {page_num + 1} ---\n{text}")
                except Exception as text_error:
                    result['errors'].append(f"Text extraction error on page {page_num + 1}: {str(text_error)}")

                # Extract images with coordinates
                try:
                    image_list = page.get_images()
                    for img_index, img in enumerate(image_list):
                        image_count += 1
                        try:
                            # Get image data
                            xref = img[0]
                            base_image = pdf_document.extract_image(xref)
                            image_bytes = base_image["image"]
                            image_ext = base_image["ext"]

                            # Save image
                            image_filename = f"page_{page_num + 1}_img_{img_index}"
                            saved_path = self.save_image(image_bytes, image_filename, output_dir)

                            # Get image coordinates
                            img_rects = page.get_image_rects(xref)
                            bbox = list(img_rects[0]) if img_rects else []

                            result['images'].append({
                                'page': page_num + 1,
                                'bbox': bbox,
                                'xref': xref,
                                'width': img[2],
                                'height': img[3],
                                'image_file': saved_path,
                                'format': image_ext
                            })
                        except Exception as img_extract_error:
                            result['errors'].append(f"Failed to extract image {img_index} on page {page_num + 1}: {str(img_extract_error)}")
                            result['images'].append({
                                'page': page_num + 1,
                                'xref': img[0],
                                'width': img[2],
                                'height': img[3],
                                'image_file': None
                            })
                except Exception as img_error:
                    result['errors'].append(f"Image processing error on page {page_num + 1}: {str(img_error)}")

            pdf_document.close()
            result['text'] = '\n\n'.join(all_text)
            result['features'].extend([
                "High-performance text extraction",
                f"Image extraction with coordinates: {image_count} images",
                "Text blocks with positioning",
                "Annotation support",
                "Very fast processing"
            ])

        except Exception as e:
            result['errors'].append(f"PyMuPDF error: {str(e)}")

        result['execution_time'] = time.time() - start_time
        return result

    def extract_with_pdfminer(self) -> Dict[str, Any]:
        """Extract using PDFminer.six with proper image extraction"""
        start_time = time.time()
        result = {
            'library': 'PDFminer.six',
            'text': '',
            'images': [],
            'pages': 0,
            'errors': [],
            'execution_time': 0,
            'memory_usage': 'N/A',
            'features': []
        }

        output_dir = self.create_library_output_dir('PDFminer.six')

        try:
            from pdfminer.high_level import extract_pages
            from pdfminer.layout import LTTextContainer, LTImage, LTFigure, LTContainer
            from pdfminer.image import ImageWriter
            
            # Initialize ImageWriter for image extraction
            image_writer = ImageWriter(output_dir / "images")
            
            all_text = []
            image_count = 0
            page_count = 0
            
            # Extract pages using the high-level API
            for page_layout in extract_pages(self.pdf_path):
                page_count += 1
                page_text = []
                
                # Process each element in the page
                for element in page_layout:
                    try:
                        # Extract text
                        if isinstance(element, LTTextContainer):
                            text = element.get_text()
                            if text.strip():
                                page_text.append(text)
                        
                        # Extract images - check for LTImage objects
                        elif isinstance(element, LTImage):
                            image_count += 1
                            try:
                                # Use ImageWriter to extract and save the image
                                image_filename = image_writer.export_image(element)
                                
                                result['images'].append({
                                    'page': page_count,
                                    'bbox': [element.x0, element.y0, element.x1, element.y1],
                                    'width': int(element.width),
                                    'height': int(element.height),
                                    'image_file': f"images/{image_filename}" if image_filename else None,
                                    'objid': element.stream.objid if hasattr(element, 'stream') else None
                                })
                            except Exception as img_extract_error:
                                result['errors'].append(f"Failed to extract image on page {page_count}: {str(img_extract_error)}")
                                result['images'].append({
                                    'page': page_count,
                                    'bbox': [element.x0, element.y0, element.x1, element.y1],
                                    'width': int(element.width),
                                    'height': int(element.height),
                                    'image_file': None
                                })
                        
                        # Check for images within figures or other containers
                        elif isinstance(element, LTContainer):
                            for child in element:
                                if isinstance(child, LTImage):
                                    image_count += 1
                                    try:
                                        image_filename = image_writer.export_image(child)
                                        
                                        result['images'].append({
                                            'page': page_count,
                                            'bbox': [child.x0, child.y0, child.x1, child.y1],
                                            'width': int(child.width),
                                            'height': int(child.height),
                                            'image_file': f"images/{image_filename}" if image_filename else None,
                                            'objid': child.stream.objid if hasattr(child, 'stream') else None
                                        })
                                    except Exception as img_extract_error:
                                        result['errors'].append(f"Failed to extract image from container on page {page_count}: {str(img_extract_error)}")
                                        result['images'].append({
                                            'page': page_count,
                                            'bbox': [child.x0, child.y0, child.x1, child.y1],
                                            'width': int(child.width),
                                            'height': int(child.height),
                                            'image_file': None
                                        })
                    
                    except Exception as element_error:
                        result['errors'].append(f"Error processing element on page {page_count}: {str(element_error)}")
                
                # Add page text
                if page_text:
                    all_text.append(f"--- Page {page_count} ---\n{''.join(page_text)}")
            
            result['pages'] = page_count
            result['text'] = '\n\n'.join(all_text)
            result['features'].extend([
                "Advanced layout analysis",
                f"Image extraction with coordinates: {image_count} images",
                "Detailed text positioning",
                "Font and character-level analysis",
                "Table of contents extraction"
            ])

        except Exception as e:
            result['errors'].append(f"PDFminer.six error: {str(e)}")

        result['execution_time'] = time.time() - start_time
        return result

    def save_extracted_content(self, result: Dict[str, Any], filename: str):
        """Save extracted content to files for manual review"""
        library_name = result['library']
        output_dir = self.create_library_output_dir(library_name)

        # Save text content
        text_file = output_dir / f"{filename}_text.txt"
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])

        # Save image information
        if result['images']:
            images_file = output_dir / f"{filename}_images.json"
            with open(images_file, 'w', encoding='utf-8') as f:
                json.dump(result['images'], f, indent=2)

        # Save full results
        results_file = output_dir / f"{filename}_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)

    def create_html_reassembly(self, result: Dict[str, Any], filename: str) -> str:
        """Create HTML reassembly of extracted content"""
        library_name = result['library']
        output_dir = self.create_library_output_dir(library_name)

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{library_name} - {filename} Extraction</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        .header {{
            background-color: #f4f4f4;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .page-section {{
            margin-bottom: 30px;
            padding: 20px;
            border-left: 4px solid #007acc;
            background-color: #f9f9f9;
        }}
        .page-header {{
            font-size: 1.2em;
            font-weight: bold;
            color: #007acc;
            margin-bottom: 15px;
        }}
        .text-content {{
            white-space: pre-wrap;
            font-family: monospace;
            background-color: white;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}
        .image-section {{
            margin: 20px 0;
            padding: 15px;
            background-color: #fff;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}
        .image-item {{
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
        .image-item img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .image-info {{
            font-size: 0.9em;
            color: #666;
            margin-top: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .stat-item {{
            background-color: white;
            padding: 15px;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}
        .stat-label {{
            font-weight: bold;
            color: #333;
        }}
        .stat-value {{
            font-size: 1.1em;
            color: #007acc;
        }}
        .errors {{
            background-color: #ffe6e6;
            border: 1px solid #ff9999;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }}
        .error-item {{
            margin-bottom: 5px;
            color: #cc0000;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{library_name} - PDF Extraction Results</h1>
        <p><strong>File:</strong> {filename}</p>
        <p><strong>Extraction Time:</strong> {result['execution_time']:.3f} seconds</p>
    </div>
    
    <div class="stats">
        <div class="stat-item">
            <div class="stat-label">Pages Processed</div>
            <div class="stat-value">{result['pages']}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Text Characters</div>
            <div class="stat-value">{len(result['text']):,}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Images Found</div>
            <div class="stat-value">{len(result['images'])}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Errors</div>
            <div class="stat-value">{len(result['errors'])}</div>
        </div>
    </div>
"""

        # Add errors section if any
        if result['errors']:
            html_content += '<div class="errors"><h3>Errors:</h3>\n'
            for error in result['errors']:
                html_content += f'<div class="error-item">• {error}</div>\n'
            html_content += '</div>\n'

        # Split text by pages and create sections
        pages = result['text'].split('--- Page ')
        for i, page_content in enumerate(pages):
            if not page_content.strip():
                continue

            if i == 0:
                continue  # Skip empty first split

            page_num = page_content.split(' ---')[0].strip()
            page_text = page_content.split(' ---\n', 1)[1] if ' ---\n' in page_content else page_content

            html_content += f"""
    <div class="page-section">
        <div class="page-header">Page {page_num}</div>
        <div class="text-content">{page_text}</div>
"""

            # Add images for this page
            page_images = [img for img in result['images'] if img['page'] == int(page_num)]
            if page_images:
                html_content += '<div class="image-section"><h4>Images on this page:</h4>\n'
                for img in page_images:
                    html_content += '<div class="image-item">\n'
                    if img.get('image_file'):
                        html_content += f'<img src="{img["image_file"]}" alt="Page {page_num} Image">\n'
                    else:
                        html_content += '<div style="background-color: #f0f0f0; padding: 20px; text-align: center; border: 1px dashed #ccc;">Image not extracted</div>\n'

                    # Add image info
                    html_content += '<div class="image-info">\n'
                    html_content += f'<strong>Dimensions:</strong> {img.get("width", "unknown")} x {img.get("height", "unknown")}<br>\n'
                    if img.get('bbox'):
                        html_content += f'<strong>Position:</strong> {img["bbox"]}<br>\n'
                    if img.get('format'):
                        html_content += f'<strong>Format:</strong> {img["format"]}<br>\n'
                    html_content += '</div>\n'
                    html_content += '</div>\n'
                html_content += '</div>\n'

            html_content += '    </div>\n'

        html_content += """
</body>
</html>
"""

        # Save HTML file
        html_file = output_dir / f"{filename}_reassembled.html"
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return str(html_file)

    def extract_images_fallback(self, output_dir: Path, result: Dict[str, Any]) -> None:
        """Fallback image extraction using pdf2image"""
        try:
            from pdf2image import convert_from_path
            import tempfile

            # Convert PDF pages to images as fallback
            pages = convert_from_path(self.pdf_path, dpi=150)

            for page_num, page_image in enumerate(pages):
                # Save the page as an image
                page_filename = f"page_{page_num + 1}_fallback"
                image_path = output_dir / "images" / f"{page_filename}.png"
                page_image.save(image_path, "PNG")

                # Add to results
                result['images'].append({
                    'page': page_num + 1,
                    'type': 'page_image',
                    'width': page_image.width,
                    'height': page_image.height,
                    'image_file': f"images/{page_filename}.png",
                    'note': 'Full page image (fallback method)'
                })

        except Exception as e:
            result['errors'].append(f"Fallback image extraction failed: {str(e)}")

    def run_comparison(self, pdf_file: str) -> Dict[str, Any]:
        """Run all extraction methods and compare results"""
        filename = Path(pdf_file).stem

        extractors = [
            ('PDFPlumber', self.extract_with_pdfplumber),
            ('PyMuPDF', self.extract_with_pymupdf),
            ('PDFminer.six', self.extract_with_pdfminer),
        ]

        results = {}

        for name, extractor in extractors:
            print(f"Testing {name}...")
            try:
                result = extractor()

                # If no images were extracted, try fallback method
                if len(result['images']) == 0 and name in ['PDFPlumber', 'PDFminer.six']:
                    print(f"  No images found with {name}, trying fallback method...")
                    output_dir = self.create_library_output_dir(name)
                    self.extract_images_fallback(output_dir, result)
                    if result['images']:
                        print(f"  Fallback method found {len(result['images'])} page images")

                results[name] = result
                self.save_extracted_content(result, filename)

                # Create HTML reassembly
                html_file = self.create_html_reassembly(result, filename)
                print(f"✓ {name} completed in {result['execution_time']:.3f}s")
                print(f"  Images: {len(result['images'])}, Errors: {len(result['errors'])}")
                print(f"  HTML output: {html_file}")

            except Exception as e:
                print(f"✗ {name} failed: {str(e)}")
                print(f"  Full error: {traceback.format_exc()}")
                results[name] = {
                    'library': name,
                    'text': '',
                    'images': [],
                    'pages': 0,
                    'errors': [f"Fatal error: {str(e)}"],
                    'execution_time': 0,
                    'features': []
                }

        return results

    def generate_report(self, results: Dict[str, Any], pdf_file: str) -> str:
        """Generate a comprehensive comparison report"""
        report = []
        report.append("PDF EXTRACTION LIBRARY COMPARISON REPORT")
        report.append("=" * 50)
        report.append(f"PDF File: {pdf_file}")
        report.append(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary table
        table_data = []
        for lib_name, result in results.items():
            table_data.append([
                lib_name,
                f"{result['execution_time']:.3f}s",
                result['pages'],
                f"{len(result['text']):,}",
                len(result['images']),
                len(result['errors']),
                "✓" if not result['errors'] else "✗"
            ])

        headers = ["Library", "Time", "Pages", "Text Length", "Images", "Errors", "Success"]
        report.append("PERFORMANCE SUMMARY")
        report.append("-" * 20)
        report.append(tabulate(table_data, headers=headers, tablefmt="grid"))
        report.append("")

        # Detailed results
        for lib_name, result in results.items():
            report.append(f"DETAILED RESULTS - {lib_name}")
            report.append("-" * 30)
            report.append(f"Execution Time: {result['execution_time']:.3f} seconds")
            report.append(f"Pages Processed: {result['pages']}")
            report.append(f"Text Characters: {len(result['text']):,}")
            report.append(f"Images Found: {len(result['images'])}")

            if result['features']:
                report.append("Features:")
                for feature in result['features']:
                    report.append(f"  - {feature}")

            if result['errors']:
                report.append("Errors:")
                for error in result['errors']:
                    report.append(f"  - {error}")

            report.append("")

        # Recommendations
        report.append("RECOMMENDATIONS")
        report.append("-" * 15)

        # Filter out failed libraries for recommendations
        successful_results = {k: v for k, v in results.items() if v['execution_time'] > 0}

        if successful_results:
            fastest = min(successful_results.items(), key=lambda x: x[1]['execution_time'])
            most_images = max(successful_results.items(), key=lambda x: len(x[1]['images']))
            most_text = max(successful_results.items(), key=lambda x: len(x[1]['text']))

            report.append(f"Fastest: {fastest[0]} ({fastest[1]['execution_time']:.3f}s)")
            report.append(f"Most Images Detected: {most_images[0]} ({len(most_images[1]['images'])} images)")
            report.append(f"Most Text Extracted: {most_text[0]} ({len(most_text[1]['text']):,} characters)")

            # Error-free libraries
            error_free_libs = [name for name, result in successful_results.items() if not result['errors']]
            if error_free_libs:
                report.append(f"Error-free Libraries: {', '.join(error_free_libs)}")

        report.append("")
        report.append("OUTPUT STRUCTURE")
        report.append("-" * 16)
        report.append(f"Base directory: {self.base_output_dir}")
        report.append("Each library has its own subdirectory containing:")
        report.append("  - *_text.txt: Extracted text content")
        report.append("  - *_images.json: Image metadata")
        report.append("  - *_results.json: Complete results")
        report.append("  - *_reassembled.html: HTML view with images")
        report.append("  - images/: Extracted image files")

        report.append("")
        report.append("LIBRARY-SPECIFIC NOTES")
        report.append("-" * 22)

        for lib_name, result in results.items():
            if result['execution_time'] > 0:  # Only show notes for libraries that ran
                report.append(f"{lib_name}:")
                if lib_name == "PDFPlumber":
                    report.append("  - Best for layout preservation and table extraction")
                    report.append("  - Limited native image extraction capabilities")
                elif lib_name == "PDFminer.six":
                    report.append("  - Advanced layout analysis and text positioning")
                    report.append("  - Good image extraction with ImageWriter")
                    report.append("  - Detailed font and character-level analysis")
                elif lib_name == "PyMuPDF":
                    report.append("  - Excellent image extraction with coordinates")
                    report.append("  - High performance and comprehensive features")

                # Add specific insights based on results
                if len(result['images']) > 0:
                    extracted_images = sum(1 for img in result['images'] if img.get('image_file'))
                    report.append(f"  - Successfully extracted {extracted_images}/{len(result['images'])} image files")

                if result['errors']:
                    report.append(f"  - {len(result['errors'])} errors encountered")

        return "\n".join(report)

def main():
    """Main execution function"""
    print("PDF Extraction Library Comparison Tool")
    print("=" * 40)

    # Check dependencies
    print("Checking and installing dependencies...")
    try:
        check_and_install_dependencies()
        print("✓ Dependencies ready")
    except Exception as e:
        print(f"✗ Dependency installation failed: {e}")
        print("Please install manually: pip install pdfplumber PyMuPDF pdfminer.six pdf2image Pillow tabulate")
        sys.exit(1)

    # Get PDF file path
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        pdf_file = input("Enter PDF file path: ").strip()

    if not os.path.exists(pdf_file):
        print(f"Error: PDF file '{pdf_file}' not found.")
        sys.exit(1)

    # Create extractor and run comparison
    extractor = PDFExtractor(pdf_file)

    print(f"\nStarting PDF extraction comparison for: {pdf_file}")
    print("=" * 60)
    print("Note: Some warnings about color values or image formats are normal and can be ignored.")
    print("=" * 60)

    results = extractor.run_comparison(pdf_file)

    # Generate and save report
    report = extractor.generate_report(results, pdf_file)

    # Save report to file
    report_file = extractor.base_output_dir / "comparison_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    # Display report
    print("\n" + "=" * 60)
    print("COMPARISON COMPLETE")
    print("=" * 60)
    print(report)
    print(f"\nFull report saved to: {report_file}")

    # Show directory structure
    print(f"\nOutput directory structure:")
    for item in extractor.base_output_dir.iterdir():
        if item.is_dir():
            print(f"  {item.name}/")
            for subitem in item.iterdir():
                if subitem.is_dir():
                    print(f"    {subitem.name}/")
                    for file in subitem.iterdir():
                        print(f"      {file.name}")
                else:
                    print(f"    {subitem.name}")

    # Summary recommendation
    print(f"\n" + "=" * 60)
    print("QUICK RECOMMENDATION")
    print("=" * 60)

    successful_results = {k: v for k, v in results.items() if v['execution_time'] > 0}

    if successful_results:
        # Find best overall library
        best_overall = None
        best_score = 0

        for name, result in successful_results.items():
            # Score based on: images found, text length, low errors, fast execution
            score = 0
            score += len(result['images']) * 10  # Images are important
            score += len(result['text']) / 1000  # Text extraction quality
            score -= len(result['errors']) * 5   # Penalize errors
            score += (1 / result['execution_time']) * 2  # Reward speed

            if score > best_score:
                best_score = score
                best_overall = name

        print(f"Best Overall: {best_overall}")
        print(f"  - {len(successful_results[best_overall]['images'])} images extracted")
        print(f"  - {len(successful_results[best_overall]['text']):,} text characters")
        print(f"  - {len(successful_results[best_overall]['errors'])} errors")
        print(f"  - {successful_results[best_overall]['execution_time']:.3f}s execution time")

        print(f"\nFor manual review, check the HTML files:")
        for name in successful_results:
            html_file = extractor.base_output_dir / name.lower().replace(' ', '_').replace('.', '_') / f"{Path(pdf_file).stem}_reassembled.html"
            if html_file.exists():
                print(f"  - {html_file}")
    else:
        print("No libraries completed successfully. Check the errors above.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()