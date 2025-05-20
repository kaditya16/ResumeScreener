// Main JavaScript file for Resume Shortlisting Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // File input validation
    const resumeInput = document.getElementById('resume');
    if (resumeInput) {
        resumeInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name || '';
            
            if (fileName && !fileName.toLowerCase().endsWith('.pdf')) {
                alert('Please upload a PDF file only.');
                this.value = ''; // Clear the file input
            }
            
            const fileSize = this.files[0]?.size || 0;
            const maxSize = 16 * 1024 * 1024; // 16MB
            
            if (fileSize > maxSize) {
                alert('File size exceeds the 16MB limit. Please upload a smaller file.');
                this.value = ''; // Clear the file input
            }
        });
    }

    // Form validation for create/edit JD form
    const jdForm = document.querySelector('form[action*="jd"]');
    if (jdForm) {
        jdForm.addEventListener('submit', function(event) {
            const jdId = document.getElementById('jd_id');
            const description = document.getElementById('description');
            
            if (jdId && jdId.value.trim() === '') {
                event.preventDefault();
                alert('Job ID cannot be empty.');
                jdId.focus();
                return false;
            }
            
            if (description.value.trim() === '') {
                event.preventDefault();
                alert('Job description cannot be empty.');
                description.focus();
                return false;
            }
            
            if (description.value.length < 50) {
                event.preventDefault();
                alert('Job description is too short. Please provide a more detailed description.');
                description.focus();
                return false;
            }
            
            return true;
        });
    }

    // Auto-expand textarea for job description
    const textareas = document.querySelectorAll('textarea');
    textareas.forEach(textarea => {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
        
        // Trigger on load to adjust for initial content
        const event = new Event('input');
        textarea.dispatchEvent(event);
    });

    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.alert-dismissible');
    flashMessages.forEach(message => {
        setTimeout(() => {
            const closeButton = message.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000); // Auto-dismiss after 5 seconds
    });
});
