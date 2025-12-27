// Main Site JavaScript
(function() {
    'use strict';

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    function initializeApp() {
        initializeNavigation();
        initializeCards();
        initializeForms();
        initializeSearch();
        initializeModals();
        initializeTooltips();
        initializeLazyLoading();
        initializeScrollEffects();
    }

    // Navigation functionality
    function initializeNavigation() {
        const navbar = document.querySelector('.navbar');
        let lastScrollTop = 0;

        // Navbar scroll effect
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // Scrolling down
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Scrolling up
                navbar.style.transform = 'translateY(0)';
            }
            
            lastScrollTop = scrollTop;
        });

        // Mobile menu toggle
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');

        if (navbarToggler && navbarCollapse) {
            navbarToggler.addEventListener('click', function() {
                navbarCollapse.classList.toggle('show');
            });
        }

        // Close mobile menu when clicking outside
        document.addEventListener('click', function(event) {
            const isClickInsideNav = navbarCollapse?.contains(event.target) || navbarToggler?.contains(event.target);
            
            if (!isClickInsideNav && navbarCollapse?.classList.contains('show')) {
                navbarCollapse.classList.remove('show');
            }
        });
    }

    // Card animations and interactions
    function initializeCards() {
        const cards = document.querySelectorAll('.group-card, .category-card, .stats-card');
        
        // Add intersection observer for card animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '50px'
        });

        cards.forEach(card => {
            observer.observe(card);
            
            // Add hover effect for group cards
            if (card.classList.contains('group-card')) {
                card.addEventListener('mouseenter', function() {
                    this.style.transform = 'translateY(-8px)';
                });
                
                card.addEventListener('mouseleave', function() {
                    this.style.transform = 'translateY(0)';
                });
            }
        });
    }

    // Form enhancements
    function initializeForms() {
        // Form validation
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(event) {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });

        // Input animations
        const inputs = document.querySelectorAll('.form-control, .form-select');
        
        inputs.forEach(input => {
            // Focus effects
            input.addEventListener('focus', function() {
                this.parentElement.classList.add('focused');
            });
            
            input.addEventListener('blur', function() {
                this.parentElement.classList.remove('focused');
            });

            // Floating labels
            if (input.value) {
                input.classList.add('has-value');
            }
            
            input.addEventListener('input', function() {
                if (this.value) {
                    this.classList.add('has-value');
                } else {
                    this.classList.remove('has-value');
                }
            });
        });

        // Copy to clipboard functionality
        const copyButtons = document.querySelectorAll('[data-copy]');
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const textToCopy = this.getAttribute('data-copy');
                copyToClipboard(textToCopy);
                showToast('Copied to clipboard!', 'success');
            });
        });
    }

    // Search functionality
    function initializeSearch() {
        const searchForm = document.querySelector('.search-form');
        const searchInput = document.querySelector('input[name="q"]');
        
        if (searchInput) {
            // Search suggestions (if needed)
            let searchTimeout;
            
            searchInput.addEventListener('input', function() {
                clearTimeout(searchTimeout);
                const query = this.value.trim();
                
                if (query.length >= 2) {
                    searchTimeout = setTimeout(() => {
                        // Could implement search suggestions here
                        console.log('Search query:', query);
                    }, 300);
                }
            });

            // Search form submission
            if (searchForm) {
                searchForm.addEventListener('submit', function(event) {
                    const query = searchInput.value.trim();
                    if (!query) {
                        event.preventDefault();
                        showToast('Please enter a search term', 'warning');
                    }
                });
            }
        }
    }

    // Modal functionality
    function initializeModals() {
        const modals = document.querySelectorAll('.modal');
        
        modals.forEach(modal => {
            modal.addEventListener('show.bs.modal', function() {
                document.body.classList.add('modal-open');
            });
            
            modal.addEventListener('hidden.bs.modal', function() {
                document.body.classList.remove('modal-open');
            });
        });
    }

    // Tooltip initialization
    function initializeTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Lazy loading for images
    function initializeLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.getAttribute('data-src');
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        images.forEach(img => {
            imageObserver.observe(img);
        });
    }

    // Scroll effects
    function initializeScrollEffects() {
        // Smooth scrolling for anchor links
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        
        anchorLinks.forEach(link => {
            link.addEventListener('click', function(event) {
                const targetId = this.getAttribute('href');
                const targetElement = document.querySelector(targetId);
                
                if (targetElement) {
                    event.preventDefault();
                    targetElement.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Back to top button
        const backToTopButton = createBackToTopButton();
        
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.classList.add('show');
            } else {
                backToTopButton.classList.remove('show');
            }
        });
    }

    // Utility functions
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            return navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = text;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            return Promise.resolve();
        }
    }

    function showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed top-0 end-0 m-3`;
        toast.style.zIndex = '9999';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        document.body.appendChild(toast);
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove from DOM after hiding
        toast.addEventListener('hidden.bs.toast', function() {
            document.body.removeChild(toast);
        });
    }

    function createBackToTopButton() {
        const button = document.createElement('button');
        button.className = 'btn btn-primary position-fixed bottom-0 end-0 m-4 rounded-circle back-to-top';
        button.style.width = '50px';
        button.style.height = '50px';
        button.style.zIndex = '999';
        button.style.opacity = '0';
        button.style.visibility = 'hidden';
        button.style.transition = 'all 0.3s ease';
        button.innerHTML = '<i class="fas fa-arrow-up"></i>';
        
        button.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
        
        // Add CSS for show state
        const style = document.createElement('style');
        style.textContent = `
            .back-to-top.show {
                opacity: 1 !important;
                visibility: visible !important;
            }
            .back-to-top:hover {
                transform: translateY(-3px);
            }
        `;
        document.head.appendChild(style);
        document.body.appendChild(button);
        
        return button;
    }

    // Group interaction functions
    function trackGroupClick(groupId, action) {
        // Analytics tracking
        if (typeof gtag !== 'undefined') {
            gtag('event', action, {
                'event_category': 'group_interaction',
                'event_label': groupId,
                'value': 1
            });
        }
    }

    function shareGroup(groupName, groupUrl) {
        if (navigator.share) {
            navigator.share({
                title: groupName,
                text: `Check out this WhatsApp group: ${groupName}`,
                url: groupUrl
            }).catch(console.error);
        } else {
            copyToClipboard(groupUrl);
            showToast('Group link copied to clipboard!', 'success');
        }
    }

    // Filter functionality
    function initializeFilters() {
        const filterForm = document.querySelector('.filter-form');
        const filterSelects = document.querySelectorAll('.filter-form select');
        
        filterSelects.forEach(select => {
            select.addEventListener('change', function() {
                // Auto-submit filters when changed
                if (this.value) {
                    filterForm.submit();
                }
            });
        });
    }

    // Performance monitoring
    function initializePerformanceMonitoring() {
        // Monitor page load time
        window.addEventListener('load', function() {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log('Page load time:', loadTime + 'ms');
            
            // Track to analytics if available
            if (typeof gtag !== 'undefined') {
                gtag('event', 'timing_complete', {
                    'name': 'page_load',
                    'value': loadTime
                });
            }
        });
    }

    // Error handling
    function initializeErrorHandling() {
        window.addEventListener('error', function(event) {
            console.error('JavaScript error:', event.error);
            
            // Show user-friendly error message
            showToast('Something went wrong. Please refresh the page.', 'danger');
        });
        
        // Handle unhandled promise rejections
        window.addEventListener('unhandledrejection', function(event) {
            console.error('Unhandled promise rejection:', event.reason);
        });
    }

    // Expose useful functions globally
    window.WhatsAppDirectory = {
        showToast,
        copyToClipboard,
        trackGroupClick,
        shareGroup
    };

    // Initialize additional features
    initializeFilters();
    initializePerformanceMonitoring();
    initializeErrorHandling();

})();
