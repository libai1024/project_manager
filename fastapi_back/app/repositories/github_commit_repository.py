"""
GitHub Commit仓库层
"""
from typing import Optional, List
from sqlmodel import Session, select, and_
from datetime import datetime
from app.models.github_commit import GitHubCommit, GitHubCommitCreate, GitHubCommitUpdate


class GitHubCommitRepository:
    """GitHub Commit仓库"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, commit_data: GitHubCommitCreate) -> GitHubCommit:
        """创建GitHub Commit"""
        commit = GitHubCommit(**commit_data.dict())
        self.session.add(commit)
        self.session.commit()
        self.session.refresh(commit)
        return commit
    
    def get_by_id(self, commit_id: int) -> Optional[GitHubCommit]:
        """根据ID获取Commit"""
        return self.session.get(GitHubCommit, commit_id)
    
    def get_by_sha(self, project_id: int, sha: str) -> Optional[GitHubCommit]:
        """根据SHA获取Commit"""
        statement = select(GitHubCommit).where(
            and_(
                GitHubCommit.project_id == project_id,
                GitHubCommit.sha == sha
            )
        )
        return self.session.exec(statement).first()
    
    def get_by_project_and_branch(
        self, 
        project_id: int, 
        branch: str,
        limit: Optional[int] = None
    ) -> List[GitHubCommit]:
        """根据项目和分支获取Commits"""
        statement = select(GitHubCommit).where(
            and_(
                GitHubCommit.project_id == project_id,
                GitHubCommit.branch == branch
            )
        ).order_by(GitHubCommit.commit_date.desc())
        
        if limit:
            statement = statement.limit(limit)
        
        return list(self.session.exec(statement).all())
    
    def get_latest_sync_time(self, project_id: int, branch: str) -> Optional[datetime]:
        """获取最新的同步时间"""
        statement = select(GitHubCommit).where(
            and_(
                GitHubCommit.project_id == project_id,
                GitHubCommit.branch == branch
            )
        ).order_by(GitHubCommit.synced_at.desc()).limit(1)
        
        commit = self.session.exec(statement).first()
        return commit.synced_at if commit else None
    
    def delete_by_project_and_branch(self, project_id: int, branch: str) -> int:
        """删除指定项目和分支的所有commits"""
        statement = select(GitHubCommit).where(
            and_(
                GitHubCommit.project_id == project_id,
                GitHubCommit.branch == branch
            )
        )
        commits = list(self.session.exec(statement).all())
        count = len(commits)
        for commit in commits:
            self.session.delete(commit)
        self.session.commit()
        return count
    
    def bulk_create(self, commits_data: List[GitHubCommitCreate]) -> List[GitHubCommit]:
        """批量创建Commits"""
        commits = [GitHubCommit(**data.dict()) for data in commits_data]
        self.session.add_all(commits)
        self.session.commit()
        for commit in commits:
            self.session.refresh(commit)
        return commits
    
    def update(self, commit: GitHubCommit, commit_data: GitHubCommitUpdate) -> GitHubCommit:
        """更新Commit"""
        update_data = commit_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(commit, field, value)
        commit.updated_at = datetime.utcnow()
        self.session.add(commit)
        self.session.commit()
        self.session.refresh(commit)
        return commit
    
    def delete(self, commit: GitHubCommit) -> None:
        """删除Commit"""
        self.session.delete(commit)
        self.session.commit()

