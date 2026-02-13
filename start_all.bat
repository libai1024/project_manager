@echo off
REM 外包项目管理系统 - 一键启动脚本（同时启动前后端）(Windows)

echo ==========================================
echo   外包项目管理系统 - 一键启动
echo ==========================================
echo.

REM 检查是否在项目根目录
if not exist "fastapi_back" (
    echo [错误] 请在项目根目录运行此脚本
    pause
    exit /b 1
)

if not exist "project_manager_vue3" (
    echo [错误] 请在项目根目录运行此脚本
    pause
    exit /b 1
)

REM 创建日志目录
if not exist "logs" mkdir logs

REM 启动后端（新窗口）
echo [启动] 启动后端服务...
start "后端服务" cmd /k "cd fastapi_back && start.bat"
timeout /t 3 /nobreak >nul
echo [OK] 后端服务已启动
echo.

REM 启动前端（新窗口）
echo [启动] 启动前端服务...
start "前端服务" cmd /k "cd project_manager_vue3 && start.bat"
echo [OK] 前端服务已启动
echo.

echo ==========================================
echo   服务启动完成！
echo ==========================================
echo [地址] 前端: http://localhost:5173
echo [地址] 后端API: http://localhost:8000
echo [地址] API文档: http://localhost:8000/docs
echo.
echo [提示] 服务已在独立窗口中运行，关闭窗口即可停止服务
echo.
pause

