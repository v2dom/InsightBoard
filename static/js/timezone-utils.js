const TimezoneUtils = {
    convertToLocalTime(utcTimestamp, format = 'full') {
        if (!utcTimestamp) return '';
        
        try {
            const utcDate = new Date(utcTimestamp);
            
            if (isNaN(utcDate.getTime())) {
                console.warn('Invalid timestamp:', utcTimestamp);
                return utcTimestamp;
            }
            
            const localDate = new Date(utcDate.getTime());
            
            switch (format) {
                case 'relative':
                    return this.getRelativeTime(localDate);
                case 'short':
                    return localDate.toLocaleDateString() + ' ' + localDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                case 'time-only':
                    return localDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
                case 'full':
                default:
                    return localDate.toLocaleString();
            }
        } catch (error) {
            console.error('Error converting timestamp:', error);
            return utcTimestamp;
        }
    },
    
    getRelativeTime(date) {
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);
        
        if (diffInSeconds < 60) {
            return 'Just now';
        }
        
        const diffInMinutes = Math.floor(diffInSeconds / 60);
        if (diffInMinutes < 60) {
            return `${diffInMinutes} minute${diffInMinutes !== 1 ? 's' : ''} ago`;
        }
        
        const diffInHours = Math.floor(diffInMinutes / 60);
        if (diffInHours < 24) {
            return `${diffInHours} hour${diffInHours !== 1 ? 's' : ''} ago`;
        }
        
        const diffInDays = Math.floor(diffInHours / 24);
        if (diffInDays === 1) {
            return 'Yesterday';
        }
        if (diffInDays < 7) {
            return `${diffInDays} days ago`;
        }
        
        return date.toLocaleDateString();
    },
    
    convertAllTimestamps() {
        const timestampElements = document.querySelectorAll('[data-timestamp]');
        
        timestampElements.forEach(element => {
            const utcTimestamp = element.getAttribute('data-timestamp');
            const format = element.getAttribute('data-time-format') || 'full';
            
            if (utcTimestamp) {
                const localTime = this.convertToLocalTime(utcTimestamp, format);
                element.textContent = localTime;
                
                if (format !== 'full') {
                    element.title = this.convertToLocalTime(utcTimestamp, 'full');
                }
            }
        });
    },
    
    init() {
        this.convertAllTimestamps();
        
        if (window.MutationObserver) {
            const observer = new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.type === 'childList') {
                        mutation.addedNodes.forEach((node) => {
                            if (node.nodeType === Node.ELEMENT_NODE) {
                                const timestampElements = node.querySelectorAll('[data-timestamp]');
                                if (timestampElements.length > 0) {
                                    this.convertAllTimestamps();
                                }
                            }
                        });
                    }
                });
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    TimezoneUtils.init();
});

if (typeof module !== 'undefined' && module.exports) {
    module.exports = TimezoneUtils;
} 