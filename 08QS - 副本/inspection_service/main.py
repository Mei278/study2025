from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import requests
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 其他服务URL
PROCUREMENT_SERVICE_URL = "http://localhost:5001"
REJECTION_SERVICE_URL = "http://localhost:5003"


def init_db():
    conn = sqlite3.connect('inspection.db')
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS inspection_records
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       order_id
                       INTEGER
                       NOT
                       NULL
                       UNIQUE,
                       order_number
                       TEXT
                       NOT
                       NULL,
                       product_name
                       TEXT
                       NOT
                       NULL,
                       inspector
                       TEXT
                       NOT
                       NULL,
                       result
                       TEXT
                       NOT
                       NULL,
                       check_items
                       TEXT
                       NOT
                       NULL,
                       unqualified_items
                       TEXT,
                       notes
                       TEXT,
                       inspection_date
                       TEXT
                       NOT
                       NULL
                   )
                   ''')
    conn.commit()
    conn.close()


@app.route('/api/inspections', methods = ['GET'])
def get_inspections():
    conn = sqlite3.connect('inspection.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inspection_records')
    records = cursor.fetchall()
    conn.close()

    result = []
    for record in records:
        result.append({
            'id': record[0],
            'order_id': record[1],
            'order_number': record[2],
            'product_name': record[3],
            'inspector': record[4],
            'result': record[5],
            'check_items': json.loads(record[6]),
            'unqualified_items': json.loads(record[7]) if record[7] else [],
            'notes': record[8],
            'inspection_date': record[9]
        })
    return jsonify(result)


@app.route('/api/inspections', methods = ['POST'])
def create_inspection():
    data = request.json
    required_fields = ['order_id', 'order_number', 'product_name', 'inspector', 'result', 'check_items']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # 检查是否已经检验过
    conn = sqlite3.connect('inspection.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM inspection_records WHERE order_id = ?', (data['order_id'],))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'This order has already been inspected'}), 400

    # 保存检验记录
    try:
        cursor.execute('''
                       INSERT INTO inspection_records
                       (order_id, order_number, product_name, inspector, result, check_items,
                        unqualified_items, notes, inspection_date)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ''', (
                           data['order_id'],
                           data['order_number'],
                           data['product_name'],
                           data['inspector'],
                           data['result'],
                           json.dumps(data['check_items'], ensure_ascii = False),
                           json.dumps(data.get('unqualified_items', []), ensure_ascii = False),
                           data.get('notes', ''),
                           datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                       ))
        conn.commit()
        inspection_id = cursor.lastrowid
        conn.close()
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

    # 更新采购订单状态
    try:
        status_map = {'合格': '检验合格', '不合格': '检验不合格'}
        new_status = status_map.get(data['result'], '检验中')

        requests.put(
            f"{PROCUREMENT_SERVICE_URL}/api/purchase_orders/{data['order_id']}/status",
            json = {'status': new_status},
            timeout = 5
        )
    except requests.exceptions.RequestException as e:
        print(f"Failed to update procurement service: {e}")

    # 如果不合格，发送到不合格产品服务
    if data['result'] == '不合格':
        try:
            rejection_data = {
                'order_id': data['order_id'],
                'order_number': data['order_number'],
                'product_name': data['product_name'],
                'quantity': data.get('quantity', 0),
                'reason': data.get('notes', '检验不合格'),
                'unqualified_items': data.get('unqualified_items', [])
            }
            requests.post(
                f"{REJECTION_SERVICE_URL}/api/rejections",
                json = rejection_data,
                timeout = 5
            )
        except requests.exceptions.RequestException as e:
            print(f"Failed to send to rejection service: {e}")

    return jsonify({
        'message': 'Inspection record created successfully',
        'id': inspection_id
    }), 201


@app.route('/api/inspections/<int:inspection_id>', methods = ['GET'])
def get_inspection(inspection_id):
    conn = sqlite3.connect('inspection.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM inspection_records WHERE id = ?', (inspection_id,))
    record = cursor.fetchone()
    conn.close()

    if record:
        return jsonify({
            'id': record[0],
            'order_id': record[1],
            'order_number': record[2],
            'product_name': record[3],
            'inspector': record[4],
            'result': record[5],
            'check_items': json.loads(record[6]),
            'unqualified_items': json.loads(record[7]) if record[7] else [],
            'notes': record[8],
            'inspection_date': record[9]
        })
    return jsonify({'error': 'Inspection record not found'}), 404


if __name__ == '__main__':
    init_db()
    app.run(port = 5002, debug = True)