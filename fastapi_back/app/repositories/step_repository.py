"""
项目步骤数据访问层

重构后继承 BaseRepository，复用通用 CRUD 方法。
"""
from typing import Optional, List
from sqlmodel import Session, select

from app.repositories.base import BaseRepository
from app.models.project import ProjectStep
from app.schemas.project import ProjectStepCreate
from app.utils.constants import StepStatus


class StepRepository(BaseRepository[ProjectStep]):
    """项目步骤数据访问层"""

    def __init__(self, session: Session):
        super().__init__(session, ProjectStep)

    def create(self, step_data: ProjectStepCreate, project_id: int = None) -> ProjectStep:
        """创建步骤"""
        step_dict = step_data.model_dump()
        step_dict['project_id'] = project_id
        if 'status' not in step_dict or not step_dict['status']:
            step_dict['status'] = "待开始"
        step = ProjectStep(**step_dict)
        return super().create(step)

    def list_by_project(self, project_id: int) -> List[ProjectStep]:
        """获取项目的所有步骤（按order_index排序）"""
        query = select(ProjectStep).where(ProjectStep.project_id == project_id)
        return list(self.session.exec(query.order_by(ProjectStep.order_index)).all())

    def list_todo_steps(self, project_ids: List[int]) -> List[ProjectStep]:
        """获取待办步骤列表"""
        query = select(ProjectStep).where(
            ProjectStep.project_id.in_(project_ids),
            ProjectStep.is_todo == True,
            ProjectStep.status != "已完成"
        )
        return list(self.session.exec(query.order_by(ProjectStep.order_index)).all())

    def list_in_progress_steps(self, project_ids: List[int]) -> List[ProjectStep]:
        """获取进行中的步骤列表"""
        query = select(ProjectStep).where(
            ProjectStep.project_id.in_(project_ids),
            ProjectStep.status != "已完成"
        )
        return list(self.session.exec(query).all())

    def update(self, step: ProjectStep, update_data: dict) -> ProjectStep:
        """更新步骤信息"""
        return super().update(step, update_data)

    def delete(self, step: ProjectStep) -> bool:
        """删除步骤"""
        return super().delete(step)

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
