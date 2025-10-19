# run_all.py
import subprocess
import time
import sys
import os

# 把当前文件夹（项目根目录）加入 Python 模块搜索路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

services = [
    ("procurement_service.main:app", 8001),
    ("inspection_service.main:app", 8002),
    ("rejection_service.main:app", 8003),
    ("frontend_service.main:app", 8000),
]

procs = []
for svc, port in services:
    cmd = ["uvicorn", svc, "--port", str(port), "--reload"]
    print(f"🚀 启动服务 {svc} (端口 {port}) ...")
    procs.append(subprocess.Popen(cmd))
    time.sleep(1)

print("✅ 所有服务已启动！访问示例：")
print(" - 采购到货: http://127.0.0.1:8001/docs")
print(" - 质量检验: http://127.0.0.1:8002/docs")
print(" - 不合格品: http://127.0.0.1:8003/docs")

try:
    for p in procs:
        p.wait()
except KeyboardInterrupt:
    print("⛔ 停止所有服务中...")
    for p in procs:
        p.terminate()
