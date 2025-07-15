"""
Utilities Module
Common utilities and helper functions
"""

import logging
import subprocess
import sys
from typing import List, Dict, Any


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('pdf_extractor.log')
        ]
    )
    return logging.getLogger(__name__)


def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fitz',  # PyMuPDF
        'PIL',  # Pillow
    ]

    missing_packages = []

    for package in required_packages:
        try:
            if package == 'fitz':
                import fitz
            elif package == 'PIL':
                import PIL
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        package_names = []
        for pkg in missing_packages:
            if pkg == 'fitz':
                package_names.append('PyMuPDF')
            elif pkg == 'PIL':
                package_names.append('Pillow')

        raise ImportError(f"Missing packages: {', '.join(package_names)}")


def install_package(package: str) -> bool:
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        return True
    except subprocess.CalledProcessError:
        return False


def format_file_size(size_bytes: int) -> str:
    """Format bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def create_safe_filename(filename: str) -> str:
    """Create a safe filename by removing/replacing problematic characters"""
    import re
    # Remove or replace problematic characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple consecutive underscores
    safe_name = re.sub(r'_+', '_', safe_name)
    # Remove leading/trailing underscores and dots
    safe_name = safe_name.strip('_.')

    return safe_name[:200]  # Limit length


def validate_google_api_key(api_key: str) -> bool:
    """Validate Google API key format"""
    if not api_key:
        return False

    # Basic validation - Google API keys are typically 39 characters
    if len(api_key) < 30 or len(api_key) > 50:
        return False

    # Should contain only alphanumeric characters, hyphens, and underscores
    import re
    if not re.match(r'^[A-Za-z0-9_-]+$', api_key):
        return False

    return True


def extract_text_preview(text: str, max_length: int = 200) -> str:
    """Extract a preview of text content"""
    if not text:
        return "No text content"

    # Remove extra whitespace
    cleaned_text = ' '.join(text.split())

    if len(cleaned_text) <= max_length:
        return cleaned_text

    # Find a good breaking point
    preview = cleaned_text[:max_length]
    last_space = preview.rfind(' ')

    if last_space > max_length * 0.8:  # If space is reasonably close to end
        preview = preview[:last_space]

    return preview + "..."


def calculate_image_stats(images: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate statistics about extracted images"""
    if not images:
        return {
            'total_count': 0,
            'successful_count': 0,
            'failed_count': 0,
            'total_size_bytes': 0,
            'formats': {},
            'avg_dimensions': {'width': 0, 'height': 0}
        }

    successful = [img for img in images if img.get('filename')]
    failed = [img for img in images if not img.get('filename')]

    # Calculate format distribution
    formats = {}
    for img in successful:
        fmt = img.get('format', 'unknown').lower()
        formats[fmt] = formats.get(fmt, 0) + 1

    # Calculate total size
    total_size = sum(img.get('size_bytes', 0) for img in successful)

    # Calculate average dimensions
    avg_width = sum(img.get('width', 0) for img in successful) / len(successful) if successful else 0
    avg_height = sum(img.get('height', 0) for img in successful) / len(successful) if successful else 0

    return {
        'total_count': len(images),
        'successful_count': len(successful),
        'failed_count': len(failed),
        'total_size_bytes': total_size,
        'total_size_formatted': format_file_size(total_size),
        'formats': formats,
        'avg_dimensions': {
            'width': round(avg_width, 1),
            'height': round(avg_height, 1)
        }
    }


def generate_color_palette(count: int = 5) -> List[str]:
    """Generate a color palette for UI elements"""
    colors = [
        '#3B82F6',  # Blue
        '#8B5CF6',  # Purple
        '#10B981',  # Green
        '#F59E0B',  # Orange
        '#EF4444',  # Red
        '#06B6D4',  # Cyan
        '#84CC16',  # Lime
        '#F97316',  # Orange
        '#EC4899',  # Pink
        '#6366F1',  # Indigo
    ]

    return colors[:count]


def create_progress_bar_html(percentage: int, color: str = '#3B82F6') -> str:
    """Create HTML for a progress bar"""
    return f"""
    <div class="w-full bg-gray-200 rounded-full h-2">
        <div class="bg-blue-500 h-2 rounded-full transition-all duration-300" style="width: {percentage}%; background-color: {color}"></div>
    </div>
    """


def sanitize_html(text: str) -> str:
    """Sanitize text for HTML output"""
    import html
    return html.escape(text)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get file information"""
    from pathlib import Path
    import time

    path = Path(file_path)
    stat = path.stat()

    return {
        'name': path.name,
        'size': stat.st_size,
        'size_formatted': format_file_size(stat.st_size),
        'modified': time.ctime(stat.st_mtime),
        'created': time.ctime(stat.st_ctime),
        'extension': path.suffix.lower(),
        'exists': path.exists(),
        'is_file': path.is_file(),
        'absolute_path': str(path.absolute())
    }


class ProgressTracker:
    """Simple progress tracker for long operations"""

    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = None

    def start(self):
        """Start tracking progress"""
        import time
        self.start_time = time.time()
        self.update(0)

    def update(self, current: int):
        """Update progress"""
        self.current = current
        percentage = (current / self.total) * 100 if self.total > 0 else 0

        # Simple progress bar
        bar_length = 30
        filled_length = int(bar_length * current // self.total) if self.total > 0 else 0
        bar = '█' * filled_length + '-' * (bar_length - filled_length)

        print(f'\r{self.description}: |{bar}| {percentage:.1f}% ({current}/{self.total})', end='')

    def finish(self):
        """Finish progress tracking"""
        import time
        if self.start_time:
            elapsed = time.time() - self.start_time
            print(f' - Completed in {elapsed:.2f}s')
        else:
            print(' - Completed')
