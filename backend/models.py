from sqlalchemy import Column, Integer, String, Time, Date, DateTime, Boolean, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship, Session
from sqlalchemy.orm import object_session
from sqlalchemy.sql import func
from .database import Base
from datetime import datetime, time, timedelta, date as date_type, UTC
from pydantic import BaseModel
import enum
import logging

logger = logging.getLogger(__name__)

# Enum for dependency types
class DependencyType(enum.Enum):
    DRUG = "drug"           # Depends on another drug
    MEAL = "meal"           # Depends on meal time
    ABSOLUTE = "absolute"   # Absolute time
    INDEPENDENT = "independent"  # No dependencies

# Core drug information
class DrugORM(Base):
    __tablename__ = 'drugs'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    kind = Column(String, nullable=False)
    amount_per_dose = Column(Integer, nullable=False)

    # Relationships
    schedules = relationship("DrugSchedule", foreign_keys="[DrugSchedule.drug_id]", back_populates="drug", cascade="all, delete-orphan")
    dependent_schedules = relationship("DrugSchedule", foreign_keys="[DrugSchedule.depends_on_drug_id]", back_populates="depends_on_drug", cascade="all, delete-orphan")

    @property
    def duration(self) -> int | None:
        """Computed duration in days from the active schedule (inclusive),
        or None if open-ended or missing dates. For backward compatibility with tests."""
        session = object_session(self)
        if session is None:
            return None
        sched = (
            session.query(DrugSchedule)
            .filter(DrugSchedule.drug_id == self.id, DrugSchedule.is_active == True)
            .first()
        )
        if not sched or not sched.start_date or not sched.end_date:
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
            .filter(DrugSchedule.drug_id == self.id, DrugSchedule.is_active == True)
            .first()
        )
        if not sched:
            return None
        return sched.frequency_per_day

# Meal schedules
class MealSchedule(Base):
    __tablename__ = 'meal_schedules'
    
    id = Column(Integer, primary_key=True, index=True)
    meal_name = Column(String(50), nullable=False)
    base_time = Column(Time, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))

    # Relationships
    drug_schedules = relationship("DrugSchedule", back_populates="meal_schedule", cascade="all, delete-orphan")

# Drug schedules with flexible dependency system
class DrugSchedule(Base):
    __tablename__ = 'drug_schedules'
    
    id = Column(Integer, primary_key=True, index=True)
    drug_id = Column(Integer, ForeignKey('drugs.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    
    # Dependency configuration
    dependency_type = Column(Enum(DependencyType), nullable=False, default=DependencyType.INDEPENDENT)
    
    # For DRUG dependency
    depends_on_drug_id = Column(Integer, ForeignKey('drugs.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    drug_offset_minutes = Column(Integer, nullable=True)  # Minutes after/before dependent drug
    
    # For MEAL dependency
    meal_schedule_id = Column(Integer, ForeignKey('meal_schedules.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    meal_offset_minutes = Column(Integer, nullable=True)  # Minutes before/after meal
    meal_timing = Column(String(10), nullable=True)  # 'before' or 'after'
    
    # For ABSOLUTE dependency
    absolute_time = Column(Time, nullable=True)  # Specific time of day
    
    # Schedule properties
    frequency_per_day = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))
    
    # Relationships
    drug = relationship("DrugORM", foreign_keys=[drug_id], back_populates="schedules")
    depends_on_drug = relationship("DrugORM", foreign_keys=[depends_on_drug_id], back_populates="dependent_schedules")
    meal_schedule = relationship("MealSchedule", back_populates="drug_schedules")
    notification_overrides = relationship("NotificationOverride", back_populates="schedule", cascade="all, delete-orphan")

# Notification overrides for snooze/dismiss
class NotificationOverride(Base):
    __tablename__ = 'notification_overrides'

    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey('drug_schedules.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    override_date = Column(Date, nullable=False, index=True)
    snoozed_until = Column(DateTime, nullable=True)
    dismissed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC).replace(tzinfo=None))

    schedule = relationship("DrugSchedule", back_populates="notification_overrides")


class TimelineItem(BaseModel):
    """Pydantic model for timeline items returned by TimelineCalculator"""
    schedule_id: int
    drug_id: int
    drug_name: str
    scheduled_time: datetime
    dependency_type: str
    amount_per_dose: int
    kind: str


# Timeline calculation service
class TimelineCalculator:
    def __init__(self, db_session: Session) -> None:
        self.db: Session = db_session
    
    def calculate_daily_timeline(self, date: date_type) -> list[TimelineItem]:
        """Calculate timeline for a specific date, returning only notifications ready to show now"""
        
        # Get all active drug schedules for the date
        schedules = self.db.query(DrugSchedule).filter(
            DrugSchedule.start_date <= date,
            (DrugSchedule.end_date >= date) | (DrugSchedule.end_date.is_(None)),
            DrugSchedule.is_active == True
        ).all()
        
        timeline = []
        drug_times = {}  # Cache for calculated times
        now = datetime.now()
        
        # Calculate times for each schedule
        for schedule in schedules:
            calculated_time = self._calculate_drug_time(schedule, date, drug_times)
            drug_times[schedule.drug_id] = calculated_time
            
            # Check for notification overrides (snooze/dismiss)
            override = self.db.query(NotificationOverride).filter(
                NotificationOverride.schedule_id == schedule.id,
                NotificationOverride.override_date == date
            ).order_by(NotificationOverride.id.desc()).first()
            
            if override:
                if override.dismissed:
                    continue
                if override.snoozed_until:
                    # Use the snoozed time as the notification time
                    calculated_time = override.snoozed_until
            
            # Only include notifications that are ready to show now (within a small window)
            time_diff = (calculated_time - now).total_seconds()   # seconds
            
            # Show notifications that are due now 
            if -60 <= time_diff <= 5 :
                timeline.append(TimelineItem(
                    schedule_id=schedule.id,
                    drug_id=schedule.drug_id,
                    drug_name=schedule.drug.name,
                    scheduled_time=calculated_time,
                    dependency_type=schedule.dependency_type.value,
                    amount_per_dose=schedule.drug.amount_per_dose,
                    kind=schedule.drug.kind
                ))
        
        # Sort by time
        timeline.sort(key=lambda x: x.scheduled_time)
        
        # Ensure each drug appears only once (deduplicate by drug_id)
        seen_drugs = set()
        unique_timeline = []
        for item in timeline:
            if item.drug_id not in seen_drugs:
                seen_drugs.add(item.drug_id)
                unique_timeline.append(item)
        
        return unique_timeline
    
    def _calculate_drug_time(self, schedule: DrugSchedule, date: date_type, drug_times: dict[int, datetime]) -> datetime:
        """Calculate time for a drug based on its dependency type"""
        
        if schedule.dependency_type == DependencyType.ABSOLUTE:
            # Absolute time: take at specific time
            if schedule.absolute_time is None:
                # Fallback if absolute_time is not set
                return datetime.combine(date, time(9, 0))
            return datetime.combine(date, schedule.absolute_time)
        
        elif schedule.dependency_type == DependencyType.MEAL:
            # Meal dependency: take before/after meal
            if schedule.meal_schedule is None or schedule.meal_offset_minutes is None:
                # Fallback if meal schedule or offset is not set
                return datetime.combine(date, time(9, 0))
            meal_time = schedule.meal_schedule.base_time
            base_time = datetime.combine(date, meal_time)
            
            if schedule.meal_timing == 'before':
                return base_time - timedelta(minutes=schedule.meal_offset_minutes)
            else:  # 'after'
                return base_time + timedelta(minutes=schedule.meal_offset_minutes)
        
        elif schedule.dependency_type == DependencyType.DRUG:
            # Drug dependency: take after/before another drug
            if schedule.depends_on_drug_id in drug_times:
                base_time = drug_times[schedule.depends_on_drug_id]
                if schedule.drug_offset_minutes is None:
                    # Fallback if offset is not set
                    return base_time
                return base_time + timedelta(minutes=schedule.drug_offset_minutes)
            else:
                # Dependent drug not calculated yet, use default time
                return datetime.combine(date, time(9, 0))
        
        else:  # INDEPENDENT
            # Independent: use default time
            return datetime.combine(date, time(9, 0))