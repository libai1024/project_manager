#!/bin/bash

# 毕设代做管理系统 - 一键启动脚本（同时启动前后端）

echo "=========================================="
echo "  毕设代做管理系统 - 一键启动"
echo "=========================================="
echo ""

# 检查是否在项目根目录
if [ ! -d "fastapi_back" ] || [ ! -d "project_manager_vue3" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 启动后端（后台运行）
echo "🚀 启动后端服务..."
cd fastapi_back
bash start.sh > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"
echo "   日志文件: logs/backend.log"
echo ""

# 等待后端启动
echo "⏳ 等待后端服务启动..."
sleep 5

# 启动前端（前台运行）
echo "🚀 启动前端服务..."
cd project_manager_vue3
bash start.sh > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"
echo "   日志文件: logs/frontend.log"
echo ""

echo "=========================================="
echo "  服务启动完成！"
echo "=========================================="
echo "📍 前端地址: http://localhost:5173"
echo "📍 后端API: http://localhost:8000"
echo "📍 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止所有服务"
echo ""

# 等待用户中断
trap "echo ''; echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# 保持脚本运行
wait

