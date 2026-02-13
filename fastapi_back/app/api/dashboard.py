"""
Dashboard API路由层（重构后）
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.services.dashboard_service import DashboardService, DashboardStats
from app.models.user import User
from app.api.responses import ApiResponse, success

router = APIRouter()


@router.get("/stats", response_model=ApiResponse[DashboardStats])
async def get_dashboard_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取Dashboard统计数据"""
    dashboard_service = DashboardService(session)
    stats = dashboard_service.get_dashboard_stats(
        user_id=current_user.id if current_user.role != "admin" else None,
        is_admin=(current_user.role == "admin")
    )
    return success(stats)
