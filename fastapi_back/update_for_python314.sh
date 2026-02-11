#!/bin/bash
# 为 Python 3.14 更新依赖

echo "=========================================="
echo "  为 Python 3.14 更新依赖"
echo "=========================================="
echo ""

# 激活虚拟环境
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "❌ 未找到虚拟环境，请先运行 start.sh"
    exit 1
fi

echo ""
echo "📦 升级 pip 和构建工具..."
pip install --upgrade pip setuptools wheel

echo ""
echo "📦 卸载旧版本依赖..."
pip uninstall -y pydantic pydantic-settings fastapi uvicorn sqlmodel pyyaml 2>/dev/null || true

echo ""
echo "📦 安装兼容 Python 3.14 的依赖..."
pip install --upgrade \
    fastapi>=0.115.0 \
    uvicorn[standard]>=0.32.0 \
    sqlmodel>=0.0.22 \
    python-jose[cryptography]>=3.3.0 \
    passlib[bcrypt]>=1.7.4 \
    bcrypt>=4.2.0 \
    python-multipart>=0.0.12 \
    pydantic>=2.9.0 \
    pydantic-settings>=2.5.0 \
    pyyaml>=6.0.1

echo ""
echo "✅ 依赖更新完成！"
echo ""
echo "现在可以重新启动服务："
echo "  ./start.sh"

