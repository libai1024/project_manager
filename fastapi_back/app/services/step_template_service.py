"""
步骤模板服务层
"""
import logging
from typing import List, Optional
from sqlmodel import Session
from fastapi import HTTPException, status
from app.repositories.step_template_repository import StepTemplateRepository
from app.models.step_template import (
    StepTemplate, StepTemplateItem,
    StepTemplateCreate, StepTemplateUpdate, StepTemplateRead
)
from app.utils.constants import DEFAULT_STEPS

logger = logging.getLogger(__name__)


class StepTemplateService:
    """步骤模板服务"""
    
    def __init__(self, session: Session):
        self.session = session
        self.template_repo = StepTemplateRepository(session)
    
    def create_template(self, template_data: StepTemplateCreate, user_id: Optional[int] = None) -> StepTemplateRead:
        """创建模板"""
        # 检查名称是否已存在
        existing = self.template_repo.list_all(user_id)
        for t in existing:
            if t.name == template_data.name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Template with name '{template_data.name}' already exists"
                )
        
        # 创建模板
        template_dict = {
            "name": template_data.name,
            "description": template_data.description,
            "is_default": False
        }
        template = self.template_repo.create(template_dict, user_id)
        
        # 创建步骤项
        self.template_repo.create_items(template.id, template_data.steps)
        
        return self.get_template(template.id)
    
    def get_template(self, template_id: int) -> StepTemplateRead:
        """获取模板"""
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        items = self.template_repo.get_items_by_template(template_id)
        step_names = [item.name for item in items]
        
        return StepTemplateRead(
            id=template.id,
            name=template.name,
            description=template.description,
            is_default=template.is_default,
            user_id=template.user_id,
            created_at=template.created_at,
            updated_at=template.updated_at,
            steps=step_names
        )
    
    def list_templates(self, user_id: Optional[int] = None) -> List[StepTemplateRead]:
        """获取所有模板"""
        templates = self.template_repo.list_all(user_id)
        result = []
        for template in templates:
            items = self.template_repo.get_items_by_template(template.id)
            step_names = [item.name for item in items]
            result.append(StepTemplateRead(
                id=template.id,
                name=template.name,
                description=template.description,
                is_default=template.is_default,
                user_id=template.user_id,
                created_at=template.created_at,
                updated_at=template.updated_at,
                steps=step_names
            ))
        return result
    
    def update_template(self, template_id: int, template_data: StepTemplateUpdate, user_id: Optional[int] = None) -> StepTemplateRead:
        """更新模板"""
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # 检查权限（非管理员只能修改自己的模板）
        if user_id and template.user_id != user_id and not template.is_default:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        # 不能修改默认模板的名称和is_default状态
        update_dict = {}
        if template_data.name and not template.is_default:
            update_dict["name"] = template_data.name
        if template_data.description is not None:
            update_dict["description"] = template_data.description
        
        if update_dict:
            self.template_repo.update(template, update_dict)
        
        # 更新步骤项
        if template_data.steps is not None:
            self.template_repo.update_items(template_id, template_data.steps)
        
        return self.get_template(template_id)
    
    def delete_template(self, template_id: int, user_id: Optional[int] = None) -> None:
        """删除模板"""
        template = self.template_repo.get_by_id(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        # 检查权限
        if user_id and template.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        
        self.template_repo.delete(template)
    
    def ensure_default_template(self) -> StepTemplate:
        """确保默认模板存在"""
        default_template = self.template_repo.get_default_template()
        if not default_template:
            # 创建默认模板
            template_dict = {
                "name": "默认模板",
                "description": "系统默认的项目步骤模板",
                "is_default": True
            }
            default_template = self.template_repo.create(template_dict)
            self.template_repo.create_items(default_template.id, DEFAULT_STEPS)
        return default_template
    
    def get_default_template_steps(self) -> List[str]:
        """获取默认模板的步骤列表"""
        default_template = self.ensure_default_template()
        items = self.template_repo.get_items_by_template(default_template.id)
        return [item.name for item in items]

