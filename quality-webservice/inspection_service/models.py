# inspection_service/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from shared.db import Base

class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    id = Column(Integer, primary_key=True, index=True)
    purchase_id = Column(Integer, index=True)
    item_name = Column(String)
    inspected_quantity = Column(Float)
    passed_quantity = Column(Float)
    failed_quantity = Column(Float)
    status = Column(String)
