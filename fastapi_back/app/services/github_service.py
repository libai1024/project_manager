"""
GitHub服务层 - 同步GitHub仓库提交记录
"""
import logging
import requests
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlmodel import Session
from fastapi import HTTPException, status
from app.repositories.github_commit_repository import GitHubCommitRepository
from app.repositories.project_repository import ProjectRepository
from app.models.github_commit import GitHubCommitCreate, GitHubCommitRead

logger = logging.getLogger(__name__)

# 同步间隔：1分钟
SYNC_INTERVAL = timedelta(minutes=1)


class GitHubService:
    """GitHub服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.commit_repo = GitHubCommitRepository(session)
        self.project_repo = ProjectRepository(session)
    
    def parse_github_url(self, github_url: str) -> Optional[Dict[str, str]]:
        """解析GitHub URL，提取owner和repo"""
        if not github_url:
            return None
        
        # 支持多种格式：
        # https://github.com/owner/repo
        # https://github.com/owner/repo.git
        # git@github.com:owner/repo.git
        import re
        patterns = [
            r'github\.com[/:]([\w\-\.]+)/([\w\-\.]+)',
            r'github\.com/([\w\-\.]+)/([\w\-\.]+)\.git',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, github_url)
            if match:
                return {
                    'owner': match.group(1),
                    'repo': match.group(2).replace('.git', '')
                }
        
        return None
    
    def fetch_commits_from_github(
        self, 
        owner: str, 
        repo: str, 
        branch: str = 'main'
    ) -> List[Dict]:
        """从GitHub API获取提交记录"""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        commits_data = []
        page = 1
        
        headers = {
            "Accept": "application/vnd.github.v3+json",
            # 如果需要提高API速率限制，可以添加Token
            # "Authorization": "token YOUR_GITHUB_TOKEN"
        }
        
        while True:
            try:
                logger.info(f"正在抓取 {owner}/{repo} 分支 {branch} 第 {page} 页...")
                params = {
                    'page': page,
                    'per_page': 100,  # 每页最多100条
                    'sha': branch
                }
                
                response = requests.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 404:
                    logger.warning(f"仓库 {owner}/{repo} 或分支 {branch} 不存在")
                    break
                
                if response.status_code == 403:
                    logger.warning("GitHub API速率限制，请稍后重试或添加Token")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="GitHub API速率限制，请稍后重试"
                    )
                
                if response.status_code != 200:
                    logger.error(f"请求失败: {response.status_code}, {response.text}")
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail=f"GitHub API请求失败: {response.status_code}"
                    )
                
                data = response.json()
                if not data:
                    break  # 没有更多数据了
                
                for commit in data:
                    commit_info = {
                        'sha': commit['sha'],
                        'author': commit['commit']['author']['name'],
                        'date': commit['commit']['author']['date'],
                        'message': commit['commit']['message'],
                        'url': commit['html_url']
                    }
                    commits_data.append(commit_info)
                
                # 如果返回的数据少于100条，说明已经是最后一页
                if len(data) < 100:
                    break
                
                page += 1
                
                # 限制最多抓取10页（1000条记录）
                if page > 10:
                    logger.info(f"已达到最大页数限制（10页），停止抓取")
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"请求GitHub API时出错: {e}")
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=f"无法连接到GitHub API: {str(e)}"
                )
        
        logger.info(f"共获取到 {len(commits_data)} 条 Commit 记录")
        return commits_data
    
    def should_sync(self, project_id: int, branch: str) -> bool:
        """检查是否需要同步（距离上次同步超过1分钟）"""
        latest_sync = self.commit_repo.get_latest_sync_time(project_id, branch)
        
        if latest_sync is None:
            return True  # 从未同步过
        
        time_since_sync = datetime.utcnow() - latest_sync.replace(tzinfo=None)
        return time_since_sync >= SYNC_INTERVAL
    
    def sync_commits(
        self, 
        project_id: int, 
        branch: str = 'main',
        force: bool = False
    ) -> List[GitHubCommitRead]:
        """同步GitHub提交记录"""
        # 检查项目是否存在
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="项目不存在"
            )
        
        if not project.github_url:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="项目未设置GitHub地址"
            )
        
        # 解析GitHub URL
        parsed = self.parse_github_url(project.github_url)
        if not parsed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GitHub地址格式不正确"
            )
        
        # 检查是否需要同步
        if not force and not self.should_sync(project_id, branch):
            logger.info(f"项目 {project_id} 分支 {branch} 在1分钟内已同步过，返回缓存数据")
            # 返回缓存的commits
            commits = self.commit_repo.get_by_project_and_branch(project_id, branch)
            return [GitHubCommitRead.model_validate(c) for c in commits]
        
        # 从GitHub获取commits
        try:
            github_commits = self.fetch_commits_from_github(
                parsed['owner'],
                parsed['repo'],
                branch
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"获取GitHub commits失败: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"获取GitHub提交记录失败: {str(e)}"
            )
        
        # 删除该分支的旧数据
        self.commit_repo.delete_by_project_and_branch(project_id, branch)
        
        # 保存新的commits
        commit_creates = []
        sync_time = datetime.utcnow()
        
        for commit_data in github_commits:
            # 解析日期
            date_str = commit_data['date']
            # 处理ISO格式日期，支持多种格式
            if date_str.endswith('Z'):
                date_str = date_str.replace('Z', '+00:00')
            elif '+' not in date_str and '-' in date_str:
                # 如果没有时区信息，添加UTC时区
                date_str = date_str + '+00:00'
            
            try:
                commit_date = datetime.fromisoformat(date_str)
                # 转换为UTC时间（如果有时区信息）
                if commit_date.tzinfo:
                    commit_date = commit_date.astimezone().replace(tzinfo=None)
            except ValueError:
                # 如果解析失败，使用当前时间
                logger.warning(f"无法解析日期: {date_str}，使用当前时间")
                commit_date = datetime.utcnow()
            
            commit_create = GitHubCommitCreate(
                project_id=project_id,
                sha=commit_data['sha'],
                branch=branch,
                author=commit_data['author'],
                message=commit_data['message'],
                commit_date=commit_date,
                url=commit_data['url'],
                synced_at=sync_time
            )
            commit_creates.append(commit_create)
        
        # 批量创建
        if commit_creates:
            commits = self.commit_repo.bulk_create(commit_creates)
            logger.info(f"成功同步 {len(commits)} 条commits到数据库")
            return [GitHubCommitRead.model_validate(c) for c in commits]
        else:
            logger.info("没有新的commits需要同步")
            return []
    
    def get_commits(
        self, 
        project_id: int, 
        branch: str = 'main',
        limit: Optional[int] = None
    ) -> List[GitHubCommitRead]:
        """获取项目的commits（不触发同步）"""
        commits = self.commit_repo.get_by_project_and_branch(project_id, branch, limit)
        return [GitHubCommitRead.model_validate(c) for c in commits]

