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
            const completedSections = content.user_progress?.completed_sections || [];
            const totalSections = content.sections.length;
            const allCompleted = completedSections.length === totalSections && totalSections > 0;
            
            console.log(`[CHECKBOX] Module ${content.id}: completed=${completedSections.length}/${totalSections}, allCompleted=${allCompleted}`);
            console.log(`[CHECKBOX] Completed sections:`, completedSections);
            console.log(`[CHECKBOX] All section IDs:`, content.sections.map(s => s.id));
            
            content.sections.forEach((section, index) => {
                const isCompleted = completedSections.includes(section.id);
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
            
            // Add ONE completion checkbox at the very end of all sections
            html += `
                <div class="mt-8 pt-6 border-t-2 border-gray-300 flex items-center justify-center bg-gradient-to-r from-blue-50 to-green-50 p-6 rounded-lg shadow-md">
                    <div class="flex items-center space-x-4">
                        <label class="checkbox-container group cursor-pointer flex items-center space-x-4">
                            <input type="checkbox" 
                                   class="module-checkbox hidden" 
                                   data-module-id="${content.id}"
                                   ${allCompleted ? 'checked' : ''}
                                   onchange="SecureTrainer.LearningCenter.toggleModuleCompletion(this, '${content.id}')">
                            <div class="checkbox-visual w-8 h-8 border-2 border-gray-400 rounded-lg flex items-center justify-center transition-all duration-200 ${
                                allCompleted ? 'bg-green-500 border-green-500' : 'bg-white group-hover:border-blue-500'
                            }">
                                ${allCompleted ? '<i class="fas fa-check text-white text-lg"></i>' : ''}
                            </div>
                            <span class="text-lg font-semibold ${allCompleted ? 'text-green-600' : 'text-gray-800 group-hover:text-blue-600'} transition-colors">
                                ${allCompleted ? 'Module Completed! ✨' : 'Mark module as complete'}
                            </span>
                        </label>
                    </div>
                </div>
            `;
        }

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
        console.log('📊 Updating progress display:', progressData);
        
        // Update overall stats
        if (progressData.overall) {
            // Overall progress percentage
            const totalProgress = document.getElementById('total-progress');
            if (totalProgress) totalProgress.textContent = `${Math.round(progressData.overall.percentage)}%`;

            const overallBar = document.getElementById('overall-learning-bar');
            if (overallBar) overallBar.style.width = `${progressData.overall.percentage}%`;

            const overallText = document.getElementById('overall-learning-progress');
            if (overallText) overallText.textContent = `${Math.round(progressData.overall.percentage)}%`;
            
            // Study time
            const studyTime = document.getElementById('study-time');
            if (studyTime) {
                const hours = Math.round(progressData.overall.total_study_time / 60);
                const minutes = progressData.overall.total_study_time % 60;
                if (hours > 0) {
                    studyTime.textContent = `${hours}h ${minutes}m`;
                } else {
                    studyTime.textContent = `${minutes}m`;
                }
            }
        }

        // Update module stats
        if (progressData.modules) {
            let completedModules = 0;
            const totalModules = Object.keys(progressData.modules).length;
            
            Object.entries(progressData.modules).forEach(([moduleId, data]) => {
                const progressBar = document.getElementById(`${moduleId}-learning-bar`);
                const progressText = document.getElementById(`${moduleId}-learning-progress`);

                if (progressBar) progressBar.style.width = `${data.percentage}%`;
                if (progressText) progressText.textContent = `${Math.round(data.percentage)}%`;
                
                // Count completed modules (100%)
                if (data.percentage >= 100) {
                    completedModules++;
                }
            });
            
            // Update "3 of 6 completed" text
            const completedModulesDisplay = document.getElementById('completed-modules');
            if (completedModulesDisplay) {
                completedModulesDisplay.textContent = completedModules;
            }
            
            // Update nav progress text
            const navProgressText = document.getElementById('nav-progress-text');
            if (navProgressText) {
                navProgressText.textContent = `${completedModules} of ${totalModules} completed`;
            }
            
            // Update progress bar
            const navProgressFill = document.querySelector('.nav-progress-fill');
            if (navProgressFill) {
                const percentage = (completedModules / totalModules) * 100;
                navProgressFill.style.width = `${percentage}%`;
            }
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

    navigateContent(direction) {
        // Logic to find next/prev section based on currentSection
        // and calling loadContent with the new ID
    },

    // Toggle module completion (marks all sections as complete/incomplete)
    async toggleModuleCompletion(checkbox, moduleId) {
        const isCompleted = checkbox.checked;
        console.log(`[INFO] Toggling module completion: ${moduleId} -> ${isCompleted}`);
        
        // Update visual state immediately
        const label = checkbox.closest('.checkbox-container');
        const visualCheckbox = label.querySelector('.checkbox-visual');
        const statusText = label.querySelector('span');
        
        if (isCompleted) {
            visualCheckbox.classList.remove('bg-white', 'group-hover:border-blue-500');
            visualCheckbox.classList.add('bg-green-500', 'border-green-500');
            visualCheckbox.innerHTML = '<i class="fas fa-check text-white text-lg"></i>';
            statusText.classList.remove('text-gray-800', 'group-hover:text-blue-600');
            statusText.classList.add('text-green-600');
            statusText.textContent = 'Module Completed! ✨';
        } else {
            visualCheckbox.classList.remove('bg-green-500', 'border-green-500');
            visualCheckbox.classList.add('bg-white', 'group-hover:border-blue-500');
            visualCheckbox.innerHTML = '';
            statusText.classList.remove('text-green-600');
            statusText.classList.add('text-gray-800', 'group-hover:text-blue-600');
            statusText.textContent = 'Mark module as complete';
        }
        
        try {
            // Get all sections for this module
            const response = await fetch(`/api/learning/content/${moduleId}`);
            const data = await response.json();
            
            if (!data.success || !data.content) {
                throw new Error('Failed to load module content');
            }
            
            const sections = data.content.sections || [];
            console.log(`[INFO] Module has ${sections.length} sections`);
            
            // Mark all sections as complete/incomplete
            for (const section of sections) {
                const sectionResponse = await fetch(`/api/learning/progress/${moduleId}/${section.id}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        completed: isCompleted
                    })
                });
                
                const sectionData = await sectionResponse.json();
                if (!sectionData.success) {
                    console.error(`[ERROR] Failed to update section ${section.id}`);
                }
            }
            
            console.log('[SUCCESS] All sections updated, refreshing progress...');
            
            // Clear the server-side enhanced learning cache
            try {
                await fetch('/api/learning/clear-cache', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ module_id: moduleId })
                });
                console.log('[INFO] Server cache cleared');
            } catch (cacheError) {
                console.log('[WARNING] Failed to clear server cache:', cacheError);
            }
            
            // Clear cache for this module to force refresh
            this.contentCache.delete(moduleId);
            
            // Refresh progress data - this will update all the stats
            await this.loadProgressData();
            
            // Reload the current content to show updated checkbox state
            await this.loadContent(moduleId);
            
            console.log('[SUCCESS] Progress updated and content reloaded');
        } catch (error) {
            console.error('[ERROR] Error updating module completion:', error);
            // Revert checkbox state
            checkbox.checked = !isCompleted;
            // Revert visual state
            if (!isCompleted) {
                visualCheckbox.classList.remove('bg-white', 'group-hover:border-blue-500');
                visualCheckbox.classList.add('bg-green-500', 'border-green-500');
                visualCheckbox.innerHTML = '<i class="fas fa-check text-white text-lg"></i>';
                statusText.classList.remove('text-gray-800', 'group-hover:text-blue-600');
                statusText.classList.add('text-green-600');
                statusText.textContent = 'Module Completed! ✨';
            } else {
                visualCheckbox.classList.remove('bg-green-500', 'border-green-500');
                visualCheckbox.classList.add('bg-white', 'group-hover:border-blue-500');
                visualCheckbox.innerHTML = '';
                statusText.classList.remove('text-green-600');
                statusText.classList.add('text-gray-800', 'group-hover:text-blue-600');
                statusText.textContent = 'Mark module as complete';
            }
        }
    },

    // Update module completion count in sidebar
    async updateModuleCompletionCount(moduleId) {
        try {
            // Reload the current content to get updated completion status
            const response = await fetch(`/api/learning/content/${moduleId}`);
            const data = await response.json();
            
            if (data.success && data.content) {
                const completedSections = data.content.user_progress?.completed_sections || [];
                const totalSections = data.content.sections?.length || 0;
                const completedCount = completedSections.length;
                
                console.log(`📈 Module ${moduleId}: ${completedCount}/${totalSections} sections completed`);
                
                // Update nav progress indicator dots
                const navLink = document.querySelector(`[data-content="${moduleId}"]`);
                if (navLink) {
                    const progressIndicator = navLink.querySelector('.nav-progress-indicator');
                    if (progressIndicator) {
                        const dots = progressIndicator.querySelectorAll('.progress-dot');
                        dots.forEach((dot, index) => {
                            if (index < completedCount) {
                                dot.classList.add('completed');
                            } else {
                                dot.classList.remove('completed');
                            }
                        });
                    }
                }
            }
        } catch (error) {
            console.error('Error updating module completion count:', error);
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    SecureTrainer.LearningCenter.init();
});