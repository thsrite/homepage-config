from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from core.yaml_handler import YAMLHandler
from typing import Dict, Any

router = APIRouter()
yaml_handler = YAMLHandler()

@router.get("/", response_class=HTMLResponse)
async def get_preview():
    """Generate preview HTML for the current configuration"""
    config = yaml_handler.load_config()
    categories = yaml_handler.parse_services(config)

    # Generate preview HTML
    html = generate_preview_html(categories)
    return HTMLResponse(content=html)

@router.post("/", response_class=HTMLResponse)
async def preview_config(config_data: Dict[str, Any]):
    """Preview a specific configuration without saving"""
    categories = config_data.get("categories", {})
    html = generate_preview_html(categories)
    return HTMLResponse(content=html)

def generate_preview_html(categories: Dict) -> str:
    """Generate HTML preview for Homepage dashboard"""

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Homepage Preview</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            .header {
                text-align: center;
                color: white;
                margin-bottom: 30px;
            }
            .header h1 {
                font-size: 2.5rem;
                margin-bottom: 10px;
            }
            .preview-notice {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                padding: 10px 20px;
                border-radius: 5px;
                display: inline-block;
                font-size: 0.9rem;
            }
            .categories {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
                gap: 20px;
            }
            .category {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 10px;
                padding: 20px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            }
            .category-title {
                font-size: 1.3rem;
                font-weight: 600;
                margin-bottom: 15px;
                color: #333;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }
            .services {
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            .service {
                display: flex;
                align-items: center;
                padding: 12px;
                background: #f8f9fa;
                border-radius: 8px;
                transition: all 0.3s ease;
                cursor: pointer;
                text-decoration: none;
                color: #333;
            }
            .service:hover {
                background: #e9ecef;
                transform: translateX(5px);
            }
            .service-icon {
                width: 32px;
                height: 32px;
                margin-right: 12px;
                border-radius: 5px;
                background: #667eea;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
            }
            .service-icon img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                border-radius: 5px;
            }
            .service-name {
                font-weight: 500;
                flex-grow: 1;
            }
            .service-status {
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #28a745;
                margin-left: 10px;
            }
            .service-widget {
                margin-top: 8px;
                padding: 8px;
                background: white;
                border-radius: 5px;
                font-size: 0.85rem;
                color: #666;
                display: flex;
                gap: 15px;
            }
            .widget-stat {
                display: flex;
                flex-direction: column;
            }
            .widget-label {
                font-size: 0.75rem;
                color: #999;
            }
            .widget-value {
                font-weight: 600;
                color: #333;
            }
            .empty-category {
                color: #999;
                font-style: italic;
                padding: 20px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Homepage Dashboard</h1>
                <div class="preview-notice">Preview Mode</div>
            </div>
            <div class="categories">
    """

    # Generate categories
    for category_name, services in categories.items():
        html += f"""
            <div class="category">
                <div class="category-title">{category_name}</div>
                <div class="services">
        """

        if services:
            for service in services:
                service_name = service['name']
                config = service.get('config', {})
                href = config.get('href', '#')
                icon = config.get('icon', '')

                # Service item
                html += f"""
                    <a href="{href}" class="service" target="_blank">
                        <div class="service-icon">
                """

                if icon:
                    html += f'<img src="{icon}" alt="{service_name}" onerror="this.style.display=\'none\'; this.parentElement.innerHTML=\'{service_name[0]}\'">'
                else:
                    html += service_name[0].upper()

                html += f"""
                        </div>
                        <div class="service-name">{service_name}</div>
                        <div class="service-status"></div>
                    </a>
                """

                # Add widget info if available
                widget = config.get('widget')
                if widget and config.get('showStats'):
                    widget_type = widget.get('type', 'unknown')
                    html += f"""
                    <div class="service-widget">
                        <div class="widget-stat">
                            <span class="widget-label">Type</span>
                            <span class="widget-value">{widget_type}</span>
                        </div>
                    """

                    # Add mock stats based on widget type
                    if widget_type == 'emby':
                        html += """
                        <div class="widget-stat">
                            <span class="widget-label">Movies</span>
                            <span class="widget-value">1,234</span>
                        </div>
                        <div class="widget-stat">
                            <span class="widget-label">Shows</span>
                            <span class="widget-value">567</span>
                        </div>
                        """
                    elif widget_type == 'qbittorrent':
                        html += """
                        <div class="widget-stat">
                            <span class="widget-label">Download</span>
                            <span class="widget-value">45.3 MB/s</span>
                        </div>
                        <div class="widget-stat">
                            <span class="widget-label">Upload</span>
                            <span class="widget-value">12.1 MB/s</span>
                        </div>
                        """
                    elif widget_type == 'customapi':
                        mappings = widget.get('mappings', [])
                        for i, mapping in enumerate(mappings[:2]):  # Show max 2 stats
                            label = mapping.get('label', f'Field {i+1}')
                            html += f"""
                            <div class="widget-stat">
                                <span class="widget-label">{label}</span>
                                <span class="widget-value">--</span>
                            </div>
                            """

                    html += "</div>"
        else:
            html += '<div class="empty-category">No services in this category</div>'

        html += """
                </div>
            </div>
        """

    if not categories:
        html += """
            <div class="category" style="grid-column: 1 / -1;">
                <div class="empty-category">
                    No categories configured yet. Add some services to get started!
                </div>
            </div>
        """

    html += """
            </div>
        </div>
        <script>
            // Add some interactivity
            document.querySelectorAll('.service').forEach(service => {
                service.addEventListener('click', (e) => {
                    if (service.href === '#' || service.href.endsWith('#')) {
                        e.preventDefault();
                        console.log('Service clicked:', service.querySelector('.service-name').textContent);
                    }
                });
            });

            // Simulate status indicators
            document.querySelectorAll('.service-status').forEach(status => {
                const random = Math.random();
                if (random > 0.9) {
                    status.style.background = '#dc3545'; // Red - offline
                } else if (random > 0.8) {
                    status.style.background = '#ffc107'; // Yellow - warning
                } else {
                    status.style.background = '#28a745'; // Green - online
                }
            });
        </script>
    </body>
    </html>
    """

    return html