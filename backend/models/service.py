from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from .widget import WidgetConfig

class ServiceConfig(BaseModel):
    """Service configuration model"""
    icon: Optional[str] = Field(None, description="Icon URL")
    href: Optional[str] = Field(None, description="Service URL")
    ping: Optional[str] = Field(None, description="Health check URL")
    server: Optional[str] = Field(None, description="Server name")
    container: Optional[str] = Field(None, description="Container name")
    showStats: Optional[bool] = Field(None, description="Show statistics")
    display: Optional[str] = Field(None, description="Display mode (list, grid)")
    widget: Optional[WidgetConfig] = Field(None, description="Widget configuration")

    class Config:
        json_schema_extra = {
            "example": {
                "icon": "https://example.com/icon.png",
                "href": "http://10.0.0.2:8096",
                "ping": "http://10.0.0.2:8096",
                "server": "unraid",
                "container": "emby",
                "widget": {
                    "type": "emby",
                    "url": "http://10.0.0.2:8096",
                    "key": "api_key_here"
                }
            }
        }

class Service(BaseModel):
    """Service model"""
    name: str = Field(..., description="Service name")
    category: str = Field(..., description="Category name")
    config: ServiceConfig = Field(default_factory=ServiceConfig)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Emby",
                "category": "Media",
                "config": {
                    "icon": "https://example.com/emby-icon.png",
                    "href": "http://10.0.0.2:8096"
                }
            }
        }

class ServiceCreate(BaseModel):
    """Model for creating a service"""
    name: str = Field(..., description="Service name")
    category: str = Field(..., description="Category name")
    config: Optional[ServiceConfig] = Field(default_factory=ServiceConfig)

class ServiceUpdate(BaseModel):
    """Model for updating a service"""
    name: Optional[str] = Field(None, description="Service name")
    category: Optional[str] = Field(None, description="Category name")
    config: Optional[ServiceConfig] = Field(None, description="Service configuration")