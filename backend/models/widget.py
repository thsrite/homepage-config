from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, ClassVar

class WidgetConfig(BaseModel):
    """Widget configuration model"""
    type: str = Field(..., description="Widget type")
    url: Optional[str] = Field(None, description="Widget API URL")
    key: Optional[str] = Field(None, description="API key")
    username: Optional[str] = Field(None, description="Username for authentication")
    password: Optional[str] = Field(None, description="Password for authentication")

    # Generic fields for various widget types
    method: Optional[str] = Field(None, description="HTTP method for custom API")
    mappings: Optional[List[Dict[str, str]]] = Field(None, description="Field mappings for custom API")
    fields: Optional[List[str]] = Field(None, description="Fields to display")

    # Emby specific
    enableBlocks: Optional[bool] = Field(None, description="Enable blocks display")
    enableNowPlaying: Optional[bool] = Field(None, description="Enable now playing display")

    # Qbittorrent specific
    rpcUrl: Optional[str] = Field(None, description="RPC URL")

    # Tailscale specific
    deviceid: Optional[str] = Field(None, description="Device ID")

    # Openwrt specific
    interfaceName: Optional[str] = Field(None, description="Interface name")

    # DiskStation specific
    volume: Optional[str] = Field(None, description="Volume name")

    # Other widget-specific fields can be added here

    class Config:
        extra = "allow"  # Allow additional fields for flexibility
        json_schema_extra = {
            "example": {
                "type": "emby",
                "url": "http://10.0.0.2:8096",
                "key": "api_key_here",
                "enableBlocks": True,
                "enableNowPlaying": True
            }
        }

class Widget(BaseModel):
    """Widget model with predefined types"""

    WIDGET_TYPES: ClassVar[List[str]] = [
        "emby",
        "jellyfin",
        "plex",
        "qbittorrent",
        "transmission",
        "customapi",
        "homeassistant",
        "adguard",
        "tailscale",
        "openwrt",
        "diskstation",
        "audiobookshelf",
        "jellyseerr",
        "glances",
        "xteve"
    ]

    type: str = Field(..., description="Widget type")
    config: WidgetConfig = Field(..., description="Widget configuration")

    @classmethod
    def get_widget_types(cls) -> List[str]:
        """Get list of available widget types"""
        return cls.WIDGET_TYPES

    @classmethod
    def get_widget_schema(cls, widget_type: str) -> Dict[str, Any]:
        """Get schema for a specific widget type"""
        schemas = {
            "emby": {
                "required": ["url", "key"],
                "optional": ["enableBlocks", "enableNowPlaying"]
            },
            "qbittorrent": {
                "required": ["url", "username", "password"],
                "optional": ["rpcUrl"]
            },
            "customapi": {
                "required": ["url", "method"],
                "optional": ["mappings"]
            },
            "homeassistant": {
                "required": ["url", "key"],
                "optional": ["fields"]
            },
            "diskstation": {
                "required": ["url", "username", "password"],
                "optional": ["volume"]
            },
            "tailscale": {
                "required": ["deviceid", "key"],
                "optional": []
            },
            "openwrt": {
                "required": ["url", "username", "password"],
                "optional": ["interfaceName"]
            }
        }
        return schemas.get(widget_type, {"required": [], "optional": []})