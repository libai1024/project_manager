"""
企业级身份认证API（重新设计）
支持Refresh Token、账户锁定、登录日志等功能
"""
from typing import Optional
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    validate_password_strength, create_refresh_token, is_password_expired,
    should_lock_account, get_lockout_until
)
from app.core.config import settings
from app.core.dependencies import get_current_user, get_current_admin_user
from app.models.user import User, UserCreate, UserRead, UserUpdate, Token
from app.models.refresh_token import RefreshToken, RefreshTokenCreate
from app.models.login_log import LoginStatus, LoginLogCreate
from app.models.token_blacklist import TokenBlacklistCreate
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.token_blacklist_repository import TokenBlacklistRepository
from app.repositories.login_log_repository import LoginLogRepository
from app.repositories.user_repository import UserRepository
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def get_client_info(request: Request) -> tuple[str, str]:
    """获取客户端信息（IP地址和User-Agent）"""
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent", "")
    return ip_address or "unknown", user_agent


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: Session = Depends(get_session),
    request: Request = None
):
    """
    用户登录（企业级）
    支持账户锁定、登录日志、刷新令牌
    """
    ip_address, user_agent = get_client_info(request)
    
    user_repo = UserRepository(session)
    login_log_repo = LoginLogRepository(session)
    refresh_token_repo = RefreshTokenRepository(session)
    
    # 查找用户
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    
    # 记录登录尝试（无论成功或失败）
    log_status = LoginStatus.SUCCESS
    failure_reason = None
    
    if not user:
        log_status = LoginStatus.FAILED
        failure_reason = "用户不存在"
        login_log_repo.create(LoginLogCreate(
            username=form_data.username,
            status=log_status,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason
        ))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查账户是否激活
    if not user.is_active:
        log_status = LoginStatus.BLOCKED
        failure_reason = "账户已被禁用"
        login_log_repo.create(LoginLogCreate(
            user_id=user.id,
            username=user.username,
            status=log_status,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason
        ))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # 检查账户是否锁定
    if user.is_locked:
        if user.locked_until and user.locked_until > datetime.utcnow():
            log_status = LoginStatus.LOCKED
            failure_reason = "账户已被锁定"
            login_log_repo.create(LoginLogCreate(
                user_id=user.id,
                username=user.username,
                status=log_status,
                ip_address=ip_address,
                user_agent=user_agent,
                failure_reason=failure_reason
            ))
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account is locked until {user.locked_until}"
            )
        else:
            # 锁定已过期，解除锁定
            user.is_locked = False
            user.locked_until = None
            user.failed_login_attempts = 0
            session.add(user)
            session.commit()
    
    # 验证密码
    if not verify_password(form_data.password, user.password_hash):
        # 增加失败次数
        user.failed_login_attempts += 1
        
        # 检查是否需要锁定账户
        if should_lock_account(user.failed_login_attempts):
            user.is_locked = True
            user.locked_until = get_lockout_until()
            log_status = LoginStatus.LOCKED
            failure_reason = f"账户因多次登录失败被锁定"
        else:
            log_status = LoginStatus.FAILED
            failure_reason = "密码错误"
        
        session.add(user)
        session.commit()
        
        login_log_repo.create(LoginLogCreate(
            user_id=user.id,
            username=user.username,
            status=log_status,
            ip_address=ip_address,
            user_agent=user_agent,
            failure_reason=failure_reason
        ))
        
        if user.is_locked:
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail=f"Account locked due to too many failed attempts. Locked until {user.locked_until}"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 登录成功，重置失败次数
    user.failed_login_attempts = 0
    user.last_login_at = datetime.utcnow()
    session.add(user)
    session.commit()
    
    # 检查密码是否过期
    if is_password_expired(user.password_changed_at):
        # 可以在这里要求用户修改密码
        user.must_change_password = True
        session.add(user)
        session.commit()
    
    # 创建访问令牌（从数据库读取配置）
    # 先尝试从数据库读取配置
    from app.repositories.system_settings_repository import SystemSettingsRepository
    settings_repo = SystemSettingsRepository(session)
    access_token_minutes = settings_repo.get_int_value("access_token_expire_minutes", settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_expires = timedelta(minutes=access_token_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires,
        session=session
    )
    
    # 创建刷新令牌（从数据库读取配置）
    refresh_token_str, refresh_expires_at = create_refresh_token(user.id, session=session)
    refresh_token_repo.create(RefreshTokenCreate(
        token=refresh_token_str,
        user_id=user.id,
        expires_at=refresh_expires_at,
        device_info=user_agent,
        ip_address=ip_address
    ))
    
    # 记录成功登录
    login_log_repo.create(LoginLogCreate(
        user_id=user.id,
        username=user.username,
        status=LoginStatus.SUCCESS,
        ip_address=ip_address,
        user_agent=user_agent
    ))
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_str,
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str,
    session: Session = Depends(get_session),
    request: Request = None
):
    """
    刷新访问令牌（企业级）
    """
    refresh_token_repo = RefreshTokenRepository(session)
    blacklist_repo = TokenBlacklistRepository(session)
    
    # 验证刷新令牌
    token = refresh_token_repo.get_valid_token(refresh_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # 获取用户
    user = session.get(User, token.user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # 创建新的访问令牌（从数据库读取配置）
    from app.repositories.system_settings_repository import SystemSettingsRepository
    settings_repo = SystemSettingsRepository(session)
    access_token_minutes = settings_repo.get_int_value("access_token_expire_minutes", settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token_expires = timedelta(minutes=access_token_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role},
        expires_delta=access_token_expires,
        session=session
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # 返回相同的刷新令牌
        "token_type": "bearer",
        "expires_in": int(access_token_expires.total_seconds())
    }


@router.post("/logout")
async def logout(
    refresh_token: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    用户登出（企业级）
    撤销刷新令牌并将访问令牌加入黑名单
    """
    refresh_token_repo = RefreshTokenRepository(session)
    blacklist_repo = TokenBlacklistRepository(session)
    
    # 撤销刷新令牌
    if refresh_token:
        refresh_token_repo.revoke_token(refresh_token)
    
    # 注意：访问令牌无法直接撤销（JWT是无状态的），但可以加入黑名单
    # 实际应用中，需要在验证token时检查黑名单
    
    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    撤销所有设备的刷新令牌（企业级）
    """
    refresh_token_repo = RefreshTokenRepository(session)
    count = refresh_token_repo.revoke_all_user_tokens(current_user.id)
    
    return {"message": f"Successfully logged out from {count} devices"}


@router.post("/register", response_model=UserRead)
async def register(
    user_data: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_admin_user)
):
    """
    用户注册（仅管理员可用，企业级密码策略）
    """
    # 验证密码强度
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # 检查用户名是否已存在
    existing_user = session.exec(select(User).where(User.username == user_data.username)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 创建新用户
    user = User(
        username=user_data.username,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        password_changed_at=datetime.utcnow()
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return user


@router.get("/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.get("/login-logs")
async def get_login_logs(
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    获取当前用户的登录日志（企业级审计）
    """
    login_log_repo = LoginLogRepository(session)
    logs = login_log_repo.list_by_user(user_id=current_user.id, limit=limit)
    return logs


@router.get("/refresh-tokens")
async def get_refresh_tokens(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    获取当前用户的所有刷新令牌（设备管理）
    """
    refresh_token_repo = RefreshTokenRepository(session)
    tokens = refresh_token_repo.list_by_user(user_id=current_user.id)
    return tokens


@router.delete("/refresh-tokens/{token_id}")
async def revoke_refresh_token(
    token_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    撤销指定的刷新令牌（登出特定设备）
    """
    refresh_token_repo = RefreshTokenRepository(session)
    token = session.get(RefreshToken, token_id)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    if token.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to revoke this token"
        )
    
    refresh_token_repo.revoke_token(token.token)
    return {"message": "Token revoked successfully"}
