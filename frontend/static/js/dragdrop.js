// Drag and drop functionality using SortableJS

// Use window scope to avoid conflicts
window.categorySortable = null;
window.serviceSortables = [];

// Setup drag and drop for categories and services
window.setupDragDrop = function() {
    // Clear existing sortables
    if (window.categorySortable) {
        window.categorySortable.destroy();
        window.categorySortable = null;
    }
    if (window.serviceSortables) {
        window.serviceSortables.forEach(s => s.destroy());
        window.serviceSortables = [];
    }

    // Setup category sorting
    const categoriesContainer = document.getElementById('categoriesContainer');
    if (categoriesContainer && categoriesContainer.children.length > 0) {
        window.categorySortable = Sortable.create(categoriesContainer, {
            animation: 150,
            handle: '.drag-handle',
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            onEnd: handleCategoryReorder
        });
    }

    // Setup service sorting within each category
    document.querySelectorAll('.category-body').forEach(categoryBody => {
        const sortable = Sortable.create(categoryBody, {
            group: 'services',
            animation: 150,
            ghostClass: 'sortable-ghost',
            dragClass: 'sortable-drag',
            handle: '.drag-handle',  // Only drag using the handle
            draggable: '.service-item',  // Make service items draggable
            onAdd: handleServiceMove,
            onEnd: handleServiceReorder
        });
        window.serviceSortables.push(sortable);
    });
}

// Handle category reorder
async function handleCategoryReorder(evt) {
    // Get new category order
    const categoryOrder = Array.from(evt.target.children).map(el =>
        el.dataset.category
    );

    try {
        await axios.post('/api/categories/reorder', categoryOrder);
        showToast('Categories reordered successfully', 'success');
        refreshPreview();
    } catch (error) {
        console.error('Error reordering categories:', error);
        showToast('Failed to reorder categories', 'error');
        // Reload to restore original order
        loadConfiguration();
    }
}

// Handle service reorder within a category
async function handleServiceReorder(evt) {
    // Skip if service was moved to another category (handled by onAdd)
    if (evt.from !== evt.to) return;

    const categoryName = evt.target.dataset.category;
    const serviceOrder = Array.from(evt.target.children)
        .filter(el => el.classList.contains('service-item'))
        .map(el => el.dataset.service);

    try {
        await axios.post('/api/services/reorder', {
            category: categoryName,
            service_order: serviceOrder
        });
        showToast('Services reordered successfully', 'success');
        refreshPreview();
    } catch (error) {
        console.error('Error reordering services:', error);
        showToast('Failed to reorder services', 'error');
        loadConfiguration();
    }
}

// Handle service move between categories
async function handleServiceMove(evt) {
    const serviceName = evt.item.dataset.service;
    const fromCategory = evt.from.dataset.category;
    const toCategory = evt.to.dataset.category;

    // Skip if same category
    if (fromCategory === toCategory) return;

    try {
        await axios.post('/api/services/move', {
            service_name: serviceName,
            from_category: fromCategory,
            to_category: toCategory
        });

        // Update the data attributes
        evt.item.dataset.category = toCategory;

        showToast(`Moved "${serviceName}" to "${toCategory}"`, 'success');
        refreshPreview();

        // Trigger reorder for the destination category
        const serviceOrder = Array.from(evt.to.children)
            .filter(el => el.classList.contains('service-item'))
            .map(el => el.dataset.service);

        await axios.post('/api/services/reorder', {
            category: toCategory,
            service_order: serviceOrder
        });
    } catch (error) {
        console.error('Error moving service:', error);
        showToast('Failed to move service', 'error');
        loadConfiguration();
    }
}

// Enable/disable drag mode
let dragModeEnabled = true;

function toggleDragMode() {
    dragModeEnabled = !dragModeEnabled;

    if (window.categorySortable) {
        window.categorySortable.option('disabled', !dragModeEnabled);
    }

    if (window.serviceSortables) {
        window.serviceSortables.forEach(sortable => {
            sortable.option('disabled', !dragModeEnabled);
        });
    }

    // Update UI indicator
    document.querySelectorAll('.drag-handle').forEach(handle => {
        handle.style.display = dragModeEnabled ? 'inline' : 'none';
    });
}

// Visual feedback during drag
document.addEventListener('dragstart', (e) => {
    if (e.target.classList.contains('service-item') ||
        e.target.classList.contains('category-card')) {
        e.target.style.opacity = '0.5';
    }
});

document.addEventListener('dragend', (e) => {
    if (e.target.classList.contains('service-item') ||
        e.target.classList.contains('category-card')) {
        e.target.style.opacity = '';
    }
});