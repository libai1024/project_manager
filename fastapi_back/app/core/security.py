from datetime import datetime, timedelta
from typing import Optional, Tuple
from jose import JWTError, jwt
import bcrypt
import secrets
import re
from app.core.config import settings
from sqlmodel import Session

# bcrypt 轮数
BCRYPT_ROUNDS = 12


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    try:
        # 确保密码是字节类型
        if isinstance(plain_password, str):
            plain_password_bytes = plain_password.encode('utf-8')
            # bcrypt 限制密码长度不超过 72 字节
            if len(plain_password_bytes) > 72:
                plain_password_bytes = plain_password_bytes[:72]
        else:
            plain_password_bytes = plain_password
        
        # 确保哈希是字节类型
        if isinstance(hashed_password, str):
            hashed_password_bytes = hashed_password.encode('utf-8')
        else:
            hashed_password_bytes = hashed_password
        
        return bcrypt.checkpw(plain_password_bytes, hashed_password_bytes)
    except Exception as e:
        print(f"密码验证错误: {e}")
        return False


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    try:
        # 确保密码是字节类型
        if isinstance(password, str):
            password_bytes = password.encode('utf-8')
            # bcrypt 限制密码长度不超过 72 字节，如果超过则截断
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]
        else:
            password_bytes = password
        
        # 生成 salt 并哈希密码
        salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
        hashed = bcrypt.hashpw(password_bytes, salt)
        
        # 返回字符串格式
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"密码哈希错误: {e}")
        raise


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None, session: Optional[Session] = None) -> str:
    """
    创建JWT token
    
    Args:
        data: token 数据
        expires_delta: 可选的过期时间增量
        session: 数据库会话（用于从数据库读取配置）
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # 尝试从数据库读取配置，如果不存在则使用默认值
        expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        if session:
            try:
                from app.repositories.system_settings_repository import SystemSettingsRepository
                settings_repo = SystemSettingsRepository(session)
                expire_minutes = settings_repo.get_int_value("access_token_expire_minutes", settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            except Exception:
                # 如果读取失败，使用默认值
                pass
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """解码JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    验证密码强度（企业级密码策略）
    
    Returns:
        (is_valid, error_message)
    """
    if len(password) < settings.PASSWORD_MIN_LENGTH:
        return False, f"密码长度至少需要 {settings.PASSWORD_MIN_LENGTH} 个字符"
    
    if settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        return False, "密码必须包含至少一个大写字母"
    
    if settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        return False, "密码必须包含至少一个小写字母"
    
    if settings.PASSWORD_REQUIRE_NUMBER and not re.search(r'\d', password):
        return False, "密码必须包含至少一个数字"
    
    if settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "密码必须包含至少一个特殊字符"
    
    return True, None


def generate_refresh_token() -> str:
    """生成安全的刷新令牌（使用secrets模块）"""
    return secrets.token_urlsafe(32)


def create_refresh_token(user_id: int, session: Optional[Session] = None) -> Tuple[str, datetime]:
    """
    创建刷新令牌
    
    Args:
        user_id: 用户ID
        session: 数据库会话（用于从数据库读取配置）
    
    Returns:
        (token, expires_at)
    """
    token = generate_refresh_token()
    # 尝试从数据库读取配置，如果不存在则使用默认值
    expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
    if session:
        try:
            from app.repositories.system_settings_repository import SystemSettingsRepository
            settings_repo = SystemSettingsRepository(session)
            expire_days = settings_repo.get_int_value("refresh_token_expire_days", settings.REFRESH_TOKEN_EXPIRE_DAYS)
        except Exception:
            # 如果读取失败，使用默认值
            pass
    expires_at = datetime.utcnow() + timedelta(days=expire_days)
    return token, expires_at


def is_password_expired(password_changed_at: Optional[datetime]) -> bool:
    """检查密码是否过期"""
    if not settings.PASSWORD_EXPIRE_DAYS or not password_changed_at:
        return False
    
    expire_date = password_changed_at + timedelta(days=settings.PASSWORD_EXPIRE_DAYS)
    return datetime.utcnow() > expire_date


def should_lock_account(failed_attempts: int) -> bool:
    """判断是否应该锁定账户"""
    return failed_attempts >= settings.MAX_LOGIN_ATTEMPTS


def get_lockout_until() -> datetime:
    """获取账户锁定到期时间"""
    return datetime.utcnow() + timedelta(minutes=settings.LOCKOUT_DURATION_MINUTES)

