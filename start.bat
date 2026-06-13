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

echo 🔧 启动后端 (http://127.0.0.1:8000)...
start "MedExamAgent-Backend" python -m uvicorn api:app --host 127.0.0.1 --port 8000

timeout /t 3 /nobreak >nul

echo 🌐 启动前端 (http://127.0.0.1:3000)...
start "MedExamAgent-Frontend" python -m http.server 3000 --bind 127.0.0.1

echo.
echo ✅ 启动成功！
echo    封面入口: http://localhost:3000/preview.html
echo.

:: 尝试多种方式打开浏览器
set "URL=http://localhost:3000/preview.html"

:: 方法1：explorer（通常有效）
explorer "%URL%" 2>nul
if %ERRORLEVEL% EQU 0 goto :done

:: 方法2：start 直接打开默认浏览器
start "" "%URL%" 2>nul
if %ERRORLEVEL% EQU 0 goto :done

:: 方法3：指定 Chrome 路径（如果存在）
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "%URL%"
    goto :done
)

:: 方法4：指定 Edge 路径（Windows 10/11 自带）
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" "%URL%"
    goto :done
)

:: 全部失败，提示手动打开
echo ⚠️  无法自动打开浏览器，请手动访问上述地址。
goto :eof

:done
echo 🌐 浏览器正在打开封面页面...
pause