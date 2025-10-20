from fastapi import APIRouter, HTTPException, Body
from typing import List, Dict, Any
from models import Service, ServiceCreate, ServiceUpdate
from core.yaml_handler import YAMLHandler

router = APIRouter()
yaml_handler = YAMLHandler()

@router.get("/", response_model=Dict[str, List[Dict[str, Any]]])
async def get_all_services():
    """Get all services grouped by category"""
    config = yaml_handler.load_config()
    categories = yaml_handler.parse_services(config)
    return categories

@router.get("/{category}/{service_name}", response_model=Dict[str, Any])
async def get_service(category: str, service_name: str):
    """Get a specific service"""
    config = yaml_handler.load_config()
    categories = yaml_handler.parse_services(config)

    if category not in categories:
        raise HTTPException(status_code=404, detail="Category not found")

    for service in categories[category]:
        if service['name'] == service_name:
            return {
                "name": service['name'],
                "category": category,
                "config": service.get('config', {})
            }

    raise HTTPException(status_code=404, detail="Service not found")

@router.post("/", response_model=Dict[str, str])
async def create_service(service: ServiceCreate):
    """Create a new service"""
    config_dict = service.config.model_dump(exclude_none=True) if service.config else {}

    success = yaml_handler.add_service(
        category=service.category,
        service_name=service.name,
        service_config=config_dict
    )

    if success:
        return {"message": "Service created successfully"}
    else:
        raise HTTPException(status_code=400, detail="Service already exists or creation failed")

@router.put("/{category}/{service_name}", response_model=Dict[str, str])
async def update_service(
    category: str,
    service_name: str,
    service_update: ServiceUpdate
):
    """Update an existing service"""
    # Get current service
    config = yaml_handler.load_config()
    categories = yaml_handler.parse_services(config)

    if category not in categories:
        raise HTTPException(status_code=404, detail="Category not found")

    # Find the service
    current_service = None
    for service in categories[category]:
        if service['name'] == service_name:
            current_service = service
            break

    if not current_service:
        raise HTTPException(status_code=404, detail="Service not found")

    # Handle category change
    new_category = service_update.category if service_update.category else category
    new_name = service_update.name if service_update.name else service_name

    # If category changed, move the service
    if new_category != category:
        yaml_handler.move_service(service_name, category, new_category)
        category = new_category

    # Update configuration
    if service_update.config:
        config_dict = service_update.config.model_dump(exclude_none=True)
        success = yaml_handler.update_service(category, service_name, config_dict)

        if not success:
            raise HTTPException(status_code=400, detail="Update failed")

    # Handle name change (delete old, create new)
    if new_name != service_name:
        current_config = current_service.get('config', {})
        if service_update.config:
            current_config.update(service_update.config.model_dump(exclude_none=True))

        yaml_handler.delete_service(category, service_name)
        yaml_handler.add_service(category, new_name, current_config)

    return {"message": "Service updated successfully"}

@router.delete("/{category}/{service_name}", response_model=Dict[str, str])
async def delete_service(category: str, service_name: str):
    """Delete a service"""
    success = yaml_handler.delete_service(category, service_name)

    if success:
        return {"message": "Service deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Service not found or deletion failed")

@router.post("/reorder", response_model=Dict[str, str])
async def reorder_services(
    category: str = Body(...),
    service_order: List[str] = Body(...)
):
    """Reorder services within a category"""
    success = yaml_handler.reorder_services(category, service_order)

    if success:
        return {"message": "Services reordered successfully"}
    else:
        raise HTTPException(status_code=400, detail="Reorder failed")

@router.post("/move", response_model=Dict[str, str])
async def move_service(
    service_name: str = Body(...),
    from_category: str = Body(...),
    to_category: str = Body(...)
):
    """Move a service between categories"""
    success = yaml_handler.move_service(service_name, from_category, to_category)

    if success:
        return {"message": "Service moved successfully"}
    else:
        raise HTTPException(status_code=400, detail="Move failed")