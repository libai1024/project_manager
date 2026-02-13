#!/bin/bash

# Docker 管理脚本
# 用法: ./docker.sh [command]

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印信息
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker 未安装，请先安装 Docker"
    fi
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose 未安装，请先安装 Docker Compose"
    fi
}

# 创建环境文件
create_env() {
    if [ ! -f .env ]; then
        info "创建 .env 文件..."
        cp .env.example .env
        # 生成随机 SECRET_KEY
        if command -v openssl &> /dev/null; then
            SECRET_KEY=$(openssl rand -hex 32)
            if [[ "$OSTYPE" == "darwin"* ]]; then
                sed -i '' "s/your-super-secret-key-change-in-production/$SECRET_KEY/" .env
            else
                sed -i "s/your-super-secret-key-change-in-production/$SECRET_KEY/" .env
            fi
        fi
        info ".env 文件已创建"
    else
        info ".env 文件已存在，跳过创建"
    fi
}

# 构建镜像
build() {
    info "构建 Docker 镜像..."
    docker-compose build --no-cache
    info "构建完成"
}

# 启动服务
start() {
    check_docker
    create_env
    info "启动服务..."
    docker-compose up -d
    info "服务已启动"
    info "前端: http://localhost"
    info "后端 API: http://localhost:8000"
    info "API 文档: http://localhost:8000/docs"
}

# 停止服务
stop() {
    info "停止服务..."
    docker-compose down
    info "服务已停止"
}

# 重启服务
restart() {
    stop
    start
}

# 查看日志
logs() {
    docker-compose logs -f $@
}

# 进入后端容器
shell_backend() {
    docker-compose exec backend /bin/bash
}

# 进入前端容器
shell_frontend() {
    docker-compose exec frontend /bin/sh
}

# 清理
clean() {
    warn "这将删除所有容器、镜像和数据卷！"
    read -p "确定要继续吗？(y/N): " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        docker-compose down -v --rmi all
        info "清理完成"
    else
        info "已取消"
    fi
}

# 查看状态
status() {
    docker-compose ps
}

# 帮助信息
help() {
    echo "Docker 管理脚本"
    echo ""
    echo "用法: ./docker.sh [command]"
    echo ""
    echo "命令:"
    echo "  start       启动所有服务"
    echo "  stop        停止所有服务"
    echo "  restart     重启所有服务"
    echo "  build       构建 Docker 镜像"
    echo "  logs        查看日志 (可选: backend, frontend)"
    echo "  status      查看服务状态"
    echo "  shell-backend   进入后端容器"
    echo "  shell-frontend  进入前端容器"
    echo "  clean       清理所有容器、镜像和数据卷"
    echo "  help        显示帮助信息"
}

# 主命令
case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    build)
        build
        ;;
    logs)
        logs ${@:2}
        ;;
    status)
        status
        ;;
    shell-backend)
        shell_backend
        ;;
    shell-frontend)
        shell_frontend
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        help
        ;;
    *)
        if [ -n "$1" ]; then
            error "未知命令: $1"
        fi
        help
        ;;
esac
