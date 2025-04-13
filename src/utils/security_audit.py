import logging
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from src.utils.database import Base
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean

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
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    success: bool = True
) -> None:
    """Log a security event to the database"""
    audit_log = SecurityAuditLog(
        event_type=event_type,
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
        success=success
    )
    
    db.add(audit_log)
    db.commit()
    
    # Also log to file
    log_level = logging.INFO if success else logging.WARNING
    logging.getLogger("security").log(
        log_level,
        f"Security event: {event_type} | User: {user_id} | IP: {ip_address} | Success: {success}"
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
        user_agent=user_agent,
        details=details,
        success=success
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
        user_agent=user_agent,
        details=details,
        success=success
    )

def log_api_access(
    db: Session,
    endpoint: str,
    method: str,
    ip_address: str,
    user_agent: str,
    user_id: Optional[str] = None,
    success: bool = True,
    error: Optional[str] = None
) -> None:
    """Log API access"""
    details = {
        "endpoint": endpoint,
        "method": method,
        "error": error
    }
    log_security_event(
        db=db,
        event_type="api_access",
        user_id=user_id,
        ip_address=ip_address,
        user_agent=user_agent,
        details=details,
        success=success
    ) 