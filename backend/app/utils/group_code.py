import random
import string
from sqlalchemy.orm import Session
from ..models import Group


def generate_group_code(db: Session, length: int = 8) -> str:
    """
    Generate a unique group code.
    
    Args:
        db: Database session
        length: Length of the code (default 8)
        
    Returns:
        Unique group code
    """
    while True:
        # Generate random alphanumeric code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        code = f"SUSU{code[:4]}"  # Format: SUSUXXXX
        
        # Check if code already exists
        existing = db.query(Group).filter(Group.group_code == code).first()
        if not existing:
            return code

