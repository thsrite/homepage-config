// Service management functions

// Add service
function addService(categoryName) {
    editingService = null;

    // Set modal title
    document.getElementById('serviceModalTitle').textContent = 'Add Service';

    // Load categories into select
    loadCategoriesSelect(categoryName);

    // Clear form
    document.getElementById('serviceForm').reset();

    // Disable Health Check fields by default
    document.getElementById('enableHealthCheck').checked = false;
    toggleHealthCheckFields();

    // Hide Display Mode by default (only show for Custom API widgets)
    toggleDisplayMode();

    // Show modal
    const modal = new bootstrap.Modal(document.getElementById('serviceModal'));
    modal.show();
}

// Edit service
async function editService(categoryName, serviceName) {
    editingService = { category: categoryName, name: serviceName };

    // Set modal title
    document.getElementById('serviceModalTitle').textContent = 'Edit Service';

    try {
        // Get service data
        const response = await axios.get(`/api/services/${categoryName}/${serviceName}`);
        const service = response.data;

        // Load categories into select
        loadCategoriesSelect(categoryName);

        // Fill form with service data
        document.getElementById('serviceName').value = service.name;
        document.getElementById('serviceCategory').value = categoryName;

        const config = service.config || {};
        document.getElementById('serviceIcon').value = config.icon || '';
        document.getElementById('serviceHref').value = config.href || '';
        document.getElementById('serviceDisplay').value = config.display || '';
        document.getElementById('serviceShowStats').checked = config.showStats || false;

        // Handle Health Check fields
        // Check if health check is enabled
        // If any of the health check fields exist in config and healthCheckDisabled is not true, enable it
        const hasHealthCheck = !config.healthCheckDisabled && (
            'ping' in config || 'server' in config || 'container' in config
        );

        // Set the checkbox state
        document.getElementById('enableHealthCheck').checked = hasHealthCheck;

        // Load values first (before enabling/disabling fields)
        document.getElementById('servicePing').value = config.ping || '';
        document.getElementById('serviceServer').value = config.server || '';
        document.getElementById('serviceContainer').value = config.container || '';

        // Enable/disable fields based on checkbox (without clearing values)
        toggleHealthCheckFields(false);

        // Load widget configuration if exists
        if (config.widget) {
            document.getElementById('widgetType').value = config.widget.type;
            updateWidgetFields();
            fillWidgetFields(config.widget);

            // Expand widget accordion
            const widgetCollapse = new bootstrap.Collapse(document.getElementById('widgetConfig'), {
                show: true
            });
        } else {
            // If no widget, hide Display Mode
            toggleDisplayMode();
        }

        // Show modal
        const modal = new bootstrap.Modal(document.getElementById('serviceModal'));
        modal.show();
    } catch (error) {
        console.error('Error loading service:', error);
        showToast('Failed to load service', 'error');
    }
}

// Delete service
async function deleteService(categoryName, serviceName) {
    if (!confirm(`Delete service "${serviceName}"?`)) return;

    try {
        await axios.delete(`/api/services/${categoryName}/${serviceName}`);
        showToast('Service deleted successfully', 'success');
        loadConfiguration();
    } catch (error) {
        console.error('Error deleting service:', error);
        showToast('Failed to delete service', 'error');
    }
}

// Toggle service visibility
async function toggleServiceVisibility(categoryName, serviceName) {
    try {
        // Get current service data
        const response = await axios.get(`/api/services/${categoryName}/${serviceName}`);
        const service = response.data;
        const config = service.config || {};

        // Toggle hidden status
        const newHiddenStatus = !config.hidden;

        // Create updated config
        const updatedConfig = { ...config };

        if (newHiddenStatus) {
            // Hide: set hidden to true
            updatedConfig.hidden = true;
        } else {
            // Show: remove hidden field entirely
            delete updatedConfig.hidden;
            delete updatedConfig.healthCheckDisabled;  // Also remove this internal flag if exists
        }

        // Update service with new hidden status
        await axios.put(`/api/services/${categoryName}/${serviceName}`, {
            name: serviceName,
            category: categoryName,
            config: updatedConfig
        });

        showToast(`Service ${newHiddenStatus ? 'hidden' : 'shown'} successfully`, 'success');
        loadConfiguration();
    } catch (error) {
        console.error('Error toggling service visibility:', error);
        showToast('Failed to toggle service visibility', 'error');
    }
}

// Save service (add or update)
async function saveService() {
    const form = document.getElementById('serviceForm');

    // Validate form
    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    // Gather form data
    const serviceName = document.getElementById('serviceName').value;
    const categoryName = document.getElementById('serviceCategory').value;

    const config = {
        icon: document.getElementById('serviceIcon').value || undefined,
        href: document.getElementById('serviceHref').value || undefined,
        display: document.getElementById('serviceDisplay').value || undefined,
        showStats: document.getElementById('serviceShowStats').checked || undefined
    };

    // Handle Health Check fields
    if (document.getElementById('enableHealthCheck').checked) {
        // Include Health Check fields when enabled
        config.ping = document.getElementById('servicePing').value || undefined;
        config.server = document.getElementById('serviceServer').value || undefined;
        config.container = document.getElementById('serviceContainer').value || undefined;
    } else {
        // When disabled, add the healthCheckDisabled flag
        // This tells the backend to comment out these fields in YAML
        config.healthCheckDisabled = true;
    }

    // Add widget configuration if selected
    const widgetType = document.getElementById('widgetType').value;
    if (widgetType) {
        config.widget = getWidgetConfiguration(widgetType);
    }

    // Remove undefined values
    Object.keys(config).forEach(key => {
        if (config[key] === undefined || config[key] === '') {
            delete config[key];
        }
    });

    try {
        if (editingService) {
            // Update existing service
            await axios.put(`/api/services/${editingService.category}/${editingService.name}`, {
                name: serviceName,
                category: categoryName,
                config: config
            });
            showToast('Service updated successfully', 'success');
        } else {
            // Create new service
            await axios.post('/api/services/', {
                name: serviceName,
                category: categoryName,
                config: config
            });
            showToast('Service added successfully', 'success');
        }

        // Close modal and reload
        bootstrap.Modal.getInstance(document.getElementById('serviceModal')).hide();
        loadConfiguration();
    } catch (error) {
        console.error('Error saving service:', error);
        showToast('Failed to save service', 'error');
    }
}

// Load categories into select
function loadCategoriesSelect(selectedCategory = null) {
    const select = document.getElementById('serviceCategory');
    select.innerHTML = '';

    for (const categoryName of Object.keys(currentConfig)) {
        const option = document.createElement('option');
        option.value = categoryName;
        option.textContent = categoryName;
        if (categoryName === selectedCategory) {
            option.selected = true;
        }
        select.appendChild(option);
    }
}

// Toggle Health Check fields based on checkbox
function toggleHealthCheckFields(clearValues = true) {
    const enabled = document.getElementById('enableHealthCheck').checked;
    document.getElementById('servicePing').disabled = !enabled;
    document.getElementById('serviceServer').disabled = !enabled;
    document.getElementById('serviceContainer').disabled = !enabled;

    // Clear values when disabled (only if clearValues is true)
    if (!enabled && clearValues) {
        document.getElementById('servicePing').value = '';
        document.getElementById('serviceServer').value = '';
        document.getElementById('serviceContainer').value = '';
    }
}

// Toggle Display Mode visibility based on widget type
function toggleDisplayMode() {
    const widgetType = document.getElementById('widgetType').value;
    const displayModeContainer = document.getElementById('displayModeContainer');

    if (widgetType === 'customapi') {
        displayModeContainer.style.display = 'block';
    } else {
        displayModeContainer.style.display = 'none';
    }
}

// Update widget fields based on type
function updateWidgetFields() {
    const widgetType = document.getElementById('widgetType').value;
    const container = document.getElementById('widgetFields');

    if (!widgetType) {
        container.innerHTML = '';
        toggleDisplayMode();
        return;
    }

    let fields = '';

    switch (widgetType) {
        case 'emby':
        case 'jellyfin':
            fields = `
                <div class="widget-field">
                    <label class="form-label">API URL *</label>
                    <input type="url" class="form-control" id="widget_url" placeholder="http://10.0.0.2:8096" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">API Key *</label>
                    <input type="text" class="form-control" id="widget_key" required>
                </div>
                <div class="form-check widget-field">
                    <input class="form-check-input" type="checkbox" id="widget_enableBlocks">
                    <label class="form-check-label" for="widget_enableBlocks">Enable Blocks</label>
                </div>
                <div class="form-check widget-field">
                    <input class="form-check-input" type="checkbox" id="widget_enableNowPlaying" checked>
                    <label class="form-check-label" for="widget_enableNowPlaying">Enable Now Playing</label>
                </div>
            `;
            break;

        case 'qbittorrent':
        case 'transmission':
            fields = `
                <div class="widget-field">
                    <label class="form-label">API URL *</label>
                    <input type="url" class="form-control" id="widget_url" placeholder="http://10.0.0.2:8889" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">Username *</label>
                    <input type="text" class="form-control" id="widget_username" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">Password *</label>
                    <input type="password" class="form-control" id="widget_password" required>
                </div>
            `;
            break;

        case 'customapi':
            fields = `
                <div class="widget-field">
                    <label class="form-label">API URL *</label>
                    <input type="url" class="form-control" id="widget_url" placeholder="http://10.0.0.2:3003/api/v1/..." required>
                </div>
                <div class="widget-field">
                    <label class="form-label">HTTP Method *</label>
                    <select class="form-select" id="widget_method" required>
                        <option value="GET">GET</option>
                        <option value="POST">POST</option>
                    </select>
                </div>
                <div class="widget-field">
                    <label class="form-label">Field Mappings</label>
                    <div id="mappingsContainer">
                        <!-- Mappings will be added here -->
                    </div>
                    <button type="button" class="btn btn-sm btn-secondary" onclick="addMapping()">
                        <i class="bi bi-plus"></i> Add Mapping
                    </button>
                </div>
            `;
            break;

        case 'homeassistant':
            fields = `
                <div class="widget-field">
                    <label class="form-label">API URL *</label>
                    <input type="url" class="form-control" id="widget_url" placeholder="http://10.0.0.2:8123" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">Access Token *</label>
                    <input type="text" class="form-control" id="widget_key" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">Fields (comma-separated)</label>
                    <input type="text" class="form-control" id="widget_fields" placeholder="lights_on, switches_on">
                </div>
            `;
            break;

        case 'diskstation':
            fields = `
                <div class="widget-field">
                    <label class="form-label">API URL *</label>
                    <input type="url" class="form-control" id="widget_url" placeholder="http://10.0.0.3:5000" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">Username *</label>
                    <input type="text" class="form-control" id="widget_username" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">Password *</label>
                    <input type="password" class="form-control" id="widget_password" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">Volume</label>
                    <input type="text" class="form-control" id="widget_volume" placeholder="volume_1">
                </div>
            `;
            break;

        case 'tailscale':
            fields = `
                <div class="widget-field">
                    <label class="form-label">Device ID *</label>
                    <input type="text" class="form-control" id="widget_deviceid" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">API Key *</label>
                    <input type="text" class="form-control" id="widget_key" required>
                </div>
            `;
            break;

        case 'openwrt':
            fields = `
                <div class="widget-field">
                    <label class="form-label">API URL *</label>
                    <input type="url" class="form-control" id="widget_url" placeholder="http://10.0.0.244" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">Username *</label>
                    <input type="text" class="form-control" id="widget_username" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">Password *</label>
                    <input type="password" class="form-control" id="widget_password" required>
                </div>
                <div class="widget-field">
                    <label class="form-label">Interface Name</label>
                    <input type="text" class="form-control" id="widget_interfaceName" placeholder="br-lan">
                </div>
            `;
            break;

        default:
            fields = '<p class="text-muted">No specific configuration for this widget type</p>';
    }

    container.innerHTML = fields;
    toggleDisplayMode();
}

// Get widget configuration from form
function getWidgetConfiguration(widgetType) {
    const widget = { type: widgetType };

    // Get common fields
    const url = document.getElementById('widget_url');
    const key = document.getElementById('widget_key');
    const username = document.getElementById('widget_username');
    const password = document.getElementById('widget_password');

    if (url) widget.url = url.value;
    if (key) widget.key = key.value;
    if (username) widget.username = username.value;
    if (password) widget.password = password.value;

    // Get widget-specific fields
    switch (widgetType) {
        case 'emby':
        case 'jellyfin':
            const enableBlocks = document.getElementById('widget_enableBlocks');
            const enableNowPlaying = document.getElementById('widget_enableNowPlaying');
            if (enableBlocks) widget.enableBlocks = enableBlocks.checked;
            if (enableNowPlaying) widget.enableNowPlaying = enableNowPlaying.checked;
            break;

        case 'customapi':
            const method = document.getElementById('widget_method');
            if (method) widget.method = method.value;

            // Get mappings
            const mappings = [];
            document.querySelectorAll('.mapping-item').forEach(item => {
                const field = item.querySelector('.mapping-field').value;
                const label = item.querySelector('.mapping-label').value;
                if (field && label) {
                    mappings.push({ field, label });
                }
            });
            if (mappings.length > 0) widget.mappings = mappings;
            break;

        case 'homeassistant':
            const fields = document.getElementById('widget_fields');
            if (fields && fields.value) {
                widget.fields = fields.value.split(',').map(f => f.trim());
            }
            break;

        case 'diskstation':
            const volume = document.getElementById('widget_volume');
            if (volume) widget.volume = volume.value;
            break;

        case 'tailscale':
            const deviceid = document.getElementById('widget_deviceid');
            if (deviceid) widget.deviceid = deviceid.value;
            break;

        case 'openwrt':
            const interfaceName = document.getElementById('widget_interfaceName');
            if (interfaceName) widget.interfaceName = interfaceName.value;
            break;
    }

    return widget;
}

// Fill widget fields with existing data
function fillWidgetFields(widgetData) {
    // Wait for fields to be created
    setTimeout(() => {
        for (const [key, value] of Object.entries(widgetData)) {
            const field = document.getElementById(`widget_${key}`);
            if (field) {
                if (field.type === 'checkbox') {
                    field.checked = value;
                } else {
                    field.value = value;
                }
            }
        }

        // Handle special cases
        if (widgetData.type === 'customapi' && widgetData.mappings) {
            widgetData.mappings.forEach(mapping => {
                addMapping(mapping.field, mapping.label);
            });
        }

        if (widgetData.type === 'homeassistant' && widgetData.fields) {
            document.getElementById('widget_fields').value = widgetData.fields.join(', ');
        }
    }, 100);
}

// Add mapping field for custom API
function addMapping(field = '', label = '') {
    const container = document.getElementById('mappingsContainer');
    const mappingHTML = `
        <div class="mapping-item">
            <button type="button" class="btn btn-sm btn-danger btn-remove" onclick="this.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
            <div class="row">
                <div class="col-md-6">
                    <input type="text" class="form-control form-control-sm mapping-field" placeholder="Field name" value="${field}">
                </div>
                <div class="col-md-6">
                    <input type="text" class="form-control form-control-sm mapping-label" placeholder="Display label" value="${label}">
                </div>
            </div>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', mappingHTML);
}