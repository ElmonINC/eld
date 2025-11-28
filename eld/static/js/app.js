// eld - Main JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('🎉 eld loaded!');
    
    // Initialize confetti for fun holidays
    window.celebrateHoliday = function(isFun) {
        if (isFun) {
            confetti({
                particleCount: 100,
                spread: 70,
                origin: { y: 0.6 }
            });
        }
    };
    
    // Dark mode persistence
    const darkModeToggle = () => {
        const isDark = document.documentElement.classList.contains('dark');
        localStorage.setItem('darkMode', isDark);
    };
    
    // HTMX event listeners
    document.body.addEventListener('htmx:afterSwap', function(event) {
        // Re-initialize any JavaScript components after HTMX swap
        console.log('HTMX swapped:', event.detail.target);
        
        // Trigger confetti if element has data attribute
        if (event.detail.target.dataset.celebrate) {
            confetti({
                particleCount: 50,
                spread: 60,
                origin: { y: 0.7 }
            });
        }
    });
    
    document.body.addEventListener('htmx:afterRequest', function(event) {
        // Handle errors
        if (event.detail.failed) {
            console.error('Request failed:', event.detail.xhr);
        }
    });
    
    // Countdown timer for holidays
    function updateCountdowns() {
        document.querySelectorAll('[data-countdown]').forEach(function(element) {
            const targetDate = new Date(element.dataset.countdown);
            const now = new Date();
            const diff = targetDate - now;
            
            if (diff > 0) {
                const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                element.textContent = `${days}d ${hours}h`;
            } else {
                element.textContent = 'Today! 🎉';
            }
        });
    }
    
    // Update countdowns every minute
    updateCountdowns();
    setInterval(updateCountdowns, 60000);
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });
    
    // Copy to clipboard helper
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(function() {
            // Show toast notification
            showToast('Copied to clipboard! 📋', 'success');
        }).catch(function(err) {
            console.error('Failed to copy:', err);
            showToast('Failed to copy', 'error');
        });
    };
    
    // Toast notification system
    window.showToast = function(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white transform transition-all duration-300 z-50 ${
            type === 'success' ? 'bg-green-500' :
            type === 'error' ? 'bg-red-500' :
            'bg-blue-500'
        }`;
        toast.textContent = message;
        
        document.body.appendChild(toast);
        
        // Slide in
        setTimeout(() => {
            toast.style.transform = 'translateY(0)';
        }, 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            toast.style.transform = 'translateY(100px)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    };
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K: Focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[type="text"][placeholder*="Search"]');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape: Clear filters
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('input[type="text"]');
            if (searchInput && searchInput.value) {
                searchInput.value = '';
                searchInput.dispatchEvent(new Event('input'));
            }
        }
    });
    
    // Lazy load images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img.lazy').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Performance monitoring
    if (window.performance && window.performance.timing) {
        window.addEventListener('load', function() {
            const perfData = window.performance.timing;
            const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
            console.log(`⚡ Page loaded in ${pageLoadTime}ms`);
        });
    }
});

// Service Worker registration for PWA (future enhancement)
if ('serviceWorker' in navigator) {
    // Uncomment when service worker is ready
    // navigator.serviceWorker.register('/sw.js').then(function(registration) {
    //     console.log('ServiceWorker registered:', registration);
    // });
}