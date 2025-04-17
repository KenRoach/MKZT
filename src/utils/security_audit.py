import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from src.utils.database import Base
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from src.utils.logger import logger
from src.models.audit_log import AuditLog

# Security audit model
class SecurityAuditLog(Base):
    __tablename__ = "security_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    event_type = Column(String, nullable=False)
    user_id = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    details = Column(JSON, nullable=True)
    success = Column(Boolean, nullable=False, default=True)

def log_security_event(
    db: Session,
    event_type: str,
    user_id: Optional[str],
    ip_address: str,
    details: dict
):
    try:
        audit_log = AuditLog(
            event_type=event_type,
            user_id=user_id,
            ip_address=ip_address,
            event_details=details,
            timestamp=datetime.utcnow()
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to log security event: {str(e)}")
        db.rollback()

def log_failed_login(db: Session, username: str, ip_address: str, reason: str):
    log_security_event(
        db=db,
        event_type="failed_login",
        user_id=username,
        ip_address=ip_address,
        details={"reason": reason}
    )

def log_api_access(
    db: Session,
    request_path: str,
    method: str,
    ip_address: str,
    user_id: Optional[str],
    status_code: int,
    processing_time: float
):
    log_security_event(
        db=db,
        event_type="api_access",
        user_id=user_id,
        ip_address=ip_address,
        details={
            "path": request_path,
            "method": method,
            "status_code": status_code,
            "processing_time_ms": processing_time
        }
    )

def log_login_attempt(
    db: Session,
    user_id: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    failure_reason: Optional[str] = None
) -> None:
    """Log a login attempt"""
    details = {"failure_reason": failure_reason} if not success else None
    log_security_event(
        db=db,
        event_type="login_attempt",
        user_id=user_id,
        ip_address=ip_address,
        details=details
    )

def log_password_change(
    db: Session,
    user_id: str,
    ip_address: str,
    user_agent: str,
    success: bool,
    failure_reason: Optional[str] = None
) -> None:
    """Log a password change attempt"""
    details = {"failure_reason": failure_reason} if not success else None
    log_security_event(
        db=db,
        event_type="password_change",
        user_id=user_id,
        ip_address=ip_address,
        details=details
    ) 