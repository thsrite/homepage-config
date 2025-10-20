// Global variables
let currentConfig = {};
let editingService = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Page loaded, initializing...');

    // Load configuration first
    loadConfiguration().then(() => {
        console.log('Configuration loaded successfully');
    }).catch(error => {
        console.error('Failed to load configuration:', error);
    });

    // Setup event listeners
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    // Modal events
    const serviceModal = document.getElementById('serviceModal');
    serviceModal.addEventListener('hidden.bs.modal', () => {
        document.getElementById('serviceForm').reset();
        editingService = null;
    });
}

// Load configuration from backend
async function loadConfiguration() {
    try {
        const response = await axios.get('/api/services/');
        currentConfig = response.data;
        renderCategories();

        // Setup drag and drop - since scripts are loaded in order, this should work
        if (typeof setupDragDrop === 'function') {
            setupDragDrop();
        } else {
            console.warn('setupDragDrop function not available');
        }

        // Don't auto-refresh preview, let user control it
    } catch (error) {
        console.error('Error loading configuration:', error);
        showToast('Failed to load configuration', 'error');
    }
}

// Render categories and services
function renderCategories() {
    const container = document.getElementById('categoriesContainer');

    if (Object.keys(currentConfig).length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <i class="bi bi-folder-plus"></i>
                <p>No categories yet. Click "Add Category" to get started!</p>
            </div>
        `;
        return;
    }

    let html = '';
    for (const [categoryName, services] of Object.entries(currentConfig)) {
        html += createCategoryHTML(categoryName, services);
    }

    container.innerHTML = html;
}

// Create HTML for a category
function createCategoryHTML(categoryName, services) {
    let servicesHTML = '';

    if (services.length === 0) {
        servicesHTML = '<div class="empty-state"><small>No services in this category</small></div>';
    } else {
        services.forEach(service => {
            servicesHTML += createServiceHTML(service, categoryName);
        });
    }

    return `
        <div class="category-card card" data-category="${categoryName}">
            <div class="category-header">
                <span class="category-title">
                    <i class="bi bi-grip-vertical drag-handle"></i>
                    ${categoryName}
                </span>
                <div class="category-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="addService('${categoryName}')">
                        <i class="bi bi-plus"></i> Add Service
                    </button>
                    <button class="btn btn-sm btn-outline-warning" onclick="renameCategory('${categoryName}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteCategory('${categoryName}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
            <div class="category-body" data-category="${categoryName}">
                ${servicesHTML}
            </div>
        </div>
    `;
}

// Create HTML for a service
function createServiceHTML(service, categoryName) {
    const config = service.config || {};
    const icon = config.icon || '';
    const href = config.href || '#';

    let iconHTML = '';
    if (icon) {
        iconHTML = `<img src="${icon}" alt="${service.name}" onerror="this.style.display='none'; this.parentElement.innerHTML='${service.name[0].toUpperCase()}'">`;
    } else {
        iconHTML = service.name[0].toUpperCase();
    }

    return `
        <div class="service-item" data-service="${service.name}" data-category="${categoryName}">
            <i class="bi bi-grip-vertical drag-handle" style="cursor: move; margin-right: 10px; color: #6c757d;"></i>
            <div class="service-icon-preview">
                ${iconHTML}
            </div>
            <div class="service-info">
                <div class="service-name">${service.name}</div>
                <div class="service-details">
                    ${config.widget ? `<span class="badge bg-info">${config.widget.type}</span>` : ''}
                    ${config.container ? `<span class="badge bg-secondary">${config.container}</span>` : ''}
                </div>
            </div>
            <div class="service-actions">
                <button class="btn btn-sm btn-outline-primary" onclick="editService('${categoryName}', '${service.name}')">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteService('${categoryName}', '${service.name}')">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    `;
}

// Add category
function addCategory() {
    const name = prompt('Enter category name:');
    if (!name) return;

    axios.post('/api/categories/', { name })
        .then(() => {
            showToast('Category added successfully', 'success');
            loadConfiguration();
        })
        .catch(error => {
            showToast('Failed to add category', 'error');
            console.error(error);
        });
}

// Rename category
function renameCategory(oldName) {
    const newName = prompt(`Rename category "${oldName}" to:`, oldName);
    if (!newName || newName === oldName) return;

    axios.put(`/api/categories/${oldName}`, { new_name: newName })
        .then(() => {
            showToast('Category renamed successfully', 'success');
            loadConfiguration();
        })
        .catch(error => {
            showToast('Failed to rename category', 'error');
            console.error(error);
        });
}

// Delete category
function deleteCategory(categoryName) {
    if (!confirm(`Delete category "${categoryName}" and all its services?`)) return;

    axios.delete(`/api/categories/${categoryName}?force=true`)
        .then(() => {
            showToast('Category deleted successfully', 'success');
            loadConfiguration();
        })
        .catch(error => {
            showToast('Failed to delete category', 'error');
            console.error(error);
        });
}

// Save configuration
function saveConfig() {
    showToast('Configuration saved!', 'success');
    refreshPreview();
}

// Import configuration
function importConfig() {
    const modal = new bootstrap.Modal(document.getElementById('importModal'));
    modal.show();
}

// Perform import
async function performImport() {
    const fileInput = document.getElementById('importFile');
    const file = fileInput.files[0];

    if (!file) {
        showToast('Please select a file', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
        const response = await axios.post('/api/config/import', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });

        const data = response.data;
        const message = `Configuration imported successfully! ${data.categories} categories, ${data.services} services`;
        showToast(message, 'success');
        bootstrap.Modal.getInstance(document.getElementById('importModal')).hide();
        loadConfiguration();
    } catch (error) {
        let errorMessage = 'Failed to import configuration';
        if (error.response && error.response.data && error.response.data.detail) {
            errorMessage = error.response.data.detail;
        }
        showToast(errorMessage, 'error');
        console.error('Import error:', error);
    }
}

// Export configuration
function exportConfig() {
    window.location.href = '/api/config/export';
}

// Show toast notification
function showToast(message, type = 'info') {
    // Create toast container if it doesn't exist
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toastHTML = `
        <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;

    container.insertAdjacentHTML('beforeend', toastHTML);
    const toastElement = container.lastElementChild;
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}