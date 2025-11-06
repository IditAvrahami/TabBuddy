import enum
import logging
from datetime import UTC, date, datetime, time

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    object_session,
    relationship,
)

from .database import Base

__all__ = [
    "Base",
    "DependencyType",
    "DrugORM",
    "DrugSchedule",
    "MealSchedule",
    "NotificationOverride",
]

logger = logging.getLogger(__name__)


# Enum for dependency types
class DependencyType(enum.Enum):
    DRUG = "drug"  # Depends on another drug
    MEAL = "meal"  # Depends on meal time
    ABSOLUTE = "absolute"  # Absolute time
    INDEPENDENT = "independent"  # No dependencies


# Core drug information
class DrugORM(Base):
    __tablename__ = "drugs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    amount_per_dose: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    schedules: Mapped[list["DrugSchedule"]] = relationship(
        "DrugSchedule",
        foreign_keys="[DrugSchedule.drug_id]",
        back_populates="drug",
        cascade="all, delete-orphan",
    )
    dependent_schedules: Mapped[list["DrugSchedule"]] = relationship(
        "DrugSchedule",
        foreign_keys="[DrugSchedule.depends_on_drug_id]",
        back_populates="depends_on_drug",
        cascade="all, delete-orphan",
    )

    @property
    def duration(self) -> int | None:
        """Computed duration in days from the active schedule (inclusive),
        or None if open-ended or missing dates. For backward compatibility with tests.
        """
        session = object_session(self)
        if session is None:
            return None
        sched = (
            session.query(DrugSchedule)
            .filter(DrugSchedule.drug_id == self.id, DrugSchedule.is_active)
            .first()
        )
        if not sched or sched.end_date is None:
            return None
        return (sched.end_date - sched.start_date).days + 1

    @property
    def amount_per_day(self) -> int | None:
        """Computed alias for legacy field, mapped from schedule.frequency_per_day."""
        session = object_session(self)
        if session is None:
            return None
        sched = (
            session.query(DrugSchedule)
            .filter(DrugSchedule.drug_id == self.id, DrugSchedule.is_active)
            .first()
        )
        if not sched:
            return None
        return sched.frequency_per_day


# Meal schedules
class MealSchedule(Base):
    __tablename__ = "meal_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    meal_name: Mapped[str] = mapped_column(String(50), nullable=False)
    base_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )

    # Relationships
    drug_schedules: Mapped[list["DrugSchedule"]] = relationship(
        "DrugSchedule", back_populates="meal_schedule", cascade="all, delete-orphan"
    )


# Drug schedules with flexible dependency system
class DrugSchedule(Base):
    __tablename__ = "drug_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    drug_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("drugs.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    # Dependency configuration
    dependency_type: Mapped[DependencyType] = mapped_column(
        Enum(DependencyType), nullable=False, default=DependencyType.INDEPENDENT
    )

    # For DRUG dependency
    depends_on_drug_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("drugs.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    drug_offset_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # Minutes after/before dependent drug

    # For MEAL dependency
    meal_schedule_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("meal_schedules.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=True,
    )
    meal_offset_minutes: Mapped[int | None] = mapped_column(
        Integer, nullable=True
    )  # Minutes before/after meal
    meal_timing: Mapped[str | None] = mapped_column(
        String(10), nullable=True
    )  # 'before' or 'after'

    # For ABSOLUTE dependency
    absolute_time: Mapped[time | None] = mapped_column(
        Time, nullable=True
    )  # Specific time of day

    # Schedule properties
    frequency_per_day: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )

    # Relationships
    drug: Mapped["DrugORM"] = relationship(
        "DrugORM", foreign_keys=[drug_id], back_populates="schedules"
    )
    depends_on_drug: Mapped["DrugORM | None"] = relationship(
        "DrugORM",
        foreign_keys=[depends_on_drug_id],
        back_populates="dependent_schedules",
    )
    meal_schedule: Mapped["MealSchedule | None"] = relationship(
        "MealSchedule", back_populates="drug_schedules"
    )
    notification_overrides: Mapped[list["NotificationOverride"]] = relationship(
        "NotificationOverride", back_populates="schedule", cascade="all, delete-orphan"
    )


# Notification overrides for snooze/dismiss
class NotificationOverride(Base):
    __tablename__ = "notification_overrides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    schedule_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("drug_schedules.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        index=True,
    )
    override_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    snoozed_until: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    dismissed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None)
    )

    schedule: Mapped["DrugSchedule"] = relationship(
        "DrugSchedule", back_populates="notification_overrides"
    )
