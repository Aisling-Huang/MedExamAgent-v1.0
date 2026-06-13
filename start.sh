#!/bin/bash
echo "========================================="
echo "   🩺  MedExamAgent 启动中..."
echo "========================================="

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python"
    exit 1
fi

# 检查依赖
if ! python3 -c "import fastapi" &> /dev/null; then
    echo "📦 正在安装依赖..."
    pip install -r requirements.txt
fi

# 启动后端（默认监听 127.0.0.1，如需局域网访问请改为 0.0.0.0）
echo "🔧 启动后端 (http://127.0.0.1:8000)..."
python3 -m uvicorn api:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

sleep 2

# 启动前端（同样默认监听 127.0.0.1）
echo "🌐 启动前端 (http://127.0.0.1:3000)..."
python3 -m http.server 3000 --bind 127.0.0.1 &
FRONTEND_PID=$!

echo ""
echo "✅ 启动成功！"
echo "   本地访问: http://localhost:3000/app.html"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 打开浏览器（可选）
if command -v open &> /dev/null; then
    open http://localhost:3000/app.html
fi

wait $BACKEND_PID $FRONTEND_PID