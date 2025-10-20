from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import Response
from core.yaml_handler import YAMLHandler
import yaml

router = APIRouter()
yaml_handler = YAMLHandler()

@router.get("/")
async def get_config():
    """Get current configuration"""
    config = yaml_handler.load_config()
    categories = yaml_handler.parse_services(config)
    return {
        "raw": config,
        "parsed": categories
    }

@router.post("/import")
async def import_config(file: UploadFile = File(...)):
    """Import configuration from uploaded YAML file"""
    if not file.filename.endswith(('.yaml', '.yml')):
        raise HTTPException(status_code=400, detail="File must be a YAML file")

    try:
        contents = await file.read()
        yaml_content = contents.decode('utf-8')

        # Handle document separator
        if yaml_content.startswith('---'):
            yaml_content = yaml_content[3:].strip()

        # Clean up tabs and trailing spaces
        lines = yaml_content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Replace tabs with spaces and strip trailing whitespace
            cleaned_line = line.replace('\t', '    ').rstrip()
            cleaned_lines.append(cleaned_line)
        yaml_content = '\n'.join(cleaned_lines)

        # Validate YAML
        try:
            # Remove inline comments for validation
            import re
            # Remove inline comments but preserve line structure
            clean_content = re.sub(r'#.*$', '', yaml_content, flags=re.MULTILINE)
            config = yaml.safe_load(clean_content)
        except yaml.YAMLError as e:
            error_msg = str(e)
            # Try to extract line number from error
            import re
            line_match = re.search(r'line (\d+)', error_msg)
            if line_match:
                line_num = line_match.group(1)
                raise HTTPException(
                    status_code=400,
                    detail=f"YAML parsing error at line {line_num}: {error_msg}"
                )
            raise HTTPException(status_code=400, detail=f"Invalid YAML: {error_msg}")

        # Save the configuration (pass the cleaned content)
        if yaml_handler.import_yaml(yaml_content):
            # Get the parsed configuration to return summary
            loaded_config = yaml_handler.load_config()
            categories = yaml_handler.parse_services(loaded_config)

            summary = {
                "message": "Configuration imported successfully",
                "categories": len(categories),
                "services": sum(len(services) for services in categories.values())
            }
            return summary
        else:
            raise HTTPException(status_code=500, detail="Failed to save configuration")

    except HTTPException:
        raise
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding error. Please ensure the file is UTF-8 encoded.")
    except Exception as e:
        import traceback
        print(f"Import error: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.get("/export")
async def export_config():
    """Export current configuration as YAML file"""
    yaml_content = yaml_handler.export_yaml()

    return Response(
        content=yaml_content,
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": "attachment; filename=services.yaml"
        }
    )

@router.post("/validate")
async def validate_config(yaml_content: str):
    """Validate YAML configuration"""
    try:
        config = yaml.safe_load(yaml_content)

        # Basic validation
        if not isinstance(config, list):
            return {
                "valid": False,
                "errors": ["Configuration must be a list of categories"]
            }

        errors = []
        warnings = []

        for item in config:
            if not isinstance(item, dict):
                errors.append("Each item must be a dictionary")
                continue

            for category_name, services in item.items():
                if not isinstance(services, list):
                    errors.append(f"Services in category '{category_name}' must be a list")
                    continue

                for service in services:
                    if not isinstance(service, dict):
                        errors.append(f"Service in category '{category_name}' must be a dictionary")
                        continue

                    # Check for service name
                    if not service:
                        warnings.append(f"Empty service in category '{category_name}'")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    except yaml.YAMLError as e:
        return {
            "valid": False,
            "errors": [f"YAML parsing error: {str(e)}"],
            "warnings": []
        }

@router.post("/backup")
async def create_backup():
    """Create a backup of current configuration"""
    from datetime import datetime
    import shutil
    from pathlib import Path

    try:
        config_path = Path(yaml_handler.config_path)
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="No configuration to backup")

        # Create backup directory
        backup_dir = Path("configs/backups")
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create backup with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"services_backup_{timestamp}.yaml"

        shutil.copy(config_path, backup_path)

        return {
            "message": "Backup created successfully",
            "backup_file": str(backup_path)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")

@router.get("/example")
async def get_example_config():
    """Get example configuration"""
    example = """
- Media:
    - Emby:
        icon: https://example.com/emby-icon.png
        href: http://10.0.0.2:8096
        ping: http://10.0.0.2:8096
        server: unraid
        container: emby
        widget:
            type: emby
            url: http://10.0.0.2:8096
            key: your_api_key_here
            enableBlocks: true
            enableNowPlaying: true

    - Qbittorrent:
        icon: https://example.com/qb-icon.png
        href: http://10.0.0.2:8889
        ping: http://10.0.0.2:8889
        widget:
            type: qbittorrent
            url: http://10.0.0.2:8889
            username: admin
            password: your_password

- Tools:
    - FileBrowser:
        icon: https://example.com/filebrowser-icon.png
        href: http://10.0.0.2:380
        ping: http://10.0.0.2:380
        server: unraid
        container: FileBrowser
    """
    return Response(
        content=example.strip(),
        media_type="text/plain"
    )