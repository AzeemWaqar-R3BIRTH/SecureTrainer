/**
 * Learning Center JavaScript Module
 * Handles content loading, progress tracking, and interactive learning features
 */

// Ensure SecureTrainer namespace exists
if (typeof SecureTrainer === 'undefined') {
    window.SecureTrainer = {};
}

SecureTrainer.LearningCenter = {
    // Learning state
    currentSection: 'intro',
    completedSections: new Set(),
    contentCache: new Map(),
    studyStartTime: null,
    totalStudyTime: 0,

    // Initialize Learning Center
    init() {
        console.log('📚 Learning Center initializing...');
        this.setupEventHandlers();
        this.loadInitialContent();
        this.loadProgressData();
        this.startStudyTimer();
        this.setupProgressToggle();
        console.log('📚 Learning Center initialized successfully');
    },

    // Setup event handlers
    setupEventHandlers() {
        // Content search
        const searchInput = document.getElementById('content-search');
        if (searchInput) {
            searchInput.addEventListener('input', SecureTrainer.Utils.debounce((e) => {
                this.performSearch(e.target.value);
            }, 300));
        }

        // Navigation clicks
        document.addEventListener('click', (event) => {
            if (event.target.matches('.nav-link') || event.target.closest('.nav-link')) {
                event.preventDefault();
                const link = event.target.matches('.nav-link') ? event.target : event.target.closest('.nav-link');
                const content = link.dataset.content;
                if (content) {
                    this.loadContent(content);
                }
            }
        });

        // Content navigation
        const prevBtn = document.getElementById('prev-content');
        const nextBtn = document.getElementById('next-content');

        if (prevBtn) prevBtn.addEventListener('click', () => this.navigateContent('prev'));
        if (nextBtn) nextBtn.addEventListener('click', () => this.navigateContent('next'));

        // Module completion checkbox handler
        document.addEventListener('change', (event) => {
            if (event.target.classList.contains('module-complete-checkbox')) {
                const moduleId = event.target.dataset.moduleId;
                const isChecked = event.target.checked;
                this.handleModuleCompletion(moduleId, isChecked);
            }
        });
    },

    // Load initial content
    async loadInitialContent() {
        try {
            // Check URL hash first
            const hash = window.location.hash.substring(1);
            const initialSection = hash || 'intro';
            console.log(`Loading initial content: ${initialSection}`);
            await this.loadContent(initialSection);
        } catch (error) {
            console.error('Failed to load initial content:', error);
            this.showErrorState('Failed to load initial content. Please refresh the page.');
        }
    },

    // Load content by section
    async loadContent(sectionId) {
        try {
            console.log(`📚 Loading content for section: ${sectionId}`);

            // Update navigation state
            this.updateNavigationState(sectionId);

            // Check cache first
            if (this.contentCache.has(sectionId)) {
                console.log(`📚 Loading ${sectionId} from cache`);
                this.renderContent(this.contentCache.get(sectionId));
            } else {
                // Show loading state
                this.showLoadingState();

                // Load content from API
                console.log(`📚 Fetching content for ${sectionId}...`);
                const content = await this.fetchContent(sectionId);
                console.log(`📚 Content fetched:`, content);
                this.contentCache.set(sectionId, content);
                this.renderContent(content);
            }

            this.currentSection = sectionId;
            window.location.hash = sectionId;

        } catch (error) {
            console.error('Failed to load content:', error);
            this.showErrorState('Failed to load content. Please try again.');
        }
    },

    // Fetch content data from API
    async fetchContent(sectionId) {
        try {
            const response = await fetch(`/api/learning/content/${sectionId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            if (!data.success) {
                throw new Error(data.error || 'Failed to fetch content');
            }
            return data.content;
        } catch (error) {
            console.error(`Error fetching content for ${sectionId}:`, error);
            throw error;
        }
    },

    // Render content
    renderContent(content) {
        console.log(`📚 Rendering content:`, content);
        const contentArea = document.getElementById('content-area');
        if (contentArea && content) {

            // Hide default content
            const defaultContent = document.getElementById('default-content');
            if (defaultContent) {
                defaultContent.style.display = 'none';
            }

            // Generate HTML structure
            const htmlContent = this.generateContentHTML(content);

            // Update breadcrumb
            const currentSection = document.getElementById('current-section');
            if (currentSection) {
                currentSection.textContent = content.title;
            }

            // Set the new content
            contentArea.innerHTML = htmlContent;

            // Update page title
            document.title = `${content.title} - SecureTrainer`;

            // Scroll to top
            contentArea.scrollTop = 0;

            // Add smooth transition
            contentArea.style.opacity = '0';
            setTimeout(() => {
                contentArea.style.opacity = '1';
            }, 100);

            console.log(`📚 Content rendered successfully`);
        } else {
            console.error(`📚 Failed to render content:`, { contentArea, content });
        }
    },

    // Generate HTML from structured content
    generateContentHTML(content) {
        let html = `<h1 class="text-3xl font-bold mb-4 text-gray-800">${content.title}</h1>`;

        if (content.description) {
            html += `<p class="text-lg text-gray-600 mb-8">${content.description}</p>`;
        }

        if (content.sections) {
            content.sections.forEach(section => {
                html += `<div class="mb-8 section-block" id="${section.id}">`;

                if (section.title) {
                    html += `<h2 class="text-2xl font-semibold mb-4 text-gray-800">${section.title}</h2>`;
                }

                switch (section.type) {
                    case 'text':
                        html += `<div class="prose max-w-none text-gray-700">${section.content}</div>`;
                        break;

                    case 'video':
                        // Convert regular YouTube URL to nocookie embed URL
                        let embedUrl = section.video_url;
                        if (embedUrl.includes('youtube.com/embed/')) {
                            embedUrl = embedUrl.replace('youtube.com', 'youtube-nocookie.com');
                        }
                        html += `
                            <div class="video-container mb-4 rounded-lg overflow-hidden shadow-lg">
                                <iframe src="${embedUrl}?rel=0&modestbranding=1" 
                                        title="${section.title}" 
                                        frameborder="0" 
                                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                                        referrerpolicy="strict-origin-when-cross-origin"
                                        allowfullscreen
                                        class="w-full aspect-video">
                                </iframe>
                            </div>`;
                        break;

                    case 'interactive':
                        html += `
                            <div class="interactive-demo-container bg-blue-50 border border-blue-200 rounded-lg p-6">
                                <div class="flex items-start mb-4">
                                    <div class="flex-shrink-0 bg-blue-100 rounded-full p-3 mr-4">
                                        <i class="fas fa-flask text-blue-600 text-xl"></i>
                                    </div>
                                    <div>
                                        <h3 class="text-lg font-semibold text-blue-900">Interactive Challenge</h3>
                                        <p class="text-blue-800 mb-4">${section.content}</p>
                                        ${section.challenge_id ? `
                                            <a href="/challenges?start=${section.challenge_id}" class="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors">
                                                <i class="fas fa-play mr-2"></i> Start Challenge
                                            </a>
                                        ` : ''}
                                    </div>
                                </div>
                            </div>`;
                        break;

                    case 'resource':
                        if (section.resources) {
                            html += `<div class="grid grid-cols-1 md:grid-cols-2 gap-4">`;
                            section.resources.forEach(res => {
                                html += `
                                    <a href="${res.url}" target="_blank" class="flex items-center p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow group">
                                        <div class="flex-shrink-0 w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mr-4 group-hover:bg-blue-100 transition-colors">
                                            <i class="${res.icon || 'fas fa-file-download'} text-gray-500 group-hover:text-blue-600"></i>
                                        </div>
                                        <div>
                                            <h4 class="font-medium text-gray-900 group-hover:text-blue-600 transition-colors">${res.title}</h4>
                                            <p class="text-sm text-gray-500">Download Resource</p>
                                        </div>
                                    </a>`;
                            });
                            html += `</div>`;
                        } else if (section.resource_url) {
                            html += `
                                <a href="${section.resource_url}" target="_blank" class="inline-flex items-center p-4 bg-white border border-gray-200 rounded-lg hover:shadow-md transition-shadow group">
                                    <i class="fas fa-file-download text-gray-500 mr-3 group-hover:text-blue-600"></i>
                                    <span class="font-medium text-gray-900 group-hover:text-blue-600">${section.content}</span>
                                </a>`;
                        }
                        break;
                }

                html += `</div>`;
            });
        }

        // Add completion checkbox at the end
        // Check if module is already completed from user_progress
        const isCompleted = content.user_progress && content.user_progress.is_complete ? 'checked' : '';
        
        html += `
            <div class="module-completion-section" style="margin-top: 3rem; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 1rem; text-align: center;">
                <div style="background: rgba(255,255,255,0.95); padding: 2rem; border-radius: 0.75rem;">
                    <h3 style="font-size: 1.5rem; font-weight: 700; color: #1f2937; margin-bottom: 1rem;">
                        <i class="fas fa-check-circle" style="color: #10b981; margin-right: 0.5rem;"></i>
                        Mark Module as Complete
                    </h3>
                    <p style="color: #6b7280; margin-bottom: 1.5rem;">
                        I have finished reviewing all the content in this module
                    </p>
                    <label class="completion-checkbox-label" style="display: inline-flex; align-items: center; cursor: pointer; font-size: 1.1rem; font-weight: 600; color: #374151;">
                        <input type="checkbox" id="module-complete-checkbox-${content.id}" 
                               class="module-complete-checkbox" 
                               data-module-id="${content.id}"
                               ${isCompleted}
                               style="width: 24px; height: 24px; margin-right: 0.75rem; cursor: pointer; accent-color: #10b981;">
                        <span>I have completed this module</span>
                    </label>
                </div>
            </div>
        `;

        return html;
    },

    // Update navigation state
    updateNavigationState(sectionId) {
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            // Check if the link's data-content matches the sectionId
            if (link.dataset.content === sectionId) {
                link.classList.add('active');

                // Update progress indicator visuals if needed
                const indicator = link.querySelector('.nav-progress-indicator');
                if (indicator) {
                    // Logic to update dots could go here
                }
            }
        });
    },

    // Show loading state
    showLoadingState() {
        const contentArea = document.getElementById('content-area');
        if (contentArea) {
            // Hide default content
            const defaultContent = document.getElementById('default-content');
            if (defaultContent) {
                defaultContent.style.display = 'none';
            }

            contentArea.innerHTML = `
                <div class="loading-content flex flex-col items-center justify-center py-20">
                    <div class="loading-spinner mb-4 w-12 h-12 border-4 border-blue-200 border-t-blue-600 rounded-full animate-spin"></div>
                    <span class="text-gray-600 font-medium">Loading content...</span>
                </div>
            `;
        }
    },

    // Show error state
    showErrorState(message) {
        const contentArea = document.getElementById('content-area');
        if (contentArea) {
            contentArea.innerHTML = `
                <div class="error-content flex flex-col items-center justify-center py-20 text-center">
                    <i class="fas fa-exclamation-triangle text-red-500 text-5xl mb-6"></i>
                    <h3 class="text-xl font-bold text-gray-800 mb-2">Something went wrong</h3>
                    <p class="text-gray-600 mb-6">${message}</p>
                    <button onclick="SecureTrainer.LearningCenter.loadContent('intro')" class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors">
                        Return to Introduction
                    </button>
                </div>
            `;
        }
    },

    // Perform content search
    async performSearch(query) {
        if (query.length < 2) {
            this.hideSearchResults();
            return;
        }

        try {
            const response = await fetch(`/api/learning/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.success) {
                this.displaySearchResults(data.results);
            }
        } catch (error) {
            console.error('Search failed:', error);
        }
    },

    // Display search results
    displaySearchResults(results) {
        const searchResults = document.getElementById('search-results');
        if (!searchResults) return;

        if (results.length === 0) {
            searchResults.innerHTML = '<div class="p-3 text-gray-500 text-center">No results found</div>';
        } else {
            const resultsHTML = results.map(result => `
                <div class="search-result-item p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-0" 
                     onclick="SecureTrainer.LearningCenter.loadContent('${result.module_id}')">
                    <div class="font-medium text-gray-800">${result.title}</div>
                    <div class="text-sm text-gray-500 truncate">${result.description || result.module_title}</div>
                </div>
            `).join('');

            searchResults.innerHTML = resultsHTML;
        }

        searchResults.style.display = 'block';
    },

    // Hide search results
    hideSearchResults() {
        const searchResults = document.getElementById('search-results');
        if (searchResults) {
            searchResults.style.display = 'none';
        }
    },

    // Load progress data
    async loadProgressData() {
        try {
            const response = await fetch('/api/learning/progress');
            const data = await response.json();

            if (data.success) {
                this.updateProgressDisplay(data.progress);
            }
        } catch (error) {
            console.error('Failed to load progress:', error);
        }
    },

    // Update progress display
    updateProgressDisplay(progressData) {
        // Update overall stats
        if (progressData.overall) {
            const totalProgress = document.getElementById('total-progress');
            if (totalProgress) totalProgress.textContent = `${progressData.overall.percentage}%`;

            const overallBar = document.getElementById('overall-learning-bar');
            if (overallBar) overallBar.style.width = `${progressData.overall.percentage}%`;

            const overallText = document.getElementById('overall-learning-progress');
            if (overallText) overallText.textContent = `${progressData.overall.percentage}%`;
            
            // Update hero section study time
            const studyTimeElement = document.getElementById('study-time');
            if (studyTimeElement && progressData.overall.total_study_time) {
                const hours = Math.floor(progressData.overall.total_study_time / 3600);
                const minutes = Math.floor((progressData.overall.total_study_time % 3600) / 60);
                if (hours > 0) {
                    studyTimeElement.textContent = `${hours}.${Math.floor(minutes / 6)}h`;
                } else {
                    studyTimeElement.textContent = `${minutes}m`;
                }
            }
        }

        // Update module stats and count completed modules
        let completedCount = 0;
        let totalModules = 0;
        
        if (progressData.modules) {
            totalModules = Object.keys(progressData.modules).length;
            
            Object.entries(progressData.modules).forEach(([moduleId, data]) => {
                const progressBar = document.getElementById(`${moduleId}-learning-bar`);
                const progressText = document.getElementById(`${moduleId}-learning-progress`);

                if (progressBar) progressBar.style.width = `${data.percentage}%`;
                if (progressText) progressText.textContent = `${data.percentage}%`;
                
                // Count completed modules (100% progress AND is_complete flag)
                if (data.is_complete && data.percentage >= 100) {
                    completedCount++;
                }
            });
        }
        
        // Update hero section "MODULES COMPLETED" stat
        const completedModulesElement = document.getElementById('completed-modules');
        if (completedModulesElement) {
            completedModulesElement.textContent = completedCount;
        }
        
        // Update navigation progress text
        const navProgressText = document.getElementById('nav-progress-text');
        if (navProgressText) {
            navProgressText.textContent = `${completedCount} of ${totalModules} completed`;
        }
        
        // Update navigation progress bar
        const navProgressFill = document.getElementById('nav-progress-fill');
        if (navProgressFill && totalModules > 0) {
            const navPercentage = (completedCount / totalModules) * 100;
            navProgressFill.style.width = `${navPercentage}%`;
        }
    },

    // Start study timer
    startStudyTimer() {
        this.studyStartTime = Date.now();
        setInterval(() => {
            this.updateStudyTimeDisplay();
        }, 60000); // Update every minute
    },

    updateStudyTimeDisplay() {
        // In a real app, this would sync with the backend
        // For now, just a visual update
    },

    setupProgressToggle() {
        const toggle = document.getElementById('progress-toggle');
        const content = document.getElementById('progress-content');

        if (toggle && content) {
            toggle.addEventListener('click', () => {
                const isHidden = content.style.display === 'none';
                content.style.display = isHidden ? 'block' : 'none';
                toggle.querySelector('i').className = isHidden ? 'fas fa-chevron-up' : 'fas fa-chevron-down';
            });
        }
    },

    async handleModuleCompletion(moduleId, isComplete) {
        try {
            console.log(`Marking module ${moduleId} as ${isComplete ? 'complete' : 'incomplete'}`);
            
            const response = await fetch(`/api/learning/module/${moduleId}/complete`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ completed: isComplete })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Reload progress to update UI
                await this.loadProgressData();
                
                // Show success message
                this.showCompletionMessage(isComplete);
            } else {
                console.error('Failed to update completion status:', data.error);
                // Revert checkbox
                const checkbox = document.querySelector(`[data-module-id="${moduleId}"]`);
                if (checkbox) checkbox.checked = !isComplete;
            }
        } catch (error) {
            console.error('Error updating module completion:', error);
            // Revert checkbox
            const checkbox = document.querySelector(`[data-module-id="${moduleId}"]`);
            if (checkbox) checkbox.checked = !isComplete;
        }
    },

    showCompletionMessage(isComplete) {
        const message = document.createElement('div');
        message.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${isComplete ? '#10b981' : '#6b7280'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 10px 25px rgba(0,0,0,0.2);
            z-index: 10000;
            animation: slideIn 0.3s ease-out;
        `;
        message.innerHTML = `
            <i class="fas fa-${isComplete ? 'check' : 'times'}-circle" style="margin-right: 0.5rem;"></i>
            Module marked as ${isComplete ? 'complete' : 'incomplete'}!
        `;
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.style.animation = 'slideOut 0.3s ease-out';
            setTimeout(() => message.remove(), 300);
        }, 3000);
    },

    navigateContent(direction) {
        // Logic to find next/prev section based on currentSection
        // and calling loadContent with the new ID
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    SecureTrainer.LearningCenter.init();
});