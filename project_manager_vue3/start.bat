@echo off
REM 毕设代做管理系统 - 前端启动脚本 (Windows)

echo ==========================================
echo   毕设代做管理系统 - 前端启动脚本
echo ==========================================
echo.

REM 检查Node.js是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Node.js，请先安装 Node.js 16+
    pause
    exit /b 1
)

REM 检查npm是否安装
npm --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 npm，请先安装 npm
    pause
    exit /b 1
)

echo [OK] Node.js 版本:
node --version
echo [OK] npm 版本:
npm --version
echo.

REM 检查package.json是否存在
if not exist "package.json" (
    echo [错误] 未找到 package.json 文件
    pause
    exit /b 1
)

REM 检查node_modules是否存在
if not exist "node_modules" (
    echo [安装] 安装项目依赖（首次运行可能需要几分钟）...
    call npm install
    echo [OK] 依赖安装完成
    echo.
) else (
    echo [检查] 检查依赖更新...
    call npm install
    echo [OK] 依赖检查完成
    echo.
)

REM 启动开发服务器
echo [启动] 启动前端开发服务器...
echo [地址] 前端: http://localhost:5173
echo [地址] 后端API: http://localhost:8000
echo.
echo [提示] 请确保后端服务已启动（运行 fastapi_back\start.bat）
echo.
echo 按 Ctrl+C 停止服务
echo ==========================================
echo.

call npm run dev

