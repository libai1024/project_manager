#!/bin/bash
# 修复依赖版本冲突的脚本

echo "=========================================="
echo "  修复 FastAPI 依赖版本冲突"
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
echo "📦 卸载冲突的包..."
pip uninstall -y pydantic pydantic-settings fastapi 2>/dev/null || true

echo ""
echo "📦 安装正确版本的依赖..."
pip install pydantic==1.10.13
pip install pydantic-settings==1.10.1
pip install fastapi==0.104.1

echo ""
echo "📦 安装其他依赖..."
pip install -r requirements.txt

echo ""
echo "✅ 依赖修复完成！"
echo ""
echo "现在可以重新启动服务："
echo "  ./start.sh"

