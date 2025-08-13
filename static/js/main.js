// Main JavaScript file for the Hybrid Text Compression System

// Loading overlay functions
function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'flex';
    }
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
}

// Toast notification system
function showToast(message, type = 'info') {
    // Create container if it doesn't exist
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon;
    switch (type) {
        case 'success':
            icon = 'fas fa-check-circle';
            break;
        case 'error':
            icon = 'fas fa-exclamation-circle';
            break;
        case 'warning':
            icon = 'fas fa-exclamation-triangle';
            break;
        default:
            icon = 'fas fa-info-circle';
    }

    toast.innerHTML = `
        <div class="toast-content">
            <i class="${icon}"></i>
            <span>${message}</span>
        </div>
        <button class="toast-close" onclick="this.parentElement.remove()">
            <i class="fas fa-times"></i>
        </button>
    `;

    container.appendChild(toast);

    // Show the toast immediately
    setTimeout(() => {
        toast.classList.add('toast-show');
    }, 100);

    // Auto remove after 6 seconds (increased from 5)
    setTimeout(() => {
        if (toast.parentElement) {
            toast.classList.remove('toast-show');
            setTimeout(() => {
                if (toast.parentElement) {
                    toast.remove();
                }
            }, 300);
        }
    }, 6000);
}

// File size formatter
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Form validation utilities
function validateEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

function validatePassword(password) {
    return password.length >= 6;
}

function validateUsername(username) {
    return username.length >= 3 && /^[a-zA-Z0-9_]+$/.test(username);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Hide loading overlay on page load
    hideLoading();
    
    // Add smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.alert');
    flashMessages.forEach(message => {
        setTimeout(() => {
            if (message.parentElement) {
                message.style.opacity = '0';
                setTimeout(() => message.remove(), 300);
            }
        }, 5000);
    });
});

// Network request helper with better error handling
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Request failed:', error);
        throw error;
    }
}

// Drag and drop utilities
function setupDragAndDrop(element, callback) {
    if (!element) return;

    element.addEventListener('dragover', (e) => {
        e.preventDefault();
        element.classList.add('drag-over');
    });

    element.addEventListener('dragleave', (e) => {
        e.preventDefault();
        element.classList.remove('drag-over');
    });

    element.addEventListener('drop', (e) => {
        e.preventDefault();
        element.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0 && callback) {
            callback(files[0]);
        }
    });
}

// Password toggle functionality
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const toggle = field.parentElement.querySelector('.password-toggle');
    const icon = toggle.querySelector('i');
    
    if (field.type === 'password') {
        field.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        field.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// Form submission helpers
function handleFormSubmission(formId, submitUrl, options = {}) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const jsonData = Object.fromEntries(formData);
        
        // Custom validation if provided
        if (options.validate && !options.validate(jsonData)) {
            return;
        }
        
        showLoading();
        
        try {
            const response = await makeRequest(submitUrl, {
                method: 'POST',
                body: JSON.stringify(jsonData)
            });
            
            if (response.success) {
                showToast(response.message || 'Success!', 'success');
                if (options.onSuccess) {
                    options.onSuccess(response);
                }
            } else {
                showToast(response.message || 'An error occurred', 'error');
                if (options.onError) {
                    options.onError(response);
                }
            }
        } catch (error) {
            showToast('Network error. Please try again.', 'error');
            console.error('Form submission error:', error);
        } finally {
            hideLoading();
        }
    });
}

// Utility to debounce function calls
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

// Copy to clipboard utility
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}