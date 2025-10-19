from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import sqlite3
import os

app = FastAPI(title="采购到货服务")
templates = Jinja2Templates(directory="templates")
DB_FILE = "procurement.db"

# 初始化数据库
def init_db():
    if not os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
        CREATE TABLE purchase_orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            supplier TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            arrival_date TEXT,
            status TEXT DEFAULT '待检验'
        );
        """)
        conn.commit()
        conn.close()

init_db()

# ---------- CRUD 操作 ----------
def get_all_orders():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM purchase_orders")
    orders = c.fetchall()
    conn.close()
    return orders

def get_order(order_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM purchase_orders WHERE id=?", (order_id,))
    order = c.fetchone()
    conn.close()
    return order

def add_order(order_number, supplier, product_name, quantity, arrival_date):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO purchase_orders (order_number, supplier, product_name, quantity, arrival_date) VALUES (?, ?, ?, ?, ?)",
        (order_number, supplier, product_name, quantity, arrival_date)
    )
    conn.commit()
    conn.close()

def update_order(order_id, order_number, supplier, product_name, quantity, arrival_date, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        UPDATE purchase_orders 
        SET order_number=?, supplier=?, product_name=?, quantity=?, arrival_date=?, status=?
        WHERE id=?
    """, (order_number, supplier, product_name, quantity, arrival_date, status, order_id))
    conn.commit()
    conn.close()

def delete_order(order_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM purchase_orders WHERE id=?", (order_id,))
    conn.commit()
    conn.close()

# ---------- 页面路由 ----------
@app.get("/")
def home():
    return RedirectResponse(url="/orders/")

@app.get("/orders/")
def order_list(request: Request):
    orders = get_all_orders()
    return templates.TemplateResponse("order_list.html", {"request": request, "orders": orders})

@app.get("/orders/add/")
def order_add_form(request: Request):
    return templates.TemplateResponse("order_add.html", {"request": request})

@app.post("/orders/add/")
def order_add(
    order_number: str = Form(...),
    supplier: str = Form(...),
    product_name: str = Form(...),
    quantity: int = Form(...),
    arrival_date: str = Form(...)
):
    add_order(order_number, supplier, product_name, quantity, arrival_date)
    return RedirectResponse(url="/orders/", status_code=303)

@app.get("/orders/edit/{order_id}")
def order_edit_form(request: Request, order_id: int):
    order = get_order(order_id)
    return templates.TemplateResponse("order_edit.html", {"request": request, "order": order})

@app.post("/orders/edit/{order_id}")
def order_edit(
    order_id: int,
    order_number: str = Form(...),
    supplier: str = Form(...),
    product_name: str = Form(...),
    quantity: int = Form(...),
    arrival_date: str = Form(...),
    status: str = Form(...)
):
    update_order(order_id, order_number, supplier, product_name, quantity, arrival_date, status)
    return RedirectResponse(url="/orders/", status_code=303)

@app.get("/orders/delete/{order_id}")
def order_delete(order_id: int):
    delete_order(order_id)
    return RedirectResponse(url="/orders/", status_code=303)

# ---------- 对外API（供检验服务调用） ----------
@app.get("/arrivals/")
def api_arrivals():
    orders = get_all_orders()
    # 返回 JSON 数据
    result = [
        {
            "id": o[0],
            "order_number": o[1],
            "supplier": o[2],
            "product_name": o[3],
            "quantity": o[4],
            "arrival_date": o[5],
            "status": o[6]
        }
        for o in orders
    ]
    return result
