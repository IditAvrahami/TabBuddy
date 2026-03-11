import logging
from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, field_serializer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import (
    DependencyType,
    DrugORM,
    DrugSchedule,
    NotificationOverride,
)
from backend.services.notification_scheduler import (
    NotificationScheduler,
    get_notification_scheduler,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Timezone conversion removed - now handled in frontend


class DrugCreateCompat(BaseModel):
    # Core
    name: str = Field(..., description="Drug name")
    kind: str = Field(..., pattern="^(pill|liquid)$", description="pill or liquid")
    amount_per_dose: int = Field(..., description="Amount per dose")

    # New scheduling fields (preferred)
    dependency_type: str = Field("absolute", description="absolute|meal|drug")
    start_date: date | None = Field(None, description="Start date")
    end_date: date | None = Field(None, description="End date (optional)")
    absolute_time: time | None = Field(
        None, description="Absolute time (for absolute dependency)"
    )
    meal_schedule_id: int | None = Field(
        None, description="Meal schedule ID (for meal dependency)"
    )
    meal_offset_minutes: int | None = Field(
        None,
        description="Signed minutes: negative = before meal, positive = after meal",
    )
    depends_on_schedule_id: int | None = Field(
        None, description="Schedule ID to depend on (for drug dependency)"
    )
    drug_offset_minutes: int | None = Field(
        None, description="Minutes after dependent schedule"
    )


class DrugResponse(BaseModel):
    id: int
    name: str
    kind: str
    amount_per_dose: int
    start_date: date
    end_date: date | None
    duration: int | None = None
    amount_per_day: int | None = None
    dependency_type: str
    absolute_time: time | None
    meal_schedule_id: int | None
    meal_offset_minutes: int | None
    depends_on_schedule_id: int | None
    drug_offset_minutes: int | None
    is_active: bool
    created_at: datetime | None

    model_config = ConfigDict()

    @field_serializer("absolute_time")
    def serialize_time(self, value: time | None) -> str | None:
        return value.isoformat() if value else None


class DependentSchedulePreview(BaseModel):
    schedule_id: int
    drug_name: str
    current_depends_on_name: str
    current_offset_minutes: int
    new_dependency_type: str
    new_depends_on_name: str | None
    new_offset_minutes: int
    new_absolute_time: str | None


class DependentsResponse(BaseModel):
    has_dependents: bool
    dependents: list[DependentSchedulePreview]


def schedule_to_response(schedule: DrugSchedule) -> DrugResponse:
    """Helper function to convert a DrugSchedule to DrugResponse"""
    return DrugResponse(
        id=schedule.id,
        name=schedule.drug.name,
        kind=schedule.drug.kind,
        amount_per_dose=schedule.drug.amount_per_dose,
        start_date=schedule.start_date,
        end_date=schedule.end_date,
        duration=schedule.drug.duration,
        amount_per_day=schedule.drug.amount_per_day,
        dependency_type=schedule.dependency_type.value,
        absolute_time=schedule.absolute_time,
        meal_schedule_id=schedule.meal_schedule_id,
        meal_offset_minutes=schedule.meal_offset_minutes,
        depends_on_schedule_id=schedule.depends_on_schedule_id,
        drug_offset_minutes=schedule.drug_offset_minutes,
        is_active=schedule.is_active,
        created_at=schedule.created_at,
    )


def validate_dependent_schedule(
    db: Session,
    depends_on_schedule_id: int | None,
    schedule_start_date: date,
    schedule_end_date: date | None,
    schedule_id: int | None = None,
) -> None:
    """Validate that a dependent schedule is valid for a DRUG dependency.

    Args:
        db: Database session
        depends_on_schedule_id: The schedule ID to depend on (None if not a DRUG dependency)
        schedule_start_date: Start date of the schedule being created/updated
        schedule_end_date: End date of the schedule being created/updated (None if open-ended)
        schedule_id: ID of the schedule being updated (None for new schedules)

    Raises:
        HTTPException: If the dependent schedule is invalid
    """
    if depends_on_schedule_id is None:
        return  # Not a DRUG dependency, no validation needed

    # Check if dependent schedule exists
    dependent_schedule = (
        db.query(DrugSchedule).filter(DrugSchedule.id == depends_on_schedule_id).first()
    )
    if not dependent_schedule:
        raise HTTPException(
            status_code=404,
            detail=f"Dependent schedule (schedule_id={depends_on_schedule_id}) not found",
        )

    # Prevent self-dependency
    if schedule_id is not None and depends_on_schedule_id == schedule_id:
        raise HTTPException(status_code=400, detail="Schedule cannot depend on itself")

    # Check if dependent schedule is active
    if not dependent_schedule.is_active:
        raise HTTPException(
            status_code=400,
            detail=f"Dependent schedule (schedule_id={depends_on_schedule_id}) is not active",
        )

    # Check if date ranges overlap
    # Dependent schedule must be valid for at least part of the new schedule's date range
    dependent_start = dependent_schedule.start_date
    dependent_end = dependent_schedule.end_date

    # Check if dependent schedule starts after the new schedule's end date
    if dependent_end is not None and dependent_end < schedule_start_date:
        raise HTTPException(
            status_code=400,
            detail=f"Dependent schedule (schedule_id={depends_on_schedule_id}) ends before the schedule start date ({schedule_start_date})",
        )

    # Check if dependent schedule ends before the new schedule's start date
    if schedule_end_date is not None and dependent_start > schedule_end_date:
        raise HTTPException(
            status_code=400,
            detail=f"Dependent schedule (schedule_id={depends_on_schedule_id}) starts after the schedule end date ({schedule_end_date})",
        )

    # If new schedule has no end date, check that dependent schedule covers at least the start date
    if schedule_end_date is None:
        if dependent_end is not None and dependent_end < schedule_start_date:
            raise HTTPException(
                status_code=400,
                detail=f"Dependent schedule (schedule_id={depends_on_schedule_id}) ends before the schedule start date ({schedule_start_date})",
            )


@router.post("/drug")
async def add_drug(
    drug: DrugCreateCompat,
    db: Session = Depends(get_db),
    scheduler: NotificationScheduler = Depends(get_notification_scheduler),
) -> DrugResponse:
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

    # Compute schedule attributes
    dep_type_str = drug.dependency_type
    start_date = drug.start_date or date.today()
    end_date = drug.end_date
    # Frontend now sends UTC time directly
    absolute_time = drug.absolute_time
    dependency_type = DependencyType(dep_type_str)

    # Validate dependent schedule if this is a DRUG dependency
    if dependency_type == DependencyType.DRUG:
        validate_dependent_schedule(
            db, drug.depends_on_schedule_id, start_date, end_date
        )

    # Create a single schedule
    schedule = DrugSchedule(
        drug_id=drug_orm.id,
        dependency_type=dependency_type,
        start_date=start_date,
        end_date=end_date,
        absolute_time=absolute_time,
        meal_schedule_id=drug.meal_schedule_id,
        meal_offset_minutes=drug.meal_offset_minutes,
        depends_on_schedule_id=drug.depends_on_schedule_id,
        drug_offset_minutes=drug.drug_offset_minutes,
    )
    db.add(schedule)
    db.flush()  # Flush to get the schedule ID without committing
    db.refresh(schedule)  # Refresh to get the latest data

    # Schedule notifications in Redis (critical - must succeed)
    await scheduler.schedule_notification(schedule.id, start_date)
    # Also schedule for today if start_date is today or in the past
    if start_date <= date.today():
        await scheduler.schedule_notification(schedule.id, date.today())

    logger.info("POST /drug success name=%s", drug.name)
    return schedule_to_response(schedule)


@router.get("/drug")
def get_all_drugs(db: Session = Depends(get_db)) -> list[DrugResponse]:
    logger.info("GET /drug")
    schedules = db.query(DrugSchedule).filter(DrugSchedule.is_active).all()

    items = []
    for schedule in schedules:
        # Debug timezone conversion
        if schedule.absolute_time and "Timezone" in schedule.drug.name:
            logger.info("🔧 GET /drug Timezone Debug:")
            logger.info(f"  Drug name: {schedule.drug.name}")
            logger.info(f"  DB absolute_time: {schedule.absolute_time}")
            logger.info(f"  Type: {type(schedule.absolute_time)}")
            logger.info(f"  String: {str(schedule.absolute_time)}")

        items.append(schedule_to_response(schedule))

    logger.info("GET /drug count=%d", len(items))
    return items


@router.put("/drug-id/{drug_id}")
async def update_drug(
    drug_id: int,
    drug: DrugCreateCompat,
    db: Session = Depends(get_db),
    scheduler: NotificationScheduler = Depends(get_notification_scheduler),
) -> DrugResponse:
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
    dep_type_str = drug.dependency_type
    dependency_type = DependencyType(dep_type_str)
    schedule.dependency_type = dependency_type

    if drug.start_date is not None:
        schedule.start_date = drug.start_date
    if drug.end_date is not None:
        schedule.end_date = drug.end_date
    if drug.absolute_time is not None:
        # Check if absolute_time is actually changing
        if old_absolute_time != drug.absolute_time:
            absolute_time_changed = True
            logger.info(
                "Absolute time changed from %s to %s for schedule %d",
                old_absolute_time,
                drug.absolute_time,
                schedule.id,
            )
        # Frontend now sends UTC time directly
        schedule.absolute_time = drug.absolute_time
    schedule.meal_schedule_id = drug.meal_schedule_id
    schedule.meal_offset_minutes = drug.meal_offset_minutes

    # Validate dependent schedule if this is a DRUG dependency
    if dependency_type == DependencyType.DRUG:
        # Get the updated dates for validation
        updated_start_date = schedule.start_date
        updated_end_date = schedule.end_date
        if drug.start_date is not None:
            updated_start_date = drug.start_date
        if drug.end_date is not None:
            updated_end_date = drug.end_date
        validate_dependent_schedule(
            db,
            drug.depends_on_schedule_id,
            updated_start_date,
            updated_end_date,
            schedule.id,
        )

    schedule.depends_on_schedule_id = drug.depends_on_schedule_id
    schedule.drug_offset_minutes = drug.drug_offset_minutes

    # If absolute_time changed, clear notification overrides for today and future dates
    # This prevents snooze mechanism from using old times
    if absolute_time_changed:
        today = date.today()
        logger.info(
            "Absolute time changed for schedule %d, clearing notification overrides for today and future dates",
            schedule.id,
        )
        # Delete all notification overrides (snoozes and dismissals) for this schedule from today onwards
        # This ensures the next snooze will use the new absolute_time
        deleted_count = (
            db.query(NotificationOverride)
            .filter(
                NotificationOverride.schedule_id == schedule.id,
                NotificationOverride.override_date >= today,
            )
            .delete()
        )
        logger.info(
            "Cleared %d notification override(s) for schedule %d",
            deleted_count,
            schedule.id,
        )

    db.flush()  # Flush to ensure changes are available
    db.refresh(schedule)  # Refresh to get the latest data

    # Reschedule notifications in Redis (critical - must succeed)
    await scheduler.reschedule_schedule(schedule.id)

    logger.info("PUT /drug/%d success name=%s", drug_id, drug.name)
    return schedule_to_response(schedule)


@router.get("/drug-id/{drug_id}/dependents")
def get_schedule_dependents(
    drug_id: int,
    db: Session = Depends(get_db),
) -> DependentsResponse:
    logger.info("GET /drug-id/%d/dependents", drug_id)

    schedule = db.query(DrugSchedule).filter(DrugSchedule.id == drug_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Drug schedule not found")

    previews = compute_rewire_preview(db, schedule)
    return DependentsResponse(
        has_dependents=len(previews) > 0,
        dependents=previews,
    )


def rewire_and_delete_schedule(
    db: Session, schedule: DrugSchedule
) -> list[DrugSchedule]:
    """Rewire children of the schedule being deleted, then delete it.

    Returns the list of rewired child schedules so the caller can
    reschedule their notifications.
    """
    children = (
        db.query(DrugSchedule)
        .filter(DrugSchedule.depends_on_schedule_id == schedule.id)
        .all()
    )

    parent_schedule_id = schedule.depends_on_schedule_id
    parent_offset = schedule.drug_offset_minutes or 0

    for child in children:
        child_offset = child.drug_offset_minutes or 0

        if parent_schedule_id is not None:
            child.depends_on_schedule_id = parent_schedule_id
            child.drug_offset_minutes = child_offset + parent_offset
        elif schedule.dependency_type == DependencyType.ABSOLUTE:
            abs_time = schedule.absolute_time
            if abs_time is None:
                raise ValueError("ABSOLUTE schedule is missing absolute_time")
            base_minutes = abs_time.hour * 60 + abs_time.minute
            total = (base_minutes + child_offset) % 1440
            child.dependency_type = DependencyType.ABSOLUTE
            child.depends_on_schedule_id = None
            child.drug_offset_minutes = None
            child.absolute_time = time(total // 60, total % 60)
        elif schedule.dependency_type == DependencyType.MEAL:
            child.dependency_type = DependencyType.MEAL
            child.depends_on_schedule_id = None
            child.drug_offset_minutes = None
            child.meal_schedule_id = schedule.meal_schedule_id
            child.meal_offset_minutes = (
                schedule.meal_offset_minutes or 0
            ) + child_offset
        else:
            child.dependency_type = DependencyType.ABSOLUTE
            child.depends_on_schedule_id = None
            child.drug_offset_minutes = None
            child.absolute_time = time(0, 0)

    db.delete(schedule)
    db.delete(schedule.drug)

    return children


def compute_rewire_preview(
    db: Session, schedule: DrugSchedule
) -> list[DependentSchedulePreview]:
    """Compute what would happen to children if this schedule were deleted."""
    children = (
        db.query(DrugSchedule)
        .filter(DrugSchedule.depends_on_schedule_id == schedule.id)
        .all()
    )

    parent_schedule_id = schedule.depends_on_schedule_id
    parent_offset = schedule.drug_offset_minutes or 0
    previews: list[DependentSchedulePreview] = []

    for child in children:
        child_offset = child.drug_offset_minutes or 0
        common = {
            "schedule_id": child.id,
            "drug_name": child.drug.name,
            "current_depends_on_name": schedule.drug.name,
            "current_offset_minutes": child_offset,
        }

        if parent_schedule_id is not None:
            parent = (
                db.query(DrugSchedule)
                .filter(DrugSchedule.id == parent_schedule_id)
                .first()
            )
            preview = DependentSchedulePreview(
                **common,
                new_dependency_type="drug",
                new_depends_on_name=parent.drug.name if parent else None,
                new_offset_minutes=child_offset + parent_offset,
                new_absolute_time=None,
            )
        elif schedule.dependency_type == DependencyType.ABSOLUTE:
            abs_time = schedule.absolute_time
            if abs_time is None:
                raise ValueError("ABSOLUTE schedule is missing absolute_time")
            base_minutes = abs_time.hour * 60 + abs_time.minute
            total = (base_minutes + child_offset) % 1440
            preview = DependentSchedulePreview(
                **common,
                new_dependency_type="absolute",
                new_depends_on_name=None,
                new_offset_minutes=0,
                new_absolute_time=f"{total // 60:02d}:{total % 60:02d}",
            )
        elif schedule.dependency_type == DependencyType.MEAL:
            preview = DependentSchedulePreview(
                **common,
                new_dependency_type="meal",
                new_depends_on_name=(
                    schedule.meal_schedule.meal_name if schedule.meal_schedule else None
                ),
                new_offset_minutes=(schedule.meal_offset_minutes or 0) + child_offset,
                new_absolute_time=None,
            )
        else:
            preview = DependentSchedulePreview(
                **common,
                new_dependency_type="absolute",
                new_depends_on_name=None,
                new_offset_minutes=0,
                new_absolute_time=None,
            )

        previews.append(preview)

    return previews


@router.delete("/drug-id/{drug_id}")
async def delete_drug(
    drug_id: int,
    db: Session = Depends(get_db),
    scheduler: NotificationScheduler = Depends(get_notification_scheduler),
) -> DrugResponse:
    logger.info("DELETE /drug/%d", drug_id)

    schedule = db.query(DrugSchedule).filter(DrugSchedule.id == drug_id).first()
    if not schedule:
        logger.warning("DELETE /drug schedule not found id=%d", drug_id)
        raise HTTPException(status_code=404, detail="Drug schedule not found")

    response = schedule_to_response(schedule)

    today = date.today()
    for i in range(30):
        target_date = today + timedelta(days=i)
        await scheduler.unschedule_notification(schedule.id, target_date)

    rewired_children = rewire_and_delete_schedule(db, schedule)
    db.commit()

    for child in rewired_children:
        await scheduler.reschedule_schedule(child.id)

    logger.info("DELETE /drug/%d success", drug_id)
    return response


# Compatibility endpoints using name instead of id
@router.put("/drug/{name}")
async def update_drug_by_name(
    name: str,
    drug: DrugCreateCompat,
    db: Session = Depends(get_db),
    scheduler: NotificationScheduler = Depends(get_notification_scheduler),
) -> DrugResponse:
    logger.info("PUT /drug/%s payload=%s", name, drug.model_dump())
    schedule = (
        db.query(DrugSchedule)
        .join(DrugSchedule.drug)
        .filter(DrugSchedule.is_active, DrugORM.name == name)
        .first()
    )
    if not schedule:
        raise HTTPException(status_code=404, detail="Drug not found")
    return await update_drug(schedule.id, drug, db, scheduler)


@router.delete("/drug/{name}")
async def delete_drug_by_name(
    name: str,
    db: Session = Depends(get_db),
    scheduler: NotificationScheduler = Depends(get_notification_scheduler),
) -> DrugResponse:
    logger.info("DELETE /drug/%s", name)
    schedule = (
        db.query(DrugSchedule)
        .join(DrugSchedule.drug)
        .filter(DrugORM.name == name)
        .first()
    )
    if not schedule:
        # Fallback: if 'name' looks like an integer id, try deleting by id
        try:
            schedule_id = int(name)
            schedule = (
                db.query(DrugSchedule).filter(DrugSchedule.id == schedule_id).first()
            )
            if not schedule:
                raise HTTPException(status_code=404, detail="Drug not found")
            return await delete_drug(schedule.id, db, scheduler)
        except ValueError:
            raise HTTPException(status_code=404, detail="Drug not found") from None
    return await delete_drug(schedule.id, db, scheduler)


# ID-based deletion kept for compatibility with tests calling /drug/{id}
@router.delete("/drug/{schedule_id}")
async def delete_drug_by_id_compat(
    schedule_id: int,
    db: Session = Depends(get_db),
    scheduler: NotificationScheduler = Depends(get_notification_scheduler),
) -> DrugResponse:
    logger.info("DELETE /drug/%d", schedule_id)
    schedule = db.query(DrugSchedule).filter(DrugSchedule.id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Drug not found")
    return await delete_drug(schedule.id, db, scheduler)


# NOTE: Meal schedule endpoints are defined in backend.api.meal; duplicates removed here.
