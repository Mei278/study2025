# procurement_service/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from shared.db import Base, engine, get_db
from . import models, schemas

Base.metadata.create_all(bind=engine)
app = FastAPI(title="采购到货服务")

@app.post("/arrivals/", response_model=schemas.PurchaseArrivalRead)
def create_arrival(arrival: schemas.PurchaseArrivalCreate, db: Session = Depends(get_db)):
    db_item = models.PurchaseArrival(**arrival.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/arrivals/", response_model=list[schemas.PurchaseArrivalRead])
def list_arrivals(db: Session = Depends(get_db)):
    return db.query(models.PurchaseArrival).all()
