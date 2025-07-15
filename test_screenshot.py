import fitz
from pathlib import Path

pdf_path = "test.pdf"  # Replace with a path to a real PDF file
output_dir = Path("test_output")
output_dir.mkdir(exist_ok=True)

try:
    pdf_document = fitz.open(pdf_path)
    page = pdf_document[0]
    pix = page.get_pixmap()
    screenshot_path = output_dir / "screenshot.png"
    pix.save(str(screenshot_path))
    print(f"Screenshot saved to {screenshot_path}")
except Exception as e:
    print(f"Error: {e}")
