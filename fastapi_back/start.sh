#!/bin/bash

# 毕设代做管理系统 - 后端启动脚本

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  毕设代做管理系统 - 后端启动脚本"
echo "=========================================="
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 Python3，请先安装 Python 3.8+"
    exit 1
fi

echo "✅ Python 版本: $(python3 --version)"
echo ""

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建成功"
    echo ""
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate
echo "✅ 虚拟环境已激活"
echo ""

# 升级pip
echo "📦 升级 pip..."
pip install --upgrade pip -q
echo "✅ pip 升级完成"
echo ""

# 检查requirements.txt是否存在
if [ ! -f "requirements.txt" ]; then
    echo "❌ 错误: 未找到 requirements.txt 文件"
    exit 1
fi

# 安装依赖
echo "📦 安装项目依赖..."
pip install -r requirements.txt --upgrade
echo "✅ 依赖安装完成"
echo ""

# 检查数据库是否存在，如果不存在则初始化
if [ ! -f "project_manager.db" ]; then
    echo "🗄️  初始化数据库..."
    PYTHONPATH=. python -m app.init_db
    echo "✅ 数据库初始化完成"
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

# 启动服务
echo "🚀 启动 FastAPI 服务..."
echo "📍 API 文档地址（本地）: http://localhost:8000/docs"
echo "📍 ReDoc 文档（本地）: http://localhost:8000/redoc"
if [ ! -z "$LOCAL_IP" ]; then
    echo "📍 API 文档地址（局域网）: http://$LOCAL_IP:8000/docs"
    echo "📍 ReDoc 文档（局域网）: http://$LOCAL_IP:8000/redoc"
fi
echo ""
echo "💡 提示: 服务已绑定到 0.0.0.0，局域网内其他设备可通过上述IP地址访问"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

# 启动 uvicorn，支持大文件上传（1GB）
# --limit-max-requests: 最大并发请求数（默认1000）
# --timeout-keep-alive: 保持连接超时时间（秒），增加到30分钟以支持大文件上传
# 注意：文件上传使用流式处理，不会一次性加载到内存
uvicorn main:app --reload --host 0.0.0.0 --port 8000 --timeout-keep-alive 1800
