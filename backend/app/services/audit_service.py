from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..models import AuditLog


class AuditService:
    """Service for managing audit logs."""
    
    @staticmethod
    def log(
        db: Session,
        entity_type: str,
        entity_id: int,
        action: str,
        old_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
        performed_by: Optional[int] = None,
        details: Optional[str] = None
    ) -> AuditLog:
        """
        Create an audit log entry.
        
        Args:
            db: Database session
            entity_type: Type of entity (e.g., "payment", "payout")
            entity_id: ID of the entity
            action: Action performed (e.g., "create", "update", "approve")
            old_value: Previous state (for updates)
            new_value: New state
            performed_by: User ID who performed the action
            details: Additional context
            
        Returns:
            Created audit log entry
        """
        audit_log = AuditLog(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            performed_by=performed_by,
            details=details
        )
        
        db.add(audit_log)
        db.commit()
        db.refresh(audit_log)
        
        return audit_log
    
    @staticmethod
    def get_logs(
        db: Session,
        entity_type: Optional[str] = None,
        entity_id: Optional[int] = None,
        limit: int = 100
    ):
        """
        Retrieve audit logs with optional filters.
        
        Args:
            db: Database session
            entity_type: Filter by entity type
            entity_id: Filter by entity ID
            limit: Maximum number of logs to return
            
        Returns:
            List of audit logs
        """
        query = db.query(AuditLog)
        
        if entity_type:
            query = query.filter(AuditLog.entity_type == entity_type)
        
        if entity_id:
            query = query.filter(AuditLog.entity_id == entity_id)
        
        return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()

