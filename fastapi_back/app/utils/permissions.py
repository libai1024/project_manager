"""
权限检查工具模块

提供统一的权限检查函数，消除代码重复。
符合国内互联网企业级规范。

使用示例:
    from app.utils.permissions import check_project_access, is_admin

    # 检查项目访问权限
    check_project_access(current_user, project)

    # 检查管理员权限
    if is_admin(current_user):
        # 管理员逻辑
        pass
"""
from typing import Optional
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.models.user import User
from app.models.project import Project


# ==================== 用户角色检查 ====================

def is_admin(user: Optional[User]) -> bool:
    """
    检查用户是否为管理员

    Args:
        user: 用户对象

    Returns:
        是否为管理员

    Example:
        if is_admin(current_user):
            # 管理员可以查看所有项目
            pass
    """
    return user is not None and user.role == "admin"


def is_user_active(user: Optional[User]) -> bool:
    """
    检查用户是否激活

    Args:
        user: 用户对象

    Returns:
        是否激活
    """
    return user is not None and user.is_active


def is_user_locked(user: Optional[User]) -> bool:
    """
    检查用户是否被锁定

    Args:
        user: 用户对象

    Returns:
        是否被锁定
    """
    if user is None:
        return False
    return user.is_locked is True


# ==================== 资源访问权限检查 ====================

def check_project_access(
    user: User,
    project: Project,
    require_owner: bool = False,
    raise_exception: bool = True
) -> bool:
    """
    检查项目访问权限

    Args:
        user: 当前用户
        project: 项目对象
        require_owner: 是否要求必须是所有者
        raise_exception: 权限不足时是否抛出异常

    Returns:
        是否有权限

    Raises:
        ForbiddenException: 权限不足时抛出（raise_exception=True时）

    Example:
        # 检查查看权限
        check_project_access(current_user, project)

        # 检查修改权限（必须是自己或管理员）
        check_project_access(current_user, project, require_owner=True)
    """
    # 管理员拥有所有权限
    if is_admin(user):
        return True

    # 检查是否为项目所有者
    is_owner = project.user_id == user.id

    if require_owner and not is_owner:
        if raise_exception:
            raise ForbiddenException("您没有权限操作此项目")
        return False

    if not is_owner:
        if raise_exception:
            raise ForbiddenException("您没有权限访问此项目")
        return False

    return True


def check_project_access_by_id(
    user_id: int,
    project: Project,
    is_admin_user: bool = False,
    require_owner: bool = False,
    raise_exception: bool = True
) -> bool:
    """
    通过用户ID检查项目访问权限（用于Service层）

    Args:
        user_id: 当前用户ID
        project: 项目对象
        is_admin_user: 是否为管理员
        require_owner: 是否要求必须是所有者
        raise_exception: 权限不足时是否抛出异常

    Returns:
        是否有权限

    Raises:
        ForbiddenException: 权限不足时抛出（raise_exception=True时）

    Example:
        # 在Service层使用
        check_project_access_by_id(current_user_id, project, is_admin_user=admin)
    """
    # 管理员拥有所有权限
    if is_admin_user:
        return True

    # 检查是否为项目所有者
    is_owner = project.user_id == user_id

    if require_owner and not is_owner:
        if raise_exception:
            raise ForbiddenException("您没有权限操作此项目")
        return False

    if not is_owner:
        if raise_exception:
            raise ForbiddenException("您没有权限访问此项目")
        return False

    return True


def check_project_read_access(user: User, project: Project) -> None:
    """
    检查项目读取权限（简化版）

    Args:
        user: 当前用户
        project: 项目对象

    Raises:
        ForbiddenException: 权限不足时抛出
    """
    check_project_access(user, project, require_owner=False)


def check_project_write_access(user: User, project: Project) -> None:
    """
    检查项目写入权限

    Args:
        user: 当前用户
        project: 项目对象

    Raises:
        ForbiddenException: 权限不足时抛出
    """
    check_project_access(user, project, require_owner=True)


def can_access_user_resources(current_user: User, target_user_id: int) -> bool:
    """
    检查是否可以访问指定用户的资源

    Args:
        current_user: 当前用户
        target_user_id: 目标用户ID

    Returns:
        是否有权限
    """
    # 管理员可以访问所有用户资源
    if is_admin(current_user):
        return True
    # 用户只能访问自己的资源
    return current_user.id == target_user_id


def check_user_resource_access(
    current_user: User,
    target_user_id: int,
    raise_exception: bool = True
) -> bool:
    """
    检查并断言用户资源访问权限

    Args:
        current_user: 当前用户
        target_user_id: 目标用户ID
        raise_exception: 权限不足时是否抛出异常

    Returns:
        是否有权限

    Raises:
        ForbiddenException: 权限不足时抛出
    """
    if can_access_user_resources(current_user, target_user_id):
        return True

    if raise_exception:
        raise ForbiddenException("您没有权限访问此用户的资源")
    return False


# ==================== 条件断言 ====================

def assert_admin(user: User, msg: str = "需要管理员权限") -> None:
    """
    断言用户是管理员

    Args:
        user: 用户对象
        msg: 错误消息

    Raises:
        ForbiddenException: 不是管理员时抛出

    Example:
        assert_admin(current_user)
        # 执行管理员操作
    """
    if not is_admin(user):
        raise ForbiddenException(msg)


def assert_active(user: User, msg: str = "用户已被禁用") -> None:
    """
    断言用户已激活

    Args:
        user: 用户对象
        msg: 错误消息

    Raises:
        ForbiddenException: 用户未激活时抛出
    """
    if not is_user_active(user):
        raise ForbiddenException(msg)


def assert_not_locked(user: User, msg: str = "用户已被锁定") -> None:
    """
    断言用户未被锁定

    Args:
        user: 用户对象
        msg: 错误消息

    Raises:
        ForbiddenException: 用户被锁定时抛出
    """
    if is_user_locked(user):
        raise ForbiddenException(msg)


def assert_owner(user: User, resource_user_id: int, msg: str = "您没有权限操作此资源") -> None:
    """
    断言用户是资源所有者

    Args:
        user: 用户对象
        resource_user_id: 资源所属用户ID
        msg: 错误消息

    Raises:
        ForbiddenException: 不是所有者时抛出
    """
    if not is_admin(user) and user.id != resource_user_id:
        raise ForbiddenException(msg)


# ==================== 权限装饰器（可选） ====================

def require_admin(func):
    """
    管理员权限装饰器

    用法:
        @require_admin
        async def admin_only_endpoint(current_user: User = Depends(get_current_user)):
            pass
    """
    import functools

    @functools.wraps(func)
    async def wrapper(*args, current_user: User = None, **kwargs):
        if current_user is None:
            raise UnauthorizedException()
        assert_admin(current_user)
        return await func(*args, current_user=current_user, **kwargs)

    return wrapper


def require_owner(get_resource_user_id):
    """
    资源所有者权限装饰器

    Args:
        get_resource_user_id: 获取资源所属用户ID的函数

    用法:
        @require_owner(lambda project_id: get_project_user_id(project_id))
        async def update_project(project_id: int, current_user: User = Depends(get_current_user)):
            pass
    """
    import functools

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, current_user: User = None, **kwargs):
            if current_user is None:
                raise UnauthorizedException()

            # 获取资源所属用户ID
            resource_user_id = get_resource_user_id(*args, **kwargs)

            if not is_admin(current_user) and current_user.id != resource_user_id:
                raise ForbiddenException("您没有权限操作此资源")

            return await func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator
