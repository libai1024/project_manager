"""
GitHub Commits API路由
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.services.github_service import GitHubService
from app.models.user import User
from app.models.github_commit import GitHubCommitRead

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/github-commits", tags=["GitHub Commits"])


@router.get("/projects/{project_id}/commits", response_model=List[GitHubCommitRead])
async def get_project_commits(
    project_id: int,
    branch: str = Query("main", description="分支名称"),
    limit: Optional[int] = Query(None, ge=1, le=1000, description="限制返回数量"),
    force_sync: bool = Query(False, description="强制同步（忽略1分钟限制）"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取项目的GitHub提交记录
    
    - 如果force_sync=True，会强制从GitHub同步
    - 如果force_sync=False，会检查是否需要同步（1分钟限制）
    - 返回缓存的commits或同步后的commits
    """
    try:
        github_service = GitHubService(session)
        
        if force_sync:
            # 强制同步
            commits = github_service.sync_commits(project_id, branch, force=True)
        else:
            # 检查是否需要同步
            if github_service.should_sync(project_id, branch):
                # 需要同步
                commits = github_service.sync_commits(project_id, branch, force=False)
            else:
                # 使用缓存
                commits = github_service.get_commits(project_id, branch, limit)
        
        return commits
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取项目 {project_id} 的commits失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取提交记录失败: {str(e)}"
        )


@router.post("/projects/{project_id}/sync", response_model=List[GitHubCommitRead])
async def sync_project_commits(
    project_id: int,
    branch: str = Query("main", description="分支名称"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """
    手动触发同步GitHub提交记录（忽略1分钟限制）
    """
    try:
        github_service = GitHubService(session)
        commits = github_service.sync_commits(project_id, branch, force=True)
        return commits
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"同步项目 {project_id} 的commits失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"同步提交记录失败: {str(e)}"
        )

