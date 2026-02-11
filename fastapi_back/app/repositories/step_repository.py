"""
项目步骤数据访问层
"""
from typing import Optional, List
from sqlmodel import Session, select
from sqlalchemy import inspect, Engine
from app.models.project import ProjectStep, ProjectStepCreate, StepStatus


class StepRepository:
    """项目步骤数据访问层"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, step_data: ProjectStepCreate, project_id: int = None) -> ProjectStep:
        """创建步骤"""
        step_dict = step_data.model_dump()
        step_dict['project_id'] = project_id
        if 'status' not in step_dict:
            step_dict['status'] = StepStatus.PENDING
        step = ProjectStep(**step_dict)
        self.session.add(step)
        self.session.commit()
        self.session.refresh(step)
        return step
    
    def get_by_id(self, step_id: int) -> Optional[ProjectStep]:
        """根据ID获取步骤"""
        return self.session.get(ProjectStep, step_id)
    
    def list_by_project(self, project_id: int) -> List[ProjectStep]:
        """获取项目的所有步骤（按order_index排序）"""
        query = select(ProjectStep).where(ProjectStep.project_id == project_id)
        return list(self.session.exec(query.order_by(ProjectStep.order_index)).all())
    
    def list_todo_steps(self, project_ids: List[int]) -> List[ProjectStep]:
        """获取待办步骤列表"""
        query = select(ProjectStep).where(
                ProjectStep.project_id.in_(project_ids),
                ProjectStep.is_todo == True,
                ProjectStep.status != StepStatus.DONE
            )
        return list(self.session.exec(query.order_by(ProjectStep.order_index)).all())
    
    def list_in_progress_steps(self, project_ids: List[int]) -> List[ProjectStep]:
        """获取进行中的步骤列表"""
        query = select(ProjectStep).where(
                ProjectStep.project_id.in_(project_ids),
                ProjectStep.status != StepStatus.DONE
            )
        return list(self.session.exec(query).all())
    
    def update(self, step: ProjectStep, update_data: dict) -> ProjectStep:
        """更新步骤信息"""
        for field, value in update_data.items():
            setattr(step, field, value)
        self.session.add(step)
        self.session.commit()
        self.session.refresh(step)
        return step
    
    def delete(self, step: ProjectStep) -> None:
        """删除步骤"""
        self.session.delete(step)
        self.session.commit()
    
    def bulk_update_order(self, step_orders: List[dict]) -> None:
        """批量更新步骤顺序"""
        for item in step_orders:
            step_id = item.get("step_id")
            order_index = item.get("order_index")
            step = self.get_by_id(step_id)
            if step:
                step.order_index = order_index
                self.session.add(step)
        self.session.commit()
    
    def toggle_todo(self, step: ProjectStep) -> ProjectStep:
        """切换步骤的Todo状态"""
        step.is_todo = not step.is_todo
        self.session.add(step)
        self.session.commit()
        self.session.refresh(step)
        return step

