from fastapi import APIRouter, Depends, Form, Response, Request
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..services import USSDService
from ..config import settings

router = APIRouter(prefix="/ussd", tags=["USSD"])


@router.post("/callback")
async def ussd_callback(
    request: Request,
    sessionId: str = Form(None),
    serviceCode: str = Form(None),
    phoneNumber: str = Form(None),
    text: str = Form(default=""),
    db: Session = Depends(get_db)
):
    """
    Handle USSD callback from MTN or AfricaTalking.
    
    Supports both MTN and AfricaTalking USSD formats:
    
    AfricaTalking format:
    - sessionId: Unique session identifier
    - serviceCode: The USSD code that was dialed (e.g., *384*12345#)
    - phoneNumber: User's phone number (with country code)
    - text: User's input concatenated with * (empty on first request)
    
    MTN format (JSON):
    - sessionId: Unique session identifier
    - msisdn: User's phone number
    - ussdString: User input
    - serviceCode: USSD code dialed
    
    Response format:
    - "CON [message]" - Continue the session (show menu and wait for input)
    - "END [message]" - End the session (show final message)
    
    Args:
        request: FastAPI request object
        sessionId: USSD session ID
        serviceCode: USSD service code dialed
        phoneNumber: User's phone number
        text: User input text (empty for initial request)
        db: Database session
        
    Returns:
        Plain text USSD response
    """
    # Try to detect MTN format (JSON body)
    if not sessionId or not phoneNumber:
        try:
            body = await request.json()
            sessionId = body.get("sessionId", body.get("session_id"))
            phoneNumber = body.get("msisdn", body.get("phoneNumber"))
            text = body.get("ussdString", body.get("text", ""))
            serviceCode = body.get("serviceCode", settings.MTN_USSD_SERVICE_CODE)
        except:
            # If JSON parsing fails, use form data (already captured)
            pass
    
    # Use MTN service code if not provided
    if not serviceCode:
        serviceCode = settings.MTN_USSD_SERVICE_CODE if settings.USE_MTN_SERVICES else settings.AT_USSD_SERVICE_CODE
    
    # Process the USSD request
    response_text = USSDService.handle_ussd_request(
        db=db,
        session_id=sessionId,
        phone_number=phoneNumber,
        text=text,
        service_code=serviceCode
    )
    
    # Return as plain text (required by both MTN and AfricaTalking)
    return Response(content=response_text, media_type="text/plain")


@router.get("/health")
async def ussd_health():
    """Health check endpoint for USSD service."""
    provider = "MTN" if settings.USE_MTN_SERVICES else "AfricaTalking"
    service_code = settings.MTN_USSD_SERVICE_CODE if settings.USE_MTN_SERVICES else settings.AT_USSD_SERVICE_CODE
    environment = settings.MTN_ENVIRONMENT if settings.USE_MTN_SERVICES else settings.AT_ENVIRONMENT
    
    return {
        "status": "healthy",
        "service": "ussd",
        "provider": provider,
        "environment": environment,
        "service_code": service_code,
        "callback_url": settings.MTN_CALLBACK_URL
    }

