from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.historical_project import HistoricalProject


class GitHubCommitBase(SQLModel):
    """GitHub Commit基础模型"""
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", index=True, description="所属项目ID")
    historical_project_id: Optional[int] = Field(default=None, foreign_key="historicalproject.id", index=True, description="所属历史项目ID")
    sha: str = Field(index=True, max_length=40)
    branch: str = Field(index=True, max_length=255)
    author: str = Field(max_length=255)
    message: str
    commit_date: datetime
    url: str = Field(max_length=500)
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class GitHubCommit(GitHubCommitBase, table=True):
    """GitHub Commit数据库模型"""
    __tablename__ = "github_commit"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 关系
    project: Optional["Project"] = Relationship(back_populates="github_commits")
    historical_project: Optional["HistoricalProject"] = Relationship(back_populates="github_commits")


class GitHubCommitRead(GitHubCommitBase):
    """GitHub Commit读取模型"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GitHubCommitCreate(GitHubCommitBase):
    """GitHub Commit创建模型"""
    pass


class GitHubCommitUpdate(SQLModel):
    """GitHub Commit更新模型"""
    author: Optional[str] = None
    message: Optional[str] = None
    commit_date: Optional[datetime] = None
    url: Optional[str] = None
    synced_at: Optional[datetime] = None

