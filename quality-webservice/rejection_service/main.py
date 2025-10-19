# rejection_service/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from shared.db import Base, engine, get_db
from . import models, schemas
import requests

Base.metadata.create_all(bind=engine)
app = FastAPI(title="不合格品提交服务")

INSPECTION_URL = "http://127.0.0.1:8002/inspections/"

@app.get("/rejections/", response_model=list[schemas.RejectionRead])
def list_rejections(db: Session = Depends(get_db)):
    return db.query(models.RejectionRecord).all()

@app.post("/rejections/", response_model=schemas.RejectionRead)
def create_rejection(record: schemas.RejectionCreate, db: Session = Depends(get_db)):
    db_record = models.RejectionRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

@app.get("/sync_inspections/")
def get_inspections_from_quality():
    resp = requests.get(INSPECTION_URL)
    return resp.json()
