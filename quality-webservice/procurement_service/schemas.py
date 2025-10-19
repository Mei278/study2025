# procurement_service/schemas.py
from pydantic import BaseModel
from datetime import date

class PurchaseArrivalCreate(BaseModel):
    item_name: str
    quantity: float
    supplier: str
    arrival_date: date

class PurchaseArrivalRead(PurchaseArrivalCreate):
    id: int

    class Config:
        orm_mode = True
