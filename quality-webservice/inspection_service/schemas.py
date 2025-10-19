# inspection_service/schemas.py
from pydantic import BaseModel

class InspectionCreate(BaseModel):
    purchase_id: int
    item_name: str
    inspected_quantity: float
    passed_quantity: float
    failed_quantity: float
    status: str

class InspectionRead(InspectionCreate):
    id: int
    class Config:
        orm_mode = True
