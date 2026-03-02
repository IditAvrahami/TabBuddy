from __future__ import annotations

import logging
from datetime import date, datetime, timedelta

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    DependencyType,
    DrugSchedule,
    NotificationOverride,
)
from backend.schemas import NotificationDto
from backend.services.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """Service for scheduling notifications in Redis using two-level structure:
    - Index ZSET: notifications:{date} with scores (timestamps) and values (data key references)
    - Data keys: notification:{schedule_id}:{date} with actual notification JSON
    """

    def __init__(self, db_session: Session, redis_client: Redis):  # type: ignore[type-arg]
        self.db: Session = db_session
        self.redis_client: Redis = redis_client  # type: ignore[type-arg]

    def _get_index_key(self, target_date: date) -> str:
        """Get the index ZSET key for a date"""
        return f"notifications:{target_date.isoformat()}"

    def _get_notification_key(self, schedule_id: int, target_date: date) -> str:
        """Get the data key for a specific schedule notification"""
        return f"notification:{schedule_id}:{target_date.isoformat()}"

    def _calculate_drug_time(
        self, schedule: DrugSchedule, target_date: date
    ) -> datetime:
        """Calculate time for a drug based on its dependency type

        Raises:
            ValueError: If required fields are missing for the dependency type
            AssertionError: If null checks fail
        """
        if schedule.dependency_type == DependencyType.ABSOLUTE:
            # Absolute time: take at specific time
            assert (
                schedule.absolute_time is not None
            ), f"absolute_time is required for ABSOLUTE dependency type (schedule_id={schedule.id})"
            return datetime.combine(target_date, schedule.absolute_time)

        elif schedule.dependency_type == DependencyType.MEAL:
            # Meal dependency: take before/after meal
            # meal_offset_minutes is signed: negative = before, positive = after
            assert (
                schedule.meal_schedule is not None
            ), f"meal_schedule is required for MEAL dependency type (schedule_id={schedule.id})"
            assert (
                schedule.meal_offset_minutes is not None
            ), f"meal_offset_minutes is required for MEAL dependency type (schedule_id={schedule.id})"

            meal_time = schedule.meal_schedule.base_time
            base_time = datetime.combine(target_date, meal_time)
            # Always add the offset (negative values = before, positive = after)
            return base_time + timedelta(minutes=schedule.meal_offset_minutes)

        elif schedule.dependency_type == DependencyType.DRUG:
            # Drug dependency: take after/before another schedule
            assert (
                schedule.depends_on_schedule is not None
            ), f"depends_on_schedule is required for DRUG dependency type (schedule_id={schedule.id})"
            assert (
                schedule.drug_offset_minutes is not None
            ), f"drug_offset_minutes is required for DRUG dependency type (schedule_id={schedule.id})"

            dependent_schedule = schedule.depends_on_schedule
            base_time = self._calculate_drug_time(dependent_schedule, target_date)
            return base_time + timedelta(minutes=schedule.drug_offset_minutes)

        else:
            raise ValueError(
                f"Unknown dependency type: {schedule.dependency_type} (schedule_id={schedule.id})"
            )

    async def schedule_notification(
        self, schedule_id: int, target_date: date | None = None
    ) -> None:
        """Calculate and store one notification for a schedule on a specific date.

        Args:
            schedule_id: The drug schedule ID
            target_date: The date to schedule for (defaults to today)
        """
        if target_date is None:
            target_date = date.today()

        schedule = (
            self.db.query(DrugSchedule)
            .filter(DrugSchedule.id == schedule_id, DrugSchedule.is_active)
            .first()
        )

        if not schedule:
            logger.warning(f"Schedule {schedule_id} not found or inactive")
            return

        # Check date range
        if schedule.start_date > target_date:
            logger.info(f"Schedule {schedule_id} starts after {target_date}, skipping")
            return
        if schedule.end_date is not None and schedule.end_date < target_date:
            logger.info(f"Schedule {schedule_id} ended before {target_date}, skipping")
            return

        # Calculate time for THIS schedule based on its dependency type
        try:
            calculated_time = self._calculate_drug_time(schedule, target_date)
        except (AssertionError, ValueError) as e:
            logger.warning(
                f"Cannot schedule notification for schedule_id={schedule_id}: {e}"
            )
            return

        # Check for notification overrides (snooze/dismiss)
        override = (
            self.db.query(NotificationOverride)
            .filter(
                NotificationOverride.schedule_id == schedule.id,
                NotificationOverride.override_date == target_date,
            )
            .order_by(NotificationOverride.id.desc())
            .first()
        )

        if override:
            if override.dismissed:
                logger.info(
                    f"Notification for schedule {schedule_id} on {target_date} is dismissed, skipping"
                )
                return
            if override.snoozed_until:
                calculated_time = override.snoozed_until

        # Create notification
        notification = NotificationDto(
            schedule_id=schedule.id,
            drug_id=schedule.drug_id,
            drug_name=schedule.drug.name,
            scheduled_time=calculated_time.isoformat(),
            dependency_type=schedule.dependency_type.value,
            amount_per_dose=schedule.drug.amount_per_dose,
            kind=schedule.drug.kind,
        )

        # Store in two-level structure
        index_key = self._get_index_key(target_date)
        data_key = self._get_notification_key(schedule_id, target_date)
        notification_json = notification.model_dump_json()
        score = calculated_time.timestamp()

        # 1. Store actual notification data
        await self.redis_client.set(data_key, notification_json)
        await self.redis_client.expire(data_key, 2 * 24 * 60 * 60)  # 2 days TTL

        # 2. Add reference to index ZSET (data_key as value, timestamp as score)
        await self.redis_client.zadd(index_key, {data_key: score})

        logger.info(
            f"Scheduled notification for {notification.drug_name} "
            f"(schedule_id={schedule_id}) at {notification.scheduled_time}"
        )

    async def unschedule_notification(
        self, schedule_id: int, target_date: date | None = None
    ) -> None:
        """Remove one notification for a schedule on a specific date - O(1) operations!

        Args:
            schedule_id: The drug schedule ID
            target_date: The date to unschedule for (defaults to today)
        """
        if target_date is None:
            target_date = date.today()

        index_key = self._get_index_key(target_date)
        data_key = self._get_notification_key(schedule_id, target_date)

        # 1. Remove from index ZSET (by value - the data key reference)
        removed_from_index = await self.redis_client.zrem(index_key, data_key)

        # 2. Delete the data key
        deleted_data = await self.redis_client.delete(data_key)

        if removed_from_index or deleted_data:
            logger.info(
                f"Removed notification for schedule_id={schedule_id} on {target_date}"
            )

    async def reschedule_notification(
        self, schedule_id: int, new_time: datetime, target_date: date | None = None
    ) -> None:
        """Update notification time for snooze.

        Args:
            schedule_id: The drug schedule ID
            new_time: The new scheduled time
            target_date: The date (defaults to today)
        """
        if target_date is None:
            target_date = date.today()

        # Get schedule to create new notification
        schedule = (
            self.db.query(DrugSchedule)
            .filter(DrugSchedule.id == schedule_id, DrugSchedule.is_active)
            .first()
        )

        if not schedule:
            logger.warning(f"Schedule {schedule_id} not found for reschedule")
            return

        # Create new notification with updated time
        notification = NotificationDto(
            schedule_id=schedule.id,
            drug_id=schedule.drug_id,
            drug_name=schedule.drug.name,
            scheduled_time=new_time.isoformat(),
            dependency_type=schedule.dependency_type.value,
            amount_per_dose=schedule.drug.amount_per_dose,
            kind=schedule.drug.kind,
        )

        index_key = self._get_index_key(target_date)
        data_key = self._get_notification_key(schedule_id, target_date)
        notification_json = notification.model_dump_json()
        new_score = new_time.timestamp()

        # 1. Update data
        await self.redis_client.set(data_key, notification_json)
        await self.redis_client.expire(data_key, 2 * 24 * 60 * 60)

        # 2. Update index (remove old entry, add new with new score)
        await self.redis_client.zrem(index_key, data_key)
        await self.redis_client.zadd(index_key, {data_key: new_score})

        logger.info(
            f"Rescheduled notification for {notification.drug_name} "
            f"(schedule_id={schedule_id}) to {new_time.isoformat()}"
        )

    async def dismiss_notification(
        self, schedule_id: int, target_date: date | None = None
    ) -> None:
        """Remove notification from Redis (dismissed).

        Args:
            schedule_id: The drug schedule ID
            target_date: The date (defaults to today)
        """
        await self.unschedule_notification(schedule_id, target_date)
        logger.info(
            f"Dismissed notification for schedule_id={schedule_id} on {target_date}"
        )

    async def reschedule_schedule(self, schedule_id: int) -> None:
        """Reschedule notifications for a schedule after it was updated.

        This unschedules old notifications and schedules new ones based on the current
        schedule configuration. Handles scheduling for start_date and today if applicable.

        Args:
            schedule_id: The drug schedule ID to reschedule
        """
        schedule = (
            self.db.query(DrugSchedule)
            .filter(DrugSchedule.id == schedule_id, DrugSchedule.is_active)
            .first()
        )

        if not schedule:
            logger.warning(
                f"Schedule {schedule_id} not found or inactive for reschedule"
            )
            return

        # Unschedule old notification for today (most common case)
        # We'll reschedule for the dates that matter
        await self.unschedule_notification(schedule_id)

        # Schedule new notification for start_date
        await self.schedule_notification(schedule_id, schedule.start_date)

        # Also schedule for today if applicable
        today = date.today()
        if schedule.start_date <= today and (
            schedule.end_date is None or schedule.end_date >= today
        ):
            await self.schedule_notification(schedule_id, today)

        logger.info(f"Rescheduled notifications for schedule_id={schedule_id}")

    async def schedule_all_for_date(self, target_date: date) -> None:
        """Schedule all active notifications for a given date.

        Args:
            target_date: The date to schedule notifications for
        """
        # Get all active schedules
        schedules = (
            self.db.query(DrugSchedule)
            .filter(
                DrugSchedule.start_date <= target_date,
                (DrugSchedule.end_date >= target_date)
                | (DrugSchedule.end_date.is_(None)),
                DrugSchedule.is_active,
            )
            .all()
        )

        logger.info(
            f"Scheduling notifications for {len(schedules)} schedules on {target_date}"
        )

        for schedule in schedules:
            await self.schedule_notification(schedule.id, target_date)


def get_notification_scheduler(
    db: Session = Depends(get_db),
    redis_client: Redis = Depends(get_redis_client),  # type: ignore[type-arg]
) -> NotificationScheduler:
    """Dependency to get NotificationScheduler instance"""
    return NotificationScheduler(db, redis_client)
