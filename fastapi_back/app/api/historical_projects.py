"""
历史项目管理API路由层
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, UploadFile, File, Form
from fastapi import status as http_status
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.services.historical_project_service import HistoricalProjectService
from app.models.user import User
from app.models.historical_project import (
    HistoricalProjectCreate, HistoricalProjectReadWithRelations, HistoricalProjectUpdate,
    HistoricalProjectImportRequest
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["历史项目管理"])


@router.get("/", response_model=List[HistoricalProjectReadWithRelations])
async def list_historical_projects(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None, description="搜索关键词（标题、学生姓名、需求描述）"),
    platform_id: Optional[int] = Query(None, description="平台ID（筛选）"),
    status: Optional[str] = Query(None, description="项目状态（筛选）"),
    tag_ids: Optional[str] = Query(None, description="标签ID列表，用逗号分隔"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取历史项目列表"""
    logger.info(f"[历史项目API] list_historical_projects - 开始处理请求")
    logger.info(f"[历史项目API] 当前用户: id={current_user.id}, username={current_user.username}, role={current_user.role}")
    logger.info(f"[历史项目API] 请求参数: skip={skip}, limit={limit}, search={search}, platform_id={platform_id}, status={status}, tag_ids={tag_ids}")
    
    historical_project_service = HistoricalProjectService(session)
    
    # 如果不是管理员，只能查看自己创建的历史项目
    user_id = None if current_user.role == "admin" else current_user.id
    logger.info(f"[历史项目API] 过滤用户ID: {user_id} (admin={current_user.role == 'admin'})")
    
    # 解析标签ID列表
    tag_id_list = None
    if tag_ids:
        try:
            tag_id_list = [int(tid.strip()) for tid in tag_ids.split(',') if tid.strip()]
        except ValueError:
            tag_id_list = None
    
    try:
        result = historical_project_service.list_historical_projects(
            skip=skip,
            limit=limit,
            search=search,
            user_id=user_id,
            platform_id=platform_id,
            status=status,
            tag_ids=tag_id_list
        )
        logger.info(f"[历史项目API] list_historical_projects - 成功返回 {len(result)} 条记录")
        return result
    except Exception as e:
        logger.error(f"[历史项目API] Error in list_historical_projects API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/count")
async def get_historical_projects_count(
    search: Optional[str] = Query(None, description="搜索关键词"),
    platform_id: Optional[int] = Query(None, description="平台ID（筛选）"),
    status: Optional[str] = Query(None, description="项目状态（筛选）"),
    tag_ids: Optional[str] = Query(None, description="标签ID列表，用逗号分隔"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取历史项目总数"""
    logger.info(f"[历史项目API] get_historical_projects_count - 当前用户: id={current_user.id}, username={current_user.username}")
    historical_project_service = HistoricalProjectService(session)
    
    # 如果不是管理员，只能统计自己创建的历史项目
    user_id = None if current_user.role == "admin" else current_user.id
    
    # 解析标签ID列表
    tag_id_list = None
    if tag_ids:
        try:
            tag_id_list = [int(tid.strip()) for tid in tag_ids.split(',') if tid.strip()]
        except ValueError:
            tag_id_list = None
    
    try:
        count = historical_project_service.get_count(
            search=search,
            user_id=user_id,
            platform_id=platform_id,
            status=status,
            tag_ids=tag_id_list
        )
        logger.info(f"[历史项目API] get_historical_projects_count - 返回总数: {count}")
        return {"count": count}
    except Exception as e:
        logger.error(f"[历史项目API] Error in get_historical_projects_count API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/", response_model=HistoricalProjectReadWithRelations)
async def create_historical_project(
    project_data: HistoricalProjectCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建历史项目"""
    logger.info(f"[历史项目API] create_historical_project - 当前用户: id={current_user.id}, username={current_user.username}")
    logger.info(f"[历史项目API] 项目数据: title={project_data.title}, platform_id={project_data.platform_id}")
    historical_project_service = HistoricalProjectService(session)
    try:
        result = historical_project_service.create_historical_project(
            project_data=project_data,
            user_id=current_user.id
        )
        logger.info(f"[历史项目API] create_historical_project - 创建成功: id={result.id}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[历史项目API] Error in create_historical_project API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/import-from-project/{project_id}", response_model=HistoricalProjectReadWithRelations)
async def import_from_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """从现有项目导入为历史项目"""
    historical_project_service = HistoricalProjectService(session)
    try:
        return historical_project_service.import_from_project(
            project_id=project_id,
            user_id=current_user.id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in import_from_project API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/batch-import", response_model=List[HistoricalProjectReadWithRelations])
async def batch_import_historical_projects(
    import_request: HistoricalProjectImportRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """批量导入历史项目"""
    historical_project_service = HistoricalProjectService(session)
    try:
        return historical_project_service.batch_import(
            import_request=import_request,
            user_id=current_user.id
        )
    except Exception as e:
        logger.error(f"Error in batch_import_historical_projects API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{project_id}", response_model=HistoricalProjectReadWithRelations)
async def get_historical_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取历史项目详情"""
    logger.info(f"[历史项目API] get_historical_project - 项目ID: {project_id}, 当前用户: id={current_user.id}, username={current_user.username}")
    historical_project_service = HistoricalProjectService(session)
    try:
        result = historical_project_service.get_historical_project_with_relations(project_id)
        logger.info(f"[历史项目API] get_historical_project - 成功获取项目: id={result.id}, title={result.title}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[历史项目API] Error in get_historical_project API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.put("/{project_id}", response_model=HistoricalProjectReadWithRelations)
async def update_historical_project(
    project_id: int,
    project_data: HistoricalProjectUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新历史项目"""
    historical_project_service = HistoricalProjectService(session)
    try:
        return historical_project_service.update_historical_project(
            project_id=project_id,
            update_data=project_data,
            current_user_id=current_user.id,
            is_admin=(current_user.role == "admin")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in update_historical_project API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.delete("/{project_id}")
async def delete_historical_project(
    project_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除历史项目"""
    historical_project_service = HistoricalProjectService(session)
    try:
        historical_project_service.delete_historical_project(
            project_id=project_id,
            current_user_id=current_user.id,
            is_admin=(current_user.role == "admin")
        )
        return {"message": "历史项目已删除"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in delete_historical_project API: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

