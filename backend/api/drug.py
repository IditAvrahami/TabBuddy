import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from datetime import date, time, datetime, timedelta, UTC
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.models import DrugORM, DrugSchedule, MealSchedule, DependencyType, NotificationOverride
import time as time_module

logger = logging.getLogger(__name__)
router = APIRouter()

# Timezone conversion removed - now handled in frontend

class DrugCreateCompat(BaseModel):
    # Core
    name: str = Field(..., description="Drug name")
    kind: str = Field(..., pattern="^(pill|liquid)$", description="pill or liquid")
    amount_per_dose: int = Field(..., description="Amount per dose")

    # New scheduling fields (preferred)
    dependency_type: str | None = Field('independent', description="absolute|meal|drug|independent")
    frequency_per_day: int | None = Field(None, description="Times per day (ignored for absolute)")
    start_date: date | None = Field(None, description="Start date")
    end_date: date | None = Field(None, description="End date (optional)")
    absolute_time: time | None = Field(None, description="Absolute time (for absolute dependency)")
    meal_schedule_id: int | None = Field(None, description="Meal schedule ID (for meal dependency)")
    meal_offset_minutes: int | None = Field(None, description="Minutes before/after meal")
    meal_timing: str | None = Field(None, description="before or after meal")
    depends_on_drug_id: int | None = Field(None, description="Drug ID to depend on (for drug dependency)")
    drug_offset_minutes: int | None = Field(None, description="Minutes after dependent drug")

    # Legacy fields (for backward compatibility with tests/UI)
    duration: int | None = Field(None, description="Legacy: duration in days")
    amount_per_day: int | None = Field(None, description="Legacy: frequency per day")

class DrugResponse(BaseModel):
    id: int
    name: str
    kind: str
    amount_per_dose: int
    frequency_per_day: int
    start_date: date
    end_date: date | None
    duration: int | None = None
    amount_per_day: int | None = None
    dependency_type: str
    absolute_time: time | None
    meal_schedule_id: int | None
    meal_offset_minutes: int | None
    meal_timing: str | None
    depends_on_drug_id: int | None
    drug_offset_minutes: int | None
    is_active: bool
    created_at: datetime | None
    
    model_config = ConfigDict()
    
    @field_serializer('absolute_time')
    def serialize_time(self, value: time | None) -> str | None:
        return value.isoformat() if value else None

class MealScheduleResponse(BaseModel):
    id: int
    meal_name: str
    base_time: time
    is_active: bool

def schedule_to_response(schedule: DrugSchedule) -> DrugResponse:
    """Helper function to convert a DrugSchedule to DrugResponse"""
    return DrugResponse(
        id=schedule.id,
        name=schedule.drug.name,
        kind=schedule.drug.kind,
        amount_per_dose=schedule.drug.amount_per_dose,
        frequency_per_day=schedule.frequency_per_day,
        start_date=schedule.start_date,
        end_date=schedule.end_date,
        duration=(
            (schedule.end_date - schedule.start_date).days + 1
            if schedule.start_date and schedule.end_date
            else None
        ),
        amount_per_day=schedule.frequency_per_day,
        dependency_type=schedule.dependency_type.value,
        absolute_time=schedule.absolute_time,
        meal_schedule_id=schedule.meal_schedule_id,
        meal_offset_minutes=schedule.meal_offset_minutes,
        meal_timing=schedule.meal_timing,
        depends_on_drug_id=schedule.depends_on_drug_id,
        drug_offset_minutes=schedule.drug_offset_minutes,
        is_active=schedule.is_active,
            created_at=schedule.created_at or datetime.now(UTC),
    )

@router.post("/drug")
def add_drug(drug: DrugCreateCompat, db: Session = Depends(get_db)) -> DrugResponse:
    logger.info("POST /drug payload=%s", drug.model_dump())
    
    # Debug timezone conversion
    if drug.absolute_time:
        logger.info("🔧 Backend Timezone Debug:")
        logger.info(f"  Received absolute_time: {drug.absolute_time}")
        logger.info(f"  Type: {type(drug.absolute_time)}")
        logger.info(f"  String representation: {str(drug.absolute_time)}")
    
    # Check if drug already exists
    existing_drug = db.query(DrugORM).filter(DrugORM.name == drug.name).first()
    if existing_drug:
        logger.warning("POST /drug duplicate name=%s", drug.name)
        raise HTTPException(status_code=400, detail="Drug already exists")
    
    # Create drug row
    drug_orm = DrugORM(
        name=drug.name,
        kind=drug.kind,
        amount_per_dose=drug.amount_per_dose,
    )
    db.add(drug_orm)
    db.flush()  # Get the drug ID
    
    # Compute schedule attributes (new or legacy mapping)
    dep_type_str = drug.dependency_type or 'independent'
    # Legacy mapping: if duration/amount_per_day provided and new fields absent
    if drug.duration is not None and drug.amount_per_day is not None and drug.start_date is None:
        start_date = date.today()
        end_date = start_date + timedelta(days=max(0, drug.duration - 1))
        frequency_per_day = drug.amount_per_day
        absolute_time = None
        dependency_type = DependencyType('independent')
    else:
        start_date = drug.start_date or date.today()
        end_date = drug.end_date
        frequency_per_day = (1 if dep_type_str == 'absolute' else (drug.frequency_per_day or 1))
        # Frontend now sends UTC time directly
        absolute_time = drug.absolute_time
        dependency_type = DependencyType(dep_type_str)
    schedule = DrugSchedule(
        drug_id=drug_orm.id,
        dependency_type=dependency_type,
        frequency_per_day=frequency_per_day,
        start_date=start_date,
        end_date=end_date,
        absolute_time=absolute_time,
        meal_schedule_id=drug.meal_schedule_id,
        meal_offset_minutes=drug.meal_offset_minutes,
        meal_timing=drug.meal_timing,
        depends_on_drug_id=drug.depends_on_drug_id,
        drug_offset_minutes=drug.drug_offset_minutes,
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)  # Refresh to get the latest data
    
    logger.info("POST /drug success name=%s", drug.name)
    return schedule_to_response(schedule)

@router.get("/drug")
def get_all_drugs(db: Session = Depends(get_db)) -> list[DrugResponse]:
    logger.info("GET /drug")
    schedules = db.query(DrugSchedule).filter(DrugSchedule.is_active == True).all()
    
    items = []
    for schedule in schedules:
        # Debug timezone conversion
        if schedule.absolute_time and "Timezone" in schedule.drug.name:
            logger.info(f"🔧 GET /drug Timezone Debug:")
            logger.info(f"  Drug name: {schedule.drug.name}")
            logger.info(f"  DB absolute_time: {schedule.absolute_time}")
            logger.info(f"  Type: {type(schedule.absolute_time)}")
            logger.info(f"  String: {str(schedule.absolute_time)}")
        
        items.append(schedule_to_response(schedule))
    
    logger.info("GET /drug count=%d", len(items))
    return items

@router.put("/drug-id/{drug_id}")
def update_drug(drug_id: int, drug: DrugCreateCompat, db: Session = Depends(get_db)) -> DrugResponse:
    logger.info("PUT /drug/%d payload=%s", drug_id, drug.model_dump())
    
    schedule = db.query(DrugSchedule).filter(DrugSchedule.id == drug_id).first()
    if not schedule:
        logger.warning("PUT /drug schedule not found id=%d", drug_id)
        raise HTTPException(status_code=404, detail="Drug schedule not found")
    
    # Update drug info
    schedule.drug.name = drug.name
    schedule.drug.kind = drug.kind
    schedule.drug.amount_per_dose = drug.amount_per_dose
    
    # Store old absolute_time to detect changes
    old_absolute_time = schedule.absolute_time
    absolute_time_changed = False
    
    # Update schedule info
    dep_type_str = drug.dependency_type or schedule.dependency_type.value
    schedule.dependency_type = DependencyType(dep_type_str)
    # Legacy mapping for update: if only legacy provided
    if drug.duration is not None and drug.amount_per_day is not None and drug.start_date is None:
        schedule.start_date = date.today()
        schedule.end_date = schedule.start_date + timedelta(days=max(0, drug.duration - 1))
        schedule.frequency_per_day = drug.amount_per_day
        # If absolute_time is being removed (set to None), mark as changed
        if old_absolute_time is not None:
            absolute_time_changed = True
        schedule.absolute_time = None
    else:
        if drug.frequency_per_day is not None:
            schedule.frequency_per_day = (1 if dep_type_str == 'absolute' else drug.frequency_per_day)
        if drug.start_date is not None:
            schedule.start_date = drug.start_date
        if drug.end_date is not None:
            schedule.end_date = drug.end_date
        if drug.absolute_time is not None:
            # Check if absolute_time is actually changing
            if old_absolute_time != drug.absolute_time:
                absolute_time_changed = True
                logger.info("Absolute time changed from %s to %s for schedule %d", old_absolute_time, drug.absolute_time, schedule.id)
            # Frontend now sends UTC time directly
            schedule.absolute_time = drug.absolute_time
    schedule.meal_schedule_id = drug.meal_schedule_id
    schedule.meal_offset_minutes = drug.meal_offset_minutes
    schedule.meal_timing = drug.meal_timing
    schedule.depends_on_drug_id = drug.depends_on_drug_id
    schedule.drug_offset_minutes = drug.drug_offset_minutes
    
    # If absolute_time changed, clear notification overrides for today and future dates
    # This prevents snooze mechanism from using old times
    if absolute_time_changed:
        today = date.today()
        logger.info("Absolute time changed for schedule %d, clearing notification overrides for today and future dates", schedule.id)
        # Delete all notification overrides (snoozes and dismissals) for this schedule from today onwards
        # This ensures the next snooze will use the new absolute_time
        deleted_count = db.query(NotificationOverride).filter(
            NotificationOverride.schedule_id == schedule.id,
            NotificationOverride.override_date >= today
        ).delete()
        logger.info("Cleared %d notification override(s) for schedule %d", deleted_count, schedule.id)
    
    db.commit()
    db.refresh(schedule)  # Refresh to get the latest data
    logger.info("PUT /drug/%d success name=%s", drug_id, drug.name)
    return schedule_to_response(schedule)

@router.delete("/drug-id/{drug_id}")
def delete_drug(drug_id: int, db: Session = Depends(get_db)) -> DrugResponse:
    logger.info("DELETE /drug/%d", drug_id)
    
    schedule = db.query(DrugSchedule).filter(DrugSchedule.id == drug_id).first()
    if not schedule:
        logger.warning("DELETE /drug schedule not found id=%d", drug_id)
        raise HTTPException(status_code=404, detail="Drug schedule not found")
    
    # Create response before deleting
    response = schedule_to_response(schedule)
    
    # Delete the schedule and its drug (for compatibility with tests expecting row removal)
    db.delete(schedule)
    # Also delete the drug row
    db.delete(schedule.drug)
    db.commit()
    
    logger.info("DELETE /drug/%d success", drug_id)
    return response

# Compatibility endpoints using name instead of id
@router.put("/drug/{name}")
def update_drug_by_name(name: str, drug: DrugCreateCompat, db: Session = Depends(get_db)) -> DrugResponse:
    logger.info("PUT /drug/%s payload=%s", name, drug.model_dump())
    schedule = db.query(DrugSchedule).join(DrugSchedule.drug).filter(DrugSchedule.is_active == True, DrugORM.name == name).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Drug not found")
    return update_drug(schedule.id, drug, db)

@router.delete("/drug/{name}")
def delete_drug_by_name(name: str, db: Session = Depends(get_db)) -> DrugResponse:
    logger.info("DELETE /drug/%s", name)
    schedule = db.query(DrugSchedule).join(DrugSchedule.drug).filter(DrugORM.name == name).first()
    if not schedule:
        # Fallback: if 'name' looks like an integer id, try deleting by id
        try:
            schedule_id = int(name)
            schedule = db.query(DrugSchedule).filter(DrugSchedule.id == schedule_id).first()
            if not schedule:
                raise HTTPException(status_code=404, detail="Drug not found")
            return delete_drug(schedule.id, db)
        except ValueError:
            raise HTTPException(status_code=404, detail="Drug not found")
    return delete_drug(schedule.id, db)

# ID-based deletion kept for compatibility with tests calling /drug/{id}
@router.delete("/drug/{schedule_id}")
def delete_drug_by_id_compat(schedule_id: int, db: Session = Depends(get_db)) -> DrugResponse:
    logger.info("DELETE /drug/%d", schedule_id)
    schedule = db.query(DrugSchedule).filter(DrugSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Drug not found")
    return delete_drug(schedule.id, db)

# NOTE: Meal schedule endpoints are defined in backend.api.meal; duplicates removed here.
