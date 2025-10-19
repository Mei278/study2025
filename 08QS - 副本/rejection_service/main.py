from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)


def init_db():
    conn = sqlite3.connect('rejection.db')
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS rejected_products
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       order_id
                       INTEGER
                       NOT
                       NULL,
                       order_number
                       TEXT
                       NOT
                       NULL,
                       product_name
                       TEXT
                       NOT
                       NULL,
                       quantity
                       INTEGER
                       NOT
                       NULL,
                       reason
                       TEXT
                       NOT
                       NULL,
                       unqualified_items
                       TEXT,
                       rejection_date
                       TEXT
                       NOT
                       NULL,
                       status
                       TEXT
                       DEFAULT
                       '待处理',
                       handling_method
                       TEXT,
                       handled_by
                       TEXT,
                       handling_date
                       TEXT
                   )
                   ''')
    conn.commit()
    conn.close()


@app.route('/api/rejections', methods = ['GET'])
def get_rejections():
    conn = sqlite3.connect('rejection.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM rejected_products')
    records = cursor.fetchall()
    conn.close()

    result = []
    for record in records:
        result.append({
            'id': record[0],
            'order_id': record[1],
            'order_number': record[2],
            'product_name': record[3],
            'quantity': record[4],
            'reason': record[5],
            'unqualified_items': json.loads(record[6]) if record[6] else [],
            'rejection_date': record[7],
            'status': record[8],
            'handling_method': record[9],
            'handled_by': record[10],
            'handling_date': record[11]
        })
    return jsonify(result)


@app.route('/api/rejections', methods = ['POST'])
def create_rejection():
    data = request.json
    required_fields = ['order_id', 'order_number', 'product_name', 'reason']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    conn = sqlite3.connect('rejection.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
                       INSERT INTO rejected_products
                       (order_id, order_number, product_name, quantity, reason,
                        unqualified_items, rejection_date, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                       ''', (
                           data['order_id'],
                           data['order_number'],
                           data['product_name'],
                           data.get('quantity', 0),
                           data['reason'],
                           json.dumps(data.get('unqualified_items', []), ensure_ascii = False),
                           datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                           '待处理'
                       ))
        conn.commit()
        rejection_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'message': 'Rejection record created successfully',
            'id': rejection_id
        }), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/rejections/<int:rejection_id>/handle', methods = ['PUT'])
def handle_rejection(rejection_id):
    data = request.json
    required_fields = ['handling_method', 'handled_by']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    conn = sqlite3.connect('rejection.db')
    cursor = conn.cursor()

    cursor.execute('''
                   UPDATE rejected_products
                   SET status          = '已处理',
                       handling_method = ?,
                       handled_by      = ?,
                       handling_date   = ?
                   WHERE id = ?
                   ''', (
                       data['handling_method'],
                       data['handled_by'],
                       datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       rejection_id
                   ))

    conn.commit()
    conn.close()

    return jsonify({'message': 'Rejection handled successfully'})


if __name__ == '__main__':
    init_db()
    app.run(port = 5003, debug = True)