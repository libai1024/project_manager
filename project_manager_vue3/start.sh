#!/bin/bash

# 外包项目管理系统 - 前端启动脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  外包项目管理系统 - 前端启动脚本"
echo "=========================================="
echo ""

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "❌ 错误: 未找到 Node.js，请先安装 Node.js 16+"
    exit 1
fi

# 检查npm是否安装
if ! command -v npm &> /dev/null; then
    echo "❌ 错误: 未找到 npm，请先安装 npm"
    exit 1
fi

echo "✅ Node.js 版本: $(node --version)"
echo "✅ npm 版本: $(npm --version)"
echo ""

# 检查package.json是否存在
if [ ! -f "package.json" ]; then
    echo "❌ 错误: 未找到 package.json 文件"
    exit 1
fi

# 检查node_modules是否存在
if [ ! -d "node_modules" ]; then
    echo "📦 安装项目依赖（首次运行可能需要几分钟）..."
    npm install
    echo "✅ 依赖安装完成"
    echo ""
else
    echo "📦 检查依赖更新..."
    npm install
    echo "✅ 依赖检查完成"
    echo ""
fi

# 获取本机IP地址（用于局域网访问）
get_local_ip() {
    # macOS/Linux
    if [[ "$OSTYPE" == "darwin"* ]] || [[ "$OSTYPE" == "linux-gnu"* ]]; then
        ip=$(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1' | head -n 1)
        if [ -z "$ip" ]; then
            ip=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "")
        fi
    else
        ip=""
    fi
    echo "$ip"
}

LOCAL_IP=$(get_local_ip)

# 启动开发服务器
echo "🚀 启动前端开发服务器..."
echo "📍 本地地址: http://localhost:5173"
if [ ! -z "$LOCAL_IP" ]; then
    echo "📍 局域网地址: http://$LOCAL_IP:5173"
fi
echo "📍 后端API: http://localhost:8000"
if [ ! -z "$LOCAL_IP" ]; then
    echo "📍 后端API（局域网）: http://$LOCAL_IP:8000"
fi
echo ""
echo "⚠️  请确保后端服务已启动（运行 fastapi_back/start.sh）"
echo ""
echo "💡 提示: 局域网内其他设备可通过上述IP地址访问"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

npm run dev

