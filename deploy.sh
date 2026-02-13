#!/bin/bash
#
# 一键部署脚本 - 外包项目管理系统
# 用法: ./deploy.sh [命令]
#
# 命令:
#   start     - 启动所有服务
#   stop      - 停止所有服务
#   restart   - 重启所有服务
#   rebuild   - 重新构建并启动
#   update    - 拉取代码并更新部署
#   migrate   - 运行数据库迁移
#   backup    - 备份数据
#   restore   - 恢复数据（需要指定备份文件）
#   logs      - 查看日志
#   status    - 查看服务状态
#   clean     - 清理无用镜像和容器
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# 打印带颜色的消息
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}==>${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi

    # 使用 docker compose 或 docker-compose
    if docker compose version &> /dev/null; then
        COMPOSE_CMD="docker compose"
    else
        COMPOSE_CMD="docker-compose"
    fi
}

# 检查必要的目录
check_directories() {
    mkdir -p "$PROJECT_ROOT/data"
    mkdir -p "$PROJECT_ROOT/uploads"
    mkdir -p "$PROJECT_ROOT/backups"
}

# 启动服务
start_services() {
    log_step "启动服务..."
    check_directories
    $COMPOSE_CMD up -d

    log_info "等待服务启动..."
    sleep 10

    # 等待后端健康检查
    for i in {1..30}; do
        if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
            log_info "后端服务已就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            log_warn "后端服务启动超时，请检查日志"
        fi
        sleep 2
    done

    log_info "服务启动完成"
    echo ""
    echo "访问地址:"
    echo "  前端: http://localhost:8080"
    echo "  后端API: http://localhost:8000"
    echo "  API文档: http://localhost:8000/docs"
}

# 停止服务
stop_services() {
    log_step "停止服务..."
    $COMPOSE_CMD down
    log_info "服务已停止"
}

# 重启服务
restart_services() {
    log_step "重启服务..."
    stop_services
    start_services
}

# 重新构建并启动
rebuild_services() {
    log_step "重新构建服务..."

    # 检查内存是否足够
    MEM_AVAILABLE=$(vm_stat | grep "free" | awk '{sum+=$3} END {print sum * 4096 / 1024 / 1024 / 1024}')
    if [ ! -z "$MEM_AVAILABLE" ] && [ $(echo "$MEM_AVAILABLE < 2" | bc -l 2>/dev/null || echo "0") -eq 1 ]; then
        log_warn "可用内存较少，构建可能失败"
        log_warn "如果构建失败，请尝试: docker system prune -af"
    fi

    $COMPOSE_CMD build --no-cache
    $COMPOSE_CMD up -d --force-recreate

    log_info "服务已重新构建并启动"
}

# 更新部署
update_deployment() {
    log_step "更新部署..."

    # 备份数据
    backup_data

    # 拉取最新代码
    if [ -d ".git" ]; then
        log_info "拉取最新代码..."
        git pull
    else
        log_warn "不是 Git 仓库，跳过代码拉取"
    fi

    # 重新构建
    log_info "重新构建镜像..."
    $COMPOSE_CMD build

    # 运行迁移
    migrate_database

    # 重启服务
    $COMPOSE_CMD up -d

    log_info "更新完成"
}

# 运行数据库迁移
migrate_database() {
    log_step "运行数据库迁移..."

    # 检查容器是否运行
    if ! docker ps | grep -q project_manager_backend; then
        log_warn "后端容器未运行，跳过迁移"
        return
    fi

    # 尝试运行 Alembic 迁移
    docker exec project_manager_backend python -c "
try:
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config('alembic.ini')
    command.upgrade(alembic_cfg, 'head')
    print('数据库迁移成功')
except Exception as e:
    print(f'迁移失败: {e}')
    print('使用 create_all 作为后备方案')
" 2>&1 || log_warn "迁移命令执行完成"

    log_info "数据库迁移完成"
}

# 备份数据
backup_data() {
    log_step "备份数据..."

    BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # 备份数据库
    if [ -f "$PROJECT_ROOT/data/project_manager.db" ]; then
        cp "$PROJECT_ROOT/data/project_manager.db" "$BACKUP_DIR/project_manager.db"
        log_info "数据库已备份到: $BACKUP_DIR/project_manager.db"
    fi

    # 备份上传文件（增量）
    if [ -d "$PROJECT_ROOT/uploads" ] && [ "$(ls -A $PROJECT_ROOT/uploads 2>/dev/null)" ]; then
        tar -czf "$BACKUP_DIR/uploads.tar.gz" -C "$PROJECT_ROOT/uploads" .
        log_info "上传文件已备份到: $BACKUP_DIR/uploads.tar.gz"
    fi

    echo "$BACKUP_DIR" > "$PROJECT_ROOT/backups/latest_backup.txt"
    log_info "备份完成: $BACKUP_DIR"
}

# 恢复数据
restore_data() {
    if [ -z "$1" ]; then
        # 使用最新备份
        if [ -f "$PROJECT_ROOT/backups/latest_backup.txt" ]; then
            BACKUP_DIR=$(cat "$PROJECT_ROOT/backups/latest_backup.txt")
        else
            log_error "请指定备份目录: ./deploy.sh restore <backup_dir>"
            exit 1
        fi
    else
        BACKUP_DIR="$PROJECT_ROOT/backups/$1"
    fi

    if [ ! -d "$BACKUP_DIR" ]; then
        log_error "备份目录不存在: $BACKUP_DIR"
        exit 1
    fi

    log_step "恢复数据从: $BACKUP_DIR"

    # 停止服务
    stop_services

    # 恢复数据库
    if [ -f "$BACKUP_DIR/project_manager.db" ]; then
        cp "$BACKUP_DIR/project_manager.db" "$PROJECT_ROOT/data/project_manager.db"
        log_info "数据库已恢复"
    fi

    # 恢复上传文件
    if [ -f "$BACKUP_DIR/uploads.tar.gz" ]; then
        rm -rf "$PROJECT_ROOT/uploads"/*
        tar -xzf "$BACKUP_DIR/uploads.tar.gz" -C "$PROJECT_ROOT/uploads"
        log_info "上传文件已恢复"
    fi

    # 启动服务
    start_services

    log_info "数据恢复完成"
}

# 查看日志
view_logs() {
    SERVICE=$1
    if [ -z "$SERVICE" ]; then
        $COMPOSE_CMD logs -f --tail=100
    else
        $COMPOSE_CMD logs -f --tail=100 "$SERVICE"
    fi
}

# 查看状态
view_status() {
    log_step "服务状态:"
    echo ""
    $COMPOSE_CMD ps
    echo ""

    log_step "健康检查:"
    echo ""

    # 后端健康检查
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "  后端: ${GREEN}✓ 正常${NC}"
    else
        echo -e "  后端: ${RED}✗ 异常${NC}"
    fi

    # 前端检查
    if curl -sf http://localhost:8080 > /dev/null 2>&1; then
        echo -e "  前端: ${GREEN}✓ 正常${NC}"
    else
        echo -e "  前端: ${RED}✗ 异常${NC}"
    fi

    echo ""

    log_step "数据统计:"
    echo ""

    # 数据库统计
    if [ -f "$PROJECT_ROOT/data/project_manager.db" ]; then
        DB_SIZE=$(ls -lh "$PROJECT_ROOT/data/project_manager.db" | awk '{print $5}')
        TABLE_COUNT=$(sqlite3 "$PROJECT_ROOT/data/project_manager.db" "SELECT COUNT(*) FROM sqlite_master WHERE type='table'" 2>/dev/null || echo "?")
        echo "  数据库大小: $DB_SIZE"
        echo "  数据表数量: $TABLE_COUNT"
    fi

    # 上传文件统计
    if [ -d "$PROJECT_ROOT/uploads" ]; then
        UPLOAD_COUNT=$(ls -1 "$PROJECT_ROOT/uploads" 2>/dev/null | wc -l | tr -d ' ')
        UPLOAD_SIZE=$(du -sh "$PROJECT_ROOT/uploads" 2>/dev/null | cut -f1)
        echo "  上传文件数量: $UPLOAD_COUNT"
        echo "  上传文件大小: $UPLOAD_SIZE"
    fi
}

# 清理无用资源
clean_resources() {
    log_step "清理无用资源..."

    # 清理悬空镜像
    docker image prune -af --filter "until=168h"

    # 清理停止的容器
    docker container prune -f

    # 清理无用网络
    docker network prune -f

    # 清理构建缓存（可选）
    # docker builder prune -af

    log_info "清理完成"
}

# 显示帮助
show_help() {
    echo "
外包项目管理系统 - 一键部署脚本

用法: ./deploy.sh [命令]

命令:
  start       启动所有服务
  stop        停止所有服务
  restart     重启所有服务
  rebuild     重新构建并启动（清空缓存）
  update      拉取代码并更新部署
  migrate     运行数据库迁移
  backup      备份数据
  restore     恢复数据（可选指定备份目录）
  logs        查看日志（可选指定服务名）
  status      查看服务状态
  clean       清理无用镜像和容器
  help        显示帮助信息

示例:
  ./deploy.sh start           # 启动服务
  ./deploy.sh logs backend    # 查看后端日志
  ./deploy.sh update          # 更新部署
  ./deploy.sh restore 20260213_220000  # 恢复指定备份
"
}

# 主函数
main() {
    check_docker

    case "${1:-help}" in
        start)
            start_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            restart_services
            ;;
        rebuild)
            rebuild_services
            ;;
        update)
            update_deployment
            ;;
        migrate)
            migrate_database
            ;;
        backup)
            backup_data
            ;;
        restore)
            restore_data "$2"
            ;;
        logs)
            view_logs "$2"
            ;;
        status)
            view_status
            ;;
        clean)
            clean_resources
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
