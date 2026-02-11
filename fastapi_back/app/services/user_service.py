"""
用户服务层
"""
from typing import Optional, List
from sqlmodel import Session
from fastapi import HTTPException, status
from app.repositories.user_repository import UserRepository
from app.models.user import User, UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserService:
    """用户服务层"""
    
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)
    
    def create_user(self, user_data: UserCreate) -> User:
        """创建用户"""
        # 检查用户名是否已存在
        if self.user_repo.exists_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # 加密密码
        password_hash = get_password_hash(user_data.password)
        
        # 创建用户
        return self.user_repo.create(user_data, password_hash)
    
    def get_user_by_id(self, user_id: int) -> User:
        """根据ID获取用户"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        return self.user_repo.get_by_username(username)
    
    def list_users(self) -> List[User]:
        """获取所有用户列表"""
        return self.user_repo.list_all()
    
    def update_user(self, user_id: int, user_data: UserUpdate, current_user: User) -> User:
        """更新用户信息"""
        user = self.get_user_by_id(user_id)
        
        # 保护 admin 账户的角色
        if user.username == "admin" and user_data.role and user_data.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change admin user's role"
            )
        
        # 不能修改自己的角色
        if user.id == current_user.id and user_data.role and user_data.role != user.role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot change your own role"
            )
        
        update_data = user_data.model_dump(exclude_unset=True)
        
        # 如果提供了新密码，需要加密
        if "password" in update_data:
            update_data["password_hash"] = get_password_hash(update_data.pop("password"))
        
        return self.user_repo.update(user, update_data)
    
    def delete_user(self, user_id: int, current_user: User) -> None:
        """删除用户"""
        user = self.get_user_by_id(user_id)
        
        # 保护 admin 账户
        if user.username == "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete admin user"
            )
        
        # 不能删除自己
        if user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete yourself"
            )
        
        self.user_repo.delete(user)

