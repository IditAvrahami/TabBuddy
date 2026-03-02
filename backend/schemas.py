from pydantic import BaseModel, Field


class NotificationDto(BaseModel):
    schedule_id: int
    drug_id: int
    drug_name: str
    kind: str
    amount_per_dose: int
    dependency_type: str
    scheduled_time: str = Field(..., description="ISO timestamp for notification time")
