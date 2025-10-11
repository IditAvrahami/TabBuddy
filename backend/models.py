from sqlalchemy import Column, Integer, String, Time, Boolean, DateTime
from datetime import datetime, timezone
from .database import Base

class DrugORM(Base):
	__tablename__ = 'drugs'

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, unique=True, index=True, nullable=False)
	kind = Column(String, nullable=False)  # 'pill' or 'liquid'
	amount_per_dose = Column(Integer, nullable=False)
	duration = Column(Integer, nullable=False)  # days
	amount_per_day = Column(Integer, nullable=False)

# Meal schedules
class MealSchedule(Base):
    __tablename__ = 'meal_schedules'
    
    id = Column(Integer, primary_key=True, index=True)
    meal_name = Column(String(50), unique=True, nullable=False)
    base_time = Column(Time, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
