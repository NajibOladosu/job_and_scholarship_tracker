// Job & Scholarship Tracker - Main JavaScript

// Initialize Bootstrap toasts
document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss toasts after 5 seconds
    const toastElList = document.querySelectorAll('.toast');
    toastElList.forEach(function(toastEl) {
        const toast = new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
        toast.show();
    });

    // Add active class to current navigation item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.sidebar .nav-link, .navbar .nav-link');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// Confirmation dialogs for delete actions
document.addEventListener('click', function(e) {
    if (e.target.classList.contains('delete-confirm')) {
        if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
            e.preventDefault();
        }
    }
});

// Auto-submit form on filter change (for dashboard filters)
const filterSelects = document.querySelectorAll('.auto-submit');
filterSelects.forEach(select => {
    select.addEventListener('change', function() {
        this.form.submit();
    });
});
