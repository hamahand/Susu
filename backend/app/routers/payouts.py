from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..schemas import PayoutResponse, PayoutApprove
from ..utils import get_current_user
from ..services import PayoutService

router = APIRouter(prefix="/payouts", tags=["Payouts"])


@router.post("/{payout_id}/approve", response_model=PayoutResponse)
def approve_payout(
    payout_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve a payout (admin only).
    """
    payout = PayoutService.approve_payout(db, payout_id, current_user.id)
    return payout


@router.get("/{group_id}/current", response_model=PayoutResponse)
def get_current_payout(
    group_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current round payout for a group.
    """
    payout = PayoutService.get_current_payout(db, group_id)
    
    if not payout:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No payout found for current round"
        )
    
    return payout

