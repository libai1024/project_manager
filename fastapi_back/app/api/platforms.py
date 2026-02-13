"""
平台管理API路由层（重构后）
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.services.platform_service import PlatformService
from app.models.user import User
from app.models.platform import PlatformRead, PlatformCreate, PlatformUpdate
from app.api.responses import ApiResponse, success

router = APIRouter()


@router.get("/", response_model=ApiResponse[List[PlatformRead]])
async def list_platforms(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有平台列表"""
    platform_service = PlatformService(session)
    platforms = platform_service.list_platforms()
    return success(platforms)


@router.post("/", response_model=ApiResponse[PlatformRead])
async def create_platform(
    platform_data: PlatformCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建平台"""
    platform_service = PlatformService(session)
    platform = platform_service.create_platform(platform_data)
    return success(platform, msg="平台创建成功")


@router.get("/{platform_id}", response_model=ApiResponse[PlatformRead])
async def get_platform(
    platform_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取平台详情"""
    platform_service = PlatformService(session)
    platform = platform_service.get_platform_by_id(platform_id)
    return success(platform)


@router.put("/{platform_id}", response_model=ApiResponse[PlatformRead])
async def update_platform(
    platform_id: int,
    platform_data: PlatformUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新平台信息"""
    platform_service = PlatformService(session)
    platform = platform_service.update_platform(platform_id, platform_data)
    return success(platform, msg="平台更新成功")


@router.delete("/{platform_id}", response_model=ApiResponse[None])
async def delete_platform(
    platform_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除平台"""
    platform_service = PlatformService(session)
    platform_service.delete_platform(platform_id)
    return success(msg="平台删除成功")
