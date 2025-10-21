# Homepage Configuration Tool

[![Docker Build](https://github.com/thsrite/homepage-config/actions/workflows/docker-build.yml/badge.svg)](https://github.com/thsrite/homepage-config/actions/workflows/docker-build.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker Pulls](https://img.shields.io/docker/pulls/thsrite/homepage-config)](https://hub.docker.com/r/thsrite/homepage-config)

A web-based configuration tool for [Homepage](https://gethomepage.dev/) dashboard. This tool provides a visual interface to create and manage Homepage service configurations without manually editing YAML files.

<div align="center">
    <img src="homepage-config.png" alt="IPTV Stream Sniffer" width="100">
</div>

## ✨ Features

- 🎨 **Visual Configuration Editor** - Add, edit, and delete services through a user-friendly interface
- 🔄 **Drag & Drop** - Reorder services and categories with drag-and-drop functionality
- 👁️ **Live Homepage Preview** - Display your actual Homepage dashboard in an iframe for real-time preview
- 📥 **Import/Export** - Import existing YAML configurations and export your changes
- 🔧 **Widget Support** - Full support for all Homepage widget types including:
  - Media widgets (Emby, Jellyfin, Plex, etc.)
  - Download clients (qBittorrent, Transmission)
  - Custom API widgets
  - Home Assistant, Synology, and more
- 🐳 **Docker Support** - Easy deployment with Docker and docker-compose
- 🚀 **CI/CD** - Automated builds with GitHub Actions

## 🚀 Quick Start

### Option 1: Docker (Recommended)

#### Using Docker Compose

```bash
# Clone the repository
git clone https://github.com/thsrite/homepage-config.git
cd homepage-config

# Start with docker-compose
docker-compose up -d

# Access the tool
# Open http://localhost:9835 in your browser
```

#### Using Docker Run

```bash
docker run -d \
  --name homepage-config \
  -p 9835:9835 \
  -v ./homepage/services.yaml:/app/config/services.yaml \
  -v ./homepage/bookmarks.yaml:/app/config/bookmarks.yaml \
  --restart unless-stopped \
  thsrite/homepage-config:latest
```

### Option 2: Docker Hub

```bash
docker run -d \
  --name homepage-config \
  -p 9835:9835 \
  -v ./homepage/services.yaml:/app/config/services.yaml \
  -v ./homepage/bookmarks.yaml:/app/config/bookmarks.yaml \
  thsrite/homepage-config:latest
```

### Option 3: Local Installation

#### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

#### Setup

1. Clone the repository:
```bash
git clone https://github.com/thsrite/homepage-config.git
cd homepage-config
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python3 run.py
```

4. Open your browser and navigate to:
```
http://localhost:9835
```

## 📖 Usage

### Adding a Category

1. Click the **"Add Category"** button in the Configuration Editor
2. Enter a name for your category (e.g., "Media", "Tools", "Downloads")
3. The category will appear in the editor

### Adding a Service

1. Click **"Add Service"** within a category
2. Fill in the service details:
   - **Service Name** - Display name for the service
   - **Icon URL** - URL to the service icon image
   - **Service URL** - Link to access the service
   - **Health Check URL** - URL to check if service is online
   - **Server/Container** - Docker server and container names (optional)

3. Configure widget (optional):
   - Select widget type from dropdown
   - Fill in widget-specific configuration
   - For Custom API widgets, add field mappings

4. Click **"Save Service"**

### Organizing Services

- **Drag services** using the grip handle (⋮) to reorder within a category
- **Drag services** between categories to move them
- **Drag categories** to reorder them

### Import/Export

#### Import existing configuration:
1. Click **"Import"** in the top navigation
2. Select your existing `services.yaml` file
3. Click **"Import"** to load the configuration

#### Export configuration:
1. Click **"Export"** in the top navigation
2. The `services.yaml` file will be downloaded
3. Copy it to your Homepage configuration directory

### Live Preview

The right panel can display your actual Homepage dashboard:

1. Enter your Homepage URL in the input field (e.g., `http://localhost:3000`)
2. Click **"Set URL"** to load your Homepage in the preview panel
3. Click **"Refresh"** to reload the Homepage after making configuration changes
4. The URL is saved in your browser for future sessions

## 🐳 Docker Deployment

### Building the Image

```bash
# Build locally
docker build -t homepage-config:latest .

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64,linux/arm/v7 \
  -t homepage-config:latest .
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Application port | `9835` |
| `DEBUG` | Enable debug mode | `false` |
| `CONFIG_PATH` | Configuration file path | `config/services.yaml` |

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  homepage-config:
    image: thsrite/homepage-config:latest
    container_name: homepage-config
    restart: unless-stopped
    ports:
      - "9835:9835"
    volumes:
      - ./homepage/services.yaml:/app/config/services.yaml
    environment:
      - PORT=9835
      - DEBUG=false
```

## 🔧 Configuration

### File Locations

- **Generated config**: `config/services.yaml`
- **Backups**: `config/backups/`
- **Uploads**: `uploads/`

### Widget Configuration Examples

#### Emby/Jellyfin
```yaml
widget:
  type: emby
  url: http://10.0.0.2:8096
  key: your_api_key_here
  enableBlocks: true
  enableNowPlaying: true
```

#### qBittorrent
```yaml
widget:
  type: qbittorrent
  url: http://10.0.0.2:8889
  username: admin
  password: your_password
```

#### Custom API
```yaml
widget:
  type: customapi
  url: http://10.0.0.2:3003/api/v1/stats
  method: GET
  mappings:
    - field: downloads
      label: Downloads
    - field: uploads
      label: Uploads
```

## 🔌 API Documentation

The application provides a REST API for programmatic access:

### Endpoints

- `GET /api/services/` - Get all services
- `POST /api/services/` - Create a new service
- `PUT /api/services/{category}/{name}` - Update a service
- `DELETE /api/services/{category}/{name}` - Delete a service
- `GET /api/categories/` - Get all categories
- `POST /api/categories/` - Create a new category
- `GET /api/config/export` - Export configuration as YAML
- `POST /api/config/import` - Import YAML configuration

Full API documentation is available at: `http://localhost:9835/docs`

## 🛠️ Development

### Project Structure
```
homepage-config/
├── backend/           # FastAPI backend
│   ├── api/          # API endpoints
│   ├── core/         # Core functionality
│   └── models/       # Data models
├── frontend/         # HTML/JS frontend
│   ├── static/       # CSS, JS, images
│   └── index.html    # Main page
├── config/          # Configuration files
├── .github/          # GitHub Actions workflows
├── requirements.txt  # Python dependencies
├── Dockerfile        # Docker image definition
├── docker-compose.yml # Docker compose configuration
├── run.py           # Development server
└── README.md        # This file
```

### Technologies Used
- **Backend**: FastAPI, Python 3.8+
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Libraries**: SortableJS (drag-drop), Axios (HTTP client)
- **Deployment**: Docker, GitHub Actions

### Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🐛 Troubleshooting

### Port already in use
If port 9835 is already in use, you can change it:

**Docker:**
```bash
docker run -p 8081:9835 ...
```

**Local:**
```python
# In run.py
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8081,  # Change to desired port
    ...
)
```

### Import errors
- Check for tab characters in YAML (will be auto-fixed)
- Ensure YAML syntax is valid
- Remove inline comments if causing issues

### Preview not loading?
- Check if Homepage is running
- Verify the URL is correct
- Try using IP address instead of hostname
- Check for CORS/iframe restrictions

### Services not updating?
1. Export the configuration
2. Copy `services.yaml` to Homepage config directory
3. Restart Homepage container/service
4. Click Refresh in the preview panel

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Homepage](https://gethomepage.dev/) - The awesome dashboard this tool configures
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework for building APIs
- [Bootstrap](https://getbootstrap.com/) - CSS framework for responsive design
- [SortableJS](https://sortablejs.github.io/Sortable/) - Drag and drop library

## 📮 Support

For issues, questions, or suggestions:
1. Check the [troubleshooting](#-troubleshooting) section
2. Review [Homepage documentation](https://gethomepage.dev/)
3. Open an [issue on GitHub](https://github.com/thsrite/homepage-config/issues)

## 🗺️ Roadmap

- [ ] Multi-language support
- [ ] Dark mode theme
- [ ] Configuration templates library
- [ ] Service status checking
- [ ] Bulk import/export
- [ ] Configuration validation warnings
- [ ] Keyboard shortcuts
- [ ] Mobile responsive design improvements

---

Made with ❤️ for the Homepage community