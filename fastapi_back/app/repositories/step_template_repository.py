"""
步骤模板仓库层
"""
from typing import List, Optional
from sqlmodel import Session, select
from app.models.step_template import StepTemplate, StepTemplateItem
from app.models.user import User


class StepTemplateRepository:
    """步骤模板仓库"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, template_data: dict, user_id: Optional[int] = None) -> StepTemplate:
        """创建模板"""
        template = StepTemplate(**template_data)
        if user_id:
            template.user_id = user_id
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        return template
    
    def get_by_id(self, template_id: int) -> Optional[StepTemplate]:
        """根据ID获取模板"""
        return self.session.get(StepTemplate, template_id)
    
    def get_default_template(self) -> Optional[StepTemplate]:
        """获取默认模板"""
        statement = select(StepTemplate).where(StepTemplate.is_default == True)
        return self.session.exec(statement).first()
    
    def list_all(self, user_id: Optional[int] = None) -> List[StepTemplate]:
        """获取所有模板"""
        if user_id:
            statement = select(StepTemplate).where(
                (StepTemplate.user_id == user_id) | (StepTemplate.is_default == True)
            )
        else:
            statement = select(StepTemplate)
        return list(self.session.exec(statement).all())
    
    def update(self, template: StepTemplate, update_data: dict) -> StepTemplate:
        """更新模板"""
        for key, value in update_data.items():
            setattr(template, key, value)
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)
        return template
    
    def delete(self, template: StepTemplate) -> None:
        """删除模板"""
        # 不能删除默认模板
        if template.is_default:
            raise ValueError("Cannot delete default template")
        self.session.delete(template)
        self.session.commit()
    
    def create_items(self, template_id: int, step_names: List[str]) -> List[StepTemplateItem]:
        """创建模板步骤项"""
        items = []
        for index, name in enumerate(step_names):
            item = StepTemplateItem(
                template_id=template_id,
                name=name,
                order_index=index
            )
            items.append(item)
            self.session.add(item)
        self.session.commit()
        for item in items:
            self.session.refresh(item)
        return items
    
    def get_items_by_template(self, template_id: int) -> List[StepTemplateItem]:
        """获取模板的所有步骤项"""
        statement = select(StepTemplateItem).where(
            StepTemplateItem.template_id == template_id
        ).order_by(StepTemplateItem.order_index)
        return list(self.session.exec(statement).all())
    
    def update_items(self, template_id: int, step_names: List[str]) -> List[StepTemplateItem]:
        """更新模板步骤项（先删除旧的，再创建新的）"""
        # 删除旧的步骤项
        old_items = self.get_items_by_template(template_id)
        for item in old_items:
            self.session.delete(item)
        
        # 创建新的步骤项
        return self.create_items(template_id, step_names)
    
    def delete_items_by_template(self, template_id: int) -> None:
        """删除模板的所有步骤项"""
        items = self.get_items_by_template(template_id)
        for item in items:
            self.session.delete(item)
        self.session.commit()

