/**
 * Analytics Dashboard JavaScript
 *
 * Handles:
 * - Sankey diagram rendering with Plotly.js
 * - Timeline visualization
 * - Chart download functionality
 * - Lazy loading and responsive behavior
 */

(function() {
    'use strict';

    // ========== Sankey Diagram ==========

    /**
     * Initialize Sankey diagram when element is visible
     */
    function initSankeyDiagram() {
        const container = document.getElementById('sankeyChart');
        if (!container) return;

        // Check if already rendered
        if (container.dataset.rendered === 'true') return;

        // Show loading state
        showLoading(container);

        // Fetch Sankey data from API
        fetch('/tracker/analytics/api/sankey/')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch Sankey data');
                }
                return response.json();
            })
            .then(data => {
                renderSankeyDiagram(container, data);
                container.dataset.rendered = 'true';
            })
            .catch(error => {
                console.error('Error loading Sankey diagram:', error);
                showError(container, 'Failed to load application flow diagram. Please try again.');
            });
    }

    /**
     * Render Sankey diagram with Plotly
     */
    function renderSankeyDiagram(container, data) {
        // Clear loading state
        container.innerHTML = '';

        // Check if there's data to display
        if (data.total_count === 0) {
            showEmptyState(container, 'No application data available yet. Start adding applications to see the flow diagram.');
            return;
        }

        // Prepare Plotly data
        const plotData = [{
            type: 'sankey',
            orientation: 'h',
            node: {
                pad: 15,
                thickness: 20,
                line: {
                    color: 'white',
                    width: 2
                },
                label: data.node.label,
                color: data.node.color,
                customdata: data.node.customdata,
                hovertemplate: data.node.hovertemplate || '%{label}<br>%{customdata} applications<extra></extra>',
            },
            link: {
                source: data.link.source,
                target: data.link.target,
                value: data.link.value,
                color: data.link.color,
                hovertemplate: data.link.hovertemplate || '%{value} applications<br>%{source.label} → %{target.label}<extra></extra>',
            }
        }];

        // Layout configuration
        const layout = {
            title: {
                text: 'Application Flow Diagram',
                font: {
                    size: 20,
                    family: 'system-ui, -apple-system, sans-serif',
                    color: '#1f2937'
                }
            },
            font: {
                size: 14,
                family: 'system-ui, -apple-system, sans-serif',
                color: '#4b5563'
            },
            plot_bgcolor: 'rgba(0,0,0,0)',
            paper_bgcolor: 'rgba(0,0,0,0)',
            margin: {
                l: 20,
                r: 20,
                t: 60,
                b: 20
            },
            height: 500,
        };

        // Plotly configuration
        const config = {
            responsive: true,
            displayModeBar: true,
            displaylogo: false,
            modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d', 'autoScale2d'],
            toImageButtonOptions: {
                format: 'png',
                filename: 'application_flow_sankey',
                height: 800,
                width: 1200,
                scale: 2
            }
        };

        // Render the plot
        Plotly.newPlot(container, plotData, layout, config)
            .then(() => {
                console.log('Sankey diagram rendered successfully');
            })
            .catch(error => {
                console.error('Error rendering Sankey diagram:', error);
                showError(container, 'Failed to render diagram. Please refresh the page.');
            });
    }

    /**
     * Download Sankey diagram as PNG
     */
    function downloadSankeyDiagram(format = 'png') {
        const container = document.getElementById('sankeyChart');
        if (!container) return;

        const filename = `application_flow_sankey_${new Date().toISOString().split('T')[0]}`;

        Plotly.downloadImage(container, {
            format: format,
            width: 1200,
            height: 800,
            filename: filename
        }).then(() => {
            console.log('Sankey diagram downloaded');
        }).catch(error => {
            console.error('Error downloading diagram:', error);
            alert('Failed to download diagram. Please try again.');
        });
    }

    // ========== Timeline Visualization ==========

    /**
     * Initialize timeline visualization
     */
    function initTimeline() {
        const container = document.getElementById('timelineContainer');
        if (!container) return;

        // Check if already rendered
        if (container.dataset.rendered === 'true') return;

        // Show loading state
        showLoading(container);

        // Get days filter from select (if exists)
        const daysFilter = document.getElementById('timelineDaysFilter');
        const days = daysFilter ? daysFilter.value : 30;

        // Fetch timeline data from API
        fetch(`/tracker/analytics/api/timeline/?days=${days}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to fetch timeline data');
                }
                return response.json();
            })
            .then(data => {
                renderTimeline(container, data);
                container.dataset.rendered = 'true';
            })
            .catch(error => {
                console.error('Error loading timeline:', error);
                showError(container, 'Failed to load timeline. Please try again.');
            });
    }

    /**
     * Render timeline events
     */
    function renderTimeline(container, events) {
        // Clear loading state
        container.innerHTML = '';

        // Check if there are events
        if (!events || events.length === 0) {
            showEmptyState(container, 'No upcoming deadlines or interviews in the selected timeframe.');
            return;
        }

        // Group events by category
        const now = new Date();
        const overdue = events.filter(e => e.is_overdue);
        const today = events.filter(e => e.is_today && !e.is_overdue);
        const thisWeek = events.filter(e => e.is_this_week && !e.is_today && !e.is_overdue);
        const upcoming = events.filter(e => !e.is_this_week && !e.is_overdue);

        // Create timeline HTML
        let html = '<div class="timeline">';

        // Overdue section
        if (overdue.length > 0) {
            html += createTimelineSection('Overdue', overdue, 'danger');
        }

        // Today section
        if (today.length > 0) {
            html += createTimelineSection('Today', today, 'warning');
        }

        // This week section
        if (thisWeek.length > 0) {
            html += createTimelineSection('This Week', thisWeek, 'info');
        }

        // Upcoming section
        if (upcoming.length > 0) {
            html += createTimelineSection('Upcoming', upcoming, 'secondary');
        }

        html += '</div>';
        container.innerHTML = html;
    }

    /**
     * Create timeline section HTML
     */
    function createTimelineSection(title, events, variant) {
        let html = `
            <div class="timeline-section mb-4">
                <h5 class="timeline-section-title text-${variant} fw-bold mb-3">
                    <i class="bi bi-${getIconForVariant(variant)} me-2"></i>${title}
                </h5>
                <div class="timeline-events">
        `;

        events.forEach(event => {
            html += createTimelineEvent(event, variant);
        });

        html += '</div></div>';
        return html;
    }

    /**
     * Create single timeline event HTML
     */
    function createTimelineEvent(event, variant) {
        const priorityColor = getPriorityColor(event.priority);
        const typeIcon = getTypeIcon(event.type);

        return `
            <div class="timeline-event card border-${variant} mb-3">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1 fw-bold">
                                <a href="/tracker/application/${event.id}/" class="text-decoration-none text-dark">
                                    ${escapeHtml(event.title)}
                                </a>
                            </h6>
                            <p class="text-secondary small mb-2">
                                <i class="bi bi-building me-1"></i>
                                ${escapeHtml(event.company)}
                            </p>
                            <div class="d-flex flex-wrap gap-2 align-items-center">
                                <span class="badge bg-${variant}">
                                    <i class="bi bi-${typeIcon} me-1"></i>${event.type}
                                </span>
                                <span class="badge bg-light text-dark border">
                                    ${event.status_display}
                                </span>
                                <span class="badge ${priorityColor}">
                                    ${event.priority_display} Priority
                                </span>
                            </div>
                        </div>
                        <div class="text-end ms-3">
                            <div class="text-${variant} fw-semibold small">
                                <i class="bi bi-calendar-event me-1"></i>
                                ${formatRelativeDate(event.days_until)}
                            </div>
                            <div class="text-muted" style="font-size: 0.75rem;">
                                ${formatDate(event.date)}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // ========== Utility Functions ==========

    /**
     * Show loading state in container
     */
    function showLoading(container) {
        container.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="text-muted mt-3">Loading data...</p>
            </div>
        `;
    }

    /**
     * Show error state in container
     */
    function showError(container, message) {
        container.innerHTML = `
            <div class="alert alert-danger d-flex align-items-center" role="alert">
                <i class="bi bi-exclamation-triangle-fill me-3" style="font-size: 1.5rem;"></i>
                <div>
                    <strong>Error:</strong> ${escapeHtml(message)}
                </div>
            </div>
        `;
    }

    /**
     * Show empty state in container
     */
    function showEmptyState(container, message) {
        container.innerHTML = `
            <div class="text-center py-5 text-muted">
                <i class="bi bi-inbox" style="font-size: 3rem; opacity: 0.3;"></i>
                <p class="mt-3">${escapeHtml(message)}</p>
            </div>
        `;
    }

    /**
     * Get icon for variant
     */
    function getIconForVariant(variant) {
        const icons = {
            'danger': 'exclamation-circle',
            'warning': 'clock',
            'info': 'calendar-week',
            'secondary': 'calendar-event'
        };
        return icons[variant] || 'calendar';
    }

    /**
     * Get icon for event type
     */
    function getTypeIcon(type) {
        const icons = {
            'interview': 'people',
            'deadline': 'calendar-check',
            'overdue': 'exclamation-triangle'
        };
        return icons[type] || 'calendar';
    }

    /**
     * Get priority color
     */
    function getPriorityColor(priority) {
        const colors = {
            'high': 'bg-danger',
            'medium': 'bg-warning text-dark',
            'low': 'bg-success'
        };
        return colors[priority] || 'bg-secondary';
    }

    /**
     * Format relative date
     */
    function formatRelativeDate(daysUntil) {
        if (daysUntil < 0) {
            const daysPast = Math.abs(daysUntil);
            return daysPast === 1 ? 'Yesterday' : `${daysPast} days ago`;
        } else if (daysUntil === 0) {
            return 'Today';
        } else if (daysUntil === 1) {
            return 'Tomorrow';
        } else if (daysUntil <= 7) {
            return `In ${daysUntil} days`;
        } else {
            return `In ${daysUntil} days`;
        }
    }

    /**
     * Format date string
     */
    function formatDate(isoString) {
        const date = new Date(isoString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ========== Intersection Observer for Lazy Loading ==========

    /**
     * Setup lazy loading with Intersection Observer
     */
    function setupLazyLoading() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const target = entry.target;

                    if (target.id === 'sankeyChart') {
                        initSankeyDiagram();
                        observer.unobserve(target);
                    } else if (target.id === 'timelineContainer') {
                        initTimeline();
                        observer.unobserve(target);
                    }
                }
            });
        }, {
            rootMargin: '100px' // Load 100px before element comes into view
        });

        // Observe Sankey chart
        const sankeyChart = document.getElementById('sankeyChart');
        if (sankeyChart) {
            observer.observe(sankeyChart);
        }

        // Observe timeline
        const timeline = document.getElementById('timelineContainer');
        if (timeline) {
            observer.observe(timeline);
        }
    }

    // ========== Event Listeners ==========

    /**
     * Setup event listeners
     */
    function setupEventListeners() {
        // Download button for Sankey diagram
        const downloadBtn = document.getElementById('downloadSankeyBtn');
        if (downloadBtn) {
            downloadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                downloadSankeyDiagram('png');
            });
        }

        // Timeline days filter
        const timelineDaysFilter = document.getElementById('timelineDaysFilter');
        if (timelineDaysFilter) {
            timelineDaysFilter.addEventListener('change', () => {
                const container = document.getElementById('timelineContainer');
                if (container) {
                    container.dataset.rendered = 'false';
                    initTimeline();
                }
            });
        }
    }

    // ========== Initialization ==========

    /**
     * Initialize analytics dashboard
     */
    function init() {
        // Check if Plotly is loaded
        if (typeof Plotly === 'undefined') {
            console.error('Plotly.js is not loaded. Sankey diagram will not render.');
            return;
        }

        // Setup lazy loading for charts
        setupLazyLoading();

        // Setup event listeners
        setupEventListeners();

        console.log('Analytics dashboard initialized');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose download function globally for manual use
    window.downloadSankeyDiagram = downloadSankeyDiagram;

})();
