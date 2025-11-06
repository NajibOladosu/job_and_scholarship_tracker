/**
 * Interview Management JavaScript
 *
 * Handles:
 * - Date/time picker integration for interviews
 * - Quick add interview modal
 * - Calendar view rendering
 * - Interview reminder notifications
 * - Drag-and-drop interview rescheduling
 */

(function() {
    'use strict';

    // ========== Configuration ==========

    const INTERVIEW_COLORS = {
        'scheduled': '#3b82f6',    // Blue
        'completed': '#10b981',    // Green
        'cancelled': '#ef4444',    // Red
        'rescheduled': '#f59e0b'   // Orange
    };

    // ========== State Management ==========

    let calendarEvents = [];
    let selectedDate = null;
    let draggedEvent = null;

    // ========== CSRF Token ==========

    /**
     * Get CSRF token for Django requests
     */
    function getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
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

    // ========== Date/Time Picker ==========

    /**
     * Initialize date/time pickers
     */
    function initializeDateTimePickers() {
        const dateInputs = document.querySelectorAll('.interview-date-picker');
        const timeInputs = document.querySelectorAll('.interview-time-picker');

        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];

        dateInputs.forEach(input => {
            input.setAttribute('min', today);

            // Add visual feedback on change
            input.addEventListener('change', function() {
                this.classList.add('is-valid');
                validateDateTime();
            });
        });

        timeInputs.forEach(input => {
            // Default to business hours if empty
            if (!input.value) {
                input.value = '10:00';
            }

            input.addEventListener('change', function() {
                this.classList.add('is-valid');
                validateDateTime();
            });
        });
    }

    /**
     * Validate date and time combination
     */
    function validateDateTime() {
        const dateInput = document.querySelector('.interview-date-picker');
        const timeInput = document.querySelector('.interview-time-picker');

        if (!dateInput || !timeInput) return true;

        const selectedDateTime = new Date(`${dateInput.value}T${timeInput.value}`);
        const now = new Date();

        if (selectedDateTime < now) {
            dateInput.classList.remove('is-valid');
            dateInput.classList.add('is-invalid');
            showToast('Interview date/time cannot be in the past', 'warning');
            return false;
        }

        return true;
    }

    // ========== Quick Add Interview Modal ==========

    /**
     * Initialize quick add interview modal
     */
    function initializeQuickAddModal() {
        const quickAddBtn = document.getElementById('quickAddInterviewBtn');
        const modalElement = document.getElementById('quickAddInterviewModal');

        if (!quickAddBtn || !modalElement) return;

        const modal = new bootstrap.Modal(modalElement);

        // Quick add button click
        quickAddBtn.addEventListener('click', () => {
            modal.show();
        });

        // Initialize date/time pickers in modal
        modal._element.addEventListener('shown.bs.modal', () => {
            initializeDateTimePickers();

            // Focus on first input
            const firstInput = modal._element.querySelector('input, select');
            if (firstInput) {
                firstInput.focus();
            }
        });

        // Handle form submission
        const form = modalElement.querySelector('form');
        if (form) {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();

                if (!validateDateTime()) {
                    return;
                }

                const formData = new FormData(form);

                try {
                    const response = await fetch('/tracker/api/interviews/add/', {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCsrfToken()
                        },
                        body: formData
                    });

                    const data = await response.json();

                    if (data.success) {
                        showToast('Interview scheduled successfully!', 'success');
                        modal.hide();
                        form.reset();

                        // Reload calendar if exists
                        if (typeof renderCalendar === 'function') {
                            await loadInterviewData();
                            renderCalendar();
                        }

                        // Reload page after delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500);
                    } else {
                        showToast(data.message || 'Failed to schedule interview', 'error');
                    }
                } catch (error) {
                    console.error('Error scheduling interview:', error);
                    showToast('Network error. Please try again.', 'error');
                }
            });
        }
    }

    // ========== Calendar View ==========

    /**
     * Load interview data from API
     */
    async function loadInterviewData() {
        try {
            const response = await fetch('/tracker/api/interviews/list/');
            const data = await response.json();

            if (data.success) {
                calendarEvents = data.interviews || [];
                return calendarEvents;
            } else {
                console.error('Failed to load interviews:', data.message);
                return [];
            }
        } catch (error) {
            console.error('Error loading interviews:', error);
            return [];
        }
    }

    /**
     * Render calendar view
     */
    function renderCalendar() {
        const calendarContainer = document.getElementById('interviewCalendar');
        if (!calendarContainer) return;

        const currentDate = selectedDate || new Date();
        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();

        // Generate calendar HTML
        const calendarHtml = generateCalendarHTML(year, month);
        calendarContainer.innerHTML = calendarHtml;

        // Add event listeners
        setupCalendarEventListeners();
    }

    /**
     * Generate calendar HTML for given month
     */
    function generateCalendarHTML(year, month) {
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();

        const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                           'July', 'August', 'September', 'October', 'November', 'December'];
        const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

        let html = `
            <div class="calendar-header d-flex justify-content-between align-items-center mb-4 p-3 bg-light rounded">
                <button class="btn btn-sm btn-outline-primary" id="prevMonth" aria-label="Previous month">
                    <i class="bi bi-chevron-left"></i>
                </button>
                <h4 class="mb-0 fw-bold">${monthNames[month]} ${year}</h4>
                <button class="btn btn-sm btn-outline-primary" id="nextMonth" aria-label="Next month">
                    <i class="bi bi-chevron-right"></i>
                </button>
            </div>
            <div class="calendar-grid">
                <div class="calendar-day-names row g-2 mb-2">
        `;

        // Day names header
        dayNames.forEach(day => {
            html += `<div class="col text-center fw-bold text-secondary small">${day}</div>`;
        });

        html += '</div><div class="calendar-days row g-2">';

        // Empty cells before first day
        for (let i = 0; i < startingDayOfWeek; i++) {
            html += '<div class="col calendar-day empty"></div>';
        }

        // Days of the month
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const dateString = date.toISOString().split('T')[0];
            const isToday = dateString === new Date().toISOString().split('T')[0];
            const dayEvents = calendarEvents.filter(e => e.date === dateString);

            html += `
                <div class="col calendar-day ${isToday ? 'today' : ''}" data-date="${dateString}">
                    <div class="day-number ${isToday ? 'fw-bold text-primary' : ''}">${day}</div>
            `;

            if (dayEvents.length > 0) {
                html += '<div class="day-events mt-1">';
                dayEvents.forEach(event => {
                    const color = INTERVIEW_COLORS[event.status] || INTERVIEW_COLORS.scheduled;
                    html += `
                        <div class="event-badge badge small mb-1"
                             style="background-color: ${color}; cursor: pointer; display: block;"
                             data-event-id="${event.id}"
                             draggable="true"
                             title="${escapeHtml(event.title)} - ${event.time}"
                             role="button"
                             tabindex="0"
                             aria-label="Interview: ${escapeHtml(event.title)} at ${event.time}">
                            <i class="bi bi-camera-video me-1"></i>${escapeHtml(truncate(event.title, 15))}
                        </div>
                    `;
                });
                html += '</div>';
            }

            html += '</div>';
        }

        html += '</div></div>';

        return html;
    }

    /**
     * Setup calendar event listeners
     */
    function setupCalendarEventListeners() {
        // Previous/Next month buttons
        const prevBtn = document.getElementById('prevMonth');
        const nextBtn = document.getElementById('nextMonth');

        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                const current = selectedDate || new Date();
                selectedDate = new Date(current.getFullYear(), current.getMonth() - 1, 1);
                renderCalendar();
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const current = selectedDate || new Date();
                selectedDate = new Date(current.getFullYear(), current.getMonth() + 1, 1);
                renderCalendar();
            });
        }

        // Event click handlers
        const eventBadges = document.querySelectorAll('.event-badge');
        eventBadges.forEach(badge => {
            badge.addEventListener('click', (e) => {
                const eventId = e.target.closest('.event-badge').dataset.eventId;
                showInterviewDetails(eventId);
            });

            // Keyboard accessibility
            badge.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const eventId = e.target.closest('.event-badge').dataset.eventId;
                    showInterviewDetails(eventId);
                }
            });
        });

        // Drag and drop setup
        setupDragAndDrop();
    }

    // ========== Drag and Drop ==========

    /**
     * Setup drag and drop for rescheduling
     */
    function setupDragAndDrop() {
        const eventBadges = document.querySelectorAll('.event-badge[draggable="true"]');
        const calendarDays = document.querySelectorAll('.calendar-day:not(.empty)');

        // Drag start
        eventBadges.forEach(badge => {
            badge.addEventListener('dragstart', (e) => {
                draggedEvent = {
                    id: badge.dataset.eventId,
                    element: badge
                };
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/html', badge.innerHTML);
                badge.style.opacity = '0.5';
            });

            badge.addEventListener('dragend', (e) => {
                badge.style.opacity = '1';
                draggedEvent = null;
            });
        });

        // Drop targets
        calendarDays.forEach(day => {
            day.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
                day.classList.add('drag-over');
            });

            day.addEventListener('dragleave', () => {
                day.classList.remove('drag-over');
            });

            day.addEventListener('drop', async (e) => {
                e.preventDefault();
                day.classList.remove('drag-over');

                if (!draggedEvent) return;

                const newDate = day.dataset.date;
                await rescheduleInterview(draggedEvent.id, newDate);
            });
        });
    }

    /**
     * Reschedule interview via API
     */
    async function rescheduleInterview(interviewId, newDate) {
        try {
            const response = await fetch(`/tracker/api/interviews/${interviewId}/reschedule/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken()
                },
                body: JSON.stringify({ new_date: newDate })
            });

            const data = await response.json();

            if (data.success) {
                showToast('Interview rescheduled successfully!', 'success');
                await loadInterviewData();
                renderCalendar();
            } else {
                showToast(data.message || 'Failed to reschedule interview', 'error');
            }
        } catch (error) {
            console.error('Error rescheduling interview:', error);
            showToast('Network error. Please try again.', 'error');
        }
    }

    // ========== Interview Details ==========

    /**
     * Show interview details in modal
     */
    function showInterviewDetails(interviewId) {
        const interview = calendarEvents.find(e => e.id == interviewId);
        if (!interview) return;

        const modalHtml = `
            <div class="modal fade" id="interviewDetailsModal" tabindex="-1" aria-labelledby="interviewDetailsLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered">
                    <div class="modal-content">
                        <div class="modal-header border-0 bg-light">
                            <h5 class="modal-title fw-bold" id="interviewDetailsLabel">
                                <i class="bi bi-camera-video text-primary me-2"></i>
                                Interview Details
                            </h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body p-4">
                            <h6 class="fw-bold mb-3">${escapeHtml(interview.title)}</h6>
                            <div class="mb-3">
                                <p class="mb-2">
                                    <i class="bi bi-building text-secondary me-2"></i>
                                    <strong>Company:</strong> ${escapeHtml(interview.company)}
                                </p>
                                <p class="mb-2">
                                    <i class="bi bi-calendar-event text-secondary me-2"></i>
                                    <strong>Date:</strong> ${formatDate(interview.date)}
                                </p>
                                <p class="mb-2">
                                    <i class="bi bi-clock text-secondary me-2"></i>
                                    <strong>Time:</strong> ${interview.time}
                                </p>
                                <p class="mb-2">
                                    <i class="bi bi-circle-fill text-secondary me-2" style="font-size: 0.5rem;"></i>
                                    <strong>Status:</strong> <span class="badge" style="background: ${INTERVIEW_COLORS[interview.status]}">${interview.status}</span>
                                </p>
                            </div>
                            ${interview.notes ? `<div class="alert alert-info"><strong>Notes:</strong><br>${escapeHtml(interview.notes)}</div>` : ''}
                        </div>
                        <div class="modal-footer border-0 bg-light">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                            <a href="/tracker/application/${interview.application_id}/" class="btn btn-primary">
                                <i class="bi bi-box-arrow-up-right me-1"></i>View Application
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Remove existing modal
        const existingModal = document.getElementById('interviewDetailsModal');
        if (existingModal) {
            existingModal.remove();
        }

        // Add new modal
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        const modal = new bootstrap.Modal(document.getElementById('interviewDetailsModal'));
        modal.show();

        // Cleanup on hide
        document.getElementById('interviewDetailsModal').addEventListener('hidden.bs.modal', function() {
            this.remove();
        });
    }

    // ========== Interview Reminders ==========

    /**
     * Check for upcoming interviews and show reminders
     */
    async function checkInterviewReminders() {
        const now = new Date();
        const oneDayFromNow = new Date(now.getTime() + 24 * 60 * 60 * 1000);

        const upcomingInterviews = calendarEvents.filter(interview => {
            const interviewDate = new Date(`${interview.date}T${interview.time}`);
            return interviewDate > now && interviewDate <= oneDayFromNow && interview.status === 'scheduled';
        });

        upcomingInterviews.forEach(interview => {
            const interviewDate = new Date(`${interview.date}T${interview.time}`);
            const hoursUntil = Math.round((interviewDate - now) / (1000 * 60 * 60));

            if (hoursUntil <= 24 && hoursUntil > 0) {
                showInterviewReminder(interview, hoursUntil);
            }
        });
    }

    /**
     * Show interview reminder notification
     */
    function showInterviewReminder(interview, hoursUntil) {
        const reminderKey = `interview_reminder_${interview.id}`;

        // Check if already shown in this session
        if (sessionStorage.getItem(reminderKey)) {
            return;
        }

        const timeText = hoursUntil === 1 ? '1 hour' : `${hoursUntil} hours`;

        showToast(
            `Reminder: Interview "${interview.title}" in ${timeText}`,
            'warning'
        );

        // Mark as shown
        sessionStorage.setItem(reminderKey, 'true');
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

    /**
     * Truncate text to specified length
     */
    function truncate(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength) + '...';
    }

    /**
     * Format date for display
     */
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
    }

    // ========== Initialization ==========

    /**
     * Initialize interview management
     */
    async function init() {
        console.log('Initializing interview management...');

        // Initialize date/time pickers
        initializeDateTimePickers();

        // Initialize quick add modal
        initializeQuickAddModal();

        // Load and render calendar if container exists
        const calendarContainer = document.getElementById('interviewCalendar');
        if (calendarContainer) {
            await loadInterviewData();
            renderCalendar();

            // Check for reminders
            checkInterviewReminders();

            // Set interval for periodic reminder checks (every 10 minutes)
            setInterval(checkInterviewReminders, 10 * 60 * 1000);
        }

        console.log('Interview management initialized');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose functions globally
    window.interviewManager = {
        loadInterviewData,
        renderCalendar,
        rescheduleInterview,
        showInterviewDetails
    };

    // Add calendar styles
    const calendarStyles = `
        .calendar-grid {
            user-select: none;
        }

        .calendar-day {
            min-height: 100px;
            padding: 0.75rem;
            border: 1px solid #e5e7eb;
            border-radius: 0.375rem;
            background: white;
            transition: all 0.2s;
        }

        .calendar-day:not(.empty):hover {
            background: #f9fafb;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        }

        .calendar-day.today {
            background: #eff6ff;
            border-color: #3b82f6;
        }

        .calendar-day.drag-over {
            background: #dbeafe;
            border-color: #3b82f6;
            border-width: 2px;
        }

        .calendar-day.empty {
            background: #f9fafb;
            border-color: transparent;
        }

        .day-number {
            font-size: 0.875rem;
            font-weight: 500;
            color: #6b7280;
        }

        .day-events {
            min-height: 20px;
        }

        .event-badge {
            font-size: 0.75rem;
            padding: 0.25rem 0.5rem;
            border-radius: 0.25rem;
            color: white;
            text-align: left;
            transition: transform 0.2s;
        }

        .event-badge:hover {
            transform: translateY(-2px);
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
        }

        .event-badge:focus {
            outline: 2px solid #3b82f6;
            outline-offset: 2px;
        }

        @media (max-width: 768px) {
            .calendar-day {
                min-height: 80px;
                padding: 0.5rem;
            }

            .event-badge {
                font-size: 0.65rem;
                padding: 0.2rem 0.4rem;
            }
        }
    `;

    // Inject calendar styles
    if (!document.getElementById('interview-calendar-styles')) {
        const styleSheet = document.createElement('style');
        styleSheet.id = 'interview-calendar-styles';
        styleSheet.textContent = calendarStyles;
        document.head.appendChild(styleSheet);
    }

})();
