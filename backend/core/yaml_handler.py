import yaml
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import copy
import re

class YAMLHandler:
    """Handle YAML parsing and generation for Homepage configuration"""

    def __init__(self, config_path: str = "config/services.yaml"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize ruamel.yaml instance
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.default_flow_style = False
        self.yaml.indent(mapping=2, sequence=2, offset=0)
        self.yaml.width = 4096  # Prevent line wrapping

    def load_config(self) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Load configuration from YAML file
        Returns either a list (standard format) or dict (direct format)
        Preserves comments and formatting using ruamel.yaml
        """
        if not self.config_path.exists():
            return []

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                content = self.yaml.load(f)

                # Return empty list if no content
                if content is None:
                    return []

                # Detect and flag commented health check fields
                content = self._load_commented_fields(content)

                return content
        except Exception as e:
            print(f"Error loading config: {e}")
            return []

    def save_config(self, config: List[Dict[str, Any]]) -> bool:
        """Save configuration to YAML file
        Preserves comments and formatting using ruamel.yaml
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(config, f)

            # Post-process to handle commented fields and hidden services
            self._process_comments()
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def _process_comments(self):
        """Process comments for healthCheckDisabled fields and hidden services"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            print(f"\n=== PROCESS COMMENTS DEBUG ===")

            # First pass: identify services with healthCheckDisabled or hidden
            services_to_comment_fields = set()  # Services with healthCheckDisabled
            services_to_hide = set()  # Services with hidden: true
            current_service_start = None
            current_service_name = None
            service_names = {}  # {line_num: service_name}

            for i, line in enumerate(lines):
                stripped = line.strip()

                # Detect service start (indent level 2: '  - ServiceName:')
                if stripped.startswith('- ') and ':' in stripped:
                    indent_level = len(line) - len(line.lstrip())
                    if indent_level == 2:  # Service level
                        current_service_start = i
                        current_service_name = stripped.split(':')[0][2:].strip()
                        service_names[i] = current_service_name

                # Check for healthCheckDisabled
                if 'healthCheckDisabled: true' in line and current_service_start is not None:
                    services_to_comment_fields.add(current_service_start)

                # Check for hidden
                if 'hidden: true' in line and current_service_start is not None:
                    print(f"  Found 'hidden: true' for {current_service_name} at line {i}")
                    services_to_hide.add(current_service_start)

            print(f"Services to hide: {[service_names.get(line) for line in services_to_hide]}")
            print(f"Services to comment fields: {[service_names.get(line) for line in services_to_comment_fields]}")

            # Second pass: comment out fields/services as needed, OR uncomment if should be visible
            new_lines = []
            current_service_start = None
            service_to_comment_fields = False
            service_to_hide = False
            in_hidden_service = False
            in_commented_service = False  # Track if we're in a commented service block
            hidden_service_indent = 0

            for i, line in enumerate(lines):
                stripped = line.strip()
                indent_level = len(line) - len(line.lstrip())

                # Check if we've exited the hidden/commented service
                # Only exit when we hit another service definition line
                if (in_hidden_service or in_commented_service):
                    if indent_level <= 2 and (stripped.startswith('- ') or stripped.startswith('# - ')) and ':' in stripped:
                        # Exit service state when we reach a new service at the same level
                        in_hidden_service = False
                        in_commented_service = False

                # Detect service start (indent level 2)
                if indent_level == 2:
                    # Detect commented service
                    if stripped.startswith('# - ') and ':' in stripped:
                        service_name = stripped[4:].split(':')[0].strip()
                        current_service_start = i
                        service_to_hide = i in services_to_hide

                        if not service_to_hide:
                            # This service is commented but should NOT be hidden
                            # We need to uncomment it
                            print(f"  Will uncomment service: {service_name}")
                            in_commented_service = True
                            hidden_service_indent = indent_level
                        else:
                            # Keep it commented
                            in_commented_service = False
                    # Detect normal service
                    elif stripped.startswith('- ') and ':' in stripped:
                        current_service_start = i
                        service_to_comment_fields = i in services_to_comment_fields
                        service_to_hide = i in services_to_hide

                        if service_to_hide:
                            in_hidden_service = True
                            hidden_service_indent = indent_level

                # Skip healthCheckDisabled and hidden lines (internal flags)
                if 'healthCheckDisabled:' in line or 'hidden:' in line:
                    continue

                # Skip commented service if it should be visible
                # (It's already in the file as a normal service because we added it to config)
                if in_commented_service:
                    # Skip these lines - they're duplicates
                    # The service was already added by _load_commented_fields and written by dump()
                    continue

                # Comment out entire service if marked as hidden
                elif in_hidden_service:
                    if not stripped.startswith('#'):
                        # Get the base indent (should be 2 for service level, 4+ for fields)
                        original_indent = len(line) - len(line.lstrip())
                        # For service name line (indent 2), keep it at 2
                        # For config lines (indent 4+), convert to 2 + relative indent
                        if stripped.startswith('- ') and indent_level == 2:
                            # Service line: keep at indent 2
                            line = f"  # {line.lstrip()}"
                        else:
                            # Config line: add comment at base level (2 spaces) + relative indent
                            relative_indent = original_indent - 2  # Relative to service level
                            if relative_indent < 0:
                                relative_indent = 0
                            line = f"  # {' ' * relative_indent}{line.lstrip()}"

                # Comment out health check fields if this service is marked
                elif service_to_comment_fields and any(f'{field}:' in stripped for field in ['ping', 'server', 'container']):
                    if not stripped.startswith('#'):
                        # Preserve indentation and add comment
                        indent = line[:len(line) - len(line.lstrip())]
                        line = f"{indent}# {line.lstrip()}"

                new_lines.append(line)

            # Write back
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

            print(f"Wrote {len(new_lines)} lines to file")
            print(f"=== END PROCESS COMMENTS ===\n")

        except Exception as e:
            print(f"Error processing comments: {e}")

    def _load_commented_fields(self, config: Union[List, Dict]) -> Union[List, Dict]:
        """Load and detect commented health check fields and hidden services
        Also extracts commented services and adds them back to config with hidden flag
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Track services with commented health check fields and hidden services
            current_category = None
            current_service = None
            has_commented_fields = {}
            hidden_services = {}

            # Store parsed hidden services to add to config with line numbers for ordering
            hidden_services_data = {}  # {category: [{name: config, line_number: int}]}

            i = 0
            while i < len(lines):
                line = lines[i]
                stripped = line.strip()
                indent_level = len(line) - len(line.lstrip())

                # Detect category (indent level 0: '- CategoryName:')
                if stripped.startswith('- ') and ':' in stripped and indent_level == 0:
                    current_category = stripped.split(':')[0][2:].strip()
                    current_service = None

                # Detect service within category (indent level 2)
                elif indent_level == 2 and current_category:
                    # Check if it's a commented service line
                    if stripped.startswith('# - ') and ':' in stripped:
                        start_line = i
                        current_service = stripped[4:].split(':')[0].strip()  # Remove '# - '
                        key = f"{current_category}:{current_service}"
                        hidden_services[key] = True

                        # Collect all commented lines for this service
                        service_lines = []
                        i += 1

                        # Read all commented lines that belong to this service
                        while i < len(lines):
                            next_line = lines[i]
                            next_stripped = next_line.strip()
                            next_indent = len(next_line) - len(next_line.lstrip())

                            # Stop if we hit another service (at indent 2) or category (at indent 0)
                            if next_stripped.startswith('# - ') and ':' in next_stripped and next_indent == 2:
                                # Hit another commented service
                                i -= 1
                                break
                            elif next_stripped.startswith('- ') and ':' in next_stripped and next_indent <= 2:
                                # Hit an uncommented service or category
                                i -= 1
                                break
                            elif not next_stripped.startswith('#') and next_stripped and next_indent <= 2:
                                # Hit non-commented content at service level or above
                                i -= 1
                                break

                            # Collect commented lines
                            if next_stripped.startswith('#'):
                                service_lines.append(next_line)
                            elif not next_stripped:
                                # Empty line - could be end of service
                                pass
                            else:
                                # Non-commented line - end of this service block
                                i -= 1
                                break

                            i += 1

                        # Parse the service by uncommenting and using YAML parser
                        service_config = {}
                        if service_lines:
                            # Uncomment lines while preserving relative indentation
                            # Step 1: Remove comments and measure indents
                            processed_lines = []
                            for line in service_lines:
                                stripped = line.strip()
                                if stripped.startswith('#'):
                                    # Get the content after removing '#' and one optional space
                                    content = stripped[1:]
                                    if content and content[0] == ' ':
                                        content = content[1:]

                                    # Get original indent (before the #)
                                    original_indent = len(line) - len(line.lstrip())

                                    processed_lines.append((original_indent, content))

                            # Step 2: Find base indent (minimum)
                            if processed_lines:
                                base_indent = min(indent for indent, _ in processed_lines)

                                # Step 3: Rebuild with normalized indentation
                                uncommented_lines = []
                                for original_indent, content in processed_lines:
                                    # Calculate relative indent
                                    relative_indent = original_indent - base_indent
                                    # Service fields start at 4 spaces
                                    final_indent = 4 + relative_indent
                                    uncommented_lines.append(f"{' ' * final_indent}{content}\n")

                                # Build YAML snippet
                                yaml_snippet = f"  - {current_service}:\n" + ''.join(uncommented_lines)
                            else:
                                yaml_snippet = f"  - {current_service}:\n"

                            try:
                                # Parse with YAML
                                parsed = yaml.safe_load(yaml_snippet)
                                if parsed and isinstance(parsed, list) and len(parsed) > 0:
                                    service_dict = parsed[0]
                                    if current_service in service_dict:
                                        service_config = service_dict[current_service] or {}
                            except Exception as e:
                                print(f"Warning: Failed to parse commented service {current_service}: {e}")
                                # Fall back to empty config
                                service_config = {}

                        # Store the hidden service data with line number for ordering
                        if current_category not in hidden_services_data:
                            hidden_services_data[current_category] = []
                        hidden_services_data[current_category].append({
                            'name': current_service,
                            'config': service_config,
                            'line_number': start_line
                        })

                    elif stripped.startswith('- ') and ':' in stripped:
                        current_service = stripped.split(':')[0][2:].strip()

                # Detect commented health check fields (for non-hidden services)
                if current_service and stripped.startswith('#') and current_service:
                    uncommented = stripped[1:].strip()
                    if any(field in uncommented for field in ['ping:', 'server:', 'container:']):
                        key = f"{current_category}:{current_service}"
                        if key not in has_commented_fields:
                            has_commented_fields[key] = True

                i += 1

            # Build a complete service list with line numbers for proper ordering
            # First, scan the file again to get line numbers for all services
            service_line_numbers = {}  # {category:service_name: line_number}
            current_category = None
            for i, line in enumerate(lines):
                stripped = line.strip()
                indent_level = len(line) - len(line.lstrip())

                # Detect category
                if stripped.startswith('- ') and ':' in stripped and indent_level == 0:
                    current_category = stripped.split(':')[0][2:].strip()
                # Detect service (commented or not)
                elif indent_level == 2 and current_category:
                    if stripped.startswith('# - ') and ':' in stripped:
                        service_name = stripped[4:].split(':')[0].strip()
                        service_line_numbers[f"{current_category}:{service_name}"] = i
                    elif stripped.startswith('- ') and ':' in stripped:
                        service_name = stripped.split(':')[0][2:].strip()
                        service_line_numbers[f"{current_category}:{service_name}"] = i

            # Add healthCheckDisabled and hidden flags to existing services
            # Also add hidden services to config in the correct order
            if isinstance(config, list):
                for category_item in config:
                    if isinstance(category_item, dict):
                        for category_name, services in category_item.items():
                            if isinstance(services, list):
                                # Mark existing services
                                for service_item in services:
                                    if isinstance(service_item, dict):
                                        for service_name, service_config in service_item.items():
                                            key = f"{category_name}:{service_name}"
                                            if isinstance(service_config, dict):
                                                # Mark services with commented health check fields
                                                if key in has_commented_fields:
                                                    service_config['healthCheckDisabled'] = True
                                                # Mark hidden services
                                                if key in hidden_services:
                                                    service_config['hidden'] = True

                                # Add hidden services and re-sort by line number
                                if category_name in hidden_services_data:
                                    for hidden_service in hidden_services_data[category_name]:
                                        # Check if service already exists (shouldn't happen but be safe)
                                        service_exists = False
                                        for service_item in services:
                                            if isinstance(service_item, dict):
                                                if hidden_service['name'] in service_item:
                                                    service_exists = True
                                                    break

                                        if not service_exists:
                                            # Add the hidden service with hidden flag
                                            hidden_config = hidden_service['config'].copy()
                                            hidden_config['hidden'] = True
                                            services.append({hidden_service['name']: hidden_config})

                                    # Now sort services by their line numbers in the original file
                                    def get_service_line_number(service_item):
                                        if isinstance(service_item, dict):
                                            for service_name in service_item.keys():
                                                key = f"{category_name}:{service_name}"
                                                return service_line_numbers.get(key, 999999)
                                        return 999999

                                    services.sort(key=get_service_line_number)

            return config

        except Exception as e:
            print(f"Error loading commented fields: {e}")
            import traceback
            traceback.print_exc()
            return config

    def parse_services(self, config: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Parse services from configuration into categories
        Supports both formats:
        1. List format: [{"Media": [...]}, {"Tools": [...]}]
        2. Direct format: {"Media": [...], "Tools": [...]}
        """
        result = {}

        # If config is a dict (direct format without list wrapper)
        if isinstance(config, dict):
            for category_name, services in config.items():
                if isinstance(services, list):
                    result[category_name] = []
                    for service in services:
                        if isinstance(service, dict):
                            for service_name, service_config in service.items():
                                # Convert numeric keys to strings
                                service_name = str(service_name)
                                parsed_service = {
                                    'name': service_name,
                                    'config': service_config if service_config else {}
                                }
                                result[category_name].append(parsed_service)
        # If config is a list (standard format)
        elif isinstance(config, list):
            for item in config:
                if isinstance(item, dict):
                    for category_name, services in item.items():
                        if isinstance(services, list):
                            result[category_name] = []
                            for service in services:
                                if isinstance(service, dict):
                                    for service_name, service_config in service.items():
                                        # Convert numeric keys to strings
                                        service_name = str(service_name)
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
        print(f"\n=== UPDATE SERVICE DEBUG ===")
        print(f"Service: {category}/{service_name}")
        print(f"New config has 'hidden': {'hidden' in service_config}")
        if 'hidden' in service_config:
            print(f"  hidden value: {service_config['hidden']}")

        config = self.load_config()
        categories = self.parse_services(config)

        if category not in categories:
            return False

        for i, service in enumerate(categories[category]):
            if service['name'] == service_name:
                print(f"Found service at index {i}")
                print(f"Old config had 'hidden': {'hidden' in service.get('config', {})}")

                categories[category][i]['config'] = service_config
                print(f"After update, config has 'hidden': {'hidden' in categories[category][i]['config']}")

                new_config = self.build_config(categories)
                result = self.save_config(new_config)
                print(f"Save result: {result}")
                print(f"=== END DEBUG ===\n")
                return result

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

        # Ensure we always export in list format for consistency
        if isinstance(config, dict):
            # Convert dict format to list format
            list_config = []
            for category_name, services in config.items():
                list_config.append({category_name: services})
            config = list_config

        return yaml.dump(config,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False,
                        indent=2)  # Use 2-space indent for Homepage compatibility