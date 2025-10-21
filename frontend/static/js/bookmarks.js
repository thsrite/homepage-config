// Bookmarks management functionality

// Load and display bookmarks
async function loadBookmarks() {
    try {
        const response = await fetch('/api/bookmarks/');
        const groups = await response.json();

        const container = document.getElementById('bookmarksContainer');
        container.innerHTML = '';

        groups.forEach(group => {
            const groupCard = createBookmarkGroupCard(group);
            container.appendChild(groupCard);
        });

        // Setup drag and drop for bookmarks
        setupBookmarksDragDrop();
    } catch (error) {
        console.error('Error loading bookmarks:', error);
        showToast('Failed to load bookmarks', 'error');
    }
}

// Create bookmark group card
function createBookmarkGroupCard(group) {
    const card = document.createElement('div');
    card.className = 'card bookmark-group-card mb-3';
    card.dataset.group = group.name;

    card.innerHTML = `
        <div class="bookmark-group-header">
            <span class="drag-handle">⋮</span>
            <span class="group-title">${group.name}</span>
            <div class="group-actions">
                <button class="btn btn-sm btn-primary" onclick="showAddBookmarkModal('${group.name}')">
                    <i class="bi bi-plus"></i>
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteBookmarkGroup('${group.name}')">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
        <div class="bookmark-group-body" id="group-${group.name}">
            ${group.bookmarks.map(bookmark => createBookmarkItem(group.name, bookmark)).join('')}
        </div>
    `;

    return card;
}

// Create individual bookmark item
function createBookmarkItem(groupName, bookmark) {
    return `
        <div class="bookmark-item" data-bookmark="${bookmark.name}">
            <span class="bookmark-drag-handle">⋮</span>
            ${bookmark.icon ? `<img src="${bookmark.icon}" class="bookmark-icon" alt="">` : ''}
            <div class="bookmark-details">
                <a href="${bookmark.href}" target="_blank" class="bookmark-name">${bookmark.name}</a>
                ${bookmark.description ? `<small class="text-muted">${bookmark.description}</small>` : ''}
            </div>
            <div class="bookmark-actions">
                <button class="btn btn-sm btn-link" onclick="editBookmark('${groupName}', '${bookmark.name}')">
                    <i class="bi bi-pencil"></i>
                </button>
                <button class="btn btn-sm btn-link text-danger" onclick="deleteBookmark('${groupName}', '${bookmark.name}')">
                    <i class="bi bi-trash"></i>
                </button>
            </div>
        </div>
    `;
}

// Show add bookmark modal
function showAddBookmarkModal(groupName) {
    const modal = new bootstrap.Modal(document.getElementById('bookmarkModal'));
    document.getElementById('bookmarkModalTitle').textContent = 'Add Bookmark';
    document.getElementById('bookmarkForm').reset();
    document.getElementById('bookmarkGroup').value = groupName;
    document.getElementById('bookmarkModalAction').textContent = 'Add';
    document.getElementById('bookmarkForm').dataset.mode = 'add';
    modal.show();
}

// Edit bookmark
async function editBookmark(groupName, bookmarkName) {
    try {
        const response = await fetch(`/api/bookmarks/${groupName}`);
        const data = await response.json();
        const bookmark = data.bookmarks.find(b => b.name === bookmarkName);

        if (!bookmark) {
            showToast('Bookmark not found', 'error');
            return;
        }

        const modal = new bootstrap.Modal(document.getElementById('bookmarkModal'));
        document.getElementById('bookmarkModalTitle').textContent = 'Edit Bookmark';
        document.getElementById('bookmarkGroup').value = groupName;
        document.getElementById('bookmarkName').value = bookmark.name;
        document.getElementById('bookmarkHref').value = bookmark.href;
        document.getElementById('bookmarkIcon').value = bookmark.icon || '';
        document.getElementById('bookmarkDescription').value = bookmark.description || '';
        document.getElementById('bookmarkModalAction').textContent = 'Update';
        document.getElementById('bookmarkForm').dataset.mode = 'edit';
        document.getElementById('bookmarkForm').dataset.originalName = bookmarkName;
        modal.show();
    } catch (error) {
        console.error('Error loading bookmark:', error);
        showToast('Failed to load bookmark', 'error');
    }
}

// Save bookmark (add or update)
async function saveBookmark() {
    const form = document.getElementById('bookmarkForm');
    const mode = form.dataset.mode;
    const groupName = document.getElementById('bookmarkGroup').value;
    const bookmarkData = {
        name: document.getElementById('bookmarkName').value,
        href: document.getElementById('bookmarkHref').value,
        icon: document.getElementById('bookmarkIcon').value || null,
        description: document.getElementById('bookmarkDescription').value || null
    };

    try {
        let response;
        if (mode === 'add') {
            response = await fetch(`/api/bookmarks/${groupName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookmarkData)
            });
        } else {
            const originalName = form.dataset.originalName;
            response = await fetch(`/api/bookmarks/${groupName}/${originalName}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookmarkData)
            });
        }

        if (response.ok) {
            showToast(`Bookmark ${mode === 'add' ? 'added' : 'updated'} successfully`, 'success');
            bootstrap.Modal.getInstance(document.getElementById('bookmarkModal')).hide();
            loadBookmarks();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to save bookmark', 'error');
        }
    } catch (error) {
        console.error('Error saving bookmark:', error);
        showToast('Failed to save bookmark', 'error');
    }
}

// Delete bookmark
async function deleteBookmark(groupName, bookmarkName) {
    if (!confirm(`Are you sure you want to delete "${bookmarkName}"?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/bookmarks/${groupName}/${bookmarkName}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Bookmark deleted successfully', 'success');
            loadBookmarks();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to delete bookmark', 'error');
        }
    } catch (error) {
        console.error('Error deleting bookmark:', error);
        showToast('Failed to delete bookmark', 'error');
    }
}

// Create new bookmark group
async function createBookmarkGroup() {
    const groupName = prompt('Enter group name:');
    if (!groupName) return;

    try {
        const response = await fetch(`/api/bookmarks/groups/${groupName}`, {
            method: 'POST'
        });

        if (response.ok) {
            showToast('Group created successfully', 'success');
            loadBookmarks();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to create group', 'error');
        }
    } catch (error) {
        console.error('Error creating group:', error);
        showToast('Failed to create group', 'error');
    }
}

// Delete bookmark group
async function deleteBookmarkGroup(groupName) {
    if (!confirm(`Are you sure you want to delete the group "${groupName}" and all its bookmarks?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/bookmarks/groups/${groupName}`, {
            method: 'DELETE'
        });

        if (response.ok) {
            showToast('Group deleted successfully', 'success');
            loadBookmarks();
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to delete group', 'error');
        }
    } catch (error) {
        console.error('Error deleting group:', error);
        showToast('Failed to delete group', 'error');
    }
}

// Export bookmarks
async function exportBookmarks() {
    try {
        const response = await fetch('/api/bookmarks/export');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'bookmarks.yaml';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showToast('Bookmarks exported successfully', 'success');
    } catch (error) {
        console.error('Error exporting bookmarks:', error);
        showToast('Failed to export bookmarks', 'error');
    }
}

// Import bookmarks
async function importBookmarks() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.yaml,.yml';

    input.onchange = async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/bookmarks/import', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const result = await response.json();
                showToast(`Imported ${result.groups} groups with ${result.total_bookmarks} bookmarks`, 'success');
                loadBookmarks();
            } else {
                const error = await response.json();
                showToast(error.detail || 'Failed to import bookmarks', 'error');
            }
        } catch (error) {
            console.error('Error importing bookmarks:', error);
            showToast('Failed to import bookmarks', 'error');
        }
    };

    input.click();
}

// Setup drag and drop for bookmarks
function setupBookmarksDragDrop() {
    // Implement drag and drop functionality for bookmark groups and items
    const groups = document.querySelectorAll('.bookmark-group-card');
    const groupContainer = document.getElementById('bookmarksContainer');

    if (groupContainer && groups.length > 0) {
        new Sortable(groupContainer, {
            animation: 150,
            handle: '.drag-handle',
            ghostClass: 'dragging',
            onEnd: function(evt) {
                // Save new order
                saveBookmarkOrder();
            }
        });

        // Setup sortable for bookmark items within groups
        groups.forEach(group => {
            const groupName = group.dataset.group;
            const itemsContainer = document.getElementById(`group-${groupName}`);

            if (itemsContainer) {
                new Sortable(itemsContainer, {
                    animation: 150,
                    handle: '.bookmark-drag-handle',
                    group: 'bookmarks',
                    ghostClass: 'dragging',
                    onEnd: function(evt) {
                        // Save new order
                        saveBookmarkOrder();
                    }
                });
            }
        });
    }
}

// Save bookmark order (implement if needed)
async function saveBookmarkOrder() {
    // This would save the new order to the backend
    console.log('Bookmark order changed');
}

// Show toast notification
function showToast(message, type = 'info') {
    // Implementation depends on your toast library
    console.log(`${type}: ${message}`);
    // You can use Bootstrap toasts or another notification library
}