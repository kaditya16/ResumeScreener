/**
 * Resume Shortlisting Application - Frontend JavaScript
 * Handles dynamic interactions, form validation, and API communication
 */

// Global variables
let currentUser = null;
let isAdmin = false;

// Initialize application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setupFormValidation();
    setupFileUpload();
    checkUserSession();
});

/**
 * Initialize the application
 */
function initializeApp() {
    console.log('Resume Shortlisting App initialized');
    
    // Add loading states to buttons
    setupButtonLoadingStates();
    
    // Initialize tooltips
    initializeTooltips();
    
    // Setup auto-refresh for admin dashboard
    if (window.location.pathname.includes('/admin')) {
        setupAutoRefresh();
    }
    
    // Setup theme persistence
    setupTheme();
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Navigation menu toggles
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            const target = document.querySelector(this.getAttribute('data-bs-target'));
            if (target) {
                target.classList.toggle('show');
            }
        });
    }
    
    // Sidebar links active state
    const sidebarLinks = document.querySelectorAll('.sidebar-link');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            sidebarLinks.forEach(l => l.classList.remove('active'));
            this.classList.add('active');
        });
    });
    
    // Table row clicks for better UX
    setupTableInteractions();
    
    // Search functionality
    setupSearchFeatures();
    
    // Keyboard shortcuts
    setupKeyboardShortcuts();
}

/**
 * Setup form validation
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
                return false;
            }
            
            // Add loading state to submit button
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                addLoadingState(submitBtn);
            }
        });
        
        // Real-time validation
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(this);
            });
            
            input.addEventListener('input', function() {
                clearFieldError(this);
            });
        });
    });
}

/**
 * Validate form fields
 */
function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required], textarea[required], select[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    return isValid;
}

/**
 * Validate individual field
 */
function validateField(field) {
    const value = field.value.trim();
    const fieldType = field.type;
    const fieldName = field.name;
    
    // Clear previous errors
    clearFieldError(field);
    
    // Required field validation
    if (field.required && !value) {
        showFieldError(field, 'This field is required');
        return false;
    }
    
    // Email validation
    if (fieldType === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            showFieldError(field, 'Please enter a valid email address');
            return false;
        }
    }
    
    // Password validation
    if (fieldName === 'password' && value) {
        if (value.length < 6) {
            showFieldError(field, 'Password must be at least 6 characters long');
            return false;
        }
    }
    
    // Confirm password validation
    if (fieldName === 'confirm_password' && value) {
        const passwordField = document.querySelector('input[name="password"]');
        if (passwordField && value !== passwordField.value) {
            showFieldError(field, 'Passwords do not match');
            return false;
        }
    }
    
    // File validation
    if (fieldType === 'file' && field.files.length > 0) {
        return validateFileUpload(field);
    }
    
    return true;
}

/**
 * Show field error
 */
function showFieldError(field, message) {
    field.classList.add('is-invalid');
    
    let errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentNode.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
}

/**
 * Clear field error
 */
function clearFieldError(field) {
    field.classList.remove('is-invalid');
    const errorDiv = field.parentNode.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.remove();
    }
}

/**
 * Setup file upload functionality
 */
function setupFileUpload() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            handleFileSelection(this);
        });
        
        // Drag and drop support
        const parentDiv = input.closest('.mb-3') || input.parentNode;
        setupDragAndDrop(parentDiv, input);
    });
}

/**
 * Handle file selection
 */
function handleFileSelection(input) {
    const file = input.files[0];
    
    if (!file) return;
    
    // Validate file
    if (!validateFileUpload(input)) {
        input.value = '';
        return;
    }
    
    // Show file info
    showFileInfo(input, file);
}

/**
 * Validate file upload
 */
function validateFileUpload(input) {
    const file = input.files[0];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    if (!file) return true;
    
    // Check file type
    if (input.accept && !input.accept.split(',').some(type => 
        file.type === type.trim() || file.name.toLowerCase().endsWith(type.trim().replace('*', '')))) {
        showFieldError(input, 'Invalid file type. Please select a PDF file.');
        return false;
    }
    
    // Check file size
    if (file.size > maxSize) {
        showFieldError(input, 'File size must be less than 16MB.');
        return false;
    }
    
    return true;
}

/**
 * Show file information
 */
function showFileInfo(input, file) {
    const fileSize = (file.size / 1024 / 1024).toFixed(2);
    const fileName = file.name;
    
    let infoDiv = input.parentNode.querySelector('.file-info');
    if (!infoDiv) {
        infoDiv = document.createElement('div');
        infoDiv.className = 'file-info mt-2 p-2 bg-light rounded';
        input.parentNode.appendChild(infoDiv);
    }
    
    infoDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-file-pdf text-danger me-2"></i>
            <div>
                <div class="fw-bold">${fileName}</div>
                <small class="text-muted">${fileSize} MB</small>
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger ms-auto" onclick="clearFileSelection('${input.id}')">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
}

/**
 * Clear file selection
 */
function clearFileSelection(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.value = '';
        const infoDiv = input.parentNode.querySelector('.file-info');
        if (infoDiv) {
            infoDiv.remove();
        }
    }
}

/**
 * Setup drag and drop for file uploads
 */
function setupDragAndDrop(element, input) {
    element.addEventListener('dragover', function(e) {
        e.preventDefault();
        this.classList.add('border-primary', 'bg-light');
    });
    
    element.addEventListener('dragleave', function(e) {
        e.preventDefault();
        this.classList.remove('border-primary', 'bg-light');
    });
    
    element.addEventListener('drop', function(e) {
        e.preventDefault();
        this.classList.remove('border-primary', 'bg-light');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            input.files = files;
            handleFileSelection(input);
        }
    });
}

/**
 * Setup button loading states
 */
function setupButtonLoadingStates() {
    const buttons = document.querySelectorAll('button[type="submit"], .btn-loading');
    
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.form && !this.form.checkValidity()) {
                return;
            }
            
            addLoadingState(this);
        });
    });
}

/**
 * Add loading state to button
 */
function addLoadingState(button) {
    if (button.classList.contains('loading')) return;
    
    button.classList.add('loading');
    button.disabled = true;
    
    const originalText = button.innerHTML;
    button.setAttribute('data-original-text', originalText);
    
    const loadingIcon = '<i class="fas fa-spinner fa-spin me-2"></i>';
    const loadingText = button.getAttribute('data-loading-text') || 'Processing...';
    
    button.innerHTML = loadingIcon + loadingText;
    
    // Auto-remove loading state after 30 seconds
    setTimeout(() => {
        removeLoadingState(button);
    }, 30000);
}

/**
 * Remove loading state from button
 */
function removeLoadingState(button) {
    button.classList.remove('loading');
    button.disabled = false;
    
    const originalText = button.getAttribute('data-original-text');
    if (originalText) {
        button.innerHTML = originalText;
    }
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Setup table interactions
 */
function setupTableInteractions() {
    const tableRows = document.querySelectorAll('table tbody tr');
    
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'hsl(210, 11%, 98%)';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });
}

/**
 * Setup search features
 */
function setupSearchFeatures() {
    const searchInputs = document.querySelectorAll('.search-input, input[placeholder*="search" i]');
    
    searchInputs.forEach(input => {
        let searchTimeout;
        
        input.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value, this);
            }, 300);
        });
    });
}

/**
 * Perform search functionality
 */
function performSearch(query, input) {
    const targetTable = input.getAttribute('data-search-target');
    if (!targetTable) return;
    
    const table = document.querySelector(targetTable);
    if (!table) return;
    
    const rows = table.querySelectorAll('tbody tr');
    const searchQuery = query.toLowerCase().trim();
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        if (searchQuery === '' || text.includes(searchQuery)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
    
    // Update results count
    const visibleRows = table.querySelectorAll('tbody tr:not([style*="display: none"])').length;
    updateSearchResults(visibleRows, input);
}

/**
 * Update search results count
 */
function updateSearchResults(count, input) {
    let resultsDiv = input.parentNode.querySelector('.search-results');
    if (!resultsDiv) {
        resultsDiv = document.createElement('div');
        resultsDiv.className = 'search-results text-muted small mt-1';
        input.parentNode.appendChild(resultsDiv);
    }
    
    resultsDiv.textContent = count > 0 ? `${count} result(s) found` : 'No results found';
}

/**
 * Setup keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('.search-input, input[placeholder*="search" i]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const activeSearch = document.activeElement;
            if (activeSearch && activeSearch.classList.contains('search-input')) {
                activeSearch.value = '';
                performSearch('', activeSearch);
            }
        }
    });
}

/**
 * Setup auto-refresh for admin dashboard
 */
function setupAutoRefresh() {
    const refreshInterval = 30000; // 30 seconds
    
    setInterval(() => {
        if (document.visibilityState === 'visible') {
            refreshDashboardData();
        }
    }, refreshInterval);
}

/**
 * Refresh dashboard data
 */
function refreshDashboardData() {
    // Only refresh if on admin dashboard
    if (!window.location.pathname.includes('/admin')) return;
    
    // Check if page has auto-refresh capability
    if (typeof loadJobDescriptions === 'function') {
        loadJobDescriptions();
    }
    
    if (typeof loadApplications === 'function') {
        loadApplications();
    }
}

/**
 * Setup theme persistence
 */
function setupTheme() {
    const savedTheme = localStorage.getItem('app-theme');
    if (savedTheme) {
        document.body.setAttribute('data-theme', savedTheme);
    }
}

/**
 * Check user session
 */
function checkUserSession() {
    // This would normally check with the server for session validity
    // For now, we'll check if user info is available in the page
    const userEmail = document.querySelector('[data-user-email]');
    const isAdminElement = document.querySelector('[data-is-admin]');
    
    if (userEmail) {
        currentUser = {
            email: userEmail.getAttribute('data-user-email'),
            isAdmin: isAdminElement ? isAdminElement.getAttribute('data-is-admin') === 'true' : false
        };
        isAdmin = currentUser.isAdmin;
    }
}

/**
 * Utility function to show notifications
 */
function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, duration);
}

/**
 * Utility function to format dates
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Utility function to format file sizes
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Utility function to debounce function calls
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Utility function to copy text to clipboard
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Copied to clipboard!', 'success', 2000);
    } catch (err) {
        console.error('Failed to copy: ', err);
        showNotification('Failed to copy to clipboard', 'error');
    }
}

/**
 * Export functions for global use
 */
window.AppUtils = {
    showNotification,
    formatDate,
    formatFileSize,
    copyToClipboard,
    addLoadingState,
    removeLoadingState,
    clearFileSelection,
    debounce
};

// Log initialization
console.log('Resume Shortlisting App JavaScript loaded successfully');
