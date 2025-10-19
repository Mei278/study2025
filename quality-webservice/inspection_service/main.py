# inspection_service/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from shared.db import Base, engine, get_db
from . import models, schemas
import requests

Base.metadata.create_all(bind=engine)
app = FastAPI(title="质量检验服务")

PROCUREMENT_URL = "http://127.0.0.1:8001/arrivals/"

@app.get("/inspections/", response_model=list[schemas.InspectionRead])
def list_inspections(db: Session = Depends(get_db)):
    return db.query(models.InspectionRecord).all()

@app.post("/inspections/", response_model=schemas.InspectionRead)
def create_inspection(record: schemas.InspectionCreate, db: Session = Depends(get_db)):
    db_record = models.InspectionRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/sync_arrivals/")
def get_arrivals_from_procurement():
    resp = requests.get(PROCUREMENT_URL)
    return resp.json()
