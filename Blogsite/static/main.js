document.addEventListener('DOMContentLoaded', function() {
    // Add animation classes to elements when they come into view
    const animateOnScroll = function() {
        // Only target specific content elements, not critical page elements
        const elements = document.querySelectorAll('.post-card, .feature-card, .popular-post-item');
        
        elements.forEach(element => {
            // Skip elements that are already animated
            if (element.classList.contains('animate-fadeIn')) return;
            
            const elementPosition = element.getBoundingClientRect().top;
            const screenPosition = window.innerHeight / 1.2;
            
            if (elementPosition < screenPosition) {
                element.classList.add('animate-fadeIn');
            }
        });
    };
    
    // Run on initial load
    animateOnScroll();
    
    // Run on scroll
    window.addEventListener('scroll', animateOnScroll);
    
    // Mobile menu toggle functionality
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navContainer = document.querySelector('.nav-container');
    
    if (mobileMenuBtn && navContainer) {
        mobileMenuBtn.addEventListener('click', function() {
            navContainer.classList.toggle('active');
            this.classList.toggle('active');
        });
        
        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            if (!navContainer.contains(event.target) && !mobileMenuBtn.contains(event.target) && navContainer.classList.contains('active')) {
                navContainer.classList.remove('active');
                mobileMenuBtn.classList.remove('active');
            }
        });
    }
    
    // Add dropdown menu functionality
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const dropdown = this.nextElementSibling;
            dropdown.classList.toggle('show');
            
            // Close other open dropdowns
            dropdownToggles.forEach(otherToggle => {
                if (otherToggle !== toggle) {
                    const otherDropdown = otherToggle.nextElementSibling;
                    if (otherDropdown && otherDropdown.classList.contains('show')) {
                        otherDropdown.classList.remove('show');
                    }
                }
            });
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        dropdownToggles.forEach(toggle => {
            const dropdown = toggle.nextElementSibling;
            if (dropdown && dropdown.classList.contains('show') && 
                !dropdown.contains(e.target) && 
                !toggle.contains(e.target)) {
                dropdown.classList.remove('show');
            }
        });
    });
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const x = e.clientX - e.target.getBoundingClientRect().left;
            const y = e.clientY - e.target.getBoundingClientRect().top;
            
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add dark mode toggle functionality
    const createDarkModeToggle = function() {
        const footer = document.querySelector('footer .footer-content');
        
        if (footer) {
            const darkModeContainer = document.createElement('div');
            darkModeContainer.classList.add('dark-mode-toggle');
            darkModeContainer.innerHTML = `
                <button id="darkModeToggle" class="btn btn-outline btn-sm">
                    <i class="fas fa-moon"></i> Dark Mode
                </button>
            `;
            
            footer.appendChild(darkModeContainer);
            
            const darkModeToggle = document.getElementById('darkModeToggle');
            const prefersDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
            const storedTheme = localStorage.getItem('theme');
            
            if (storedTheme === 'dark' || (!storedTheme && prefersDarkMode)) {
                document.body.classList.add('dark-mode');
                darkModeToggle.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
            }
            
            darkModeToggle.addEventListener('click', function() {
                document.body.classList.toggle('dark-mode');
                
                if (document.body.classList.contains('dark-mode')) {
                    localStorage.setItem('theme', 'dark');
                    this.innerHTML = '<i class="fas fa-sun"></i> Light Mode';
                } else {
                    localStorage.setItem('theme', 'light');
                    this.innerHTML = '<i class="fas fa-moon"></i> Dark Mode';
                }
            });
        }
    };
    
    createDarkModeToggle();
    
    // Add a "Back to Top" button functionality
    const createBackToTopButton = function() {
        const backToTopBtn = document.getElementById('backToTop');
        
        if (backToTopBtn) {
            window.addEventListener('scroll', function() {
                if (window.pageYOffset > 300) {
                    backToTopBtn.classList.add('visible');
                } else {
                    backToTopBtn.classList.remove('visible');
                }
            });
            
            backToTopBtn.addEventListener('click', function() {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }
    };
    
    createBackToTopButton();
    
    // Add estimated reading time to posts
    const addReadingTime = function() {
        const postContent = document.querySelector('.card-content');
        const postMeta = document.querySelector('.card-meta');
        
        if (postContent && postMeta) {
            const text = postContent.textContent;
            const wordCount = text.split(/\s+/).length;
            const readingTime = Math.ceil(wordCount / 200); // Average reading speed: 200 words per minute
            
            const readingTimeElement = document.createElement('span');
            readingTimeElement.innerHTML = `<i class="far fa-clock"></i> ${readingTime} min read`;
            postMeta.appendChild(readingTimeElement);
        }
    };
    
    addReadingTime();
});
