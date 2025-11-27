"""Admin authentication and authorization utilities."""
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from functools import wraps

from ..database import get_db
from ..models import User, AdminRole
from .auth import get_current_user


async def get_current_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to verify that the current user is a system administrator.
    Raises 403 if user is not an admin.
    """
    if not current_user.is_system_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. System administrator privileges required."
        )
    
    # Update last login timestamp
    from datetime import datetime
    current_user.last_login = datetime.utcnow()
    db.add(current_user)
    db.commit()
    
    return current_user


def require_admin_role(*allowed_roles: AdminRole):
    """
    Dependency factory to require specific admin roles.
    
    Usage:
        @router.get("/admin/super-only")
        def super_admin_only(admin: User = Depends(require_admin_role(AdminRole.SUPER_ADMIN))):
            ...
    
    Args:
        allowed_roles: One or more AdminRole values that are permitted
    
    Returns:
        Dependency function that validates admin role
    """
    async def _check_admin_role(
        admin: User = Depends(get_current_admin)
    ) -> User:
        if admin.admin_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role(s): {', '.join([r.value for r in allowed_roles])}"
            )
        return admin
    
    return _check_admin_role


async def get_optional_admin(
    current_user: Optional[User] = Depends(get_current_user),
) -> Optional[User]:
    """
    Optional admin dependency - returns admin user if authenticated,
    None otherwise. Useful for endpoints that behave differently for admins.
    """
    if current_user and current_user.is_system_admin:
        return current_user
    return None


def log_admin_action(action: str, entity_type: str, entity_id: Optional[int] = None):
    """
    Decorator to automatically log admin actions to audit log.
    
    Usage:
        @router.post("/admin/users/{user_id}/suspend")
        @log_admin_action("suspend_user", "user")
        def suspend_user(user_id: int, admin: User = Depends(get_current_admin)):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            from ..models import AuditLog
            from ..database import SessionLocal
            
            # Extract admin user and entity_id from kwargs
            admin = kwargs.get('admin') or kwargs.get('current_admin')
            eid = kwargs.get(f'{entity_type}_id') or entity_id
            
            # Execute the function
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            
            # Log to audit
            if admin:
                db = SessionLocal()
                try:
                    audit = AuditLog(
                        entity_type=entity_type,
                        entity_id=eid,
                        action=action,
                        performed_by=admin.id,
                        details=f"Admin {admin.name} (ID: {admin.id}) performed {action}"
                    )
                    db.add(audit)
                    db.commit()
                except Exception as e:
                    print(f"Failed to log admin action: {e}")
                finally:
                    db.close()
            
            return result
        
        return wrapper
    return decorator

