/**
 * Modern Scripts for Django Blog
 * Enhances UI functionality and user experience
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initDarkMode();
    initMobileNav();
    initDropdowns();
    initTabs();
    initTooltips();
    initAnimations();
    initDashboardCharts();
    initAjaxForms();
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Back to top button
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopBtn.classList.add('show');
            } else {
                backToTopBtn.classList.remove('show');
            }
        });
        
        backToTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
});

/**
 * Dark Mode Toggle Functionality
 */
function initDarkMode() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Check for saved theme preference or use the system preference
    const currentTheme = localStorage.getItem('theme');
    
    // If the user has explicitly chosen a theme, use it
    if (currentTheme) {
        document.body.classList.toggle('dark-mode', currentTheme === 'dark');
        if (darkModeToggle) {
            darkModeToggle.checked = currentTheme === 'dark';
        }
    } else {
        // If no theme preference saved, use system preference
        const systemPrefersDark = prefersDarkScheme.matches;
        document.body.classList.toggle('dark-mode', systemPrefersDark);
        if (darkModeToggle) {
            darkModeToggle.checked = systemPrefersDark;
        }
    }
    
    // Add event listener to toggle button
    if (darkModeToggle) {
        darkModeToggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            }
        });
    }
    
    // Listen for changes in system theme preference
    prefersDarkScheme.addEventListener('change', function(e) {
        // Only apply system preference if user hasn't set a preference
        if (!localStorage.getItem('theme')) {
            document.body.classList.toggle('dark-mode', e.matches);
            if (darkModeToggle) {
                darkModeToggle.checked = e.matches;
            }
        }
    });
}

/**
 * Mobile Navigation
 */
function initMobileNav() {
    const mobileMenuToggle = document.getElementById('mobile-menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    
    if (mobileMenuToggle && mobileMenu) {
        mobileMenuToggle.addEventListener('click', function() {
            mobileMenu.classList.toggle('show');
            document.body.classList.toggle('menu-open');
            
            // Toggle aria-expanded attribute for accessibility
            const expanded = mobileMenu.classList.contains('show');
            mobileMenuToggle.setAttribute('aria-expanded', expanded);
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(e) {
            if (mobileMenu.classList.contains('show') && 
                !mobileMenu.contains(e.target) && 
                !mobileMenuToggle.contains(e.target)) {
                mobileMenu.classList.remove('show');
                document.body.classList.remove('menu-open');
                mobileMenuToggle.setAttribute('aria-expanded', 'false');
            }
        });
    }
}

/**
 * Dropdown Menus
 */
function initDropdowns() {
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdown = this.nextElementSibling;
            
            // Close all other dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(openDropdown => {
                if (openDropdown !== dropdown) {
                    openDropdown.classList.remove('show');
                    openDropdown.previousElementSibling.setAttribute('aria-expanded', 'false');
                }
            });
            
            // Toggle current dropdown
            dropdown.classList.toggle('show');
            this.setAttribute('aria-expanded', dropdown.classList.contains('show'));
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(dropdown => {
                dropdown.classList.remove('show');
                dropdown.previousElementSibling.setAttribute('aria-expanded', 'false');
            });
        }
    });
}

/**
 * Tab functionality
 */
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabContainer = this.closest('.profile-tabs, .dashboard-content');
            if (!tabContainer) return;
            
            // Remove active class from all buttons and panes in this container
            tabContainer.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            tabContainer.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Show corresponding tab pane
            const tabId = this.getAttribute('data-tab');
            const tabPane = tabContainer.querySelector(`#${tabId}-tab`);
            if (tabPane) {
                tabPane.classList.add('active');
            }
        });
    });
}

/**
 * Tooltips
 */
function initTooltips() {
    const tooltipTriggers = document.querySelectorAll('[data-tooltip]');
    
    tooltipTriggers.forEach(trigger => {
        trigger.addEventListener('mouseenter', function() {
            const tooltipText = this.getAttribute('data-tooltip');
            
            // Create tooltip element
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = tooltipText;
            document.body.appendChild(tooltip);
            
            // Position tooltip
            const triggerRect = this.getBoundingClientRect();
            tooltip.style.top = (triggerRect.top - tooltip.offsetHeight - 10) + 'px';
            tooltip.style.left = (triggerRect.left + (triggerRect.width / 2) - (tooltip.offsetWidth / 2)) + 'px';
            
            // Show tooltip
            setTimeout(() => {
                tooltip.classList.add('show');
            }, 10);
            
            // Store tooltip reference
            this.tooltip = tooltip;
        });
        
        trigger.addEventListener('mouseleave', function() {
            if (this.tooltip) {
                this.tooltip.classList.remove('show');
                
                // Remove tooltip after animation
                setTimeout(() => {
                    if (this.tooltip && this.tooltip.parentNode) {
                        this.tooltip.parentNode.removeChild(this.tooltip);
                        this.tooltip = null;
                    }
                }, 300);
            }
        });
    });
}

/**
 * Animations
 */
function initAnimations() {
    // Animate elements when they come into view
    const animateElements = document.querySelectorAll('.animate-on-scroll');
    
    if (animateElements.length > 0) {
        const animateOnScroll = function() {
            animateElements.forEach(element => {
                const elementPosition = element.getBoundingClientRect().top;
                const screenPosition = window.innerHeight / 1.2;
                
                if (elementPosition < screenPosition) {
                    element.classList.add('animate-fadeIn');
                }
            });
        };
        
        // Run once on load
        animateOnScroll();
        
        // Run on scroll
        window.addEventListener('scroll', animateOnScroll);
    }
    
    // Animate stat cards on dashboard
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('animate-fadeIn');
        }, 100 * index);
    });
}

/**
 * Dashboard Charts
 */
function initDashboardCharts() {
    // Check if Chart.js is available
    if (typeof Chart === 'undefined') return;
    
    // Views chart
    const viewsChartCanvas = document.getElementById('views-chart');
    if (viewsChartCanvas) {
        const ctx = viewsChartCanvas.getContext('2d');
        const data = JSON.parse(viewsChartCanvas.getAttribute('data-stats'));
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Views',
                    data: data.values,
                    backgroundColor: 'rgba(67, 97, 238, 0.1)',
                    borderColor: 'rgba(67, 97, 238, 1)',
                    borderWidth: 2,
                    tension: 0.3,
                    pointBackgroundColor: 'rgba(67, 97, 238, 1)',
                    pointRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
    
    // Engagement chart (likes, comments)
    const engagementChartCanvas = document.getElementById('engagement-chart');
    if (engagementChartCanvas) {
        const ctx = engagementChartCanvas.getContext('2d');
        const data = JSON.parse(engagementChartCanvas.getAttribute('data-stats'));
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Likes',
                        data: data.likes,
                        backgroundColor: 'rgba(247, 37, 133, 0.7)',
                        borderWidth: 0
                    },
                    {
                        label: 'Comments',
                        data: data.comments,
                        backgroundColor: 'rgba(76, 201, 240, 0.7)',
                        borderWidth: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
}

/**
 * Ajax Forms
 */
function initAjaxForms() {
    const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
    
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const url = this.getAttribute('action');
            const method = this.getAttribute('method') || 'POST';
            const successCallback = this.getAttribute('data-success-callback');
            
            // Show loading state
            this.classList.add('loading');
            const submitBtn = this.querySelector('[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            }
            
            // Send request
            fetch(url, {
                method: method,
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                // Remove loading state
                this.classList.remove('loading');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
                }
                
                // Handle response
                if (data.success) {
                    // Show success message
                    showNotification(data.message || 'Success!', 'success');
                    
                    // Reset form
                    if (data.reset_form !== false) {
                        this.reset();
                    }
                    
                    // Execute success callback if provided
                    if (successCallback && typeof window[successCallback] === 'function') {
                        window[successCallback](data);
                    }
                    
                    // Redirect if provided
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    }
                    
                    // Refresh page if requested
                    if (data.refresh) {
                        window.location.reload();
                    }
                } else {
                    // Show error message
                    showNotification(data.message || 'An error occurred.', 'error');
                    
                    // Display field errors
                    if (data.errors) {
                        Object.keys(data.errors).forEach(field => {
                            const input = this.querySelector(`[name="${field}"]`);
                            if (input) {
                                input.classList.add('is-invalid');
                                
                                // Add error message
                                const errorDiv = document.createElement('div');
                                errorDiv.className = 'invalid-feedback';
                                errorDiv.textContent = data.errors[field];
                                
                                // Remove any existing error message
                                const existingError = input.nextElementSibling;
                                if (existingError && existingError.classList.contains('invalid-feedback')) {
                                    existingError.remove();
                                }
                                
                                input.parentNode.insertBefore(errorDiv, input.nextSibling);
                            }
                        });
                    }
                }
            })
            .catch(error => {
                console.error('Error:', error);
                
                // Remove loading state
                this.classList.remove('loading');
                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = submitBtn.getAttribute('data-original-text') || 'Submit';
                }
                
                // Show error message
                showNotification('An unexpected error occurred. Please try again.', 'error');
            });
        });
    });
}

/**
 * Show notification
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    // Add icon based on type
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'error') icon = 'exclamation-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="fas fa-${icon}"></i>
        </div>
        <div class="notification-content">
            ${message}
        </div>
        <button class="notification-close">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    // Add to notifications container or create one
    let notificationsContainer = document.querySelector('.notifications-container');
    if (!notificationsContainer) {
        notificationsContainer = document.createElement('div');
        notificationsContainer.className = 'notifications-container';
        document.body.appendChild(notificationsContainer);
    }
    
    notificationsContainer.appendChild(notification);
    
    // Show notification
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Add close button functionality
    const closeBtn = notification.querySelector('.notification-close');
    closeBtn.addEventListener('click', () => {
        notification.classList.remove('show');
        
        // Remove after animation
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    });
    
    // Auto-close after 5 seconds
    setTimeout(() => {
        if (notification.classList.contains('show')) {
            notification.classList.remove('show');
            
            // Remove after animation
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }
    }, 5000);
}

/**
 * Like post functionality
 */
function likePost(postId) {
    const likeBtn = document.querySelector(`.like-btn[data-post-id="${postId}"]`);
    if (!likeBtn) return;
    
    fetch(`/like-post/${postId}/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update like count
            const likeCount = likeBtn.querySelector('.like-count');
            if (likeCount) {
                likeCount.textContent = data.likes_count;
            }
            
            // Toggle liked state
            if (data.liked) {
                likeBtn.classList.add('liked');
                likeBtn.querySelector('i').classList.remove('far');
                likeBtn.querySelector('i').classList.add('fas');
            } else {
                likeBtn.classList.remove('liked');
                likeBtn.querySelector('i').classList.remove('fas');
                likeBtn.querySelector('i').classList.add('far');
            }
        } else {
            // Show error
            showNotification(data.message || 'An error occurred.', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An unexpected error occurred. Please try again.', 'error');
    });
}

/**
 * Delete post confirmation
 */
function confirmDelete(url, itemName) {
    if (confirm(`Are you sure you want to delete "${itemName}"? This action cannot be undone.`)) {
        window.location.href = url;
    }
}

/**
 * Get CSRF token from cookies
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 * Calculate reading time
 */
function calculateReadingTime() {
    const postContent = document.querySelector('.post-content');
    if (!postContent) return;
    
    const text = postContent.textContent || postContent.innerText;
    const wordCount = text.split(/\s+/).length;
    const readingTime = Math.ceil(wordCount / 200); // Assuming 200 words per minute
    
    const readingTimeElement = document.querySelector('.reading-time');
    if (readingTimeElement) {
        readingTimeElement.textContent = `${readingTime} min read`;
    }
}

// Initialize reading time calculation
document.addEventListener('DOMContentLoaded', calculateReadingTime);
