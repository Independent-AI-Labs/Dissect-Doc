"""
Enhanced HTML Template Module
Contains all HTML, CSS, and JavaScript templates with lazy loading and settings persistence
"""

class HTMLTemplate:
    """Contains all HTML templates and snippets with enhanced functionality"""
    
    @staticmethod
    def get_main_template(filename: str) -> str:
        """Main HTML document template"""
        # Pre-build the CSS and JS to avoid formatting issues
        css_styles = HTMLTemplate.get_css()
        js_script = HTMLTemplate.get_javascript()
        
        template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Analysis Report - {filename}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
{css_styles}
</head>
<body class="bg-gradient-to-br from-blue-50 via-white to-purple-50 min-h-screen">
    <!--MODAL_PLACEHOLDER-->
    <!--SETTINGS_PLACEHOLDER-->
    <!--HEADER_PLACEHOLDER-->
    <!--STATS_PLACEHOLDER-->
    <!--CONTENT_PLACEHOLDER-->
    <!--FOOTER_PLACEHOLDER-->
{js_script}
</body>
</html>"""
        
        return template

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
        
        /* Lazy loading styles */
        .page-section {
            opacity: 0;
            transform: translateY(20px);
            transition: opacity 0.5s ease, transform 0.5s ease;
        }
        
        .page-section.loaded {
            opacity: 1;
            transform: translateY(0);
        }
        
        .intersection-observer-target {
            height: 20px;
            margin: 10px 0;
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
            
            <div>
                <label class="block text-sm font-medium text-gray-700 mb-1">Pages Per Chunk</label>
                <input 
                    type="range" 
                    id="pagesPerChunkSlider"
                    min="10" 
                    max="50" 
                    value="25"
                    class="w-full"
                    onchange="updatePagesPerChunk()"
                >
                <div class="flex justify-between text-xs text-gray-500 mt-1">
                    <span>10</span>
                    <span id="pagesPerChunkValue">25</span>
                    <span>50</span>
                </div>
                <p class="text-xs text-gray-500 mt-1">Number of pages to load at once</p>
            </div>
            
            <div class="pt-3 border-t border-gray-200">
                <button 
                    onclick="saveSettings()"
                    class="w-full bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors mb-2"
                >
                    Save Settings
                </button>
                <button 
                    onclick="applySettingsToUI()"
                    class="w-full bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors mb-2"
                >
                    Apply Now
                </button>
                <button 
                    onclick="debugSettingsState()"
                    class="w-full bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors mb-2"
                >
                    Debug Settings
                </button>
                <button 
                    onclick="resetSettings()"
                    class="w-full bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-md text-sm font-medium transition-colors"
                >
                    Reset to Defaults
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
                        <div class="text-lg font-semibold text-purple-600">AI Analysis & Lazy Loading</div>
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
                    <h3 class="text-lg font-semibold text-gray-900">Display Options</h3>
                    <label class="flex items-center space-x-2 cursor-pointer">
                        <input 
                            type="checkbox" 
                            id="showSmallImages" 
                            onchange="toggleSmallImages()"
                            class="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                        >
                        <span class="text-sm text-gray-700">Show Small & UI Elements ({small_count} images)</span>
                    </label>
                    <label class="flex items-center space-x-2 cursor-pointer">
                        <input 
                            type="checkbox" 
                            id="autoLoadPages" 
                            onchange="toggleAutoLoad()"
                            checked
                            class="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
                        >
                        <span class="text-sm text-gray-700">Auto-load pages on scroll</span>
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
                    Generated by Enhanced PDF Extractor • Powered by PyMuPDF and Google AI • Lazy Loading Enabled
                </p>
            </div>
        </div>
    </div>
        """

    @staticmethod
    def get_javascript() -> str:
        """JavaScript for interactive features with lazy loading and settings persistence"""
        return """<script>
// Global variables
let API_KEY = '';
let MIN_IMAGE_SIZE = 256;
let PAGES_PER_CHUNK = 25;
let AUTO_LOAD_ENABLED = true;
let currentLoadedPages = 0;
let totalPages = 0;
let isLoading = false;
let pagesData = {};
let analysisCache = new Map();
let analysisInProgress = new Set();
let hashAnalysisCache = new Map();
let intersectionObserver = null;

// Settings management
const STORAGE_KEY = 'pdfExtractorSettings';

function loadSettings() {
    try {
        const savedSettings = localStorage.getItem(STORAGE_KEY);
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            API_KEY = settings.apiKey || '';
            MIN_IMAGE_SIZE = settings.minImageSize || 256;
            PAGES_PER_CHUNK = settings.pagesPerChunk || 25;
            AUTO_LOAD_ENABLED = settings.autoLoadEnabled !== false;
            
            // Update UI elements
            const apiInput = document.getElementById('apiKeyInput');
            const sizeSlider = document.getElementById('minImageSizeSlider');
            const chunkSlider = document.getElementById('pagesPerChunkSlider');
            const autoLoadCheck = document.getElementById('autoLoadPages');
            const showSmallCheck = document.getElementById('showSmallImages');
            
            if (apiInput) apiInput.value = API_KEY;
            if (sizeSlider) sizeSlider.value = MIN_IMAGE_SIZE;
            if (chunkSlider) chunkSlider.value = PAGES_PER_CHUNK;
            if (autoLoadCheck) autoLoadCheck.checked = AUTO_LOAD_ENABLED;
            if (showSmallCheck && settings.showSmallImages) {
                showSmallCheck.checked = settings.showSmallImages;
            }
            
            updateMinImageSize();
            updatePagesPerChunk();
            
            // Apply settings immediately
            applySettingsToUI();
        }
    } catch (error) {
        console.error('Error loading settings:', error);
    }
}

function applySettingsToUI() {
    console.log('Applying settings to UI...');
    console.log('API_KEY:', API_KEY ? `Set (${API_KEY.length} chars)` : 'Not set');
    console.log('MIN_IMAGE_SIZE:', MIN_IMAGE_SIZE);
    
    // Apply API key settings - show/hide AI buttons and sections
    if (API_KEY && API_KEY.trim() !== '') {
        console.log('API key found, enabling AI features');
        enableAIFeatures();
    } else {
        console.log('No API key, disabling AI features');
        disableAIFeatures();
    }
    
    // Apply small images setting
    const showSmallCheck = document.getElementById('showSmallImages');
    if (showSmallCheck && showSmallCheck.checked) {
        console.log('Applying small images visibility');
        toggleSmallImages();
    }
    
    // Apply auto-load setting
    if (AUTO_LOAD_ENABLED) {
        setupIntersectionObserver();
    }
    
    // Update image size filter display
    updateImageSizeDisplay();
}

function enableAIFeatures() {
    // Show all AI buttons that are currently hidden
    const aiButtons = document.querySelectorAll('[onclick*="analyzeImageFromButton"]');
    aiButtons.forEach(button => {
        button.style.display = 'flex';
        console.log('Showing AI button:', button);
    });
    
    // Show AI analysis sections that are currently hidden
    const aiSections = document.querySelectorAll('.ai-analysis-section');
    aiSections.forEach(section => {
        section.style.display = 'block';
        console.log('Showing AI section:', section);
    });
    
    // Also check for any AI elements that might be in newly loaded content
    const allImageCards = document.querySelectorAll('.relative.group');
    allImageCards.forEach(card => {
        const isSmallImage = card.querySelector('.h-20'); // Small images have h-20 class
        if (!isSmallImage) {
            // This is a regular image, should have AI features
            let aiButton = card.querySelector('[onclick*="analyzeImageFromButton"]');
            let aiSection = card.querySelector('.ai-analysis-section');
            
            // If AI button doesn't exist, create it
            if (!aiButton) {
                const imageContainer = card.querySelector('.aspect-w-16');
                if (imageContainer) {
                    const buttonHTML = `
                        <button 
                            class="absolute top-2 right-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-3 py-1 rounded-full text-xs font-semibold opacity-0 group-hover:opacity-100 transition-all duration-200 flex items-center space-x-1 cursor-pointer shadow-lg ai-analysis-button"
                            onclick="analyzeImageFromButton(this, event)"
                            title="Click for AI analysis"
                        >
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                            <span>AI</span>
                        </button>
                    `;
                    imageContainer.insertAdjacentHTML('beforeend', buttonHTML);
                }
            } else {
                aiButton.style.display = 'flex';
            }
            
            // If AI section doesn't exist, create it
            if (!aiSection) {
                const cardContent = card.querySelector('.p-3, .p-2');
                if (cardContent) {
                    const img = card.querySelector('img');
                    if (img) {
                        const imageId = img.dataset.imageId;
                        if (imageId) {
                            const sectionHTML = `
                                <div class="mt-3 pt-3 border-t border-gray-100 ai-analysis-section">
                                    <div class="flex items-center justify-between mb-2">
                                        <span class="text-xs font-semibold text-purple-600 flex items-center">
                                            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                                            </svg>
                                            AI Analysis
                                        </span>
                                        <button 
                                            class="text-xs bg-purple-100 hover:bg-purple-200 text-purple-700 px-2 py-1 rounded transition-colors"
                                            onclick="toggleAnalysis('${imageId}')"
                                            id="btn-${imageId}"
                                        >
                                            Analyze
                                        </button>
                                    </div>
                                    <div 
                                        id="analysis-${imageId}" 
                                        class="text-xs text-gray-600 hidden"
                                    >
                                        <div class="flex items-center justify-center py-4 bg-gray-50 rounded">
                                            <span class="text-gray-400">Click "Analyze" to get detailed AI description</span>
                                        </div>
                                    </div>
                                </div>
                            `;
                            cardContent.insertAdjacentHTML('beforeend', sectionHTML);
                        }
                    }
                }
            } else {
                aiSection.style.display = 'block';
            }
        }
    });
    
    console.log(`AI features enabled for ${aiButtons.length} buttons and ${aiSections.length} sections`);
}

function disableAIFeatures() {
    // Hide all AI buttons
    const aiButtons = document.querySelectorAll('[onclick*="analyzeImageFromButton"], .ai-analysis-button');
    aiButtons.forEach(button => {
        button.style.display = 'none';
    });
    
    // Hide AI analysis sections
    const aiSections = document.querySelectorAll('.ai-analysis-section');
    aiSections.forEach(section => {
        section.style.display = 'none';
    });
    
    console.log(`AI features disabled for ${aiButtons.length} buttons and ${aiSections.length} sections`);
}

function updateImageSizeDisplay() {
    // Update the filter description
    const filterDescriptions = document.querySelectorAll('.text-sm.text-gray-500');
    filterDescriptions.forEach(desc => {
        if (desc.textContent.includes('Small images are')) {
            desc.textContent = `Small images are <${MIN_IMAGE_SIZE}×${MIN_IMAGE_SIZE} pixels`;
        }
    });
    
    // Note: Full re-filtering would require regenerating content
    // For now, we'll just update the display text
    console.log(`Image size filter display updated to ${MIN_IMAGE_SIZE}px`);
}

function saveSettings() {
    try {
        const settings = {
            apiKey: API_KEY,
            minImageSize: MIN_IMAGE_SIZE,
            pagesPerChunk: PAGES_PER_CHUNK,
            autoLoadEnabled: AUTO_LOAD_ENABLED,
            timestamp: new Date().toISOString()
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
        
        // Show feedback
        const button = document.querySelector('button[onclick="saveSettings()"]');
        if (button) {
            const originalText = button.textContent;
            button.textContent = 'Saved!';
            button.classList.remove('bg-purple-600', 'hover:bg-purple-700');
            button.classList.add('bg-green-600', 'hover:bg-green-700');
            setTimeout(() => {
                button.textContent = originalText;
                button.classList.remove('bg-green-600', 'hover:bg-green-700');
                button.classList.add('bg-purple-600', 'hover:bg-purple-700');
            }, 2000);
        }
        console.log('Settings saved successfully');
    } catch (error) {
        console.error('Error saving settings:', error);
    }
}

function resetSettings() {
    try {
        localStorage.removeItem(STORAGE_KEY);
        
        // Reset to defaults
        API_KEY = '';
        MIN_IMAGE_SIZE = 256;
        PAGES_PER_CHUNK = 25;
        AUTO_LOAD_ENABLED = true;
        
        // Update UI
        const apiInput = document.getElementById('apiKeyInput');
        const sizeSlider = document.getElementById('minImageSizeSlider');
        const chunkSlider = document.getElementById('pagesPerChunkSlider');
        const autoLoadCheck = document.getElementById('autoLoadPages');
        
        if (apiInput) apiInput.value = '';
        if (sizeSlider) sizeSlider.value = 256;
        if (chunkSlider) chunkSlider.value = 25;
        if (autoLoadCheck) autoLoadCheck.checked = true;
        
        updateMinImageSize();
        updatePagesPerChunk();
        
        console.log('Settings reset to defaults');
        location.reload(); // Reload to apply changes
    } catch (error) {
        console.error('Error resetting settings:', error);
    }
}

// Settings panel functions
function toggleSettings() {
    const panel = document.getElementById('settingsPanel');
    if (panel) {
        panel.classList.toggle('show');
    }
}

function updateAPIKey() {
    const input = document.getElementById('apiKeyInput');
    if (input) {
        API_KEY = input.value.trim();
        console.log('API Key updated:', API_KEY ? 'Set' : 'Empty');
    }
}

function updateMinImageSize() {
    const slider = document.getElementById('minImageSizeSlider');
    const valueDisplay = document.getElementById('minImageSizeValue');
    if (slider && valueDisplay) {
        MIN_IMAGE_SIZE = parseInt(slider.value);
        valueDisplay.textContent = MIN_IMAGE_SIZE + 'px';
    }
}

function updatePagesPerChunk() {
    const slider = document.getElementById('pagesPerChunkSlider');
    const valueDisplay = document.getElementById('pagesPerChunkValue');
    if (slider && valueDisplay) {
        PAGES_PER_CHUNK = parseInt(slider.value);
        valueDisplay.textContent = PAGES_PER_CHUNK;
    }
}

function toggleAutoLoad() {
    const checkbox = document.getElementById('autoLoadPages');
    if (checkbox) {
        AUTO_LOAD_ENABLED = checkbox.checked;
        if (AUTO_LOAD_ENABLED) {
            setupIntersectionObserver();
        } else {
            if (intersectionObserver) {
                intersectionObserver.disconnect();
            }
        }
    }
}

function toggleSmallImages() {
    const checkbox = document.getElementById('showSmallImages');
    const smallImageContainers = document.querySelectorAll('.small-images');
    
    if (checkbox && smallImageContainers) {
        const isChecked = checkbox.checked;
        console.log(`Toggling small images: ${isChecked ? 'show' : 'hide'}`);
        
        smallImageContainers.forEach(container => {
            if (isChecked) {
                container.classList.add('show');
                container.style.display = 'block';
            } else {
                container.classList.remove('show');
                container.style.display = 'none';
            }
        });
        
        // Save this setting immediately
        const savedSettings = localStorage.getItem(STORAGE_KEY);
        if (savedSettings) {
            try {
                const settings = JSON.parse(savedSettings);
                settings.showSmallImages = isChecked;
                localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
            } catch (error) {
                console.error('Error updating small images setting:', error);
            }
        }
    }
}

// Lazy loading functions
async function loadPagesData() {
    try {
        const response = await fetch(window.location.pathname.replace('_report.html', '_pages.json'));
        if (response.ok) {
            pagesData = await response.json();
            totalPages = Object.keys(pagesData).length;
            console.log(`Loaded data for ${totalPages} pages`);
            return true;
        }
    } catch (error) {
        console.error('Error loading pages data:', error);
    }
    return false;
}

function renderPageFromData(pageNumber) {
    const pageData = pagesData[pageNumber.toString()];
    if (!pageData) return '';
    
    const page_images = pageData.images || [];
    const regular_page_images = page_images.filter(img => 
        (img.width || 0) >= MIN_IMAGE_SIZE && (img.height || 0) >= MIN_IMAGE_SIZE
    );
    const small_page_images = page_images.filter(img => 
        (img.width || 0) < MIN_IMAGE_SIZE || (img.height || 0) < MIN_IMAGE_SIZE
    );
    
    return `
        <div class="bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden page-section" data-page="${pageNumber}">
            <div class="bg-gradient-to-r from-blue-600 to-purple-600 px-6 py-4">
                <h2 class="text-xl font-semibold text-white flex items-center">
                    <span class="bg-white bg-opacity-20 rounded-full w-8 h-8 flex items-center justify-center mr-3 text-sm">
                        ${pageNumber}
                    </span>
                    Page ${pageNumber}
                    <span class="ml-auto flex items-center space-x-3 text-sm">
                        <span class="bg-white bg-opacity-20 px-2 py-1 rounded-full">
                            ${pageData.word_count.toLocaleString()} words
                        </span>
                        <span class="bg-white bg-opacity-20 px-2 py-1 rounded-full">
                            ${pageData.token_count.toLocaleString()} tokens
                        </span>
                        <span class="bg-white bg-opacity-20 px-2 py-1 rounded-full">
                            ${regular_page_images.length} images
                        </span>
                        ${small_page_images.length > 0 ? `<span class="bg-white bg-opacity-20 px-2 py-1 rounded-full text-xs">${small_page_images.length} small</span>` : ''}
                    </span>
                </h2>
            </div>
            
            <div class="p-6">
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div class="space-y-6">
                        <div>
                            <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                                <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                                </svg>
                                Text Content
                            </h3>
                            <div class="bg-gray-50 rounded-lg p-4 max-h-96 overflow-y-auto">
                                <pre class="text-sm text-gray-700 whitespace-pre-wrap font-mono leading-relaxed">${pageData.text.substring(0, 2000)}${pageData.text.length > 2000 ? '...' : ''}</pre>
                            </div>
                        </div>
                    </div>
                    
                    <div class="space-y-6">
                        ${generateImagesSection(regular_page_images, small_page_images)}
                    </div>
                </div>
            </div>
        </div>
    `;
}

function generateImagesSection(regular_images, small_images) {
    let content = `
        <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 002 2z"></path>
                </svg>
                Images (${regular_images.length} regular${small_images.length > 0 ? `, ${small_images.length} small` : ''})
            </h3>
    `;
    
    if (regular_images.length === 0 && small_images.length === 0) {
        content += `
            <div class="bg-gray-50 rounded-lg p-8 text-center">
                <svg class="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 002 2z"></path>
                </svg>
                <p class="text-gray-500">No images found on this page</p>
            </div>
        `;
    } else {
        if (regular_images.length > 0) {
            content += `<div class="grid grid-cols-1 sm:grid-cols-2 gap-4 regular-images">`;
            regular_images.forEach(img => {
                content += generateImageCard(img, false);
            });
            content += `</div>`;
        }
        
        if (small_images.length > 0) {
            content += `
                <div class="small-images mt-6">
                    <div class="mb-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                        <div class="flex items-center">
                            <svg class="w-5 h-5 text-yellow-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                            </svg>
                            <span class="text-sm font-medium text-yellow-800">Small Images & UI Elements</span>
                        </div>
                        <p class="text-xs text-yellow-600 mt-1">These images are smaller than ${MIN_IMAGE_SIZE}×${MIN_IMAGE_SIZE} pixels and likely contain UI elements, icons, or decorative graphics</p>
                    </div>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-2">
            `;
            small_images.forEach(img => {
                content += generateImageCard(img, true);
            });
            content += `
                    </div>
                </div>
            `;
        }
    }
    
    content += `</div>`;
    return content;
}

function generateImageCard(img, isSmall) {
    if (!img.filename) {
        return `
            <div class="bg-red-50 border border-red-200 rounded-lg p-4">
                <div class="flex items-center">
                    <svg class="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    <span class="text-sm text-red-700">Failed to extract image ${img.index}</span>
                </div>
            </div>
        `;
    }
    
    const cardClass = "bg-white rounded-lg border border-gray-200 overflow-hidden shadow-sm hover:shadow-md transition-shadow";
    const imageClass = isSmall ? 
        "w-full h-20 object-contain clickable-image hover:scale-105 transition-transform duration-200" :
        "w-full h-48 object-contain clickable-image hover:scale-105 transition-transform duration-200";
    const paddingClass = isSmall ? "p-2" : "p-3";
    
    const fileSize = formatBytes(img.size_bytes || 0);
    const hashShort = (img.hash || '').substring(0, 8);
    
    // Check if AI features should be shown
    const showAI = API_KEY && API_KEY.trim() !== '' && !isSmall;
    
    return `
        <div class="relative group">
            <div class="${cardClass}">
                <div class="aspect-w-16 aspect-h-9 bg-gray-100 relative" onclick="openModal('${img.filename}', '${img.page}', '${img.index}', '${img.width}', '${img.height}', '${img.format || 'unknown'}', '${fileSize}', '${hashShort}')">
                    <img 
                        src="images/${img.filename}" 
                        alt="Page ${img.page} Image ${img.index}"
                        class="${imageClass}"
                        data-image-id="${img.page}_${img.index}"
                        data-image-filename="${img.filename}"
                        data-image-hash="${img.hash || ''}"
                        loading="lazy"
                    >
                    <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-opacity duration-200"></div>
                    <div class="unique-indicator">UNIQUE</div>
                    
                    ${showAI ? `
                    <button 
                        class="absolute top-2 right-2 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white px-3 py-1 rounded-full text-xs font-semibold opacity-0 group-hover:opacity-100 transition-all duration-200 flex items-center space-x-1 cursor-pointer shadow-lg ai-analysis-button"
                        onclick="analyzeImageFromButton(this, event)"
                        title="Click for AI analysis"
                    >
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                        </svg>
                        <span>AI</span>
                    </button>` : ''}
                    
                    <div class="absolute bottom-1 right-1 bg-black bg-opacity-60 text-white px-1 py-0.5 rounded text-xs opacity-0 group-hover:opacity-100 transition-opacity duration-200 expand-pill">
                        Expand
                    </div>
                </div>
                <div class="${paddingClass}">
                    <div class="flex items-center justify-between text-xs text-gray-600">
                        <span class="font-medium">Image ${img.index}</span>
                        <span class="bg-gray-100 px-1 py-0.5 rounded text-xs">${(img.format || 'unknown').toUpperCase()}</span>
                    </div>
                    ${!isSmall ? `<div class="mt-1 text-xs text-gray-500"><span>${img.width} × ${img.height}</span></div>` : ''}
                    ${showAI ? generateAIAnalysisSection(img) : ''}
                </div>
            </div>
        </div>
    `;
}

function generateAIAnalysisSection(img) {
    const imageId = `${img.page}_${img.index}`;
    
    return `
        <div class="mt-3 pt-3 border-t border-gray-100 ai-analysis-section">
            <div class="flex items-center justify-between mb-2">
                <span class="text-xs font-semibold text-purple-600 flex items-center">
                    <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                    </svg>
                    AI Analysis
                </span>
                <button 
                    class="text-xs bg-purple-100 hover:bg-purple-200 text-purple-700 px-2 py-1 rounded transition-colors"
                    onclick="toggleAnalysis('${imageId}')"
                    id="btn-${imageId}"
                >
                    Analyze
                </button>
            </div>
            <div 
                id="analysis-${imageId}" 
                class="text-xs text-gray-600 hidden"
            >
                <div class="flex items-center justify-center py-4 bg-gray-50 rounded">
                    <span class="text-gray-400">Click "Analyze" to get detailed AI description</span>
                </div>
            </div>
        </div>
    `;
}

function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

async function loadMorePages() {
    if (isLoading || currentLoadedPages >= totalPages) return;
    
    isLoading = true;
    const loadBtn = document.getElementById('loadMoreBtn');
    const loadContainer = document.getElementById('loadMoreContainer');
    const lazyPages = document.getElementById('lazyPages');
    const endIndicator = document.getElementById('endIndicator');
    
    if (loadBtn) {
        loadBtn.disabled = true;
        loadBtn.innerHTML = '<svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>Loading...';
    }
    
    // Load next chunk of pages
    const startPage = currentLoadedPages + 1;
    const endPage = Math.min(startPage + PAGES_PER_CHUNK - 1, totalPages);
    
    let newPagesHtml = '';
    for (let pageNum = startPage; pageNum <= endPage; pageNum++) {
        newPagesHtml += renderPageFromData(pageNum);
    }
    
    if (lazyPages && newPagesHtml) {
        lazyPages.insertAdjacentHTML('beforeend', newPagesHtml);
        
        // Animate in new pages
        const newPages = lazyPages.querySelectorAll('.page-section:not(.loaded)');
        newPages.forEach((page, index) => {
            setTimeout(() => {
                page.classList.add('loaded');
            }, index * 100);
        });
        
        currentLoadedPages = endPage;
    }
    
    // Update load more button
    if (loadBtn) {
        loadBtn.disabled = false;
        if (currentLoadedPages >= totalPages) {
            loadContainer.style.display = 'none';
            endIndicator.style.display = 'block';
        } else {
            const remaining = totalPages - currentLoadedPages;
            const nextChunkSize = Math.min(PAGES_PER_CHUNK, remaining);
            loadBtn.innerHTML = `Load More Pages (${nextChunkSize} more)`;
        }
    }
    
    isLoading = false;
}

function setupIntersectionObserver() {
    if (!AUTO_LOAD_ENABLED || intersectionObserver) return;
    
    intersectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting && !isLoading && currentLoadedPages < totalPages) {
                loadMorePages();
            }
        });
    }, {
        rootMargin: '100px'
    });
    
    // Observe the load more container
    const loadContainer = document.getElementById('loadMoreContainer');
    if (loadContainer) {
        intersectionObserver.observe(loadContainer);
    }
}

// Modal functions
function openModal(filename, page, index, width, height, format, fileSize, hash) {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalInfo = document.getElementById('modalImageInfo');
    
    if (modal && modalImage && modalInfo) {
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
}

function closeModal() {
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.classList.remove('show');
        document.body.style.overflow = 'auto';
    }
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
    
    if (analysisCache.has(imageId)) {
        analysisDiv.innerHTML = analysisCache.get(imageId);
        return;
    }
    
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
        content += '<button onclick="toggleAnalysisExpansion(' + "'" + imageId + "'" + ')" class="text-xs text-purple-600 hover:text-purple-800 font-medium bg-purple-50 px-2 py-1 rounded expand-pill">Show More</button>';
        content += '</div>';
    }
    
    content += '<div class="text-xs text-gray-400 pt-2 border-t border-gray-200 mt-2">Powered by Google Gemini AI</div>';
    
    if (analysisDiv) {
        analysisDiv.innerHTML = content;
        analysisCache.set(imageId, content);
        
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
    
    if (content && button) {
        if (content.classList.contains('expanded')) {
            content.classList.remove('expanded');
            button.textContent = 'Show More';
        } else {
            content.classList.add('expanded');
            button.textContent = 'Show Less';
        }
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

// Initialization
document.addEventListener('DOMContentLoaded', async function() {
    console.log('Enhanced PDF Extractor Report loaded');
    console.log('Features: Lazy loading, Configurable settings, Modal view, AI analysis with markdown, Pixel similarity detection');
    console.log('Duplicate detection: Hash-based + 99% pixel similarity');
    
    // Load saved settings FIRST
    loadSettings();
    
    // Load pages data for lazy loading
    const dataLoaded = await loadPagesData();
    if (dataLoaded) {
        console.log(`Data loaded for ${totalPages} pages`);
        
        // Set initial loaded pages count based on what's already rendered
        const initialPages = document.querySelectorAll('#initialPages .page-section');
        currentLoadedPages = initialPages.length;
        
        // Animate in initial pages
        initialPages.forEach((page, index) => {
            setTimeout(() => {
                page.classList.add('loaded');
            }, index * 100);
        });
        
        // Show load more button if there are more pages
        if (currentLoadedPages < totalPages) {
            const loadContainer = document.getElementById('loadMoreContainer');
            if (loadContainer) {
                loadContainer.style.display = 'block';
                const remaining = totalPages - currentLoadedPages;
                const nextChunkSize = Math.min(PAGES_PER_CHUNK, remaining);
                const loadBtn = document.getElementById('loadMoreBtn');
                if (loadBtn) {
                    loadBtn.innerHTML = `Load More Pages (${nextChunkSize} more)`;
                }
            }
        } else {
            // All pages are already loaded, show end indicator
            const endIndicator = document.getElementById('endIndicator');
            if (endIndicator) {
                endIndicator.style.display = 'block';
            }
        }
        
        // Setup intersection observer for auto-loading
        if (AUTO_LOAD_ENABLED) {
            setupIntersectionObserver();
        }
    } else {
        console.warn('Could not load pages data for lazy loading');
        // Hide loading indicator if data couldn't be loaded
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.style.display = 'none';
        }
    }
    
    // Hide loading indicator
    const loadingIndicator = document.getElementById('loadingIndicator');
    if (loadingIndicator) {
        setTimeout(() => {
            loadingIndicator.style.display = 'none';
        }, 1000);
    }
    
    // Apply settings to current page content AFTER everything is loaded
    setTimeout(() => {
        applySettingsToUI();
        console.log('Settings applied to UI');
    }, 1500);
    
    // Add modal click handler
    const modal = document.getElementById('imageModal');
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
    }
    
    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeModal();
            const panel = document.getElementById('settingsPanel');
            if (panel && panel.classList.contains('show')) {
                toggleSettings();
            }
        }
        
        // Ctrl/Cmd + S to save settings
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            saveSettings();
        }
        
        // Ctrl/Cmd + L to load more pages
        if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
            e.preventDefault();
            loadMorePages();
        }
    });
    
    console.log('Keyboard shortcuts: ESC (close modals), Ctrl+S (save settings), Ctrl+L (load more pages)');
});

// Window load event for final setup
window.addEventListener('load', function() {
    console.log('All resources loaded, report ready!');
    
    // Final check for any settings that need to be applied
    const showSmallImagesCheckbox = document.getElementById('showSmallImages');
    if (showSmallImagesCheckbox) {
        // Apply saved small images setting if any
        const savedSettings = localStorage.getItem(STORAGE_KEY);
        if (savedSettings) {
            try {
                const settings = JSON.parse(savedSettings);
                if (settings.showSmallImages) {
                    showSmallImagesCheckbox.checked = true;
                    toggleSmallImages();
                }
            } catch (error) {
                console.error('Error applying saved small images setting:', error);
            }
        }
    }
});

// Debug function to check current state
function debugSettingsState() {
    console.log('=== SETTINGS DEBUG ===');
    console.log('API_KEY:', API_KEY ? `"${API_KEY.substring(0, 10)}..." (${API_KEY.length} chars)` : 'NOT SET');
    console.log('MIN_IMAGE_SIZE:', MIN_IMAGE_SIZE);
    console.log('PAGES_PER_CHUNK:', PAGES_PER_CHUNK);
    console.log('AUTO_LOAD_ENABLED:', AUTO_LOAD_ENABLED);
    
    // Check UI elements
    const apiInput = document.getElementById('apiKeyInput');
    console.log('API Input value:', apiInput ? `"${apiInput.value.substring(0, 10)}..." (${apiInput.value.length} chars)` : 'NOT FOUND');
    
    // Check AI elements
    const aiButtons = document.querySelectorAll('[onclick*="analyzeImageFromButton"]');
    const aiSections = document.querySelectorAll('.ai-analysis-section');
    console.log('AI buttons found:', aiButtons.length);
    console.log('AI sections found:', aiSections.length);
    
    // Check their visibility
    let visibleButtons = 0, visibleSections = 0;
    aiButtons.forEach(btn => {
        if (btn.style.display !== 'none') visibleButtons++;
    });
    aiSections.forEach(section => {
        if (section.style.display !== 'none') visibleSections++;
    });
    
    console.log('Visible AI buttons:', visibleButtons);
    console.log('Visible AI sections:', visibleSections);
    
    // Check small images
    const smallImageContainers = document.querySelectorAll('.small-images');
    let visibleSmallContainers = 0;
    smallImageContainers.forEach(container => {
        if (container.classList.contains('show')) visibleSmallContainers++;
    });
    console.log('Small image containers:', smallImageContainers.length);
    console.log('Visible small containers:', visibleSmallContainers);
    
    console.log('=== END DEBUG ===');
}

// Export functions for global access
window.debugSettingsState = debugSettingsState;
window.toggleSettings = toggleSettings;
window.updateAPIKey = updateAPIKey;
window.updateMinImageSize = updateMinImageSize;
window.updatePagesPerChunk = updatePagesPerChunk;
window.saveSettings = saveSettings;
window.resetSettings = resetSettings;
window.toggleAutoLoad = toggleAutoLoad;
window.toggleSmallImages = toggleSmallImages;
window.loadMorePages = loadMorePages;
window.openModal = openModal;
window.closeModal = closeModal;
window.analyzeImageFromButton = analyzeImageFromButton;
window.toggleAnalysis = toggleAnalysis;
window.toggleAnalysisExpansion = toggleAnalysisExpansion;
</script>"""