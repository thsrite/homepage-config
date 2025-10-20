from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from core.yaml_handler import YAMLHandler

router = APIRouter()
yaml_handler = YAMLHandler()

@router.get("/", response_model=List[str])
async def get_categories():
    """Get all category names"""
    config = yaml_handler.load_config()
    categories = yaml_handler.parse_services(config)
    return list(categories.keys())

@router.post("/", response_model=Dict[str, str])
async def create_category(name: str = Body(..., embed=True)):
    """Create a new category"""
    config = yaml_handler.load_config()
    categories = yaml_handler.parse_services(config)

    if name in categories:
        raise HTTPException(status_code=400, detail="Category already exists")

    categories[name] = []
    new_config = yaml_handler.build_config(categories)

    if yaml_handler.save_config(new_config):
        return {"message": "Category created successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to create category")

@router.put("/{category_name}", response_model=Dict[str, str])
async def rename_category(
    category_name: str,
    new_name: str = Body(..., embed=True)
):
    """Rename a category"""
    config = yaml_handler.load_config()
    categories = yaml_handler.parse_services(config)

    if category_name not in categories:
        raise HTTPException(status_code=404, detail="Category not found")

    if new_name in categories:
        raise HTTPException(status_code=400, detail="New category name already exists")

    # Move all services to new category
    categories[new_name] = categories[category_name]
    del categories[category_name]

    new_config = yaml_handler.build_config(categories)

    if yaml_handler.save_config(new_config):
        return {"message": "Category renamed successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to rename category")

@router.delete("/{category_name}", response_model=Dict[str, str])
async def delete_category(category_name: str, force: bool = False):
    """Delete a category"""
    config = yaml_handler.load_config()
    categories = yaml_handler.parse_services(config)

    if category_name not in categories:
        raise HTTPException(status_code=404, detail="Category not found")

    if categories[category_name] and not force:
        raise HTTPException(
            status_code=400,
            detail="Category is not empty. Set force=true to delete with all services"
        )

    del categories[category_name]
    new_config = yaml_handler.build_config(categories)

    if yaml_handler.save_config(new_config):
        return {"message": "Category deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete category")

@router.post("/reorder", response_model=Dict[str, str])
async def reorder_categories(category_order: List[str] = Body(...)):
    """Reorder categories"""
    config = yaml_handler.load_config()
    categories = yaml_handler.parse_services(config)

    # Create new ordered dict
    ordered_categories = {}
    for category_name in category_order:
        if category_name in categories:
            ordered_categories[category_name] = categories[category_name]

    # Add any missing categories at the end
    for category_name in categories:
        if category_name not in ordered_categories:
            ordered_categories[category_name] = categories[category_name]

    new_config = yaml_handler.build_config(ordered_categories)

    if yaml_handler.save_config(new_config):
        return {"message": "Categories reordered successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to reorder categories")