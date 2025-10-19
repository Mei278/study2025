from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)

# 服务配置 - 确保端口正确
SERVICES = {
    'procurement': 'http://localhost:5001',
    'inspection': 'http://localhost:5002',
    'rejection': 'http://localhost:5003'
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/arrivals/')
def arrivals():
    try:
        response = requests.get(f"{SERVICES['procurement']}/api/purchase_orders", timeout = 5)
        if response.status_code == 200:
            arrivals_data = response.json()
            print(f"获取到采购数据: {len(arrivals_data)} 条记录")  # 调试信息
        else:
            print(f"采购服务返回错误: {response.status_code}")
            arrivals_data = []
    except Exception as e:
        print(f"调用采购服务失败: {e}")
        arrivals_data = []

    return render_template('arrivals.html', arrivals = arrivals_data)


@app.route('/inspections/')
def inspections():
    try:
        response = requests.get(f"{SERVICES['inspection']}/api/inspections", timeout = 5)
        if response.status_code == 200:
            inspections_data = response.json()
            print(f"获取到检验数据: {len(inspections_data)} 条记录")  # 调试信息
        else:
            print(f"检验服务返回错误: {response.status_code}")
            inspections_data = []
    except Exception as e:
        print(f"调用检验服务失败: {e}")
        inspections_data = []

    return render_template('inspections.html', inspections = inspections_data)


@app.route('/rejections/')
def rejections():
    try:
        response = requests.get(f"{SERVICES['rejection']}/api/rejections", timeout = 5)
        if response.status_code == 200:
            rejections_data = response.json()
        else:
            rejections_data = []
    except:
        rejections_data = []

    return render_template('rejections.html', rejections = rejections_data)


@app.route('/inspection_form/<int:order_id>')
def inspection_form(order_id):
    try:
        response = requests.get(f"{SERVICES['procurement']}/api/purchase_orders/{order_id}", timeout = 5)
        if response.status_code == 200:
            order_data = response.json()
            return render_template('inspection_form.html', order = order_data)
        else:
            return render_template('error.html', message = '订单不存在或获取失败')
    except Exception as e:
        print(f"获取订单信息失败: {e}")
        return render_template('error.html', message = f'服务连接失败: {str(e)}')


@app.route('/submit_inspection', methods = ['POST'])
def submit_inspection():
    try:
        # 准备检验数据
        data = {
            'order_id': int(request.form.get('order_id')),
            'order_number': request.form.get('order_number'),
            'product_name': request.form.get('product_name'),
            'inspector': request.form.get('inspector'),
            'result': request.form.get('result'),
            'check_items': json.loads(request.form.get('check_items', '[]')),
            'unqualified_items': json.loads(request.form.get('unqualified_items', '[]')),
            'notes': request.form.get('notes', ''),
            'quantity': int(request.form.get('quantity', 0))
        }

        print(f"提交检验数据: {data}")  # 调试信息

        # 调用检验服务
        response = requests.post(
            f"{SERVICES['inspection']}/api/inspections",
            json = data,
            timeout = 10
        )

        if response.status_code == 201:
            return render_template('success.html', message = '检验记录提交成功')
        else:
            error_msg = response.json().get('error', '未知错误')
            print(f"检验服务返回错误: {error_msg}")
            return render_template('error.html', message = f'提交失败: {error_msg}')

    except Exception as e:
        print(f"提交检验记录失败: {e}")
        return render_template('error.html', message = f'服务错误: {str(e)}')


if __name__ == '__main__':
    app.run(port = 5000, debug = True)