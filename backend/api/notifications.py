import logging
from typing import List, Optional
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import DrugSchedule, DependencyType, NotificationOverride, TimelineCalculator


logger = logging.getLogger(__name__)
router = APIRouter()


class NotificationDto(BaseModel):
    schedule_id: int
    drug_id: int
    drug_name: str
    kind: str
    amount_per_dose: int
    dependency_type: str
    scheduled_time: str = Field(..., description="ISO timestamp for notification time")


@router.get("/notifications", response_model=List[NotificationDto])
def get_notifications(db: Session = Depends(get_db)):
    """Return notifications that are ready to show now.
    
    This endpoint is designed for polling - it only returns notifications
    that are due within a 5-minute window of the current time.
    """
    logger.info("GET /notifications - checking for notifications ready now")

    # Use TimelineCalculator to get notifications ready now
    calculator = TimelineCalculator(db)
    timeline = calculator.calculate_daily_timeline(date.today())
    
    # Convert to NotificationDto format
    notifications = []
    for item in timeline:
        notifications.append(NotificationDto(
            schedule_id=item['schedule_id'],
            drug_id=item['drug_id'],
            drug_name=item['drug_name'],
            kind=item['kind'],
            amount_per_dose=item['amount_per_dose'],
            dependency_type=item['dependency_type'],
            scheduled_time=item['scheduled_time'].isoformat(),
        ))

    logger.info("GET /notifications count=%d", len(notifications))
    return notifications



class SnoozeRequest(BaseModel):
    minutes: int = 10


@router.post("/notifications/{schedule_id}/snooze")
def snooze_notification(schedule_id: int, payload: SnoozeRequest, db: Session = Depends(get_db)):
    logger.info("POST /notifications/%d/snooze - minutes=%d", schedule_id, payload.minutes)
    
    schedule = db.query(DrugSchedule).filter(DrugSchedule.id == schedule_id, DrugSchedule.is_active == True).first()
    if not schedule:
        logger.error("Schedule %d not found", schedule_id)
        raise HTTPException(status_code=404, detail="Schedule not found")
    # Base time is absolute_time for now
    if schedule.dependency_type != DependencyType.ABSOLUTE or schedule.absolute_time is None:
        raise HTTPException(status_code=400, detail="Snooze supported only for absolute notifications currently")
    today = date.today()
    
    # Check if override already exists for this schedule and date
    existing_override = db.query(NotificationOverride).filter(
        NotificationOverride.schedule_id == schedule.id,
        NotificationOverride.override_date == today
    ).first()
    
    logger.info("Existing override check: %s", existing_override is not None)
    
    # Check if existing override is valid (not too old/stale)
    # If absolute_time was edited, overrides should have been cleared, but this is a safety check
    if existing_override and existing_override.snoozed_until:
        # Check if the existing snooze is reasonable (not way in the past, which would indicate stale data)
        # If snoozed_until is more than 24 hours in the past, it's likely stale and we should reset
        now = datetime.now()
        if existing_override.snoozed_until < now - timedelta(hours=24):
            logger.warning("Existing override appears stale (snoozed_until=%s), resetting to original time", existing_override.snoozed_until)
            # Delete the stale override and start fresh
            db.delete(existing_override)
            existing_override = None
            base_dt = datetime.combine(today, schedule.absolute_time)
            logger.info("Starting from original time after clearing stale override: base_dt=%s", base_dt)
        else:
            # If there's already a valid snooze, add to the existing snoozed_until time
            base_dt = existing_override.snoozed_until
            logger.info("Adding to existing snooze: base_dt=%s", base_dt)
    else:
        # Otherwise, start from the original scheduled time
        base_dt = datetime.combine(today, schedule.absolute_time)
        logger.info("Starting from original time: base_dt=%s", base_dt)
    
    # Add the new snooze minutes to the base time
    snoozed_until = base_dt + timedelta(minutes=max(1, payload.minutes))
    logger.info("Snoozed until: %s", snoozed_until)
    
    if existing_override:
        # Update existing override
        existing_override.snoozed_until = snoozed_until
        existing_override.dismissed = False
        existing_override.created_at = datetime.utcnow()
        logger.info("Updated existing override in database")
    else:
        # Create new override
        ov = NotificationOverride(schedule_id=schedule.id, override_date=today, snoozed_until=snoozed_until, dismissed=False)
        db.add(ov)
        logger.info("Created new override in database")
    
    db.commit()
    logger.info("Snooze saved successfully to database: schedule_id=%d, snoozed_until=%s", schedule_id, snoozed_until.isoformat())
    return {"message": "Snoozed", "snoozed_until": snoozed_until.isoformat()}


@router.post("/notifications/{schedule_id}/dismiss")
def dismiss_notification(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(DrugSchedule).filter(DrugSchedule.id == schedule_id, DrugSchedule.is_active == True).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    today = date.today()
    # Check if override already exists for this schedule and date
    existing_override = db.query(NotificationOverride).filter(
        NotificationOverride.schedule_id == schedule.id,
        NotificationOverride.override_date == today
    ).first()
    
    if existing_override:
        # Update existing override to dismissed
        existing_override.dismissed = True
        existing_override.snoozed_until = None
        existing_override.created_at = datetime.utcnow()
    else:
        # Create new dismissed override
        ov = NotificationOverride(schedule_id=schedule.id, override_date=today, dismissed=True)
        db.add(ov)
    
    db.commit()
    return {"message": "Dismissed"}


