"""
标签API路由层
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.tag import Tag, TagCreate, TagRead, TagUpdate, ProjectTag, HistoricalProjectTag
from app.repositories.tag_repository import TagRepository, ProjectTagRepository, HistoricalProjectTagRepository
from app.api.responses import ApiResponse, success

router = APIRouter(tags=["标签管理"])


@router.post("/", response_model=ApiResponse[TagRead])
async def create_tag(
    tag_data: TagCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建标签（全局共享，不区分用户）"""
    tag_repo = TagRepository(session)

    # 检查标签是否已存在（全局检查，不区分用户）
    existing = tag_repo.get_by_name(tag_data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"标签名称'{tag_data.name}'已存在，请直接选择该标签"
        )

    # 标签全局共享，不设置user_id（设置为None）
    tag = tag_repo.create(tag_data, user_id=None)
    tag_read = TagRead(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        description=tag.description,
        user_id=tag.user_id,
        is_common=tag.is_common,
        usage_count=tag.usage_count,
        created_at=tag.created_at,
        updated_at=tag.updated_at
    )
    return success(tag_read, msg="标签创建成功")


@router.get("/", response_model=ApiResponse[List[TagRead]])
async def list_tags(
    include_common: bool = True,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取标签列表（全局共享，所有标签）"""
    tag_repo = TagRepository(session)
    # 标签全局共享，返回所有标签（不区分用户）
    tags = tag_repo.list_all(user_id=None, include_common=include_common)
    tag_list = [
        TagRead(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            description=tag.description,
            user_id=tag.user_id,
            is_common=tag.is_common,
            usage_count=tag.usage_count,
            created_at=tag.created_at,
            updated_at=tag.updated_at
        )
        for tag in tags
    ]
    return success(tag_list)


@router.get("/common", response_model=ApiResponse[List[TagRead]])
async def list_common_tags(
    session: Session = Depends(get_session)
):
    """获取常用标签列表"""
    tag_repo = TagRepository(session)
    tags = tag_repo.list_common()
    tag_list = [
        TagRead(
            id=tag.id,
            name=tag.name,
            color=tag.color,
            description=tag.description,
            user_id=tag.user_id,
            is_common=tag.is_common,
            usage_count=tag.usage_count,
            created_at=tag.created_at,
            updated_at=tag.updated_at
        )
        for tag in tags
    ]
    return success(tag_list)


@router.get("/{tag_id}", response_model=ApiResponse[TagRead])
async def get_tag(
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取标签详情"""
    tag_repo = TagRepository(session)
    tag = tag_repo.get_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    tag_read = TagRead(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        description=tag.description,
        user_id=tag.user_id,
        is_common=tag.is_common,
        usage_count=tag.usage_count,
        created_at=tag.created_at,
        updated_at=tag.updated_at
    )
    return success(tag_read)


@router.put("/{tag_id}", response_model=ApiResponse[TagRead])
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新标签（只能更新自己创建的标签）"""
    tag_repo = TagRepository(session)
    tag = tag_repo.get_by_id(tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    # 只能更新自己创建的标签或管理员可以更新所有标签
    if tag.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此标签"
        )

    # 如果更新名称，检查是否重复
    if tag_data.name and tag_data.name != tag.name:
        existing = tag_repo.get_by_name(tag_data.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="标签名称已存在"
            )

    updated_tag = tag_repo.update(tag_id, tag_data)
    if not updated_tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    tag_read = TagRead(
        id=updated_tag.id,
        name=updated_tag.name,
        color=updated_tag.color,
        description=updated_tag.description,
        user_id=updated_tag.user_id,
        is_common=updated_tag.is_common,
        usage_count=updated_tag.usage_count,
        created_at=updated_tag.created_at,
        updated_at=updated_tag.updated_at
    )
    return success(tag_read, msg="标签更新成功")


@router.delete("/{tag_id}", response_model=ApiResponse[None])
async def delete_tag(
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除标签（只能删除自己创建的标签）"""
    tag_repo = TagRepository(session)
    tag = tag_repo.get_by_id(tag_id)

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    # 只能删除自己创建的标签或管理员可以删除所有标签
    if tag.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权删除此标签"
        )

    # 删除标签前，先删除所有关联
    project_tag_repo = ProjectTagRepository(session)
    historical_project_tag_repo = HistoricalProjectTagRepository(session)

    # 获取所有使用此标签的项目
    project_tags = list(project_tag_repo.session.exec(
        select(ProjectTag).where(ProjectTag.tag_id == tag_id)
    ).all())

    historical_project_tags = list(historical_project_tag_repo.session.exec(
        select(HistoricalProjectTag).where(HistoricalProjectTag.tag_id == tag_id)
    ).all())

    # 删除所有关联
    for pt in project_tags:
        project_tag_repo.session.delete(pt)
    for hpt in historical_project_tags:
        historical_project_tag_repo.session.delete(hpt)

    project_tag_repo.session.commit()

    # 删除标签
    success_flag = tag_repo.delete(tag_id)
    if not success_flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )

    return success(msg="标签删除成功")


@router.post("/project/{project_id}/tags", response_model=TagRead)
async def add_project_tag(
    project_id: int,
    tag_id: int = Query(..., description="标签ID"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """为项目添加标签"""
    from app.repositories.project_repository import ProjectRepository
    
    # 检查项目是否存在
    project_repo = ProjectRepository(session)
    project = project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查权限
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此项目"
        )
    
    # 检查标签是否存在
    tag_repo = TagRepository(session)
    tag = tag_repo.get_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    # 添加标签
    project_tag_repo = ProjectTagRepository(session)
    project_tag_repo.create(project_id, tag_id)
    
    return TagRead(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        description=tag.description,
        user_id=tag.user_id,
        is_common=tag.is_common,
        usage_count=tag.usage_count,
        created_at=tag.created_at,
        updated_at=tag.updated_at
    )


@router.delete("/project/{project_id}/tags/{tag_id}")
async def remove_project_tag(
    project_id: int,
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """移除项目的标签"""
    from app.repositories.project_repository import ProjectRepository
    
    # 检查项目是否存在
    project_repo = ProjectRepository(session)
    project = project_repo.get_by_id(project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="项目不存在"
        )
    
    # 检查权限
    if project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此项目"
        )
    
    # 移除标签
    project_tag_repo = ProjectTagRepository(session)
    success = project_tag_repo.delete(project_id, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签关联不存在"
        )
    
    return {"message": "标签移除成功"}


@router.post("/historical-project/{historical_project_id}/tags", response_model=TagRead)
async def add_historical_project_tag(
    historical_project_id: int,
    tag_id: int = Query(..., description="标签ID"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """为历史项目添加标签"""
    from app.repositories.historical_project_repository import HistoricalProjectRepository
    
    # 检查历史项目是否存在
    historical_project_repo = HistoricalProjectRepository(session)
    historical_project = historical_project_repo.get_by_id(historical_project_id)
    if not historical_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="历史项目不存在"
        )
    
    # 检查权限
    if historical_project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此历史项目"
        )
    
    # 检查标签是否存在
    tag_repo = TagRepository(session)
    tag = tag_repo.get_by_id(tag_id)
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签不存在"
        )
    
    # 添加标签
    historical_project_tag_repo = HistoricalProjectTagRepository(session)
    historical_project_tag_repo.create(historical_project_id, tag_id)
    
    return TagRead(
        id=tag.id,
        name=tag.name,
        color=tag.color,
        description=tag.description,
        user_id=tag.user_id,
        is_common=tag.is_common,
        usage_count=tag.usage_count,
        created_at=tag.created_at,
        updated_at=tag.updated_at
    )


@router.delete("/historical-project/{historical_project_id}/tags/{tag_id}")
async def remove_historical_project_tag(
    historical_project_id: int,
    tag_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """移除历史项目的标签"""
    from app.repositories.historical_project_repository import HistoricalProjectRepository
    
    # 检查历史项目是否存在
    historical_project_repo = HistoricalProjectRepository(session)
    historical_project = historical_project_repo.get_by_id(historical_project_id)
    if not historical_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="历史项目不存在"
        )
    
    # 检查权限
    if historical_project.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权修改此历史项目"
        )
    
    # 移除标签
    historical_project_tag_repo = HistoricalProjectTagRepository(session)
    success = historical_project_tag_repo.delete(historical_project_id, tag_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="标签关联不存在"
        )
    
    return {"message": "标签移除成功"}

