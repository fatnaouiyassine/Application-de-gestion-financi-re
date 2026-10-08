// Flash message handling
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Close flash messages on click
    const closeButtons = document.querySelectorAll('.flash-close');
    closeButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const message = this.parentElement;
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 300);
        });
    });

    // Form enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        // Add loading state to submit buttons
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
        });

        // Real-time form validation
        const inputs = form.querySelectorAll('input, select');
        inputs.forEach(function(input) {
            input.addEventListener('blur', function() {
                validateField(this);
            });
        });
    });

    // Progress bar animations
    const progressBars = document.querySelectorAll('.progress-fill');
    progressBars.forEach(function(bar) {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(function() {
            bar.style.width = width;
        }, 100);
    });

    // Smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add hover effects to cards
    const cards = document.querySelectorAll('.feature-card, .account-card, .goal-card, .summary-card');
    cards.forEach(function(card) {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Number formatting for amounts
    const amountElements = document.querySelectorAll('.amount, .balance-amount, .summary-amount');
    amountElements.forEach(function(element) {
        const text = element.textContent;
        if (text.includes('$')) {
            const number = parseFloat(text.replace('$', '').replace(',', ''));
            if (!isNaN(number)) {
                element.textContent = '$' + number.toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }
        }
    });

    // Add date picker enhancement
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        // Set minimum date to today
        const today = new Date().toISOString().split('T')[0];
        input.setAttribute('min', today);
    });

    // Add confirmation for important actions
    const deleteButtons = document.querySelectorAll('.btn-danger');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to perform this action?')) {
                e.preventDefault();
            }
        });
    });

    // Add tooltips for better UX
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(function(element) {
        element.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = this.getAttribute('data-tooltip');
            tooltip.style.cssText = `
                position: absolute;
                background: #333;
                color: white;
                padding: 8px 12px;
                border-radius: 6px;
                font-size: 12px;
                z-index: 1000;
                pointer-events: none;
                white-space: nowrap;
            `;
            
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            
            this.addEventListener('mouseleave', function() {
                tooltip.remove();
            });
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + N for new account
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            const newAccountBtn = document.querySelector('a[href*="accounts"]');
            if (newAccountBtn) {
                newAccountBtn.click();
            }
        }
        
        // Ctrl/Cmd + T for new transaction
        if ((e.ctrlKey || e.metaKey) && e.key === 't') {
            e.preventDefault();
            const newTransactionBtn = document.querySelector('a[href*="transactions"]');
            if (newTransactionBtn) {
                newTransactionBtn.click();
            }
        }
        
        // Ctrl/Cmd + G for new goal
        if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
            e.preventDefault();
            const newGoalBtn = document.querySelector('a[href*="goals"]');
            if (newGoalBtn) {
                newGoalBtn.click();
            }
        }
    });

    // Add search functionality
    const searchInputs = document.querySelectorAll('input[type="search"]');
    searchInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.transactions-section').querySelector('table');
            if (table) {
                const rows = table.querySelectorAll('tbody tr');
                rows.forEach(function(row) {
                    const text = row.textContent.toLowerCase();
                    if (text.includes(searchTerm)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }
        });
    });

    // Add sorting functionality for tables
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(function(header) {
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(this.parentElement.children).indexOf(this);
            const sortType = this.getAttribute('data-sort');
            
            rows.sort(function(a, b) {
                const aValue = a.children[columnIndex].textContent;
                const bValue = b.children[columnIndex].textContent;
                
                if (sortType === 'number') {
                    return parseFloat(aValue.replace(/[^0-9.-]+/g, '')) - parseFloat(bValue.replace(/[^0-9.-]+/g, ''));
                } else if (sortType === 'date') {
                    return new Date(aValue) - new Date(bValue);
                } else {
                    return aValue.localeCompare(bValue);
                }
            });
            
            // Toggle sort direction
            if (this.classList.contains('sorted-asc')) {
                rows.reverse();
                this.classList.remove('sorted-asc');
                this.classList.add('sorted-desc');
            } else {
                this.classList.remove('sorted-desc');
                this.classList.add('sorted-asc');
            }
            
            // Clear other headers
            sortableHeaders.forEach(h => {
                if (h !== this) {
                    h.classList.remove('sorted-asc', 'sorted-desc');
                }
            });
            
            // Reorder rows
            rows.forEach(row => tbody.appendChild(row));
        });
    });
});

// Field validation function
function validateField(field) {
    const value = field.value.trim();
    let isValid = true;
    let errorMessage = '';

    // Remove existing error styling
    field.classList.remove('error');
    const existingError = field.parentNode.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }

    // Validation rules
    if (field.hasAttribute('required') && !value) {
        isValid = false;
        errorMessage = 'This field is required';
    } else if (field.type === 'email' && value && !isValidEmail(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid email address';
    } else if (field.type === 'number' && value && isNaN(value)) {
        isValid = false;
        errorMessage = 'Please enter a valid number';
    } else if (field.type === 'date' && value) {
        const selectedDate = new Date(value);
        const today = new Date();
        if (selectedDate < today) {
            isValid = false;
            errorMessage = 'Date cannot be in the past';
        }
    }

    // Apply validation result
    if (!isValid) {
        field.classList.add('error');
        const errorElement = document.createElement('div');
        errorElement.className = 'error-message';
        errorElement.textContent = errorMessage;
        errorElement.style.cssText = `
            color: #dc3545;
            font-size: 12px;
            margin-top: 5px;
        `;
        field.parentNode.appendChild(errorElement);
    }

    return isValid;
}

// Email validation helper
function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Add CSS for error states
const style = document.createElement('style');
style.textContent = `
    .error {
        border-color: #dc3545 !important;
    }
    
    .tooltip {
        position: absolute;
        background: #333;
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 12px;
        z-index: 1000;
        pointer-events: none;
        white-space: nowrap;
    }
    
    th[data-sort] {
        cursor: pointer;
        user-select: none;
    }
    
    th[data-sort]:hover {
        background: #f8f9fa;
    }
    
    th.sorted-asc::after {
        content: ' ▲';
        color: #667eea;
    }
    
    th.sorted-desc::after {
        content: ' ▼';
        color: #667eea;
    }
`;
document.head.appendChild(style); 