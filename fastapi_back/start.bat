@echo off
REM 毕设代做管理系统 - 后端启动脚本 (Windows)

echo ==========================================
echo   毕设代做管理系统 - 后端启动脚本
echo ==========================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [OK] Python 版本:
python --version
echo.

REM 检查是否存在虚拟环境
if not exist "venv" (
    echo [创建] 创建虚拟环境...
    python -m venv venv
    echo [OK] 虚拟环境创建成功
    echo.
)

REM 激活虚拟环境
echo [激活] 激活虚拟环境...
call venv\Scripts\activate.bat
echo [OK] 虚拟环境已激活
echo.

REM 升级pip
echo [升级] 升级 pip...
python -m pip install --upgrade pip -q
echo [OK] pip 升级完成
echo.

REM 检查requirements.txt是否存在
if not exist "requirements.txt" (
    echo [错误] 未找到 requirements.txt 文件
    pause
    exit /b 1
)

REM 安装依赖
echo [安装] 安装项目依赖...
pip install -r requirements.txt --upgrade
echo [OK] 依赖安装完成
echo.

REM 检查数据库是否存在，如果不存在则初始化
if not exist "project_manager.db" (
    echo [初始化] 初始化数据库...
    set PYTHONPATH=.
    python -m app.init_db
    echo [OK] 数据库初始化完成
    echo.
)

REM 启动服务
echo [启动] 启动 FastAPI 服务...
echo [地址] API 文档: http://localhost:8000/docs
echo [地址] ReDoc 文档: http://localhost:8000/redoc
echo.
echo 按 Ctrl+C 停止服务
echo ==========================================
echo.

REM 启动 uvicorn，支持大文件上传（1GB）
REM --timeout-keep-alive: 保持连接超时时间（秒），增加到30分钟以支持大文件上传
REM 注意：文件上传使用流式处理，不会一次性加载到内存
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --timeout-keep-alive 1800
