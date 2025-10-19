# frontend_service/main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI(title="质量检验管理前端")

templates = Jinja2Templates(directory="frontend_service/templates")

PROCUREMENT_API = "http://127.0.0.1:8001/arrivals/"
INSPECTION_API = "http://127.0.0.1:8002/inspections/"
REJECTION_API = "http://127.0.0.1:8003/rejections/"


# 首页
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})


# ============= 采购到货 =============
@app.get("/arrivals")
def show_arrivals(request: Request):
    arrivals = requests.get(PROCUREMENT_API).json()
    return templates.TemplateResponse("arrivals.html", {"request": request, "arrivals": arrivals})

@app.post("/arrivals/add")
def add_arrival(
    item_name: str = Form(...),
    quantity: float = Form(...),
    supplier: str = Form(...),
    arrival_date: str = Form(...)
):
    payload = {
        "item_name": item_name,
        "quantity": quantity,
        "supplier": supplier,
        "arrival_date": arrival_date
    }
    requests.post(PROCUREMENT_API, json=payload)
    return RedirectResponse("/arrivals", status_code=303)


# ============= 质量检验 =============
@app.get("/inspections")
def show_inspections(request: Request):
    inspections = requests.get(INSPECTION_API).json()
    arrivals = requests.get(PROCUREMENT_API).json()
    return templates.TemplateResponse("inspections.html", {"request": request, "inspections": inspections, "arrivals": arrivals})

@app.post("/inspections/add")
def add_inspection(
    purchase_id: int = Form(...),
    item_name: str = Form(...),
    inspected_quantity: float = Form(...),
    passed_quantity: float = Form(...),
    failed_quantity: float = Form(...),
    status: str = Form(...)
):
    payload = {
        "purchase_id": purchase_id,
        "item_name": item_name,
        "inspected_quantity": inspected_quantity,
        "passed_quantity": passed_quantity,
        "failed_quantity": failed_quantity,
        "status": status
    }
    requests.post(INSPECTION_API, json=payload)
    return RedirectResponse("/inspections", status_code=303)


# ============= 不合格品 =============
@app.get("/rejections")
def show_rejections(request: Request):
    rejections = requests.get(REJECTION_API).json()
    inspections = requests.get(INSPECTION_API).json()
    return templates.TemplateResponse("rejections.html", {"request": request, "rejections": rejections, "inspections": inspections})

@app.post("/rejections/add")
def add_rejection(
    inspection_id: int = Form(...),
    item_name: str = Form(...),
    reason: str = Form(...)
):
    payload = {
        "inspection_id": inspection_id,
        "item_name": item_name,
        "reason": reason
    }
    requests.post(REJECTION_API, json=payload)
    return RedirectResponse("/rejections", status_code=303)
