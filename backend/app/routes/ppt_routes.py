"""
PowerPoint Generation Routes
Endpoints for generating and retrieving PowerPoint presentations
"""
from fastapi import APIRouter, HTTPException
from app.services.powerpoint_service import (
    generate_powerpoint_presentation,
    get_presentation_info,
    PPTGenerationRequest,
    PPTGenerationResponse
)

router = APIRouter()

@router.get("/ppt/health")
async def health_check():
    """Health check endpoint for PowerPoint service"""
    return {"status": "healthy", "service": "PowerPoint Generator"}

@router.post("/ppt/generate-presentation", response_model=PPTGenerationResponse)
async def generate_presentation(request: PPTGenerationRequest):
    """
    Generate PowerPoint presentation from incident data
    
    Args:
        request: PPTGenerationRequest containing query, industries, region, and shotlisted articles
        
    Returns:
        PPTGenerationResponse with download URL and presentation details
    """
    return await generate_powerpoint_presentation(request)

@router.get("/ppt/presentation/{presentation_id}")
async def get_presentation_status(presentation_id: str):
    """
    Get presentation status and download URL
    
    Args:
        presentation_id: UUID of the generated presentation
        
    Returns:
        Dictionary with presentation details and download URL
    """
    return await get_presentation_info(presentation_id)
