# rejection_service/models.py
from sqlalchemy import Column, Integer, String, ForeignKey
from shared.db import Base

class RejectionRecord(Base):
    __tablename__ = "rejection_records"

    id = Column(Integer, primary_key=True, index=True)
    inspection_id = Column(Integer, index=True)
    item_name = Column(String)
    reason = Column(String)
