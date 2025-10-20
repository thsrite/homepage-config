import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
import copy

class YAMLHandler:
    """Handle YAML parsing and generation for Homepage configuration"""

    def __init__(self, config_path: str = "config/services.yaml"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> List[Dict[str, Any]]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            return []

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                # Read content and clean tabs
                raw_content = f.read()

                # Replace tabs with spaces and clean up
                lines = raw_content.split('\n')
                cleaned_lines = []
                for line in lines:
                    # Replace tabs with 2 spaces and remove trailing whitespace
                    cleaned_line = line.replace('\t', '  ').rstrip()
                    cleaned_lines.append(cleaned_line)
                cleaned_content = '\n'.join(cleaned_lines)

                # Parse cleaned YAML
                content = yaml.safe_load(cleaned_content)
                return content if content else []
        except Exception as e:
            print(f"Error loading config: {e}")
            # Try to provide more specific error info
            if 'tab' in str(e).lower() or '\t' in str(e):
                print("Note: Tab characters found in YAML file. They have been replaced with spaces.")
            return []

    def save_config(self, config: List[Dict[str, Any]]) -> bool:
        """Save configuration to YAML file"""
        try:
            # Custom representer for cleaner YAML output
            def represent_none(self, _):
                return self.represent_scalar('tag:yaml.org,2002:null', '')

            yaml.add_representer(type(None), represent_none)

            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f,
                         default_flow_style=False,
                         allow_unicode=True,
                         sort_keys=False,
                         indent=2,  # Homepage uses 2-space indentation
                         default_style=None,
                         explicit_start=False,
                         explicit_end=False)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def parse_services(self, config: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Parse services from configuration into categories"""
        result = {}

        for item in config:
            if isinstance(item, dict):
                for category_name, services in item.items():
                    if isinstance(services, list):
                        result[category_name] = []
                        for service in services:
                            if isinstance(service, dict):
                                for service_name, service_config in service.items():
                                    parsed_service = {
                                        'name': service_name,
                                        'config': service_config if service_config else {}
                                    }
                                    result[category_name].append(parsed_service)

        return result

    def build_config(self, categories: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Build configuration from categories and services"""
        config = []

        for category_name, services in categories.items():
            category_services = []
            for service in services:
                service_dict = {service['name']: service.get('config', {})}
                category_services.append(service_dict)

            config.append({category_name: category_services})

        return config

    def add_service(self, category: str, service_name: str, service_config: Dict) -> bool:
        """Add a service to a category"""
        config = self.load_config()
        categories = self.parse_services(config)

        if category not in categories:
            categories[category] = []

        # Check if service already exists
        for service in categories[category]:
            if service['name'] == service_name:
                return False

        categories[category].append({
            'name': service_name,
            'config': service_config
        })

        new_config = self.build_config(categories)
        return self.save_config(new_config)

    def update_service(self, category: str, service_name: str, service_config: Dict) -> bool:
        """Update a service configuration"""
        config = self.load_config()
        categories = self.parse_services(config)

        if category not in categories:
            return False

        for i, service in enumerate(categories[category]):
            if service['name'] == service_name:
                categories[category][i]['config'] = service_config
                new_config = self.build_config(categories)
                return self.save_config(new_config)

        return False

    def delete_service(self, category: str, service_name: str) -> bool:
        """Delete a service from a category"""
        config = self.load_config()
        categories = self.parse_services(config)

        if category not in categories:
            return False

        categories[category] = [
            s for s in categories[category] if s['name'] != service_name
        ]

        # Remove empty categories
        if not categories[category]:
            del categories[category]

        new_config = self.build_config(categories)
        return self.save_config(new_config)

    def reorder_services(self, category: str, service_order: List[str]) -> bool:
        """Reorder services within a category"""
        config = self.load_config()
        categories = self.parse_services(config)

        if category not in categories:
            return False

        # Create a mapping of service names to service data
        service_map = {s['name']: s for s in categories[category]}

        # Reorder based on the provided order
        reordered = []
        for service_name in service_order:
            if service_name in service_map:
                reordered.append(service_map[service_name])

        categories[category] = reordered
        new_config = self.build_config(categories)
        return self.save_config(new_config)

    def move_service(self, service_name: str, from_category: str, to_category: str) -> bool:
        """Move a service from one category to another"""
        config = self.load_config()
        categories = self.parse_services(config)

        if from_category not in categories:
            return False

        # Find the service
        service_data = None
        for service in categories[from_category]:
            if service['name'] == service_name:
                service_data = service
                break

        if not service_data:
            return False

        # Remove from old category
        categories[from_category] = [
            s for s in categories[from_category] if s['name'] != service_name
        ]

        # Remove empty categories
        if not categories[from_category]:
            del categories[from_category]

        # Add to new category
        if to_category not in categories:
            categories[to_category] = []

        categories[to_category].append(service_data)

        new_config = self.build_config(categories)
        return self.save_config(new_config)

    def import_yaml(self, yaml_content: str) -> bool:
        """Import configuration from YAML string"""
        try:
            # Remove document separator if present
            if yaml_content.startswith('---'):
                yaml_content = yaml_content[3:].strip()

            # Clean up the YAML content
            import re
            # Remove trailing whitespace and tabs from each line
            lines = yaml_content.split('\n')
            cleaned_lines = []
            for line in lines:
                # Replace tabs with spaces and strip trailing whitespace
                cleaned_line = line.replace('\t', '    ').rstrip()
                cleaned_lines.append(cleaned_line)
            yaml_content = '\n'.join(cleaned_lines)

            # Parse the YAML
            config = yaml.safe_load(yaml_content)

            # Handle None or empty config
            if not config:
                return False

            # If config is not a list, wrap it in a list
            if not isinstance(config, list):
                config = [config]

            return self.save_config(config)
        except Exception as e:
            print(f"Error importing YAML: {e}")
            import traceback
            traceback.print_exc()
            return False

    def export_yaml(self) -> str:
        """Export configuration as YAML string"""
        config = self.load_config()
        return yaml.dump(config,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False,
                        indent=4)