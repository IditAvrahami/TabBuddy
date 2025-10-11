import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from datetime import time
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.models import MealSchedule

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

@router.get("/meal-schedules", response_model=List[MealScheduleDto])
def get_meal_schedules(db: Session = Depends(get_db)):
    logger.info("GET /meal-schedules")
    rows = db.query(MealSchedule).all()
    items = [
        MealScheduleDto(
            id=r.id,
            meal_name=r.meal_name,
            base_time=r.base_time.strftime("%H:%M"),
            created_at=r.created_at.isoformat()
        )
        for r in rows
    ]
    logger.info("GET /meal-schedules count=%d", len(items))
    return items

@router.post("/meal-schedules")
def create_meal_schedule(meal: MealScheduleCreate, db: Session = Depends(get_db)):
    logger.info("POST /meal-schedules payload=%s", meal.model_dump())
    
    # Check if meal already exists
    exists = db.query(MealSchedule).filter(MealSchedule.meal_name == meal.meal_name).first()
    if exists:
        logger.warning("POST /meal-schedules duplicate meal_name=%s", meal.meal_name)
        raise HTTPException(status_code=400, detail="Meal schedule already exists")
    
    # Parse time string
    try:
        time_obj = time.fromisoformat(meal.base_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
    
    row = MealSchedule(
        meal_name=meal.meal_name,
        base_time=time_obj
    )
    db.add(row)
    db.commit()
    logger.info("POST /meal-schedules success meal_name=%s", meal.meal_name)
    return {"message": f"Added {meal.meal_name} meal schedule"}

@router.put("/meal-schedules/{meal_name}")
def update_meal_schedule(meal_name: str, meal: MealScheduleUpdate, db: Session = Depends(get_db)):
    logger.info("PUT /meal-schedules/%s payload=%s", meal_name, meal.model_dump())
    
    row = db.query(MealSchedule).filter(MealSchedule.meal_name == meal_name).first()
    if not row:
        logger.warning("PUT /meal-schedules meal not found meal_name=%s", meal_name)
        raise HTTPException(status_code=404, detail="Meal schedule not found")
    
    # Parse time string
    try:
        time_obj = time.fromisoformat(meal.base_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid time format. Use HH:MM")
    
    row.base_time = time_obj
    db.commit()
    logger.info("PUT /meal-schedules/%s success", meal_name)
    return {"message": f"Updated {meal_name} meal schedule"}

@router.delete("/meal-schedules/{meal_name}")
def delete_meal_schedule(meal_name: str, db: Session = Depends(get_db)):
    logger.info("DELETE /meal-schedules/%s", meal_name)
    
    row = db.query(MealSchedule).filter(MealSchedule.meal_name == meal_name).first()
    if not row:
        logger.warning("DELETE /meal-schedules meal not found meal_name=%s", meal_name)
        raise HTTPException(status_code=404, detail="Meal schedule not found")
    
    db.delete(row)
    db.commit()
    logger.info("DELETE /meal-schedules/%s success", meal_name)
    return {"message": f"Deleted {meal_name} meal schedule"}
