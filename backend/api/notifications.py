import logging
from collections.abc import AsyncIterator
from datetime import UTC, date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import DependencyType, DrugSchedule, NotificationOverride
from backend.schemas import NotificationDto
from backend.services.notification_scheduler import (
    NotificationScheduler,
    get_notification_scheduler,
)
from backend.services.rabbitmq_client import get_notifications_queue

logger = logging.getLogger(__name__)
router = APIRouter()


class SnoozeResponse(BaseModel):
    notification: NotificationDto
    snoozed_until: str = Field(
        ..., description="ISO timestamp when notification will reappear"
    )


class DismissResponse(BaseModel):
    notification: NotificationDto
    dismissed: bool = True


@router.get("/notifications")
async def get_notifications(
    db: Session = Depends(get_db),
) -> list[NotificationDto]:
    """Return notifications that are due within the current time window (DB-based)."""
    now = datetime.now()
    today = date.today()

    window_start = now - timedelta(minutes=60)
    window_end = now + timedelta(minutes=5)

    schedules = (
        db.query(DrugSchedule)
        .filter(
            DrugSchedule.is_active,
            DrugSchedule.start_date <= today,
            (DrugSchedule.end_date >= today) | (DrugSchedule.end_date.is_(None)),
        )
        .all()
    )

    notifications = []
    for schedule in schedules:
        override = (
            db.query(NotificationOverride)
            .filter(
                NotificationOverride.schedule_id == schedule.id,
                NotificationOverride.override_date == today,
            )
            .order_by(NotificationOverride.id.desc())
            .first()
        )

        if override and override.dismissed:
            continue

        if override and override.snoozed_until:
            scheduled_time = override.snoozed_until
        else:
            try:
                scheduled_time = calculate_drug_time_for_display(schedule, today)
            except Exception:
                continue

        if window_start <= scheduled_time <= window_end:
            notifications.append(
                NotificationDto(
                    schedule_id=schedule.id,
                    drug_id=schedule.drug_id,
                    drug_name=schedule.drug.name,
                    kind=schedule.drug.kind,
                    amount_per_dose=schedule.drug.amount_per_dose,
                    dependency_type=schedule.dependency_type.value,
                    scheduled_time=scheduled_time.isoformat(),
                )
            )

    return notifications


@router.get("/notifications/stream")
async def stream_notifications() -> StreamingResponse:
    """Stream notifications via Server-Sent Events (SSE).

    Consumes from RabbitMQ queue and streams notifications to clients in real-time.
    Uses Pydantic models for validation and type safety.
    """
    logger.info("GET /notifications/stream - client connected")

    async def event_generator() -> AsyncIterator[str]:
        try:
            queue = await get_notifications_queue()
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    try:
                        # Deserialize JSON to Pydantic object (validates)
                        notification = NotificationDto.model_validate_json(
                            message.body.decode()
                        )

                        # Serialize Pydantic object to JSON for SSE
                        json_data = notification.model_dump_json()
                        yield f"data: {json_data}\n\n"

                        # Acknowledge message after successful delivery
                        await message.ack()
                        logger.info(
                            f"Streamed notification for {notification.drug_name} "
                            f"(schedule_id={notification.schedule_id})"
                        )

                    except ValidationError as e:
                        # Handle invalid data
                        logger.error(f"Invalid notification data: {e}")
                        await message.nack(requeue=False)
                    except Exception as e:
                        logger.error(f"Error processing message: {e}", exc_info=True)
                        await message.nack(requeue=True)

        except Exception as e:
            logger.error(f"Error in SSE stream: {e}", exc_info=True)
            yield "data: {}\n\n"  # Send empty event to close connection

    return StreamingResponse(event_generator(), media_type="text/event-stream")


class SnoozeRequest(BaseModel):
    minutes: int = 10


def schedule_to_notification_dto(
    schedule: DrugSchedule, scheduled_time: datetime
) -> NotificationDto:
    """Helper function to convert a DrugSchedule to NotificationDto"""
    return NotificationDto(
        schedule_id=schedule.id,
        drug_id=schedule.drug_id,
        drug_name=schedule.drug.name,
        kind=schedule.drug.kind,
        amount_per_dose=schedule.drug.amount_per_dose,
        dependency_type=schedule.dependency_type.value,
        scheduled_time=scheduled_time.isoformat(),
    )


def calculate_drug_time_for_display(
    schedule: DrugSchedule, target_date: date
) -> datetime:
    """Calculate time for a drug based on its dependency type.

    This is a simplified version for display purposes (e.g., in dismiss response).
    For actual scheduling, use NotificationScheduler._calculate_drug_time.
    """
    if schedule.dependency_type == DependencyType.ABSOLUTE:
        if schedule.absolute_time is None:
            # Fallback for display
            return datetime.combine(target_date, time(9, 0))
        return datetime.combine(target_date, schedule.absolute_time)

    elif schedule.dependency_type == DependencyType.MEAL:
        if schedule.meal_schedule is None or schedule.meal_offset_minutes is None:
            return datetime.combine(target_date, time(9, 0))
        meal_time = schedule.meal_schedule.base_time
        base_time = datetime.combine(target_date, meal_time)
        # meal_offset_minutes is signed: negative = before, positive = after
        return base_time + timedelta(minutes=schedule.meal_offset_minutes)

    elif schedule.dependency_type == DependencyType.DRUG:
        if (
            schedule.depends_on_schedule_id is None
            or schedule.depends_on_schedule is None
        ):
            return datetime.combine(target_date, time(9, 0))
        # Recursively calculate dependent schedule time
        dependent_time = calculate_drug_time_for_display(
            schedule.depends_on_schedule, target_date
        )
        if schedule.drug_offset_minutes is None:
            return dependent_time
        return dependent_time + timedelta(minutes=schedule.drug_offset_minutes)

    else:
        # Unknown dependency type: use default time
        return datetime.combine(target_date, time(9, 0))  # type: ignore[unreachable]


@router.post("/notifications/{schedule_id}/snooze")
async def snooze_notification(
    schedule_id: int,
    payload: SnoozeRequest,
    db: Session = Depends(get_db),
    scheduler: NotificationScheduler = Depends(get_notification_scheduler),
) -> SnoozeResponse:
    logger.info(
        "POST /notifications/%d/snooze - minutes=%d", schedule_id, payload.minutes
    )

    schedule = (
        db.query(DrugSchedule)
        .filter(DrugSchedule.id == schedule_id, DrugSchedule.is_active)
        .first()
    )
    if not schedule:
        logger.error("Schedule %d not found", schedule_id)
        raise HTTPException(status_code=404, detail="Schedule not found")
    # Base time is absolute_time for now
    if (
        schedule.dependency_type != DependencyType.ABSOLUTE
        or schedule.absolute_time is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Snooze supported only for absolute notifications currently",
        )
    today = date.today()

    # Check if override already exists for this schedule and date
    existing_override = (
        db.query(NotificationOverride)
        .filter(
            NotificationOverride.schedule_id == schedule.id,
            NotificationOverride.override_date == today,
        )
        .first()
    )

    logger.info("Existing override check: %s", existing_override is not None)

    # Check if existing override is valid (not too old/stale)
    # If absolute_time was edited, overrides should have been cleared, but this is a safety check
    if existing_override and existing_override.snoozed_until:
        # Check if the existing snooze is reasonable (not way in the past, which would indicate stale data)
        # If snoozed_until is more than 24 hours in the past, it's likely stale and we should reset
        now = datetime.now()
        if existing_override.snoozed_until < now - timedelta(hours=24):
            logger.warning(
                "Existing override appears stale (snoozed_until=%s), resetting to original time",
                existing_override.snoozed_until,
            )
            # Delete the stale override and start fresh
            db.delete(existing_override)
            existing_override = None
            base_dt = datetime.combine(today, schedule.absolute_time)
            logger.info(
                "Starting from original time after clearing stale override: base_dt=%s",
                base_dt,
            )
        else:
            # If there's already a valid snooze, add to the existing snoozed_until time
            if existing_override.snoozed_until is None:
                base_dt = datetime.combine(today, schedule.absolute_time)
            else:
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
        existing_override.created_at = datetime.now(UTC)
        logger.info("Updated existing override in database")
    else:
        # Create new override
        ov = NotificationOverride(
            schedule_id=schedule.id,
            override_date=today,
            snoozed_until=snoozed_until,
            dismissed=False,
        )
        db.add(ov)
        logger.info("Created new override in database")

    # Update Redis ZSET with new snoozed time (critical - must succeed)
    await scheduler.reschedule_notification(schedule_id, snoozed_until, today)

    logger.info(
        "Snooze saved successfully: schedule_id=%d, snoozed_until=%s",
        schedule_id,
        snoozed_until.isoformat(),
    )

    # Create notification DTO with the snoozed time
    notification = schedule_to_notification_dto(schedule, snoozed_until)
    return SnoozeResponse(
        notification=notification, snoozed_until=snoozed_until.isoformat()
    )


@router.post("/notifications/{schedule_id}/dismiss")
async def dismiss_notification(
    schedule_id: int,
    db: Session = Depends(get_db),
    scheduler: NotificationScheduler = Depends(get_notification_scheduler),
) -> DismissResponse:
    schedule = (
        db.query(DrugSchedule)
        .filter(DrugSchedule.id == schedule_id, DrugSchedule.is_active)
        .first()
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    today = date.today()
    # Check if override already exists for this schedule and date
    existing_override = (
        db.query(NotificationOverride)
        .filter(
            NotificationOverride.schedule_id == schedule.id,
            NotificationOverride.override_date == today,
        )
        .first()
    )

    # Calculate the scheduled time for the notification
    # If there's a snoozed_until, use that (it was the time shown)
    # Otherwise, calculate from the schedule
    if existing_override and existing_override.snoozed_until:
        scheduled_time = existing_override.snoozed_until
    else:
        # Calculate using helper function
        scheduled_time = calculate_drug_time_for_display(schedule, today)

    if existing_override:
        # Update existing override to dismissed
        existing_override.dismissed = True
        existing_override.snoozed_until = None
        existing_override.created_at = datetime.now(UTC)
    else:
        # Create new dismissed override
        ov = NotificationOverride(
            schedule_id=schedule.id, override_date=today, dismissed=True
        )
        db.add(ov)

    # Remove from Redis ZSET (critical - must succeed)
    await scheduler.dismiss_notification(schedule_id, today)

    # Create notification DTO
    notification = schedule_to_notification_dto(schedule, scheduled_time)
    return DismissResponse(notification=notification)
