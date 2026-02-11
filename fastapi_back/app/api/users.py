"""
用户管理API路由层（重构后）
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_admin_user
from app.services.user_service import UserService
from app.models.user import User, UserRead, UserUpdate

router = APIRouter()


@router.get("/", response_model=List[UserRead])
async def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """获取所有用户列表（仅管理员）"""
    user_service = UserService(session)
    return user_service.list_users()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """获取用户详情（仅管理员）"""
    user_service = UserService(session)
    return user_service.get_user_by_id(user_id)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """更新用户信息（仅管理员）"""
    user_service = UserService(session)
    return user_service.update_user(user_id, user_data, current_user)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """删除用户（仅管理员）"""
    user_service = UserService(session)
    user_service.delete_user(user_id, current_user)
    return {"message": "User deleted successfully"}
