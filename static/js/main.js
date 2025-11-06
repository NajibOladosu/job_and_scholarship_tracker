/**
 * Job & Scholarship Tracker - Main JavaScript
 *
 * Core functionality:
 * - Toast notifications system
 * - Keyboard shortcuts
 * - Bulk selection
 * - Archive confirmations
 * - Navigation active states
 * - Quick actions
 */

(function() {
    'use strict';

    // ========== State Management ==========

    const state = {
        bulkSelection: new Set(),
        keyboardShortcutsEnabled: true
    };

    // ========== Toast Notification System ==========

    /**
     * Enhanced toast notification system
     */
    const ToastManager = {
        container: null,

        /**
         * Initialize toast container
         */
        init() {
            this.container = document.querySelector('.toast-container');
            if (!this.container) {
                this.container = this.createContainer();
            }
            this.initializeExistingToasts();
        },

        /**
         * Create toast container
         */
        createContainer() {
            const container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            container.style.zIndex = '11000';
            document.body.appendChild(container);
            return container;
        },

        /**
         * Initialize existing toasts from Django messages
         */
        initializeExistingToasts() {
            const toastElList = document.querySelectorAll('.toast');
            toastElList.forEach(toastEl => {
                const toast = new bootstrap.Toast(toastEl, {
                    autohide: true,
                    delay: 5000
                });
                toast.show();
            });
        },

        /**
         * Show toast notification
         */
        show(message, type = 'info', options = {}) {
            const {
                duration = 5000,
                icon = null,
                action = null,
                dismissible = true
            } = options;

            const iconMap = {
                success: 'check-circle',
                error: 'exclamation-circle',
                warning: 'exclamation-triangle',
                info: 'info-circle',
                danger: 'exclamation-triangle'
            };

            const toastIcon = icon || iconMap[type] || 'info-circle';

            let actionHtml = '';
            if (action) {
                actionHtml = `
                    <button type="button" class="btn btn-sm btn-light ms-2"
                            onclick="${action.onClick}">
                        ${action.label}
                    </button>
                `;
            }

            const toastHtml = `
                <div class="toast align-items-center text-bg-${type} border-0"
                     role="alert" aria-live="assertive" aria-atomic="true"
                     data-bs-delay="${duration}">
                    <div class="d-flex">
                        <div class="toast-body d-flex align-items-center">
                            <i class="bi bi-${toastIcon} me-2"></i>
                            <span>${this.escapeHtml(message)}</span>
                            ${actionHtml}
                        </div>
                        ${dismissible ? '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>' : ''}
                    </div>
                </div>
            `;

            this.container.insertAdjacentHTML('beforeend', toastHtml);
            const toastElement = this.container.lastElementChild;
            const toast = new bootstrap.Toast(toastElement);
            toast.show();

            // Remove from DOM after hidden
            toastElement.addEventListener('hidden.bs.toast', () => {
                toastElement.remove();
            });

            return toast;
        },

        /**
         * Show success toast
         */
        success(message, options = {}) {
            return this.show(message, 'success', options);
        },

        /**
         * Show error toast
         */
        error(message, options = {}) {
            return this.show(message, 'danger', { ...options, duration: 8000 });
        },

        /**
         * Show warning toast
         */
        warning(message, options = {}) {
            return this.show(message, 'warning', options);
        },

        /**
         * Show info toast
         */
        info(message, options = {}) {
            return this.show(message, 'info', options);
        },

        /**
         * Escape HTML
         */
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    };

    // ========== Bulk Selection ==========

    /**
     * Initialize bulk selection functionality
     */
    function initializeBulkSelection() {
        const selectAllCheckbox = document.getElementById('selectAllItems');
        const itemCheckboxes = document.querySelectorAll('.item-checkbox');
        const bulkActionsBar = document.getElementById('bulkActionsBar');

        if (!selectAllCheckbox || itemCheckboxes.length === 0) return;

        // Select all toggle
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;

            itemCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
                if (isChecked) {
                    state.bulkSelection.add(checkbox.value);
                } else {
                    state.bulkSelection.delete(checkbox.value);
                }
            });

            updateBulkActionsBar();
        });

        // Individual checkboxes
        itemCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', function() {
                if (this.checked) {
                    state.bulkSelection.add(this.value);
                } else {
                    state.bulkSelection.delete(this.value);
                }

                // Update select all checkbox
                selectAllCheckbox.checked = itemCheckboxes.length > 0 &&
                    Array.from(itemCheckboxes).every(cb => cb.checked);

                updateBulkActionsBar();
            });
        });

        // Bulk action buttons
        setupBulkActionButtons();
    }

    /**
     * Update bulk actions bar visibility and count
     */
    function updateBulkActionsBar() {
        const bulkActionsBar = document.getElementById('bulkActionsBar');
        const selectedCount = document.getElementById('selectedCount');

        if (!bulkActionsBar) return;

        const count = state.bulkSelection.size;

        if (count > 0) {
            bulkActionsBar.classList.remove('d-none');
            if (selectedCount) {
                selectedCount.textContent = count;
            }
        } else {
            bulkActionsBar.classList.add('d-none');
        }
    }

    /**
     * Setup bulk action buttons
     */
    function setupBulkActionButtons() {
        const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
        const bulkArchiveBtn = document.getElementById('bulkArchiveBtn');
        const bulkExportBtn = document.getElementById('bulkExportBtn');

        if (bulkDeleteBtn) {
            bulkDeleteBtn.addEventListener('click', () => {
                if (confirm(`Delete ${state.bulkSelection.size} selected items? This cannot be undone.`)) {
                    performBulkAction('delete');
                }
            });
        }

        if (bulkArchiveBtn) {
            bulkArchiveBtn.addEventListener('click', () => {
                if (confirm(`Archive ${state.bulkSelection.size} selected items?`)) {
                    performBulkAction('archive');
                }
            });
        }

        if (bulkExportBtn) {
            bulkExportBtn.addEventListener('click', () => {
                performBulkAction('export');
            });
        }
    }

    /**
     * Perform bulk action on selected items
     */
    async function performBulkAction(action) {
        const ids = Array.from(state.bulkSelection);

        try {
            const response = await fetch(`/tracker/api/bulk/${action}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ ids })
            });

            const data = await response.json();

            if (data.success) {
                ToastManager.success(`${action} completed successfully`);
                setTimeout(() => window.location.reload(), 1000);
            } else {
                ToastManager.error(data.message || `Failed to ${action} items`);
            }
        } catch (error) {
            console.error(`Bulk ${action} error:`, error);
            ToastManager.error('Network error. Please try again.');
        }
    }

    // ========== Keyboard Shortcuts ==========

    /**
     * Initialize keyboard shortcuts
     */
    function initializeKeyboardShortcuts() {
        document.addEventListener('keydown', function(e) {
            if (!state.keyboardShortcutsEnabled) return;

            // Ignore shortcuts when typing in inputs
            if (e.target.matches('input, textarea, select, [contenteditable]')) {
                // Allow Ctrl/Cmd shortcuts even in inputs
                if (!e.ctrlKey && !e.metaKey) return;
            }

            // ? - Show keyboard shortcuts help
            if (e.key === '?' && !e.ctrlKey && !e.metaKey) {
                e.preventDefault();
                showKeyboardShortcutsHelp();
                return;
            }

            // Ctrl/Cmd + K - Focus search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                focusSearch();
                return;
            }

            // Ctrl/Cmd + N - New application
            if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
                e.preventDefault();
                window.location.href = '/tracker/application/create/';
                return;
            }

            // Esc - Clear selection / Close modals
            if (e.key === 'Escape') {
                clearBulkSelection();
                return;
            }

            // Ctrl/Cmd + A - Select all (on dashboard)
            if ((e.ctrlKey || e.metaKey) && e.key === 'a' && document.getElementById('selectAllItems')) {
                e.preventDefault();
                document.getElementById('selectAllItems')?.click();
                return;
            }
        });
    }

    /**
     * Show keyboard shortcuts help modal
     */
    function showKeyboardShortcutsHelp() {
        const shortcuts = [
            { keys: '?', description: 'Show keyboard shortcuts' },
            { keys: 'Ctrl/⌘ + K', description: 'Focus search' },
            { keys: 'Ctrl/⌘ + N', description: 'New application' },
            { keys: 'Ctrl/⌘ + A', description: 'Select all items' },
            { keys: 'Esc', description: 'Clear selection' },
            { keys: 'Ctrl/⌘ + S', description: 'Save (in editors)' },
            { keys: 'Ctrl/⌘ + B', description: 'Bold text (in notes)' },
            { keys: 'Ctrl/⌘ + I', description: 'Italic text (in notes)' }
        ];

        const modalHtml = `
            <div class="modal fade" id="keyboardShortcutsModal" tabindex="-1" aria-labelledby="shortcutsLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header border-0 bg-light">
                            <h5 class="modal-title fw-bold" id="shortcutsLabel">
                                <i class="bi bi-keyboard text-primary me-2"></i>
                                Keyboard Shortcuts
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body p-4">
                            <div class="list-group">
                                ${shortcuts.map(shortcut => `
                                    <div class="list-group-item border-0 d-flex justify-content-between align-items-center py-3">
                                        <span>${shortcut.description}</span>
                                        <kbd class="bg-light text-dark border px-2 py-1 rounded">${shortcut.keys}</kbd>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        <div class="modal-footer border-0 bg-light">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('keyboardShortcutsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('keyboardShortcutsModal'));
        modal.show();

        // Cleanup
        modal._element.addEventListener('hidden.bs.modal', () => {
            modal._element.remove();
        });
    }

    /**
     * Focus search input
     */
    function focusSearch() {
        const searchInput = document.querySelector('input[name="search"], #id_search, .search-input');
        if (searchInput) {
            searchInput.focus();
            searchInput.select();
        }
    }

    /**
     * Clear bulk selection
     */
    function clearBulkSelection() {
        state.bulkSelection.clear();
        document.querySelectorAll('.item-checkbox').forEach(cb => cb.checked = false);
        const selectAll = document.getElementById('selectAllItems');
        if (selectAll) selectAll.checked = false;
        updateBulkActionsBar();
    }

    // ========== Archive Confirmations ==========

    /**
     * Enhanced confirmation dialogs
     */
    function initializeConfirmations() {
        // Delete confirmations
        document.addEventListener('click', function(e) {
            if (e.target.closest('.delete-confirm')) {
                const btn = e.target.closest('.delete-confirm');
                const itemName = btn.dataset.itemName || 'this item';

                if (!confirm(`Are you sure you want to delete ${itemName}? This action cannot be undone.`)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }

            // Archive confirmations
            if (e.target.closest('.archive-confirm')) {
                const btn = e.target.closest('.archive-confirm');
                const itemName = btn.dataset.itemName || 'this item';

                if (!confirm(`Archive ${itemName}? You can restore it later from the archive.`)) {
                    e.preventDefault();
                    e.stopPropagation();
                }
            }
        });
    }

    // ========== Navigation Active States ==========

    /**
     * Set active navigation item
     */
    function setActiveNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.sidebar .nav-link, .navbar .nav-link');

        navLinks.forEach(link => {
            const href = link.getAttribute('href');

            // Exact match
            if (href === currentPath) {
                link.classList.add('active');
            }
            // Partial match for sections
            else if (href !== '/' && currentPath.startsWith(href)) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    // ========== Auto-submit Filters ==========

    /**
     * Auto-submit forms on change
     */
    function initializeAutoSubmit() {
        const filterSelects = document.querySelectorAll('.auto-submit');
        filterSelects.forEach(select => {
            select.addEventListener('change', function() {
                this.form?.submit();
            });
        });
    }

    // ========== Utility Functions ==========

    /**
     * Get CSRF token
     */
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

    // ========== Initialization ==========

    /**
     * Initialize all main functionality
     */
    function init() {
        console.log('Initializing main application...');

        // Initialize toast system
        ToastManager.init();

        // Set active navigation
        setActiveNavigation();

        // Initialize confirmations
        initializeConfirmations();

        // Initialize auto-submit
        initializeAutoSubmit();

        // Initialize bulk selection (if on dashboard)
        initializeBulkSelection();

        // Initialize keyboard shortcuts
        initializeKeyboardShortcuts();

        // Add keyboard shortcuts help button to UI
        addKeyboardShortcutsButton();

        console.log('Main application initialized');
    }

    /**
     * Add keyboard shortcuts help button to UI
     */
    function addKeyboardShortcutsButton() {
        // Check if button already exists
        if (document.getElementById('keyboardShortcutsBtn')) return;

        // Add to topbar or footer
        const topbar = document.querySelector('.topbar, .navbar');
        if (topbar) {
            const btn = document.createElement('button');
            btn.id = 'keyboardShortcutsBtn';
            btn.className = 'btn btn-link text-secondary position-fixed';
            btn.style.cssText = 'bottom: 20px; right: 20px; z-index: 1000; opacity: 0.5;';
            btn.title = 'Keyboard Shortcuts (?)';
            btn.innerHTML = '<i class="bi bi-keyboard"></i>';
            btn.setAttribute('aria-label', 'Show keyboard shortcuts');

            btn.addEventListener('click', showKeyboardShortcutsHelp);
            btn.addEventListener('mouseenter', () => btn.style.opacity = '1');
            btn.addEventListener('mouseleave', () => btn.style.opacity = '0.5');

            document.body.appendChild(btn);
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose globally
    window.AppTracker = {
        toast: ToastManager,
        bulkSelection: state.bulkSelection,
        clearSelection: clearBulkSelection,
        showKeyboardHelp: showKeyboardShortcutsHelp
    };

})();
