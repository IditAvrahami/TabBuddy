import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List
from backend.database import get_db
from sqlalchemy.orm import Session
from backend.models import DrugORM

logger = logging.getLogger(__name__)
router = APIRouter()

class Drug(BaseModel):
    name: str = Field(..., description="Drug name")
    kind: str = Field(..., pattern="^(pill|liquid)$", description="pill or liquid")
    amount_per_dose: int = Field(..., description="Amount per dose")
    duration: int = Field(..., description="Duration in days")
    amount_per_day: int = Field(..., description="Amount per day")

@router.post("/drug")
def add_drug(drug: Drug, db: Session = Depends(get_db)):
    logger.info("POST /drug payload=%s", drug.model_dump())
    exists = db.query(DrugORM).filter(DrugORM.name == drug.name).first()
    if exists:
        logger.warning("POST /drug duplicate name=%s", drug.name)
        raise HTTPException(status_code=400, detail="Drug already exists")
    row = DrugORM(
        name=drug.name,
        kind=drug.kind,
        amount_per_dose=drug.amount_per_dose,
        duration=drug.duration,
        amount_per_day=drug.amount_per_day,
    )
    db.add(row)
    db.commit()
    logger.info("POST /drug success name=%s", drug.name)
    return {"message": f"Added {drug.name}"}

@router.get("/drug", response_model=List[Drug])
def get_all_drugs(db: Session = Depends(get_db)):
    logger.info("GET /drug")
    rows = db.query(DrugORM).all()
    items = [
        Drug(
            name=r.name,
            kind=r.kind,
            amount_per_dose=r.amount_per_dose,
            duration=r.duration,
            amount_per_day=r.amount_per_day,
        )
        for r in rows
    ]
    logger.info("GET /drug count=%d", len(items))
    return items

@router.put("/drug/{name}")
def update_drug(name: str, drug: Drug, db: Session = Depends(get_db)):
    logger.info("PUT /drug/%s payload=%s", name, drug.model_dump())
    row = db.query(DrugORM).filter(DrugORM.name == name).first()
    if not row:
        logger.warning("PUT /drug name not found name=%s", name)
        raise HTTPException(status_code=404, detail="Drug not found")
    row.name = drug.name
    row.kind = drug.kind
    row.amount_per_dose = drug.amount_per_dose
    row.duration = drug.duration
    row.amount_per_day = drug.amount_per_day
    db.commit()
    logger.info("PUT /drug/%s success new_name=%s", name, drug.name)
    return {"message": f"Updated {drug.name}"}

@router.delete("/drug/{name}")
def delete_drug(name: str, db: Session = Depends(get_db)):
    logger.info("DELETE /drug/%s", name)
    row = db.query(DrugORM).filter(DrugORM.name == name).first()
    if not row:
        logger.warning("DELETE /drug name not found name=%s", name)
        raise HTTPException(status_code=404, detail="Drug not found")
    db.delete(row)
    db.commit()
    logger.info("DELETE /drug/%s success", name)
    return {"message": f"Deleted {name}"}
