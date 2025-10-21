from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List

class Bookmark(BaseModel):
    """Bookmark model for Homepage"""
    name: str = Field(..., description="Bookmark name")
    icon: Optional[str] = Field(None, description="Icon URL or icon name")
    href: str = Field(..., description="Bookmark URL")
    description: Optional[str] = Field(None, description="Bookmark description")

class BookmarkGroup(BaseModel):
    """Group of bookmarks"""
    name: str = Field(..., description="Group name")
    bookmarks: List[Bookmark] = Field(default_factory=list, description="List of bookmarks in this group")

class BookmarkCreate(BaseModel):
    """Model for creating a bookmark"""
    name: str
    icon: Optional[str] = None
    href: str
    description: Optional[str] = None

class BookmarkUpdate(BaseModel):
    """Model for updating a bookmark"""
    name: Optional[str] = None
    icon: Optional[str] = None
    href: Optional[str] = None
    description: Optional[str] = None

class BookmarkGroupCreate(BaseModel):
    """Model for creating a bookmark group"""
    name: str
    bookmarks: List[BookmarkCreate] = []