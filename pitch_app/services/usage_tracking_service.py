"""
Usage Tracking Service
Tracks API usage for OpenAI, SendGrid, and Railway
"""
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from pitch_app.models import UsageLog
import logging

logger = logging.getLogger(__name__)

# Pricing (approximate, update as needed)
OPENAI_PRICING = {
    "whisper-1": 0.006 / 60,  # $0.006 per minute
    "gpt-4": {
        "input": 0.03 / 1000,  # $0.03 per 1K tokens
        "output": 0.06 / 1000,  # $0.06 per 1K tokens
    },
    "gpt-3.5-turbo": {
        "input": 0.0015 / 1000,  # $0.0015 per 1K tokens
        "output": 0.002 / 1000,  # $0.002 per 1K tokens
    }
}

SENDGRID_PRICING = 0.0  # Free tier or based on plan
RAILWAY_PRICING_PER_GB = 0.10  # Approximate


def log_openai_usage(
    db: Session,
    operation: str,
    tokens_used: int,
    model: str = "gpt-4",
    user_id: Optional[int] = None,
    metadata: Optional[Dict] = None
) -> None:
    """Log OpenAI API usage"""
    try:
        # Calculate cost
        cost = 0.0
        if model == "whisper-1":
            # Assume metadata contains duration in seconds
            duration_minutes = metadata.get("duration_seconds", 0) / 60 if metadata else 0
            cost = duration_minutes * OPENAI_PRICING["whisper-1"]
        elif model in OPENAI_PRICING:
            # Simplified: assume half input, half output
            pricing = OPENAI_PRICING[model]
            cost = (tokens_used / 2 * pricing["input"]) + (tokens_used / 2 * pricing["output"])
        
        log_entry = UsageLog(
            service="openai",
            operation=operation,
            user_id=user_id,
            tokens_used=tokens_used,
            cost_usd=cost,
            metadata_=json.dumps(metadata) if metadata else None
        )
        db.add(log_entry)
        db.commit()
        logger.info(f"Logged OpenAI usage: {operation}, tokens: {tokens_used}, cost: ${cost:.4f}")
    except Exception as e:
        logger.error(f"Error logging OpenAI usage: {e}")
        db.rollback()


def log_sendgrid_usage(
    db: Session,
    operation: str,
    user_id: Optional[int] = None,
    metadata: Optional[Dict] = None
) -> None:
    """Log SendGrid email usage"""
    try:
        log_entry = UsageLog(
            service="sendgrid",
            operation=operation,
            user_id=user_id,
            tokens_used=None,
            cost_usd=SENDGRID_PRICING,
            metadata_=json.dumps(metadata) if metadata else None
        )
        db.add(log_entry)
        db.commit()
        logger.info(f"Logged SendGrid usage: {operation}")
    except Exception as e:
        logger.error(f"Error logging SendGrid usage: {e}")
        db.rollback()


def log_railway_usage(
    db: Session,
    operation: str,
    gb_used: float,
    metadata: Optional[Dict] = None
) -> None:
    """Log Railway resource usage"""
    try:
        cost = gb_used * RAILWAY_PRICING_PER_GB
        log_entry = UsageLog(
            service="railway",
            operation=operation,
            user_id=None,
            tokens_used=None,
            cost_usd=cost,
            metadata_=json.dumps(metadata) if metadata else None
        )
        db.add(log_entry)
        db.commit()
        logger.info(f"Logged Railway usage: {operation}, GB: {gb_used}, cost: ${cost:.4f}")
    except Exception as e:
        logger.error(f"Error logging Railway usage: {e}")
        db.rollback()


def get_usage_summary(
    db: Session,
    service: Optional[str] = None,
    days: int = 30
) -> Dict:
    """Get usage summary for the last N days"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(
            UsageLog.service,
            func.count(UsageLog.id).label("count"),
            func.sum(UsageLog.tokens_used).label("total_tokens"),
            func.sum(UsageLog.cost_usd).label("total_cost")
        ).filter(UsageLog.created_at >= start_date)
        
        if service:
            query = query.filter(UsageLog.service == service)
        
        results = query.group_by(UsageLog.service).all()
        
        summary = {}
        for row in results:
            summary[row.service] = {
                "count": row.count,
                "total_tokens": int(row.total_tokens) if row.total_tokens else 0,
                "total_cost": float(row.total_cost) if row.total_cost else 0.0
            }
        
        return summary
    except Exception as e:
        logger.error(f"Error getting usage summary: {e}")
        return {}


def get_daily_usage(
    db: Session,
    service: str,
    days: int = 30
) -> List[Dict]:
    """Get daily usage breakdown for a service"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            func.date(UsageLog.created_at).label("date"),
            func.count(UsageLog.id).label("count"),
            func.sum(UsageLog.tokens_used).label("tokens"),
            func.sum(UsageLog.cost_usd).label("cost")
        ).filter(
            and_(
                UsageLog.service == service,
                UsageLog.created_at >= start_date
            )
        ).group_by(
            func.date(UsageLog.created_at)
        ).order_by(
            func.date(UsageLog.created_at)
        ).all()
        
        daily_data = []
        for row in results:
            daily_data.append({
                "date": row.date.isoformat() if hasattr(row.date, "isoformat") else str(row.date) if row.date else None,
                "count": row.count,
                "tokens": int(row.tokens) if row.tokens else 0,
                "cost": float(row.cost) if row.cost else 0.0
            })
        
        return daily_data
    except Exception as e:
        logger.error(f"Error getting daily usage: {e}")
        return []


def get_operation_breakdown(
    db: Session,
    service: str,
    days: int = 30
) -> List[Dict]:
    """Get usage breakdown by operation type"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        results = db.query(
            UsageLog.operation,
            func.count(UsageLog.id).label("count"),
            func.sum(UsageLog.tokens_used).label("tokens"),
            func.sum(UsageLog.cost_usd).label("cost")
        ).filter(
            and_(
                UsageLog.service == service,
                UsageLog.created_at >= start_date
            )
        ).group_by(
            UsageLog.operation
        ).order_by(
            func.sum(UsageLog.cost_usd).desc()
        ).all()
        
        breakdown = []
        for row in results:
            breakdown.append({
                "operation": row.operation,
                "count": row.count,
                "tokens": int(row.tokens) if row.tokens else 0,
                "cost": float(row.cost) if row.cost else 0.0
            })
        
        return breakdown
    except Exception as e:
        logger.error(f"Error getting operation breakdown: {e}")
        return []

# Made with Bob
