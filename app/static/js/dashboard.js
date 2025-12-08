/**
 * Dashboard Chart Initialization and Real-Time Data Updates
 * SecureTrainer Platform
 */

// Global chart instances
let scoreChart = null;
let skillsChart = null;
let activityChart = null;
let achievementChart = null;

// Dashboard data refresh interval (30 seconds)
const REFRESH_INTERVAL = 30000;

/**
 * Initialize all dashboard charts with real data
 */
function initializeDashboardCharts() {
    // Get analytics data from template (passed by Flask)
    if (typeof analyticsData === 'undefined') {
        console.warn('Analytics data not available');
        return;
    }

    // Initialize Score Progression Chart
    initializeScoreChart();
    
    // Initialize Skills Radar Chart
    initializeSkillsChart();
    
    // Initialize Weekly Activity Chart
    initializeActivityChart();
    
    // Initialize Achievement Progress Chart
    initializeAchievementChart();
    
    // Start auto-refresh
    startAutoRefresh();
}

/**
 * Initialize Score Progression Line Chart
 */
function initializeScoreChart() {
    const ctx = document.getElementById('scoreChart');
    if (!ctx) return;

    const labels = analyticsData.chart_labels || [];
    const scores = analyticsData.chart_scores || [];

    if (scoreChart) {
        scoreChart.destroy();
    }

    scoreChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Score Progress',
                data: scores,
                borderColor: 'rgb(59, 130, 246)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointRadius: 4,
                pointBackgroundColor: 'rgb(59, 130, 246)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        font: {
                            size: 12,
                            family: "'Inter', sans-serif"
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    titleFont: {
                        size: 14,
                        weight: 'bold'
                    },
                    bodyFont: {
                        size: 13
                    },
                    borderColor: 'rgb(59, 130, 246)',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return 'Score: ' + context.parsed.y.toLocaleString();
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            },
            interaction: {
                mode: 'index',
                intersect: false
            }
        }
    });
}

/**
 * Initialize Skills Radar Chart
 */
function initializeSkillsChart() {
    const ctx = document.getElementById('skillsChart');
    if (!ctx) return;

    const categoryPerformance = analyticsData.category_performance || {};
    const categories = Object.keys(categoryPerformance);
    const successRates = categories.map(cat => categoryPerformance[cat].success_rate || 0);

    if (skillsChart) {
        skillsChart.destroy();
    }

    skillsChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: categories.map(cat => cat.replace('_', ' ').toUpperCase()),
            datasets: [{
                label: 'Success Rate (%)',
                data: successRates,
                borderColor: 'rgb(16, 185, 129)',
                backgroundColor: 'rgba(16, 185, 129, 0.2)',
                borderWidth: 2,
                pointBackgroundColor: 'rgb(16, 185, 129)',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.r + '%';
                        }
                    }
                }
            },
            scales: {
                r: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        stepSize: 20,
                        callback: function(value) {
                            return value + '%';
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    },
                    angleLines: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Initialize Weekly Activity Bar Chart
 */
function initializeActivityChart() {
    const ctx = document.getElementById('activityChart');
    if (!ctx) return;

    // Generate last 7 days
    const last7Days = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        last7Days.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }

    // Get activity data (mock for now, should come from backend)
    const activityData = [3, 5, 2, 8, 4, 6, 7];  // Challenges completed per day

    if (activityChart) {
        activityChart.destroy();
    }

    activityChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: last7Days,
            datasets: [{
                label: 'Challenges Completed',
                data: activityData,
                backgroundColor: 'rgba(139, 92, 246, 0.8)',
                borderColor: 'rgb(139, 92, 246)',
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        callback: function(value) {
                            return Math.floor(value);
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

/**
 * Initialize Achievement Progress Chart
 */
function initializeAchievementChart() {
    const ctx = document.getElementById('achievementChart');
    if (!ctx) return;

    // Mock data - replace with real data from backend
    const achievementData = {
        labels: ['Total Achievements', 'Earned', 'Remaining'],
        data: [20, 12, 8]
    };

    if (achievementChart) {
        achievementChart.destroy();
    }

    achievementChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Earned', 'Remaining'],
            datasets: [{
                data: [achievementData.data[1], achievementData.data[2]],
                backgroundColor: [
                    'rgba(234, 179, 8, 0.8)',
                    'rgba(229, 231, 235, 0.5)'
                ],
                borderColor: [
                    'rgb(234, 179, 8)',
                    'rgb(229, 231, 235)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    padding: 12,
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            const total = achievementData.data[0];
                            const percentage = ((value / total) * 100).toFixed(1);
                            return label + ': ' + value + ' (' + percentage + '%)';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Refresh dashboard data from server
 */
async function refreshDashboardData() {
    try {
        const response = await fetch('/dashboard/refresh');
        if (!response.ok) {
            console.error('Failed to refresh dashboard data');
            return;
        }

        const data = await response.json();
        if (data.success) {
            // Update stats cards
            updateStatsCards(data);
            
            // Update charts if new data is available
            if (data.analytics) {
                window.analyticsData = data.analytics;
                updateCharts();
            }
        }
    } catch (error) {
        console.error('Error refreshing dashboard:', error);
    }
}

/**
 * Update statistics cards with new data
 */
function updateStatsCards(data) {
    // Update score
    const scoreElement = document.querySelector('[data-stat="score"]');
    if (scoreElement && data.score !== undefined) {
        animateValue(scoreElement, parseInt(scoreElement.textContent) || 0, data.score, 1000);
    }

    // Update level
    const levelElement = document.querySelector('[data-stat="level"]');
    if (levelElement && data.level !== undefined) {
        levelElement.textContent = data.level;
    }

    // Update challenges completed
    const challengesElement = document.querySelector('[data-stat="challenges"]');
    if (challengesElement && data.challenges_completed !== undefined) {
        animateValue(challengesElement, parseInt(challengesElement.textContent) || 0, data.challenges_completed, 1000);
    }
}

/**
 * Animate number transitions
 */
function animateValue(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);  // 60fps
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.floor(current);
    }, 16);
}

/**
 * Update all charts with new data
 */
function updateCharts() {
    initializeScoreChart();
    initializeSkillsChart();
    initializeActivityChart();
    initializeAchievementChart();
}

/**
 * Start auto-refresh timer
 */
function startAutoRefresh() {
    setInterval(refreshDashboardData, REFRESH_INTERVAL);
}

/**
 * Initialize dashboard when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.error('Chart.js is not loaded');
        return;
    }

    // Initialize charts
    initializeDashboardCharts();
    
    // Check if user just completed a challenge
    const justCompleted = sessionStorage.getItem('challengeJustCompleted');
    if (justCompleted === 'true') {
        console.log('Challenge just completed - refreshing dashboard data');
        
        // Clear the flag
        sessionStorage.removeItem('challengeJustCompleted');
        
        // Show success message
        const scoreEarned = sessionStorage.getItem('lastCompletedScore') || '0';
        const challengeId = sessionStorage.getItem('lastCompletedChallenge') || '';
        
        // Clear temp data
        sessionStorage.removeItem('lastCompletedScore');
        sessionStorage.removeItem('lastCompletedChallenge');
        
        // Show notification
        showDashboardNotification(`🎉 Challenge completed! +${scoreEarned} points added to your score.`, 'success');
        
        // Refresh dashboard data
        setTimeout(() => {
            refreshDashboardData();
        }, 500);
    }
    
    console.log('Dashboard initialized successfully');
});

/**
 * Show dashboard notification
 */
function showDashboardNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 animate-slide-in`;
    
    const colors = {
        'info': 'bg-blue-500 text-white',
        'success': 'bg-green-500 text-white',
        'error': 'bg-red-500 text-white',
        'warning': 'bg-yellow-500 text-black'
    };
    
    notification.className += ` ${colors[type] || colors.info}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}
