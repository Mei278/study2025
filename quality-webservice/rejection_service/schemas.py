# rejection_service/schemas.py
from pydantic import BaseModel

class RejectionCreate(BaseModel):
    inspection_id: int
    item_name: str
    reason: str

class RejectionRead(RejectionCreate):
    id: int
    class Config:
        orm_mode = True
