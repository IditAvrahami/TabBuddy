from sqlalchemy.orm import Session
from datetime import datetime, time, timedelta, date as date_type
from pydantic import BaseModel

from backend.models import DrugSchedule, DependencyType, NotificationOverride


class TimelineItem(BaseModel):
    """Pydantic model for timeline items returned by TimelineCalculator"""
    schedule_id: int
    drug_id: int
    drug_name: str
    scheduled_time: datetime
    dependency_type: str
    amount_per_dose: int
    kind: str


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

