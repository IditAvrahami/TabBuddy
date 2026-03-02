import logging
from datetime import time

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import DrugSchedule, MealSchedule
from backend.services.notification_scheduler import (
    NotificationScheduler,
    get_notification_scheduler,
)

logger = logging.getLogger(__name__)
router = APIRouter()


class MealScheduleDto(BaseModel):
    id: int = Field(..., description="Meal schedule ID")
    meal_name: str = Field(..., description="Meal name (breakfast, lunch, dinner)")
    base_time: str = Field(..., description="Base time in HH:MM format")
    created_at: str = Field(..., description="Creation timestamp")


class MealScheduleCreate(BaseModel):
    meal_name: str = Field(..., description="Meal name (breakfast, lunch, dinner)")
    base_time: str = Field(..., description="Base time in HH:MM format")


class MealScheduleUpdate(BaseModel):
    base_time: str = Field(..., description="Base time in HH:MM format")


def meal_schedule_to_dto(meal: MealSchedule) -> MealScheduleDto:
    """Helper function to convert a MealSchedule to MealScheduleDto"""
    return MealScheduleDto(
        id=meal.id,
        meal_name=meal.meal_name,
        base_time=meal.base_time.strftime("%H:%M"),
        created_at=meal.created_at.isoformat(),
    )


@router.get("/meal-schedules")
def get_meal_schedules(db: Session = Depends(get_db)) -> list[MealScheduleDto]:
    logger.info("GET /meal-schedules")
    rows = db.query(MealSchedule).all()
    items = [meal_schedule_to_dto(r) for r in rows]
    logger.info("GET /meal-schedules count=%d", len(items))
    return items


@router.post("/meal-schedules")
def create_meal_schedule(
    meal: MealScheduleCreate, db: Session = Depends(get_db)
) -> MealScheduleDto:
    logger.info("POST /meal-schedules payload=%s", meal.model_dump())

    # Check if meal already exists
    exists = (
        db.query(MealSchedule).filter(MealSchedule.meal_name == meal.meal_name).first()
    )
    if exists:
        logger.warning("POST /meal-schedules duplicate meal_name=%s", meal.meal_name)
        raise HTTPException(status_code=400, detail="Meal schedule already exists")

    # Parse time string
    try:
        time_obj = time.fromisoformat(meal.base_time)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid time format. Use HH:MM"
        ) from e

    row = MealSchedule(meal_name=meal.meal_name, base_time=time_obj)
    db.add(row)
    db.commit()
    db.refresh(row)  # Refresh to get the latest data
    logger.info("POST /meal-schedules success meal_name=%s", meal.meal_name)
    return meal_schedule_to_dto(row)


@router.put("/meal-schedules/{meal_name}")
async def update_meal_schedule(
    meal_name: str,
    meal: MealScheduleUpdate,
    db: Session = Depends(get_db),
    scheduler: NotificationScheduler = Depends(get_notification_scheduler),
) -> MealScheduleDto:
    logger.info("PUT /meal-schedules/%s payload=%s", meal_name, meal.model_dump())

    row = db.query(MealSchedule).filter(MealSchedule.meal_name == meal_name).first()
    if not row:
        logger.warning("PUT /meal-schedules meal not found meal_name=%s", meal_name)
        raise HTTPException(status_code=404, detail="Meal schedule not found")

    # Parse time string
    try:
        time_obj = time.fromisoformat(meal.base_time)
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail="Invalid time format. Use HH:MM"
        ) from e

    row.base_time = time_obj
    db.flush()  # Flush to ensure changes are available
    db.refresh(row)  # Refresh to get the latest data

    # Reschedule all drug notifications that depend on this meal (critical - must succeed)
    # Find all drug schedules that depend on this meal
    dependent_schedules = (
        db.query(DrugSchedule)
        .filter(
            DrugSchedule.meal_schedule_id == row.id,
            DrugSchedule.is_active,
        )
        .all()
    )

    logger.info(
        f"Rescheduling notifications for {len(dependent_schedules)} schedules dependent on meal {meal_name}"
    )

    for schedule in dependent_schedules:
        await scheduler.reschedule_schedule(schedule.id)

    logger.info("PUT /meal-schedules/%s success", meal_name)
    return meal_schedule_to_dto(row)


@router.delete("/meal-schedules/{meal_name}")
def delete_meal_schedule(
    meal_name: str, db: Session = Depends(get_db)
) -> MealScheduleDto:
    logger.info("DELETE /meal-schedules/%s", meal_name)

    row = db.query(MealSchedule).filter(MealSchedule.meal_name == meal_name).first()
    if not row:
        logger.warning("DELETE /meal-schedules meal not found meal_name=%s", meal_name)
        raise HTTPException(status_code=404, detail="Meal schedule not found")

    # Create response before deleting
    response = meal_schedule_to_dto(row)
    db.delete(row)
    db.commit()
    logger.info("DELETE /meal-schedules/%s success", meal_name)
    return response
