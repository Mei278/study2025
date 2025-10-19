from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)


def init_db():
    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS purchase_orders
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       order_number
                       TEXT
                       NOT
                       NULL
                       UNIQUE,
                       supplier
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
                       arrival_date
                       TEXT,
                       status
                       TEXT
                       DEFAULT
                       '待检验'
                   )
                   ''')

    # 插入示例数据
    cursor.execute("SELECT COUNT(*) FROM purchase_orders")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ('PO-2024-001', '供应商A', '产品X', 100, '2024-01-15', '待检验'),
            ('PO-2024-002', '供应商B', '产品Y', 200, '2024-01-16', '待检验'),
            ('PO-2024-003', '供应商C', '产品Z', 150, '2024-01-17', '检验中'),
            ('PO-2024-004', '供应商A', '产品W', 80, '2024-01-18', '检验合格'),
            ('PO-2024-005', '供应商D', '产品V', 120, '2024-01-19', '检验不合格')
        ]
        cursor.executemany('''
                           INSERT INTO purchase_orders
                               (order_number, supplier, product_name, quantity, arrival_date, status)
                           VALUES (?, ?, ?, ?, ?, ?)
                           ''', sample_data)

    conn.commit()
    conn.close()


@app.route('/api/purchase_orders', methods = ['GET'])
def get_purchase_orders():
    # 支持查询参数过滤
    status_filter = request.args.get('status')
    supplier_filter = request.args.get('supplier')

    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()

    query = 'SELECT * FROM purchase_orders WHERE 1=1'
    params = []

    if status_filter:
        query += ' AND status = ?'
        params.append(status_filter)

    if supplier_filter:
        query += ' AND supplier LIKE ?'
        params.append(f'%{supplier_filter}%')

    query += ' ORDER BY id DESC'

    cursor.execute(query, params)
    orders = cursor.fetchall()
    conn.close()

    result = []
    for order in orders:
        result.append({
            'id': order[0],
            'order_number': order[1],
            'supplier': order[2],
            'product_name': order[3],
            'quantity': order[4],
            'arrival_date': order[5],
            'status': order[6]
        })
    return jsonify(result)


@app.route('/api/purchase_orders/<int:order_id>', methods = ['GET'])
def get_purchase_order(order_id):
    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM purchase_orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    conn.close()

    if order:
        return jsonify({
            'id': order[0],
            'order_number': order[1],
            'supplier': order[2],
            'product_name': order[3],
            'quantity': order[4],
            'arrival_date': order[5],
            'status': order[6]
        })
    return jsonify({'error': 'Order not found'}), 404


@app.route('/api/purchase_orders/<int:order_id>/status', methods = ['PUT'])
def update_order_status(order_id):
    data = request.json
    new_status = data.get('status')

    if not new_status:
        return jsonify({'error': 'Status is required'}), 400

    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()

    # 检查订单是否存在
    cursor.execute('SELECT id FROM purchase_orders WHERE id = ?', (order_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Order not found'}), 404

    cursor.execute(
        'UPDATE purchase_orders SET status = ? WHERE id = ?',
        (new_status, order_id)
    )
    conn.commit()
    conn.close()

    return jsonify({'message': 'Status updated successfully'})


@app.route('/api/purchase_orders/<int:order_id>', methods = ['PUT'])
def update_purchase_order(order_id):
    data = request.json

    # 检查必需字段
    required_fields = ['order_number', 'supplier', 'product_name', 'quantity']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()

    # 检查订单是否存在
    cursor.execute('SELECT id FROM purchase_orders WHERE id = ?', (order_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Order not found'}), 404

    # 检查订单号是否与其他订单冲突
    cursor.execute('SELECT id FROM purchase_orders WHERE order_number = ? AND id != ?',
                   (data['order_number'], order_id))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Order number already exists'}), 400

    try:
        cursor.execute('''
                       UPDATE purchase_orders
                       SET order_number = ?,
                           supplier     = ?,
                           product_name = ?,
                           quantity     = ?,
                           arrival_date = ?,
                           status       = ?
                       WHERE id = ?
                       ''', (
                           data['order_number'],
                           data['supplier'],
                           data['product_name'],
                           data['quantity'],
                           data.get('arrival_date'),
                           data.get('status', '待检验'),
                           order_id
                       ))
        conn.commit()
        conn.close()

        return jsonify({'message': 'Order updated successfully'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/purchase_orders/<int:order_id>', methods = ['DELETE'])
def delete_purchase_order(order_id):
    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()

    # 检查订单是否存在
    cursor.execute('SELECT id FROM purchase_orders WHERE id = ?', (order_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Order not found'}), 404

    cursor.execute('DELETE FROM purchase_orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Order deleted successfully'})


@app.route('/api/purchase_orders', methods = ['POST'])
def create_purchase_order():
    data = request.json
    required_fields = ['order_number', 'supplier', 'product_name', 'quantity']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()

    try:
        cursor.execute('''
                       INSERT INTO purchase_orders
                           (order_number, supplier, product_name, quantity, arrival_date, status)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', (
                           data['order_number'],
                           data['supplier'],
                           data['product_name'],
                           data['quantity'],
                           data.get('arrival_date', datetime.now().strftime('%Y-%m-%d')),
                           data.get('status', '待检验')
                       ))
        conn.commit()
        order_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'message': 'Order created successfully',
            'id': order_id,
            'order_number': data['order_number']
        }), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Order number already exists'}), 400
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500


@app.route('/api/purchase_orders/search', methods = ['GET'])
def search_purchase_orders():
    """搜索采购订单"""
    keyword = request.args.get('q', '').strip()

    if not keyword:
        return jsonify({'error': 'Search keyword is required'}), 400

    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()

    search_pattern = f'%{keyword}%'
    cursor.execute('''
                   SELECT *
                   FROM purchase_orders
                   WHERE order_number LIKE ?
                      OR supplier LIKE ?
                      OR product_name LIKE ?
                   ORDER BY id DESC
                   ''', (search_pattern, search_pattern, search_pattern))

    orders = cursor.fetchall()
    conn.close()

    result = []
    for order in orders:
        result.append({
            'id': order[0],
            'order_number': order[1],
            'supplier': order[2],
            'product_name': order[3],
            'quantity': order[4],
            'arrival_date': order[5],
            'status': order[6]
        })

    return jsonify({
        'results': result,
        'count': len(result)
    })


@app.route('/api/purchase_orders/stats', methods = ['GET'])
def get_purchase_stats():
    """获取采购订单统计信息"""
    conn = sqlite3.connect('procurement.db')
    cursor = conn.cursor()

    # 按状态统计
    cursor.execute('''
                   SELECT status, COUNT(*) as count
                   FROM purchase_orders
                   GROUP BY status
                   ''')
    status_stats = {row[0]: row[1] for row in cursor.fetchall()}

    # 按供应商统计
    cursor.execute('''
                   SELECT supplier, COUNT(*) as count
                   FROM purchase_orders
                   GROUP BY supplier
                   ''')
    supplier_stats = {row[0]: row[1] for row in cursor.fetchall()}

    # 总订单数和总数量
    cursor.execute('SELECT COUNT(*), SUM(quantity) FROM purchase_orders')
    total_stats = cursor.fetchone()

    conn.close()

    return jsonify({
        'status_stats': status_stats,
        'supplier_stats': supplier_stats,
        'total_orders': total_stats[0] or 0,
        'total_quantity': total_stats[1] or 0
    })


if __name__ == '__main__':
    init_db()
    app.run(port = 5001, debug = True)