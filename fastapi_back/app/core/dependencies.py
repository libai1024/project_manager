"""
认证依赖模块
提供统一的 token 解析和用户认证功能
"""
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import decode_access_token
from app.models.user import User
from app.repositories.token_blacklist_repository import TokenBlacklistRepository
import logging

logger = logging.getLogger(__name__)

# OAuth2 方案配置
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False  # 不自动抛出错误，让我们自己处理
)


async def extract_token_from_request(request: Request) -> Optional[str]:
    """
    统一的 token 提取函数
    从请求头中提取 Bearer token，支持多种 header 名称格式
    
    优先级：
    1. Authorization header (标准格式)
    2. authorization header (小写格式)
    3. X-Authorization header (备用格式)
    
    Args:
        request: FastAPI Request 对象
        
    Returns:
        token 字符串，如果未找到则返回 None
    """
    logger.info(f"[Token提取] 开始从请求头提取 token")
    logger.info(f"[Token提取] 请求路径: {request.url.path}")
    logger.info(f"[Token提取] 请求方法: {request.method}")
    
    # 尝试多种可能的 header 名称（不区分大小写）
    auth_headers = [
        request.headers.get("Authorization"),
        request.headers.get("authorization"),
        request.headers.get("X-Authorization"),
    ]
    
    logger.info(f"[Token提取] 检查的 header 值: Authorization={bool(auth_headers[0])}, authorization={bool(auth_headers[1])}, X-Authorization={bool(auth_headers[2])}")
    
    # 过滤掉 None 值
    auth_headers = [h for h in auth_headers if h is not None]
    
    if not auth_headers:
        logger.warning(f"[Token提取] 未找到 Authorization header")
        logger.warning(f"[Token提取] 可用请求头: {list(request.headers.keys())}")
        # 列出所有 header 的值（前50个字符）
        for key in request.headers.keys():
            value = request.headers.get(key)
            logger.debug(f"[Token提取]   {key}: {str(value)[:50] if value else None}...")
        return None
    
    # 使用第一个找到的 header
    authorization = auth_headers[0]
    logger.info(f"[Token提取] 找到 Authorization header，长度: {len(authorization)}, 前30字符: {authorization[:30]}...")
    
    try:
        scheme, token = get_authorization_scheme_param(authorization)
        logger.info(f"[Token提取] 解析结果: scheme={scheme}, token长度={len(token) if token else 0}")
        
        if scheme.lower() != "bearer":
            logger.warning(f"[Token提取] 无效的授权方案: {scheme}，期望 'Bearer'")
            return None
        
        if not token or not token.strip():
            logger.warning(f"[Token提取] Token 为空")
            return None
        
        token_clean = token.strip()
        logger.info(f"[Token提取] Token 提取成功，长度: {len(token_clean)}, 前30字符: {token_clean[:30]}...")
        return token_clean
        
    except Exception as e:
        logger.error(f"[Token提取] 从 header 提取 token 时出错: {e}", exc_info=True)
        return None


async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme),
    session: Session = Depends(get_session)
) -> User:
    """
    获取当前登录用户（统一的认证入口）
    
    此函数是项目中所有需要认证的端点的统一入口点。
    它会：
    1. 尝试从 OAuth2PasswordBearer 获取 token
    2. 如果失败，直接从请求头中提取 token
    3. 验证 token 并解析用户信息
    4. 返回用户对象
    
    Args:
        request: FastAPI Request 对象
        token: 从 OAuth2PasswordBearer 提取的 token（可能为 None）
        session: 数据库会话
        
    Returns:
        User 对象
        
    Raises:
        HTTPException: 如果认证失败（401 Unauthorized）
    """
    logger.info(f"[认证依赖] get_current_user - 开始处理请求: {request.method} {request.url.path}")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # 记录所有请求头（用于调试）
    all_headers = dict(request.headers)
    logger.info(f"[认证依赖] 请求头列表: {list(all_headers.keys())}")
    
    # 检查 Authorization header（多种格式）
    auth_header_raw = all_headers.get("authorization") or all_headers.get("Authorization") or all_headers.get("AUTHORIZATION")
    if auth_header_raw:
        logger.info(f"[认证依赖] 找到 Authorization header: {auth_header_raw[:30]}... (长度: {len(auth_header_raw)})")
    else:
        logger.warning(f"[认证依赖] 未找到 Authorization header")
        # 列出所有 header 的值（前50个字符）
        for key, value in all_headers.items():
            logger.debug(f"[认证依赖]   {key}: {str(value)[:50] if value else None}...")
    
    # 如果 OAuth2PasswordBearer 没有提取到 token，使用统一的提取函数
    if not token:
        logger.warning(f"[认证依赖] OAuth2PasswordBearer 返回 None，尝试直接提取")
        token = await extract_token_from_request(request)
        if token:
            logger.info(f"[认证依赖] 直接提取成功，token 长度: {len(token)}")
        else:
            logger.warning(f"[认证依赖] 直接提取也失败")
    else:
        logger.info(f"[认证依赖] OAuth2PasswordBearer 提取成功，token 长度: {len(token)}")
    
    if not token:
        logger.error(f"[认证依赖] 认证失败: 没有提供 token")
        logger.error(f"[认证依赖] 请求路径: {request.url.path}")
        logger.error(f"[认证依赖] 请求方法: {request.method}")
        logger.error(f"[认证依赖] 可用请求头: {list(request.headers.keys())}")
        raise credentials_exception
    
    logger.info(f"[认证依赖] Token 已获取，开始验证 (token 前30字符: {token[:30]}...)")
    
    # 验证和解析 token
    try:
        logger.info(f"[认证依赖] 开始验证 token")
        
        # 检查token是否在黑名单中（企业级：支持token撤销）
        blacklist_repo = TokenBlacklistRepository(session)
        is_blacklisted = blacklist_repo.is_blacklisted(token)
        logger.info(f"[认证依赖] Token 黑名单检查: {is_blacklisted}")
        if is_blacklisted:
            logger.warning(f"[认证依赖] Token 已被加入黑名单")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info(f"[认证依赖] 开始解码 token")
        payload = decode_access_token(token)
        if payload is None:
            logger.error(f"[认证依赖] Token 解码失败: 无效的 token 格式")
            raise credentials_exception
        
        logger.info(f"[认证依赖] Token 解码成功，payload keys: {list(payload.keys())}")
        
        username: str = payload.get("sub")
        user_id = payload.get("user_id")
        role = payload.get("role")
        logger.info(f"[认证依赖] Token payload: username={username}, user_id={user_id}, role={role}")
        
        if username is None:
            logger.error(f"[认证依赖] Token payload 缺少 'sub' 字段")
            raise credentials_exception
        
        logger.info(f"[认证依赖] 从数据库查询用户: {username}")
        # 从数据库获取用户
        user = session.exec(select(User).where(User.username == username)).first()
        if user is None:
            logger.error(f"[认证依赖] 用户不存在: {username}")
            raise credentials_exception
        
        logger.info(f"[认证依赖] 用户查询成功: id={user.id}, username={user.username}, role={user.role}, is_active={user.is_active}, is_locked={user.is_locked}")
        
        # 检查账户状态（企业级：账户锁定和激活检查）
        if not user.is_active:
            logger.warning(f"[认证依赖] 用户账户已禁用: {username}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        if user.is_locked:
            from datetime import datetime
            if user.locked_until and user.locked_until > datetime.utcnow():
                logger.warning(f"[认证依赖] 用户账户已锁定: {username}, 锁定至: {user.locked_until}")
                raise HTTPException(
                    status_code=status.HTTP_423_LOCKED,
                    detail=f"Account is locked until {user.locked_until}"
                )
        
        logger.info(f"[认证依赖] 用户认证成功: {username} (role: {user.role}, id: {user.id})")
        return user
        
    except HTTPException as e:
        # 重新抛出 HTTP 异常
        logger.error(f"[认证依赖] HTTP 异常: status={e.status_code}, detail={e.detail}")
        raise
    except Exception as e:
        logger.error(f"[认证依赖] 认证过程中的意外错误: {e}", exc_info=True)
        raise credentials_exception


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户（企业级）
    确保用户账户是激活的且未被锁定
    """
    logger.info(f"[认证依赖] get_current_active_user - 用户: id={current_user.id}, username={current_user.username}, is_active={current_user.is_active}, is_locked={current_user.is_locked}")
    # 这些检查已经在 get_current_user 中完成，这里只是确保
    if not current_user.is_active:
        logger.warning(f"[认证依赖] get_current_active_user - 用户账户已禁用: {current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    logger.info(f"[认证依赖] get_current_active_user - 用户验证通过: {current_user.username}")
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """获取当前管理员用户"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

