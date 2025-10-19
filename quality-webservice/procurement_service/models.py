# procurement_service/models.py
from sqlalchemy import Column, Integer, String, Float, Date
from shared.db import Base

class PurchaseArrival(Base):
    __tablename__ = "purchase_arrivals"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, index=True)
    quantity = Column(Float)
    supplier = Column(String)
    arrival_date = Column(Date)
