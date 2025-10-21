import yaml
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

class BookmarksHandler:
    """Handle YAML parsing and generation for Homepage bookmarks configuration"""

    def __init__(self, bookmarks_path: str = "config/bookmarks.yaml"):
        self.bookmarks_path = Path(bookmarks_path)
        self.bookmarks_path.parent.mkdir(parents=True, exist_ok=True)

    def load_bookmarks(self) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """Load bookmarks configuration from YAML file
        Returns either a list (standard format) or dict (direct format)
        """
        if not self.bookmarks_path.exists():
            return []

        try:
            with open(self.bookmarks_path, 'r', encoding='utf-8') as f:
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

                # Return content as-is, whether it's a list or dict
                if content is None:
                    return []
                return content
        except Exception as e:
            print(f"Error loading bookmarks: {e}")
            return []

    def save_bookmarks(self, bookmarks: List[Dict[str, Any]]) -> bool:
        """Save bookmarks configuration to YAML file"""
        try:
            # Custom representer for cleaner YAML output
            def represent_none(self, _):
                return self.represent_scalar('tag:yaml.org,2002:null', '')

            yaml.add_representer(type(None), represent_none)

            with open(self.bookmarks_path, 'w', encoding='utf-8') as f:
                yaml.dump(bookmarks, f,
                         default_flow_style=False,
                         allow_unicode=True,
                         sort_keys=False,
                         indent=2,  # Homepage uses 2-space indentation
                         default_style=None,
                         explicit_start=False,
                         explicit_end=False)
            return True
        except Exception as e:
            print(f"Error saving bookmarks: {e}")
            return False

    def parse_bookmarks(self, config: Union[List[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """Parse bookmarks from configuration into groups
        Supports both formats:
        1. List format: [{"Developer": [...]}, {"Social": [...]}]
        2. Direct format: {"Developer": [...], "Social": [...]}
        """
        result = {}

        # If config is a dict (direct format without list wrapper)
        if isinstance(config, dict):
            for group_name, bookmarks in config.items():
                if isinstance(bookmarks, list):
                    result[group_name] = []
                    for bookmark in bookmarks:
                        if isinstance(bookmark, dict):
                            for bookmark_name, bookmark_config in bookmark.items():
                                # Convert numeric keys to strings
                                bookmark_name = str(bookmark_name)
                                parsed_bookmark = {
                                    'name': bookmark_name,
                                    'config': bookmark_config if bookmark_config else {}
                                }
                                result[group_name].append(parsed_bookmark)
        # If config is a list (standard format)
        elif isinstance(config, list):
            for item in config:
                if isinstance(item, dict):
                    for group_name, bookmarks in item.items():
                        if isinstance(bookmarks, list):
                            result[group_name] = []
                            for bookmark in bookmarks:
                                if isinstance(bookmark, dict):
                                    for bookmark_name, bookmark_config in bookmark.items():
                                        # Convert numeric keys to strings
                                        bookmark_name = str(bookmark_name)
                                        parsed_bookmark = {
                                            'name': bookmark_name,
                                            'config': bookmark_config if bookmark_config else {}
                                        }
                                        result[group_name].append(parsed_bookmark)

        return result

    def build_bookmarks_config(self, groups: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """Build bookmarks configuration from groups"""
        config = []

        for group_name, bookmarks in groups.items():
            group_bookmarks = []
            for bookmark in bookmarks:
                # Get bookmark config
                bookmark_config = bookmark.get('config', {})
                # Create bookmark entry with name as key
                bookmark_dict = {bookmark['name']: bookmark_config}
                group_bookmarks.append(bookmark_dict)

            config.append({group_name: group_bookmarks})

        return config

    def add_bookmark(self, group: str, bookmark_name: str, bookmark_config: Dict) -> bool:
        """Add a bookmark to a group"""
        bookmarks = self.load_bookmarks()
        groups = self.parse_bookmarks(bookmarks)

        if group not in groups:
            groups[group] = []

        # Check if bookmark already exists
        for bookmark in groups[group]:
            if bookmark['name'] == bookmark_name:
                return False

        groups[group].append({
            'name': bookmark_name,
            'config': bookmark_config
        })

        new_config = self.build_bookmarks_config(groups)
        return self.save_bookmarks(new_config)

    def update_bookmark(self, group: str, bookmark_name: str, bookmark_config: Dict) -> bool:
        """Update a bookmark configuration"""
        bookmarks = self.load_bookmarks()
        groups = self.parse_bookmarks(bookmarks)

        if group not in groups:
            return False

        for i, bookmark in enumerate(groups[group]):
            if bookmark['name'] == bookmark_name:
                groups[group][i]['config'] = bookmark_config
                new_config = self.build_bookmarks_config(groups)
                return self.save_bookmarks(new_config)

        return False

    def delete_bookmark(self, group: str, bookmark_name: str) -> bool:
        """Delete a bookmark from a group"""
        bookmarks = self.load_bookmarks()
        groups = self.parse_bookmarks(bookmarks)

        if group not in groups:
            return False

        groups[group] = [
            b for b in groups[group] if b['name'] != bookmark_name
        ]

        # Remove empty groups
        if not groups[group]:
            del groups[group]

        new_config = self.build_bookmarks_config(groups)
        return self.save_bookmarks(new_config)

    def get_all_groups(self) -> List[str]:
        """Get list of all bookmark groups"""
        bookmarks = self.load_bookmarks()
        groups = self.parse_bookmarks(bookmarks)
        return list(groups.keys())

    def export_yaml(self) -> str:
        """Export bookmarks as YAML string"""
        bookmarks = self.load_bookmarks()

        # Ensure we always export in list format for consistency
        if isinstance(bookmarks, dict):
            # Convert dict format to list format
            list_bookmarks = []
            for group_name, group_bookmarks in bookmarks.items():
                list_bookmarks.append({group_name: group_bookmarks})
            bookmarks = list_bookmarks

        return yaml.dump(bookmarks,
                        default_flow_style=False,
                        allow_unicode=True,
                        sort_keys=False,
                        indent=2)

    def import_yaml(self, yaml_content: str) -> bool:
        """Import bookmarks from YAML string"""
        try:
            # Remove document separator if present
            if yaml_content.startswith('---'):
                yaml_content = yaml_content[3:].strip()

            # Clean up tabs and trailing spaces
            lines = yaml_content.split('\n')
            cleaned_lines = []
            for line in lines:
                cleaned_line = line.replace('\t', '  ').rstrip()
                cleaned_lines.append(cleaned_line)
            yaml_content = '\n'.join(cleaned_lines)

            # Parse and save
            bookmarks = yaml.safe_load(yaml_content)

            if not bookmarks:
                return False

            # If bookmarks is not a list, wrap it in a list for consistent storage
            if not isinstance(bookmarks, list):
                bookmarks = [bookmarks]

            return self.save_bookmarks(bookmarks)
        except Exception as e:
            print(f"Error importing bookmarks YAML: {e}")
            return False