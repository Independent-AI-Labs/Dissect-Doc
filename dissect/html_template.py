"""
HTML Template Module
Contains all HTML, CSS, and JavaScript templates for the PDF analysis report
"""

class HTMLTemplate:
    """Contains all HTML templates and snippets"""
    
    @staticmethod
    def get_main_template(filename: str) -> str:
        """Main HTML document template"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Analysis Report - {filename}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    {HTMLTemplate.get_css()}
</head>
<body class="bg-gradient-to-br from-blue-50 via-white to-purple-50 min-h-screen">
    {{modal}}
    {{settings}}
    {{header}}
    {{stats}}
    {{content}}
    {{footer}}
    {HTMLTemplate.get_javascript()}
</body>
</html>"""

    @staticmethod
    def get_css() -> str:
        """CSS styles for the application"""
        return """
    <style>
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(5px);
        }
        .modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .modal-content {
            max-width: 90vw;
            max-height: 90vh;
            position: relative;
        }
        .modal-image {
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
        }
        .duplicate-indicator {
            position: absolute;
            top: 8px;
            left: 8px;
            background: linear-gradient(45deg, #f59e0b, #f97316);
            color: white;
            padding: 2px 6px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
        }
        .unique-indicator {
            position: absolute;
            top: 8px;
            left: 8px;
            background: linear-gradient(45deg, #10b981, #059669);
            color: white;
            padding: 2px 6px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
        }
        .similar-indicator {
            position: absolute;
            top: 8px;
            left: 8px;
            background: linear-gradient(45deg, #8b5cf6, #7c3aed);
            color: white;
            padding: 2px 6px;
            border-radius: 12px;
            font-size: 10px;
            font-weight: bold;
        }
        .small-images {
            display: none;
        }
        .small-images.show {
            display: block;
        }
        .analysis-content {
            max-height: 120px;
            overflow-y: auto;
            padding: 8px;
            background: #f9fafb;
            border-radius: 6px;
        }
        .analysis-content.expanded {
            max-height: none;
        }
        .clickable-image {
            cursor: pointer;
        }
        .clickable-image:hover {
            cursor: pointer;
        }
        .expand-pill {
            cursor: pointer;
        }
        .expand-pill:hover {
            cursor: pointer;
        }
        .settings-panel {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 100;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
            padding: 20px;
            min-width: 300px;
            transform: translateX(100%);
            transition: transform 0.3s ease;
        }
        .settings-panel.show {
            transform: translateX(0);
        }
        .settings-toggle {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 101;
            background: white;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .settings-toggle:hover {
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
            transform: scale(1.05);
        }
        
        /* Markdown styling for AI analysis */
        .markdown-content h1 {
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #1f2937;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 0.25rem;
        }
        .markdown-content h2 {
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
            color: #374151;
        }
        .markdown-content h3 {
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.25rem;
            color: #4b5563;
        }
        .markdown-content p {
            margin-bottom: 0.5rem;
            line-height: 1.4;
        }
        .markdown-content ul, .markdown-content ol {
            margin-bottom: 0.5rem;
            padding-left: 1rem;
        }
        .markdown-content li {
            margin-bottom: 0.25rem;
        }
        .markdown-content strong {
            font-weight: 600;
            color: #1f2937;
        }
        .markdown-content em {
            font-style: italic;
            color: #4b5563;
        }
        .markdown-content code {
            background-color: #f3f4f6;
            padding: 0.125rem 0.25rem;
            border-radius: 0.25rem;
            font-family: monospace;
            font-size: 0.875rem;
        }
        .markdown-content blockquote {
            border-left: 4px solid #d1d5db;
            padding-left: 1rem;
            margin: 0.5rem 0;
            color: #6b7280;
        }
        .markdown-content * {
            font-size: 0.75rem !important;
        }
    </style>
        """

    @staticmethod
    def get_modal_template() -> str:
        """Modal template for image viewing"""
        return """
    <div id="imageModal" class="modal">
        <div class="modal-content">
            <button 
                onclick="closeModal()"
                class="absolute top-4 right-4 z-10 bg-black bg-opacity-50 hover:bg-opacity-70 text-white w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200"
                title="Close (ESC)"
            >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
            
            <div class="absolute bottom-4 left-4 right-4 bg-black bg-opacity-50 text-white p-4 rounded-lg">
                <div id="modalImageInfo" class="text-sm">
                    <!-- Image info will be populated here -->
                </div>
            </div>
            
            <img id="modalImage" class="modal-image" alt="Full size image">
        </div>
    </div>
        """

    @staticmethod
    def get_settings_template() -> str:
        """Settings panel template"""
        return """
    <div class="settings-toggle" onclick="toggleSettings()" title="Settings">
        <svg class="w-6 h-6 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
        </svg>
    </div>
    
    <div id="settingsPanel" class="settings-panel">
        <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-gray-900">Settings</h3>
            <button onclick="toggleSettings()" class="text-gray-400 hover:text-gray-600">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
            </button>
        </div>
        
        <div class="space-y-4">
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Google API Key</label>
                <input 
                    type="password" 
                    id="apiKeyInput" 
                    placeholder="Enter your Google API key"
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
                    onchange="updateAPIKey()"
                >
                <p class="text-xs text-gray-500 mt-1">Required for AI image analysis</p>
            </div>
            
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Small Image Filter (px)</label>
                <input 
                    type="range" 
                    id="minImageSizeSlider"
                    min="64" 
                    max="512" 
                    value="256"
                    class="w-full"
                    onchange="updateMinImageSize()"
                >
                <div class="flex justify-between text-xs text-gray-500 mt-1">
                    <span>64px</span>
                    <span id="minImageSizeValue">256px</span>
                    <span>512px</span>
                </div>
                <p class="text-xs text-gray-500 mt-1">Images smaller than this will be filtered as UI elements</p>
            </div>
            
            <div class="pt-3 border-t border-gray-200">
                <button 
                    onclick="applySettings()"
                    class="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                    Apply Settings
                </button>
            </div>
        </div>
    </div>
        """

    @staticmethod
    def get_header_template(filename: str, pages: int, unique_count: int) -> str:
        """Header template"""
        return f"""
    <div class="bg-white shadow-lg border-b border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold text-gray-900">PDF Analysis Report</h1>
                    <p class="mt-2 text-lg text-gray-600">
                        <span class="font-semibold">{filename}</span>
                        <span class="mx-2">•</span>
                        <span class="text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                            {pages} pages
                        </span>
                        <span class="mx-2">•</span>
                        <span class="text-sm bg-green-100 text-green-800 px-2 py-1 rounded-full">
                            {unique_count} unique images
                        </span>
                    </p>
                </div>
                <div class="flex items-center space-x-4">
                    <div class="text-right">
                        <div class="text-sm text-gray-500">Enhanced with</div>
                        <div class="text-lg font-semibold text-purple-600">AI Analysis</div>
                    </div>
                </div>
            </div>
        </div>
    </div>
        """

    @staticmethod
    def get_stats_template(pages: int, doc_word_count: int, doc_token_count: int, 
                          regular_count: int, small_count: int, unique_count: int, 
                          duplicate_count: int, min_image_size: int) -> str:
        """Statistics template"""
        return f"""
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-7 gap-4">
            <div class="bg-white rounded-xl shadow-md p-4 border border-gray-100">
                <div class="flex items-center">
                    <div class="p-2 bg-blue-100 rounded-lg">
                        <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-xs text-gray-600">Pages</p>
                        <p class="text-lg font-semibold text-gray-900">{pages}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-md p-4 border border-gray-100">
                <div class="flex items-center">
                    <div class="p-2 bg-green-100 rounded-lg">
                        <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"></path>
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-xs text-gray-600">Words</p>
                        <p class="text-lg font-semibold text-gray-900">{doc_word_count:,}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-md p-4 border border-gray-100">
                <div class="flex items-center">
                    <div class="p-2 bg-indigo-100 rounded-lg">
                        <svg class="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-xs text-gray-600">Tokens</p>
                        <p class="text-lg font-semibold text-gray-900">{doc_token_count:,}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-md p-4 border border-gray-100">
                <div class="flex items-center">
                    <div class="p-2 bg-purple-100 rounded-lg">
                        <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 002 2z"></path>
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-xs text-gray-600">Regular</p>
                        <p class="text-lg font-semibold text-gray-900">{regular_count}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-md p-4 border border-gray-100">
                <div class="flex items-center">
                    <div class="p-2 bg-yellow-100 rounded-lg">
                        <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z"></path>
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-xs text-gray-600">Small/UI</p>
                        <p class="text-lg font-semibold text-gray-900">{small_count}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-md p-4 border border-gray-100">
                <div class="flex items-center">
                    <div class="p-2 bg-emerald-100 rounded-lg">
                        <svg class="w-5 h-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-xs text-gray-600">Unique</p>
                        <p class="text-lg font-semibold text-gray-900">{unique_count}</p>
                    </div>
                </div>
            </div>
            
            <div class="bg-white rounded-xl shadow-md p-4 border border-gray-100">
                <div class="flex items-center">
                    <div class="p-2 bg-orange-100 rounded-lg">
                        <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7v8a2 2 0 002 2h6M8 7V5a2 2 0 012-2h4.586a1 1 0 01.707.293l4.414 4.414a1 1 0 01.293.707V15a2 2 0 01-2 2v0a2 2 0 01-2-2v-2M8 7H6a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2v-2"></path>
                        </svg>
                    </div>
                    <div class="ml-3">
                        <p class="text-xs text-gray-600">Duplicates</p>
                        <p class="text-lg font-semibold text-gray-900">{duplicate_count}</p>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Image filtering controls -->
        <div class="mt-6 bg-white rounded-xl shadow-md p-4 border border-gray-100">
            <div class="flex items-center justify-between">
                <div class="flex items-center space-x-4">
                    <h3 class="text-lg font-semibold text-gray-900">Image Filtering</h3>
                    <label class="flex items-center space-x-2 cursor-pointer">
                        <input 
                            type="checkbox" 
                            id="showSmallImages" 
                            onchange="toggleSmallImages()"
                            class="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                        >
                        <span class="text-sm text-gray-700">Show Small & UI Elements ({small_count} images)</span>
                    </label>
                </div>
                <div class="text-sm text-gray-500">
                    Small images are &lt;{min_image_size}×{min_image_size} pixels
                </div>
            </div>
        </div>
    </div>
        """

    @staticmethod
    def get_footer_template() -> str:
        """Footer template"""
        return """
    <div class="bg-gray-50 border-t border-gray-200">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div class="text-center">
                <p class="text-sm text-gray-500">
                    Generated by Enhanced PDF Extractor • Powered by PyMuPDF and Google AI
                </p>
            </div>
        </div>
    </div>
        """

    @staticmethod
    def get_javascript() -> str:
        """JavaScript for interactive features"""
        return """
<script>
let API_KEY = '';
let MIN_IMAGE_SIZE = 256;
let analysisCache = new Map();
let analysisInProgress = new Set();
let hashAnalysisCache = new Map();

// Settings functions
function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    panel.classList.toggle('show');
}

function updateAPIKey() {
    const input = document.getElementById('apiKeyInput');
    API_KEY = input.value.trim();
    console.log('API Key updated:', API_KEY ? 'Set' : 'Empty');
}

function updateMinImageSize() {
    const slider = document.getElementById('minImageSizeSlider');
    const valueDisplay = document.getElementById('minImageSizeValue');
    MIN_IMAGE_SIZE = parseInt(slider.value);
    valueDisplay.textContent = MIN_IMAGE_SIZE + 'px';
}

function applySettings() {
    // Refresh the page to apply new settings
    location.reload();
}

// Toggle small images visibility
function toggleSmallImages() {
    const checkbox = document.getElementById('showSmallImages');
    const smallImageContainers = document.querySelectorAll('.small-images');
    
    smallImageContainers.forEach(container => {
        if (checkbox.checked) {
            container.classList.add('show');
        } else {
            container.classList.remove('show');
        }
    });
}

// Modal functions
function openModal(filename, page, index, width, height, format, fileSize, hash) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalInfo = document.getElementById('modalImageInfo');
    
    modalImage.src = 'images/' + filename;
    modalImage.alt = 'Page ' + page + ' Image ' + index;
    
    let infoHTML = '<div class="grid grid-cols-2 gap-4 text-sm">';
    infoHTML += '<div><strong>Page:</strong> ' + page + '</div>';
    infoHTML += '<div><strong>Index:</strong> ' + index + '</div>';
    infoHTML += '<div><strong>Dimensions:</strong> ' + width + ' × ' + height + '</div>';
    infoHTML += '<div><strong>Format:</strong> ' + format.toUpperCase() + '</div>';
    infoHTML += '<div><strong>File Size:</strong> ' + fileSize + '</div>';
    if (hash && hash !== 'undefined') {
        infoHTML += '<div><strong>Hash:</strong> ' + hash + '...</div>';
    }
    infoHTML += '<div class="col-span-2"><strong>Filename:</strong> ' + filename + '</div>';
    infoHTML += '</div>';
    
    modalInfo.innerHTML = infoHTML;
    
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
}

// AI Analysis functions
function analyzeImageFromButton(button, event) {
    event.stopPropagation();
    const img = button.parentElement.querySelector('img');
    if (img) {
        const imageId = img.dataset.imageId;
        toggleAnalysis(imageId);
    }
}

function toggleAnalysis(imageId) {
    if (!API_KEY) {
        showError(imageId, 'Please set your Google API key in Settings');
        return;
    }
    
    const analysisDiv = document.getElementById('analysis-' + imageId);
    const button = document.getElementById('btn-' + imageId);
    
    if (!analysisDiv || !button) return;
    
    if (!analysisDiv.classList.contains('hidden')) {
        analysisDiv.classList.add('hidden');
        button.textContent = 'Analyze';
        button.classList.remove('bg-purple-200');
        button.classList.add('bg-purple-100');
        return;
    }
    
    analysisDiv.classList.remove('hidden');
    button.textContent = 'Hide';
    button.classList.add('bg-purple-200');
    button.classList.remove('bg-purple-100');
    
    // Check cache
    if (analysisCache.has(imageId)) {
        analysisDiv.innerHTML = analysisCache.get(imageId);
        return;
    }
    
    // Check hash cache for duplicates
    const img = document.querySelector('[data-image-id="' + imageId + '"]');
    if (img && img.dataset.imageHash) {
        const hash = img.dataset.imageHash;
        if (hashAnalysisCache.has(hash)) {
            const cachedAnalysis = hashAnalysisCache.get(hash);
            analysisDiv.innerHTML = cachedAnalysis;
            analysisCache.set(imageId, cachedAnalysis);
            return;
        }
    }
    
    if (analysisInProgress.has(imageId)) return;
    
    if (img) {
        startAnalysis(img, imageId);
    }
}

function startAnalysis(img, imageId) {
    const filename = img.dataset.imageFilename;
    
    if (!filename) {
        showError(imageId, 'Image filename not available');
        return;
    }
    
    analysisInProgress.add(imageId);
    showLoading(imageId);
    readImageFile(filename, imageId);
}

async function readImageFile(filename, imageId) {
    try {
        const response = await fetch('images/' + filename);
        if (response.ok) {
            const blob = await response.blob();
            const base64Data = await blobToBase64(blob);
            analyzeImage(base64Data, imageId);
            return;
        }
        throw new Error('Failed to fetch image');
    } catch (error) {
        // Fallback to canvas method
        const img = document.querySelector('[data-image-id="' + imageId + '"]');
        if (!img) {
            showError(imageId, 'Image element not found');
            analysisInProgress.delete(imageId);
            return;
        }
        
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        canvas.width = img.naturalWidth || img.width;
        canvas.height = img.naturalHeight || img.height;
        ctx.drawImage(img, 0, 0);
        
        const dataURL = canvas.toDataURL('image/jpeg', 0.8);
        const base64Data = dataURL.split(',')[1];
        
        analyzeImage(base64Data, imageId);
    }
}

function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function() {
            const base64 = reader.result.split(',')[1];
            resolve(base64);
        };
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

function showLoading(imageId) {
    const analysisDiv = document.getElementById('analysis-' + imageId);
    if (analysisDiv) {
        analysisDiv.innerHTML = '<div class="analysis-content"><div class="flex items-center space-x-3 py-3"><div class="animate-spin rounded-full h-5 w-5 border-2 border-purple-500 border-t-transparent"></div><div class="text-sm text-gray-600">Analyzing image...</div></div></div>';
    }
}

function showAnalysis(imageId, analysis) {
    const analysisDiv = document.getElementById('analysis-' + imageId);
    const isLong = analysis.length > 400;
    
    // Parse markdown using marked.js
    let parsedAnalysis;
    try {
        parsedAnalysis = marked.parse ? marked.parse(analysis) : marked(analysis);
    } catch (error) {
        console.error('Markdown parsing error:', error);
        parsedAnalysis = analysis.replace(/\\n/g, '<br>');
    }
    
    let content = '<div class="analysis-content' + (isLong ? '' : ' expanded') + '">';
    content += '<div class="flex items-start space-x-2">';
    content += '<svg class="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">';
    content += '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>';
    content += '</svg>';
    content += '<div class="text-xs text-gray-700 leading-relaxed markdown-content">' + parsedAnalysis + '</div>';
    content += '</div>';
    content += '</div>';
    
    if (isLong) {
        content += '<div class="mt-2 text-center">';
        content += '<button onclick="toggleAnalysisExpansion(\\'' + imageId + '\\')" class="text-xs text-purple-600 hover:text-purple-800 font-medium bg-purple-50 px-2 py-1 rounded expand-pill">Show More</button>';
        content += '</div>';
    }
    
    content += '<div class="text-xs text-gray-400 pt-2 border-t border-gray-200 mt-2">Powered by Google Gemini AI</div>';
    
    if (analysisDiv) {
        analysisDiv.innerHTML = content;
        analysisCache.set(imageId, content);
        
        // Cache by hash for duplicates
        const img = document.querySelector('[data-image-id="' + imageId + '"]');
        if (img && img.dataset.imageHash) {
            hashAnalysisCache.set(img.dataset.imageHash, content);
        }
    }
}

function toggleAnalysisExpansion(imageId) {
    const analysisDiv = document.getElementById('analysis-' + imageId);
    if (!analysisDiv) return;
    
    const content = analysisDiv.querySelector('.analysis-content');
    const button = analysisDiv.querySelector('.expand-pill');
    
    if (content.classList.contains('expanded')) {
        content.classList.remove('expanded');
        button.textContent = 'Show More';
    } else {
        content.classList.add('expanded');
        button.textContent = 'Show Less';
    }
}

function showError(imageId, errorMessage) {
    const analysisDiv = document.getElementById('analysis-' + imageId);
    if (analysisDiv) {
        analysisDiv.innerHTML = '<div class="analysis-content"><div class="flex items-center space-x-2 text-red-600"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg><span class="text-xs font-semibold">Error:</span></div><div class="text-xs text-gray-600 mt-1">' + errorMessage + '</div></div>';
    }
}

async function analyzeImage(base64Data, imageId) {
    try {
        if (!API_KEY) {
            throw new Error('No API key provided');
        }
        
        if (!base64Data || base64Data.length < 100) {
            throw new Error('Invalid image data');
        }
        
        const requestBody = {
            contents: [{
                parts: [
                    {
                        text: "Please provide a comprehensive analysis of this image using markdown formatting. Structure your response with clear headers and formatting. Include: **1. Overall Scene Description** - What is the main subject or scene? **2. Visual Elements** - Describe colors, lighting, composition, and style. **3. Text Content** - If there's any text, transcribe it and explain its context. **4. Technical Details** - Charts, graphs, diagrams, or technical content. **5. Objects and People** - Identify and describe any objects, people, or animals. **6. Spatial Relationships** - How elements are positioned relative to each other. **7. Context and Purpose** - What might this image be used for or represent? **8. Quality Assessment** - Image quality, resolution, any artifacts or issues. Use markdown formatting with headers, bold text, lists, and proper structure to make the analysis clear and readable."
                    },
                    {
                        inline_data: {
                            mime_type: "image/jpeg",
                            data: base64Data
                        }
                    }
                ]
            }],
            generationConfig: {
                temperature: 0.3,
                maxOutputTokens: 1000
            }
        };
        
        const response = await fetch('https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite-preview-06-17:generateContent?key=' + API_KEY, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error('API request failed');
        }
        
        const data = await response.json();
        
        if (!data.candidates || !data.candidates[0] || !data.candidates[0].content) {
            throw new Error('Invalid response format');
        }
        
        const analysis = data.candidates[0].content.parts[0].text;
        showAnalysis(imageId, analysis);
        
    } catch (error) {
        showError(imageId, error.message || 'Unknown error occurred');
    } finally {
        analysisInProgress.delete(imageId);
    }
}

// Event listeners
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
        // Also close settings panel
        const panel = document.getElementById('settingsPanel');
        if (panel.classList.contains('show')) {
            toggleSettings();
        }
    }
});

document.getElementById('imageModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

document.addEventListener('DOMContentLoaded', function() {
    console.log('Enhanced PDF Extractor Report loaded');
    console.log('Features: Configurable settings, Modal view, AI analysis with markdown, Pixel similarity detection');
    console.log('Duplicate detection: Hash-based + 99% pixel similarity');
    
    // Initialize settings
    updateMinImageSize();
});
</script>
        """