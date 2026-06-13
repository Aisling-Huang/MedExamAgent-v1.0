@echo off
echo =========================================
echo    🩺  MedExamAgent 启动中...
echo =========================================

where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ 未找到 Python，请先安装 Python
    pause
    exit /b
)

python -c "import fastapi" >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 📦 正在安装依赖...
    pip install -r requirements.txt
)

REM 启动后端（默认 127.0.0.1）
echo 🔧 启动后端 (http://127.0.0.1:8000)...
start "MedExamAgent-Backend" python -m uvicorn api:app --host 127.0.0.1 --port 8000

timeout /t 3 /nobreak >nul

REM 启动前端（默认 127.0.0.1）
echo 🌐 启动前端 (http://127.0.0.1:3000)...
start "MedExamAgent-Frontend" python -m http.server 3000 --bind 127.0.0.1

echo.
echo ✅ 启动成功！
echo    本地访问: http://localhost:3000/app.html
echo.
echo 如需从手机或其他设备访问，请修改脚本中的 127.0.0.1 为 0.0.0.0
pause

start http://localhost:3000/app.html