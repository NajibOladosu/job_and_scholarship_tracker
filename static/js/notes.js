/**
 * Rich Text Notes Editor with Auto-Save and Keyboard Shortcuts
 * Handles Quill.js editor initialization, auto-save functionality, and keyboard shortcuts
 */

(function() {
    'use strict';

    // Configuration
    const AUTOSAVE_DELAY = 3000; // 3 seconds
    const DEBOUNCE_DELAY = 500; // 0.5 seconds
    const WORD_COUNT_UPDATE_DELAY = 300; // 0.3 seconds

    // State
    let quill = null;
    let autosaveTimeout = null;
    let wordCountTimeout = null;
    let lastSavedContent = '';
    let lastSavedTitle = '';
    let lastSavedTime = null;
    let isSaving = false;
    let noteId = null;

    /**
     * Get CSRF token for Django requests
     */
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }

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
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        `;

        toastContainer.insertAdjacentHTML('beforeend', toastHtml);
        const toastElement = toastContainer.lastElementChild;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Remove from DOM after hidden
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

    /**
     * Update save status indicator
     */
    function updateSaveStatus(status) {
        const statusElement = document.getElementById('save-status');
        if (!statusElement) return;

        const statusConfig = {
            saving: {
                text: 'Saving...',
                icon: 'bi-hourglass-split',
                class: 'text-warning'
            },
            saved: {
                text: 'Saved',
                icon: 'bi-check-circle-fill',
                class: 'text-success'
            },
            error: {
                text: 'Save failed',
                icon: 'bi-exclamation-circle-fill',
                class: 'text-danger'
            },
            idle: {
                text: '',
                icon: '',
                class: ''
            }
        };

        const config = statusConfig[status] || statusConfig.idle;
        statusElement.innerHTML = config.icon ? `<i class="bi ${config.icon} me-1"></i>${config.text}` : config.text;
        statusElement.className = `small ${config.class}`;
    }

    /**
     * Update last saved timestamp
     */
    function updateLastSavedTimestamp() {
        const timestampElement = document.getElementById('last-saved-time');
        if (!timestampElement) return;

        if (lastSavedTime) {
            const now = new Date();
            const diff = Math.floor((now - lastSavedTime) / 1000); // seconds

            let timeText;
            if (diff < 60) {
                timeText = 'Just now';
            } else if (diff < 3600) {
                const minutes = Math.floor(diff / 60);
                timeText = `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
            } else {
                timeText = lastSavedTime.toLocaleTimeString('en-US', {
                    hour: 'numeric',
                    minute: '2-digit',
                    hour12: true
                });
            }

            timestampElement.innerHTML = `<i class="bi bi-clock me-1"></i>Last saved: ${timeText}`;
            timestampElement.className = 'small text-muted';
        } else {
            timestampElement.innerHTML = '';
        }
    }

    /**
     * Count words in text
     */
    function countWords(text) {
        // Strip HTML tags and get plain text
        const plainText = text.replace(/<[^>]*>/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();

        if (!plainText) return 0;

        // Count words
        const words = plainText.split(/\s+/).filter(word => word.length > 0);
        return words.length;
    }

    /**
     * Update word count display
     */
    function updateWordCount() {
        const wordCountElement = document.getElementById('word-count');
        if (!wordCountElement || !quill) return;

        const content = quill.root.innerHTML;
        const wordCount = countWords(content);
        const charCount = quill.getText().trim().length;

        wordCountElement.innerHTML = `
            <i class="bi bi-file-text me-1"></i>
            ${wordCount} word${wordCount !== 1 ? 's' : ''},
            ${charCount} character${charCount !== 1 ? 's' : ''}
        `;
        wordCountElement.className = 'small text-muted';
    }

    /**
     * Schedule word count update (debounced)
     */
    function scheduleWordCountUpdate() {
        if (wordCountTimeout) {
            clearTimeout(wordCountTimeout);
        }
        wordCountTimeout = setTimeout(updateWordCount, WORD_COUNT_UPDATE_DELAY);
    }

    /**
     * Auto-save note content
     */
    async function autoSaveNote() {
        if (isSaving) return;

        const titleInput = document.getElementById('note-title');
        const currentTitle = titleInput?.value.trim() || 'Untitled Note';
        const currentContent = quill ? quill.root.innerHTML : '';

        // Check if content has changed
        if (currentTitle === lastSavedTitle && currentContent === lastSavedContent) {
            return;
        }

        isSaving = true;
        updateSaveStatus('saving');

        try {
            const response = await fetch('/tracker/api/notes/autosave/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({
                    note_id: noteId,
                    title: currentTitle,
                    content: currentContent
                })
            });

            const data = await response.json();

            if (data.success) {
                lastSavedTitle = currentTitle;
                lastSavedContent = currentContent;
                lastSavedTime = new Date();
                updateSaveStatus('saved');
                updateLastSavedTimestamp();

                // Update note ID if this was a new note
                if (!noteId && data.note_id) {
                    noteId = data.note_id;
                    // Update hidden input if it exists
                    const noteIdInput = document.getElementById('note-id-hidden');
                    if (noteIdInput) {
                        noteIdInput.value = noteId;
                    }
                    // Update URL without reload
                    if (window.history && window.history.pushState) {
                        const newUrl = `/tracker/notes/${noteId}/edit/`;
                        window.history.pushState({ path: newUrl }, '', newUrl);
                    }
                }

                // Clear saved status after 2 seconds
                setTimeout(() => {
                    updateSaveStatus('idle');
                }, 2000);
            } else {
                updateSaveStatus('error');
                showToast(data.message || 'Failed to save note', 'error');
            }
        } catch (error) {
            console.error('Auto-save error:', error);
            updateSaveStatus('error');
            showToast('Network error: Failed to save note', 'error');
        } finally {
            isSaving = false;
        }
    }

    /**
     * Debounced auto-save
     */
    function scheduleAutoSave() {
        if (autosaveTimeout) {
            clearTimeout(autosaveTimeout);
        }
        autosaveTimeout = setTimeout(autoSaveNote, AUTOSAVE_DELAY);
    }

    /**
     * Initialize Quill editor
     */
    function initializeQuillEditor() {
        const editorElement = document.getElementById('quill-editor');
        if (!editorElement) return;

        // Initialize Quill
        quill = new Quill('#quill-editor', {
            theme: 'snow',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    [{ 'color': [] }, { 'background': [] }],
                    ['link'],
                    ['clean']
                ]
            },
            placeholder: 'Start writing your note...'
        });

        // Load existing content if editing
        const contentInput = document.getElementById('note-content-input');
        if (contentInput && contentInput.value) {
            quill.root.innerHTML = contentInput.value;
            lastSavedContent = contentInput.value;
        }

        // Store initial title
        const titleInput = document.getElementById('note-title');
        if (titleInput) {
            lastSavedTitle = titleInput.value;
        }

        // Get note ID if editing existing note
        const noteIdInput = document.getElementById('note-id-hidden');
        if (noteIdInput && noteIdInput.value) {
            noteId = parseInt(noteIdInput.value);
        }

        // Listen for content changes
        quill.on('text-change', function() {
            // Update hidden input for form submission
            if (contentInput) {
                contentInput.value = quill.root.innerHTML;
            }
            // Schedule auto-save
            scheduleAutoSave();
            // Update word count
            scheduleWordCountUpdate();
        });

        // Initial word count
        updateWordCount();

        // Listen for title changes
        if (titleInput) {
            titleInput.addEventListener('input', function() {
                scheduleAutoSave();
            });
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            // Only handle shortcuts when Quill editor is focused
            const editorFocused = document.activeElement.closest('.ql-editor');

            // Ctrl+S or Cmd+S to save
            if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                e.preventDefault();
                autoSaveNote();
                showToast('Saving note...', 'info');
                return false;
            }

            // Ctrl+B for bold (only when editor is focused)
            if (editorFocused && (e.ctrlKey || e.metaKey) && e.key === 'b') {
                e.preventDefault();
                const currentFormat = quill.getFormat();
                quill.format('bold', !currentFormat.bold);
                return false;
            }

            // Ctrl+I for italic (only when editor is focused)
            if (editorFocused && (e.ctrlKey || e.metaKey) && e.key === 'i') {
                e.preventDefault();
                const currentFormat = quill.getFormat();
                quill.format('italic', !currentFormat.italic);
                return false;
            }

            // Ctrl+U for underline (only when editor is focused)
            if (editorFocused && (e.ctrlKey || e.metaKey) && e.key === 'u') {
                e.preventDefault();
                const currentFormat = quill.getFormat();
                quill.format('underline', !currentFormat.underline);
                return false;
            }
        });

        // Update timestamp periodically
        setInterval(updateLastSavedTimestamp, 30000); // Update every 30 seconds

        // Form submission handler
        const form = document.getElementById('note-form');
        if (form) {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();

                // Save current content
                await autoSaveNote();

                // Show success message and redirect
                showToast('Note saved successfully!', 'success');
                setTimeout(() => {
                    window.location.href = '/tracker/notes/';
                }, 1000);
            });
        }

        // Warn before leaving if there are unsaved changes
        window.addEventListener('beforeunload', function(e) {
            const currentTitle = titleInput?.value.trim() || 'Untitled Note';
            const currentContent = quill ? quill.root.innerHTML : '';

            if (currentTitle !== lastSavedTitle || currentContent !== lastSavedContent) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    }

    /**
     * Initialize note list features (search, filter, pin toggle)
     */
    function initializeNoteList() {
        // Pin toggle buttons
        const pinButtons = document.querySelectorAll('.pin-toggle-btn');
        pinButtons.forEach(button => {
            button.addEventListener('click', async function(e) {
                e.preventDefault();
                const noteId = this.dataset.noteId;
                const icon = this.querySelector('i');

                try {
                    const response = await fetch(`/tracker/api/notes/${noteId}/toggle-pin/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCsrfToken()
                        }
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Update icon
                        if (data.is_pinned) {
                            icon.classList.remove('bi-pin');
                            icon.classList.add('bi-pin-fill');
                            this.classList.add('text-warning');
                            showToast('Note pinned', 'success');
                        } else {
                            icon.classList.remove('bi-pin-fill');
                            icon.classList.add('bi-pin');
                            this.classList.remove('text-warning');
                            showToast('Note unpinned', 'success');
                        }

                        // Reload page after 500ms to update order
                        setTimeout(() => {
                            window.location.reload();
                        }, 500);
                    } else {
                        showToast('Failed to toggle pin', 'error');
                    }
                } catch (error) {
                    console.error('Pin toggle error:', error);
                    showToast('Network error', 'error');
                }
            });
        });

        // Search functionality (debounced)
        const searchInput = document.getElementById('note-search');
        if (searchInput) {
            let searchTimeout;
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    const form = this.closest('form');
                    if (form) {
                        form.submit();
                    }
                }, DEBOUNCE_DELAY);
            });
        }

        // Filter by application
        const appFilter = document.getElementById('application-filter');
        if (appFilter) {
            appFilter.addEventListener('change', function() {
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            });
        }
    }

    /**
     * Initialize on DOM ready
     */
    function init() {
        // Check if we're on the editor page
        if (document.getElementById('quill-editor')) {
            // Wait for Quill to be available
            if (typeof Quill !== 'undefined') {
                initializeQuillEditor();
            } else {
                console.error('Quill.js not loaded');
            }
        }

        // Check if we're on the list page
        if (document.querySelector('.note-list-container')) {
            initializeNoteList();
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

})();
