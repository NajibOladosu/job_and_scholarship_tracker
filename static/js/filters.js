/**
 * Advanced Filters JavaScript
 *
 * Handles:
 * - Advanced filter panel with collapse/expand
 * - Save filter presets to localStorage
 * - Clear all filters button
 * - Active filter badges
 * - Filter count display
 */

(function() {
    'use strict';

    // ========== Configuration ==========

    const STORAGE_KEY = 'app_tracker_filter_presets';
    const MAX_PRESETS = 10;

    // ========== State Management ==========

    let activeFilters = {};
    let savedPresets = [];

    // ========== Local Storage ==========

    /**
     * Load filter presets from localStorage
     */
    function loadPresets() {
        try {
            const stored = localStorage.getItem(STORAGE_KEY);
            if (stored) {
                savedPresets = JSON.parse(stored);
            }
        } catch (error) {
            console.error('Error loading filter presets:', error);
            savedPresets = [];
        }
        return savedPresets;
    }

    /**
     * Save filter presets to localStorage
     */
    function savePresets() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(savedPresets));
        } catch (error) {
            console.error('Error saving filter presets:', error);
        }
    }

    /**
     * Add new filter preset
     */
    function addPreset(name, filters) {
        const preset = {
            id: Date.now(),
            name: name,
            filters: filters,
            created: new Date().toISOString()
        };

        savedPresets.unshift(preset);

        // Keep only MAX_PRESETS
        if (savedPresets.length > MAX_PRESETS) {
            savedPresets = savedPresets.slice(0, MAX_PRESETS);
        }

        savePresets();
        renderPresetsList();
        showToast(`Filter preset "${name}" saved`, 'success');
    }

    /**
     * Delete filter preset
     */
    function deletePreset(presetId) {
        savedPresets = savedPresets.filter(p => p.id !== presetId);
        savePresets();
        renderPresetsList();
        showToast('Filter preset deleted', 'info');
    }

    /**
     * Apply filter preset
     */
    function applyPreset(presetId) {
        const preset = savedPresets.find(p => p.id === presetId);
        if (!preset) return;

        // Apply filters to form
        const form = document.getElementById('filterForm');
        if (!form) return;

        Object.keys(preset.filters).forEach(key => {
            const input = form.elements[key];
            if (input) {
                input.value = preset.filters[key];
            }
        });

        // Submit form
        form.submit();
    }

    // ========== Filter Panel ==========

    /**
     * Initialize advanced filter panel
     */
    function initializeFilterPanel() {
        const filterPanel = document.getElementById('advancedFiltersPanel');
        if (!filterPanel) return;

        // Toggle collapse button
        const collapseBtn = document.getElementById('toggleFiltersBtn');
        if (collapseBtn) {
            const isCollapsed = localStorage.getItem('filters_collapsed') === 'true';

            if (isCollapsed) {
                filterPanel.classList.remove('show');
                collapseBtn.querySelector('i')?.classList.replace('bi-chevron-up', 'bi-chevron-down');
            }

            collapseBtn.addEventListener('click', () => {
                const isCurrentlyCollapsed = !filterPanel.classList.contains('show');
                localStorage.setItem('filters_collapsed', !isCurrentlyCollapsed);

                const icon = collapseBtn.querySelector('i');
                if (icon) {
                    if (isCurrentlyCollapsed) {
                        icon.classList.replace('bi-chevron-down', 'bi-chevron-up');
                    } else {
                        icon.classList.replace('bi-chevron-up', 'bi-chevron-down');
                    }
                }
            });
        }
    }

    /**
     * Get current active filters from form
     */
    function getActiveFilters() {
        const filters = {};
        const form = document.getElementById('filterForm');

        if (!form) return filters;

        // Get all form inputs
        const formData = new FormData(form);

        for (const [key, value] of formData.entries()) {
            if (value && value.trim() !== '') {
                filters[key] = value;
            }
        }

        return filters;
    }

    /**
     * Count active filters
     */
    function countActiveFilters() {
        const filters = getActiveFilters();
        return Object.keys(filters).length;
    }

    /**
     * Update filter count badge
     */
    function updateFilterCount() {
        const countBadge = document.getElementById('filterCountBadge');
        if (!countBadge) return;

        const count = countActiveFilters();

        if (count > 0) {
            countBadge.textContent = count;
            countBadge.classList.remove('d-none');
        } else {
            countBadge.classList.add('d-none');
        }
    }

    // ========== Filter Badges ==========

    /**
     * Render active filter badges
     */
    function renderFilterBadges() {
        const container = document.getElementById('activeFilterBadges');
        if (!container) return;

        const filters = getActiveFilters();
        const filterKeys = Object.keys(filters);

        if (filterKeys.length === 0) {
            container.innerHTML = '';
            container.classList.add('d-none');
            return;
        }

        container.classList.remove('d-none');

        // Create badges
        let html = '<div class="d-flex flex-wrap gap-2 align-items-center mb-3">';
        html += '<small class="text-muted fw-semibold me-2">Active Filters:</small>';

        filterKeys.forEach(key => {
            const value = filters[key];
            const displayName = getFilterDisplayName(key);
            const displayValue = getFilterDisplayValue(key, value);

            html += `
                <span class="badge bg-primary d-inline-flex align-items-center" data-filter-key="${key}">
                    <span>${displayName}: ${displayValue}</span>
                    <button type="button" class="btn-close btn-close-white ms-2"
                            style="font-size: 0.7rem; padding: 0.2rem;"
                            data-filter-remove="${key}"
                            aria-label="Remove ${displayName} filter">
                    </button>
                </span>
            `;
        });

        html += `
            <button type="button" class="btn btn-sm btn-outline-danger" id="clearAllFilters">
                <i class="bi bi-x-circle me-1"></i>Clear All
            </button>
        </div>`;

        container.innerHTML = html;

        // Add event listeners
        setupBadgeEventListeners();
    }

    /**
     * Setup event listeners for filter badges
     */
    function setupBadgeEventListeners() {
        // Individual filter remove buttons
        document.querySelectorAll('[data-filter-remove]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filterKey = e.target.dataset.filterRemove;
                removeFilter(filterKey);
            });
        });

        // Clear all filters button
        const clearAllBtn = document.getElementById('clearAllFilters');
        if (clearAllBtn) {
            clearAllBtn.addEventListener('click', clearAllFilters);
        }
    }

    /**
     * Get display name for filter key
     */
    function getFilterDisplayName(key) {
        const names = {
            'search': 'Search',
            'application_type': 'Type',
            'status': 'Status',
            'priority': 'Priority',
            'deadline_from': 'Deadline From',
            'deadline_to': 'Deadline To',
            'ordering': 'Sort By'
        };
        return names[key] || key;
    }

    /**
     * Get display value for filter
     */
    function getFilterDisplayValue(key, value) {
        // Truncate long search terms
        if (key === 'search') {
            return value.length > 20 ? value.substring(0, 20) + '...' : value;
        }

        // Format status/type values
        const formattedValue = value.replace(/_/g, ' ');
        return formattedValue.charAt(0).toUpperCase() + formattedValue.slice(1);
    }

    /**
     * Remove single filter
     */
    function removeFilter(filterKey) {
        const form = document.getElementById('filterForm');
        if (!form) return;

        const input = form.elements[filterKey];
        if (input) {
            input.value = '';
        }

        // Submit form
        form.submit();
    }

    /**
     * Clear all filters
     */
    function clearAllFilters() {
        const form = document.getElementById('filterForm');
        if (!form) {
            // Navigate to base URL without query params
            window.location.href = window.location.pathname;
            return;
        }

        // Reset all form inputs
        form.reset();

        // Navigate to base URL
        window.location.href = window.location.pathname;
    }

    // ========== Save Filter Preset ==========

    /**
     * Initialize save preset functionality
     */
    function initializeSavePreset() {
        const saveBtn = document.getElementById('saveFilterPresetBtn');
        if (!saveBtn) return;

        saveBtn.addEventListener('click', () => {
            const filters = getActiveFilters();

            if (Object.keys(filters).length === 0) {
                showToast('No active filters to save', 'warning');
                return;
            }

            showSavePresetModal(filters);
        });
    }

    /**
     * Show save preset modal
     */
    function showSavePresetModal(filters) {
        const modalHtml = `
            <div class="modal fade" id="savePresetModal" tabindex="-1" aria-labelledby="savePresetLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title fw-bold" id="savePresetLabel">
                                <i class="bi bi-bookmark-plus text-primary me-2"></i>
                                Save Filter Preset
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body">
                            <form id="savePresetForm">
                                <div class="mb-3">
                                    <label for="presetName" class="form-label">Preset Name</label>
                                    <input type="text" class="form-control" id="presetName"
                                           placeholder="e.g., High Priority Jobs" required maxlength="50">
                                    <div class="form-text">Give this filter combination a memorable name.</div>
                                </div>
                                <div class="alert alert-info small">
                                    <strong>Current filters:</strong>
                                    <ul class="mb-0 mt-2">
                                        ${Object.keys(filters).map(key =>
                                            `<li>${getFilterDisplayName(key)}: ${getFilterDisplayValue(key, filters[key])}</li>`
                                        ).join('')}
                                    </ul>
                                </div>
                            </form>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" id="confirmSavePreset">
                                <i class="bi bi-check-lg me-1"></i>Save Preset
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('savePresetModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal to DOM
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('savePresetModal'));
        modal.show();

        // Focus on input
        modal._element.addEventListener('shown.bs.modal', () => {
            document.getElementById('presetName')?.focus();
        });

        // Handle save
        document.getElementById('confirmSavePreset').addEventListener('click', () => {
            const nameInput = document.getElementById('presetName');
            const name = nameInput?.value.trim();

            if (!name) {
                nameInput?.focus();
                showToast('Please enter a preset name', 'warning');
                return;
            }

            addPreset(name, filters);
            modal.hide();
        });

        // Handle Enter key in input
        document.getElementById('presetName')?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                document.getElementById('confirmSavePreset')?.click();
            }
        });

        // Cleanup on hide
        modal._element.addEventListener('hidden.bs.modal', () => {
            modal._element.remove();
        });
    }

    // ========== Presets List ==========

    /**
     * Render saved presets list
     */
    function renderPresetsList() {
        const container = document.getElementById('filterPresetsList');
        if (!container) return;

        if (savedPresets.length === 0) {
            container.innerHTML = `
                <div class="text-center py-3 text-muted small">
                    <i class="bi bi-bookmark" style="font-size: 2rem; opacity: 0.3;"></i>
                    <p class="mt-2 mb-0">No saved filter presets yet.</p>
                </div>
            `;
            return;
        }

        let html = '<div class="list-group">';

        savedPresets.forEach(preset => {
            const filterCount = Object.keys(preset.filters).length;

            html += `
                <div class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                    <div class="flex-grow-1" role="button" tabindex="0"
                         data-preset-apply="${preset.id}"
                         style="cursor: pointer;">
                        <div class="fw-semibold">${escapeHtml(preset.name)}</div>
                        <small class="text-muted">
                            <i class="bi bi-funnel me-1"></i>${filterCount} filter${filterCount !== 1 ? 's' : ''}
                        </small>
                    </div>
                    <div class="btn-group btn-group-sm" role="group">
                        <button type="button" class="btn btn-outline-danger"
                                data-preset-delete="${preset.id}"
                                title="Delete preset"
                                aria-label="Delete preset ${escapeHtml(preset.name)}">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        });

        html += '</div>';
        container.innerHTML = html;

        // Add event listeners
        setupPresetsEventListeners();
    }

    /**
     * Setup event listeners for presets
     */
    function setupPresetsEventListeners() {
        // Apply preset
        document.querySelectorAll('[data-preset-apply]').forEach(element => {
            element.addEventListener('click', (e) => {
                const presetId = parseInt(e.target.closest('[data-preset-apply]').dataset.presetApply);
                applyPreset(presetId);
            });

            // Keyboard accessibility
            element.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const presetId = parseInt(e.target.closest('[data-preset-apply]').dataset.presetApply);
                    applyPreset(presetId);
                }
            });
        });

        // Delete preset
        document.querySelectorAll('[data-preset-delete]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const presetId = parseInt(btn.dataset.presetDelete);

                if (confirm('Are you sure you want to delete this filter preset?')) {
                    deletePreset(presetId);
                }
            });
        });
    }

    // ========== Toast Notifications ==========

    /**
     * Show toast notification
     */
    function showToast(message, type = 'success') {
        const toastContainer = document.querySelector('.toast-container') || createToastContainer();

        const iconMap = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };

        const toastHtml = `
            <div class="toast align-items-center text-bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true" data-bs-delay="3000">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="bi bi-${iconMap[type] || 'info-circle'} me-2"></i>
                        ${escapeHtml(message)}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });
    }

    /**
     * Create toast container if it doesn't exist
     */
    function createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '11000';
        document.body.appendChild(container);
        return container;
    }

    // ========== Utility Functions ==========

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // ========== Auto-submit Filters ==========

    /**
     * Setup auto-submit for select inputs
     */
    function setupAutoSubmit() {
        const form = document.getElementById('filterForm');
        if (!form) return;

        const autoSubmitInputs = form.querySelectorAll('select.auto-submit');

        autoSubmitInputs.forEach(input => {
            input.addEventListener('change', () => {
                form.submit();
            });
        });
    }

    // ========== Initialization ==========

    /**
     * Initialize filter management
     */
    function init() {
        console.log('Initializing filter management...');

        // Load saved presets
        loadPresets();

        // Initialize filter panel
        initializeFilterPanel();

        // Update filter count
        updateFilterCount();

        // Render filter badges
        renderFilterBadges();

        // Render presets list
        renderPresetsList();

        // Initialize save preset button
        initializeSavePreset();

        // Setup auto-submit
        setupAutoSubmit();

        console.log('Filter management initialized');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose functions globally
    window.filterManager = {
        getActiveFilters,
        clearAllFilters,
        savePreset: addPreset,
        applyPreset,
        deletePreset,
        loadPresets,
        renderPresetsList
    };

})();
