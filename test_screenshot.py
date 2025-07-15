import unittest
import json
from pathlib import Path
import os
import sys
import fitz  # PyMuPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# Add the dissect directory to the python path
sys.path.append(str(Path(__file__).parent / "dissect"))

from pdf_extractor_main import PDFExtractor
from html_builder import HTMLBuilder

class TestScreenshotGeneration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a test PDF and output directory."""
        cls.output_dir = Path("test_output")
        cls.output_dir.mkdir(exist_ok=True)

        cls.pdf_path = cls.output_dir / "test.pdf"
        cls.create_test_pdf(str(cls.pdf_path))

        # Run the extractor
        extractor = PDFExtractor()
        cls.result = extractor.extract_pdf(str(cls.pdf_path), str(cls.output_dir))

    @staticmethod
    def create_test_pdf(pdf_path: str):
        """Create a simple PDF for testing."""
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.drawString(100, 750, "This is a test PDF.")
        c.showPage()
        c.save()

    def test_screenshot_metadata_in_json(self):
        """Verify that screenshot metadata is correctly stored in the JSON output."""
        json_path = Path(self.result['data_file'])
        self.assertTrue(json_path.exists())

        with open(json_path, 'r') as f:
            data = json.load(f)

        # Check screenshot data for the first page
        page_data = data['pages_data'][0]
        self.assertIn('screenshot', page_data)

        screenshot_info = page_data['screenshot']
        self.assertIsNotNone(screenshot_info)

        # Verify essential keys
        self.assertIn('filename', screenshot_info)
        self.assertIn('width', screenshot_info)
        self.assertIn('height', screenshot_info)
        self.assertIn('size_bytes', screenshot_info)

        # Check that the values are reasonable
        self.assertTrue(screenshot_info['width'] > 0)
        self.assertTrue(screenshot_info['height'] > 0)
        self.assertTrue(screenshot_info['size_bytes'] > 0)
        self.assertIn("screenshot.png", screenshot_info['filename'])

    def test_screenshot_in_html_report(self):
        """Verify that the screenshot is correctly referenced in the HTML report."""
        html_path = Path(self.result['html_file'])
        self.assertTrue(html_path.exists())

        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        # Check for the screenshot image tag
        page_data = self.result['extraction_result']['pages_data'][0]
        screenshot_filename = page_data['screenshot']['filename']
        self.assertIn(f'src="./images/{screenshot_filename}"', html_content)

        # Check for the resolution display
        width = page_data['screenshot']['width']
        height = page_data['screenshot']['height']
        self.assertIn(f'{width} × {height}', html_content)

    @classmethod
    def tearDownClass(cls):
        """Clean up generated files."""
        import shutil
        shutil.rmtree(cls.output_dir)

if __name__ == '__main__':
    unittest.main()
