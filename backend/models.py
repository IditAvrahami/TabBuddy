from sqlalchemy import Column, Integer, String
from .database import Base

class DrugORM(Base):
	__tablename__ = 'drugs'

	id = Column(Integer, primary_key=True, index=True)
	name = Column(String, unique=True, index=True, nullable=False)
	kind = Column(String, nullable=False)  # 'pill' or 'liquid'
	amount_per_dose = Column(Integer, nullable=False)
	duration = Column(Integer, nullable=False)  # days
	amount_per_day = Column(Integer, nullable=False)
