from fastapi import APIRouter, HTTPException, Body, UploadFile, File
from fastapi.responses import Response
from typing import List, Dict, Any
from models import BookmarkCreate, BookmarkUpdate
from core.bookmarks_handler import BookmarksHandler

router = APIRouter()
bookmarks_handler = BookmarksHandler()

@router.get("/groups")
async def get_bookmark_groups():
    """Get all bookmark groups"""
    groups = bookmarks_handler.get_all_groups()
    return {"groups": groups}

@router.get("/")
async def get_all_bookmarks():
    """Get all bookmarks organized by groups"""
    bookmarks = bookmarks_handler.load_bookmarks()
    groups = bookmarks_handler.parse_bookmarks(bookmarks)

    # Format response
    response = []
    for group_name, bookmarks_list in groups.items():
        group_data = {
            "name": group_name,
            "bookmarks": []
        }
        for bookmark in bookmarks_list:
            bookmark_data = {
                "name": bookmark['name'],
                **bookmark.get('config', {})
            }
            group_data["bookmarks"].append(bookmark_data)
        response.append(group_data)

    return response

@router.get("/{group}")
async def get_group_bookmarks(group: str):
    """Get bookmarks for a specific group"""
    bookmarks = bookmarks_handler.load_bookmarks()
    groups = bookmarks_handler.parse_bookmarks(bookmarks)

    if group not in groups:
        raise HTTPException(status_code=404, detail=f"Group '{group}' not found")

    bookmarks_list = []
    for bookmark in groups[group]:
        bookmark_data = {
            "name": bookmark['name'],
            **bookmark.get('config', {})
        }
        bookmarks_list.append(bookmark_data)

    return {
        "group": group,
        "bookmarks": bookmarks_list
    }

@router.post("/{group}")
async def create_bookmark(group: str, bookmark: BookmarkCreate):
    """Add a bookmark to a group"""
    bookmark_config = {
        "abbr": bookmark.name,  # Add abbr field to match Homepage format
        "href": bookmark.href
    }

    if bookmark.icon:
        bookmark_config["icon"] = bookmark.icon
    if bookmark.description:
        bookmark_config["description"] = bookmark.description

    success = bookmarks_handler.add_bookmark(group, bookmark.name, bookmark_config)

    if not success:
        raise HTTPException(status_code=400, detail="Bookmark already exists or could not be added")

    return {"message": "Bookmark created successfully"}

@router.put("/{group}/{bookmark_name}")
async def update_bookmark(group: str, bookmark_name: str, bookmark: BookmarkUpdate):
    """Update a bookmark"""
    bookmarks = bookmarks_handler.load_bookmarks()
    groups = bookmarks_handler.parse_bookmarks(bookmarks)

    if group not in groups:
        raise HTTPException(status_code=404, detail=f"Group '{group}' not found")

    # Find existing bookmark
    existing = None
    for b in groups[group]:
        if b['name'] == bookmark_name:
            existing = b
            break

    if not existing:
        raise HTTPException(status_code=404, detail=f"Bookmark '{bookmark_name}' not found")

    # Update config
    bookmark_config = existing.get('config', {})

    # Update name if changed
    if bookmark.name and bookmark.name != bookmark_name:
        bookmark_config["abbr"] = bookmark.name
    elif "abbr" not in bookmark_config:
        bookmark_config["abbr"] = bookmark_name

    if bookmark.href is not None:
        bookmark_config["href"] = bookmark.href
    if bookmark.icon is not None:
        bookmark_config["icon"] = bookmark.icon
    if bookmark.description is not None:
        bookmark_config["description"] = bookmark.description

    # If name is being changed
    new_name = bookmark.name if bookmark.name else bookmark_name

    if new_name != bookmark_name:
        # Delete old and add new
        bookmarks_handler.delete_bookmark(group, bookmark_name)
        success = bookmarks_handler.add_bookmark(group, new_name, bookmark_config)
    else:
        success = bookmarks_handler.update_bookmark(group, bookmark_name, bookmark_config)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to update bookmark")

    return {"message": "Bookmark updated successfully"}

@router.delete("/{group}/{bookmark_name}")
async def delete_bookmark(group: str, bookmark_name: str):
    """Delete a bookmark"""
    success = bookmarks_handler.delete_bookmark(group, bookmark_name)

    if not success:
        raise HTTPException(status_code=404, detail="Bookmark or group not found")

    return {"message": "Bookmark deleted successfully"}

@router.post("/groups/{group}")
async def create_group(group: str):
    """Create a new bookmark group"""
    bookmarks = bookmarks_handler.load_bookmarks()
    groups = bookmarks_handler.parse_bookmarks(bookmarks)

    if group in groups:
        raise HTTPException(status_code=400, detail="Group already exists")

    # Add empty group
    groups[group] = []
    new_config = bookmarks_handler.build_bookmarks_config(groups)
    success = bookmarks_handler.save_bookmarks(new_config)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to create group")

    return {"message": "Group created successfully"}

@router.put("/groups/{group}")
async def rename_group(group: str, new_name: str = Body(..., embed=True)):
    """Rename a bookmark group"""
    bookmarks = bookmarks_handler.load_bookmarks()
    groups = bookmarks_handler.parse_bookmarks(bookmarks)

    if group not in groups:
        raise HTTPException(status_code=404, detail="Group not found")

    if new_name in groups:
        raise HTTPException(status_code=400, detail="Group with new name already exists")

    # Rename the group
    groups[new_name] = groups.pop(group)
    new_config = bookmarks_handler.build_bookmarks_config(groups)
    success = bookmarks_handler.save_bookmarks(new_config)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to rename group")

    return {"message": "Group renamed successfully"}

@router.delete("/groups/{group}")
async def delete_group(group: str):
    """Delete a bookmark group and all its bookmarks"""
    bookmarks = bookmarks_handler.load_bookmarks()
    groups = bookmarks_handler.parse_bookmarks(bookmarks)

    if group not in groups:
        raise HTTPException(status_code=404, detail="Group not found")

    del groups[group]
    new_config = bookmarks_handler.build_bookmarks_config(groups)
    success = bookmarks_handler.save_bookmarks(new_config)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete group")

    return {"message": "Group deleted successfully"}

@router.get("/export")
async def export_bookmarks():
    """Export bookmarks configuration as YAML file"""
    yaml_content = bookmarks_handler.export_yaml()

    return Response(
        content=yaml_content,
        media_type="application/x-yaml",
        headers={
            "Content-Disposition": "attachment; filename=bookmarks.yaml"
        }
    )

@router.post("/import")
async def import_bookmarks(file: UploadFile = File(...)):
    """Import bookmarks from YAML file"""
    if not file.filename.endswith(('.yaml', '.yml')):
        raise HTTPException(status_code=400, detail="File must be a YAML file")

    try:
        contents = await file.read()
        yaml_content = contents.decode('utf-8')

        success = bookmarks_handler.import_yaml(yaml_content)

        if success:
            bookmarks = bookmarks_handler.load_bookmarks()
            groups = bookmarks_handler.parse_bookmarks(bookmarks)

            summary = {
                "message": "Bookmarks imported successfully",
                "groups": len(groups),
                "total_bookmarks": sum(len(bookmarks) for bookmarks in groups.values())
            }
            return summary
        else:
            raise HTTPException(status_code=500, detail="Failed to import bookmarks")

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding error")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")