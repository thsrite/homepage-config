// Live preview functionality

let homepageUrl = localStorage.getItem('homepageUrl') || '';

// Initialize preview on load
document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('homepageUrl');
    if (urlInput && homepageUrl) {
        urlInput.value = homepageUrl;
        setHomepageUrl();
    }
});

// Set Homepage URL
function setHomepageUrl() {
    const urlInput = document.getElementById('homepageUrl');
    const url = urlInput.value.trim();

    if (!url) {
        showToast('Please enter a Homepage URL', 'warning');
        return;
    }

    // Validate URL
    try {
        new URL(url);
    } catch (e) {
        showToast('Please enter a valid URL', 'error');
        return;
    }

    homepageUrl = url;
    localStorage.setItem('homepageUrl', homepageUrl);

    const previewFrame = document.getElementById('previewFrame');
    const placeholder = document.getElementById('previewPlaceholder');

    if (previewFrame && placeholder) {
        // Hide placeholder, show iframe
        placeholder.style.display = 'none';
        previewFrame.style.display = 'block';

        // Set iframe src
        previewFrame.src = homepageUrl;

        // Handle iframe load errors
        previewFrame.onerror = () => {
            showToast('Failed to load Homepage. Check if the URL is correct and accessible.', 'error');
        };

        previewFrame.onload = () => {
            showToast('Homepage loaded successfully', 'success');
        };
    }
}

// Refresh preview
function refreshPreview() {
    if (!homepageUrl) {
        showToast('Please set a Homepage URL first', 'warning');
        return;
    }

    const previewFrame = document.getElementById('previewFrame');
    if (previewFrame) {
        // Add loading indicator
        previewFrame.classList.add('loading');

        // Reload the iframe with cache buster
        previewFrame.src = homepageUrl + (homepageUrl.includes('?') ? '&' : '?') + '_t=' + Date.now();

        // Remove loading indicator after load
        previewFrame.onload = () => {
            previewFrame.classList.remove('loading');
        };
    }
}

// Auto-refresh preview on configuration changes
function schedulePreviewUpdate() {
    // Only auto-refresh if we have a Homepage URL set
    if (homepageUrl) {
        refreshPreview();
    }
}

// Watch for configuration changes (optional - can be enabled if needed)
function watchConfigurationChanges() {
    // This function is now optional
    // You can enable it if you want automatic refresh when configuration changes
    return;
}

// Toggle preview panel
function togglePreview() {
    const previewCol = document.querySelector('.col-md-6:last-child');
    const editorCol = document.querySelector('.col-md-6:first-child');

    if (previewCol.style.display === 'none') {
        // Show preview
        previewCol.style.display = '';
        editorCol.classList.remove('col-md-12');
        editorCol.classList.add('col-md-6');
        refreshPreview();
    } else {
        // Hide preview
        previewCol.style.display = 'none';
        editorCol.classList.remove('col-md-6');
        editorCol.classList.add('col-md-12');
    }
}

// Full screen preview
function fullscreenPreview() {
    const previewFrame = document.getElementById('previewFrame');
    if (previewFrame.requestFullscreen) {
        previewFrame.requestFullscreen();
    } else if (previewFrame.webkitRequestFullscreen) {
        previewFrame.webkitRequestFullscreen();
    } else if (previewFrame.mozRequestFullScreen) {
        previewFrame.mozRequestFullScreen();
    }
}

// Clear Homepage URL
function clearHomepageUrl() {
    localStorage.removeItem('homepageUrl');
    homepageUrl = '';

    const previewFrame = document.getElementById('previewFrame');
    const placeholder = document.getElementById('previewPlaceholder');
    const urlInput = document.getElementById('homepageUrl');

    if (previewFrame && placeholder) {
        previewFrame.style.display = 'none';
        previewFrame.src = '';
        placeholder.style.display = 'block';
    }

    if (urlInput) {
        urlInput.value = '';
    }

    showToast('Homepage URL cleared', 'info');
}

// Add keyboard shortcuts for preview
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + R for preview refresh
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        refreshPreview();
    }

    // Ctrl/Cmd + F for fullscreen preview
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        fullscreenPreview();
    }
});

// Handle Enter key in URL input
document.addEventListener('DOMContentLoaded', () => {
    const urlInput = document.getElementById('homepageUrl');
    if (urlInput) {
        urlInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                setHomepageUrl();
            }
        });
    }
});