"""
Enhanced PDF Extractor with AI Analysis
Updated to use the new HTMLBuilder architecture
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import the new modules
from html_builder import HTMLBuilder
from html_template import HTMLTemplate

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF not found. Please install it with: pip install PyMuPDF")
    sys.exit(1)

class PDFExtractor:
    """Enhanced PDF extractor with AI-powered analysis"""
    
    def __init__(self, api_key: Optional[str] = None, min_image_size: int = 256):
        self.api_key = api_key
        self.min_image_size = min_image_size
        self.logger = self._setup_logging()
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def extract_pdf(self, pdf_path: str, output_dir: str = None) -> Dict[str, Any]:
        """Extract content from PDF file"""
        pdf_path = Path(pdf_path)
        
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        if output_dir is None:
            output_dir = pdf_path.parent / f"{pdf_path.stem}_extracted"
        else:
            output_dir = Path(output_dir)
        
        # Create output directory
        output_dir.mkdir(exist_ok=True)
        images_dir = output_dir / "images"
        images_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"Extracting PDF: {pdf_path}")
        self.logger.info(f"Output directory: {output_dir}")
        
        # Extract content
        extraction_result = self._extract_content(pdf_path, images_dir)
        
        # Save extraction data
        data_file = output_dir / f"{pdf_path.stem}_data.json"
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(extraction_result, f, indent=2, ensure_ascii=False)
        
        # Generate HTML report using the new HTMLBuilder
        html_builder = HTMLBuilder(
            extraction_result=extraction_result,
            output_dir=output_dir,
            filename=pdf_path.stem,
            api_key=self.api_key,
            min_image_size=self.min_image_size
        )
        
        html_file = html_builder.generate_html()
        
        self.logger.info(f"Extraction complete!")
        self.logger.info(f"HTML report: {html_file}")
        self.logger.info(f"Data file: {data_file}")
        
        return {
            'extraction_result': extraction_result,
            'html_file': html_file,
            'data_file': str(data_file),
            'images_dir': str(images_dir)
        }
    
    def _extract_content(self, pdf_path: Path, images_dir: Path) -> Dict[str, Any]:
        """Extract text and images from PDF"""
        doc = fitz.open(pdf_path)
        
        extraction_result = {
            'filename': pdf_path.name,
            'pages': len(doc),
            'text': '',
            'images': [],
            'pages_data': [],
            'metadata': {},
            'errors': [],
            'extraction_time': datetime.now().isoformat()
        }
        
        # Extract metadata
        try:
            metadata = doc.metadata
            extraction_result['metadata'] = {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'pdf_version': f"PDF {doc.pdf_version()}"
            }
        except Exception as e:
            self.logger.warning(f"Failed to extract metadata: {e}")
            extraction_result['errors'].append(f"Metadata extraction failed: {str(e)}")
        
        # Extract content from each page
        for page_num in range(len(doc)):
            try:
                page = doc[page_num]
                page_data = self._extract_page_content(page, page_num + 1, images_dir)
                extraction_result['pages_data'].append(page_data)
                extraction_result['text'] += page_data['text'] + '\n\n'
                extraction_result['images'].extend(page_data['images'])
                
            except Exception as e:
                error_msg = f"Page {page_num + 1} extraction failed: {str(e)}"
                self.logger.error(error_msg)
                extraction_result['errors'].append(error_msg)
        
        doc.close()
        
        # Post-process images to add hashes for duplicate detection
        self._add_image_hashes(extraction_result['images'])
        
        return extraction_result
    
    def _extract_page_content(self, page, page_num: int, images_dir: Path) -> Dict[str, Any]:
        """Extract content from a single page"""
        page_data = {
            'page_number': page_num,
            'text': '',
            'images': []
        }
        
        # Extract text
        try:
            page_data['text'] = page.get_text()
        except Exception as e:
            self.logger.warning(f"Text extraction failed on page {page_num}: {e}")
            page_data['text'] = ''
        
        # Extract images
        try:
            image_list = page.get_images(full=True)
            for img_index, img in enumerate(image_list):
                img_data = self._extract_image(page, img, page_num, img_index, images_dir)
                if img_data:
                    page_data['images'].append(img_data)
        except Exception as e:
            self.logger.warning(f"Image extraction failed on page {page_num}: {e}")
        
        return page_data
    
    def _extract_image(self, page, img, page_num: int, img_index: int, images_dir: Path) -> Optional[Dict[str, Any]]:
        """Extract a single image"""
        try:
            # Get image reference
            xref = img[0]
            pix = fitz.Pixmap(page.parent, xref)
            
            # Skip if image is too small or has unusual characteristics
            if pix.width < 10 or pix.height < 10:
                pix = None
                return None
            
            # Convert to RGB if necessary
            if pix.n - pix.alpha < 4:  # GRAY or RGB
                img_data = pix.tobytes("png")
                img_ext = "png"
            else:  # CMYK
                pix1 = fitz.Pixmap(fitz.csRGB, pix)
                img_data = pix1.tobytes("png")
                img_ext = "png"
                pix1 = None
            
            # Save image
            img_filename = f"page_{page_num:03d}_img_{img_index:03d}.{img_ext}"
            img_path = images_dir / img_filename
            
            with open(img_path, 'wb') as f:
                f.write(img_data)
            
            # Create image info
            img_info = {
                'page': page_num,
                'index': img_index,
                'filename': img_filename,
                'width': pix.width,
                'height': pix.height,
                'format': img_ext,
                'size_bytes': len(img_data),
                'xref': xref
            }
            
            pix = None
            return img_info
            
        except Exception as e:
            self.logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
            return {
                'page': page_num,
                'index': img_index,
                'filename': None,
                'error': str(e)
            }
    
    def _add_image_hashes(self, images: List[Dict[str, Any]]) -> None:
        """Add content hashes to images for duplicate detection"""
        import hashlib
        
        for img in images:
            if img.get('filename'):
                try:
                    # Create a simple hash based on image properties
                    # In a full implementation, you'd hash the actual image data
                    hash_input = f"{img['width']}x{img['height']}_{img['size_bytes']}_{img['format']}"
                    img['hash'] = hashlib.md5(hash_input.encode()).hexdigest()
                except Exception as e:
                    self.logger.warning(f"Failed to generate hash for {img['filename']}: {e}")
                    img['hash'] = None

def main():
    """Main function for command line usage"""
    parser = argparse.ArgumentParser(description="Enhanced PDF Extractor with AI Analysis")
    parser.add_argument("pdf_path", help="Path to PDF file")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("-k", "--api-key", help="Google API key for AI analysis")
    parser.add_argument("-s", "--min-size", type=int, default=256, 
                       help="Minimum image size for filtering (default: 256)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    
    args = parser.parse_args()
    
    # Setup logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create extractor
    extractor = PDFExtractor(
        api_key=args.api_key,
        min_image_size=args.min_size
    )
    
    try:
        # Extract PDF
        result = extractor.extract_pdf(args.pdf_path, args.output)
        
        print(f"✅ Extraction completed successfully!")
        print(f"📄 HTML Report: {result['html_file']}")
        print(f"📊 Data File: {result['data_file']}")
        print(f"🖼️  Images: {result['images_dir']}")
        
        if args.api_key:
            print(f"🤖 AI Analysis: Enabled (configure in settings panel)")
        else:
            print(f"🤖 AI Analysis: Disabled (add API key in settings panel)")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
