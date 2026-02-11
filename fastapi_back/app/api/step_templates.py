"""
步骤模板API路由层
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.core.database import get_session
from app.core.dependencies import get_current_active_user
from app.services.step_template_service import StepTemplateService
from app.models.user import User
from app.models.step_template import StepTemplateCreate, StepTemplateUpdate, StepTemplateRead

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=List[StepTemplateRead])
async def list_templates(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有模板"""
    template_service = StepTemplateService(session)
    return template_service.list_templates(current_user.id)


@router.post("/", response_model=StepTemplateRead)
async def create_template(
    template_data: StepTemplateCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建模板"""
    template_service = StepTemplateService(session)
    return template_service.create_template(template_data, current_user.id)


@router.get("/{template_id}", response_model=StepTemplateRead)
async def get_template(
    template_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取模板详情"""
    template_service = StepTemplateService(session)
    return template_service.get_template(template_id)


@router.put("/{template_id}", response_model=StepTemplateRead)
async def update_template(
    template_id: int,
    template_data: StepTemplateUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新模板"""
    template_service = StepTemplateService(session)
    return template_service.update_template(template_id, template_data, current_user.id)


@router.delete("/{template_id}")
async def delete_template(
    template_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除模板"""
    template_service = StepTemplateService(session)
    template_service.delete_template(template_id, current_user.id)
    return {"message": "Template deleted successfully"}


@router.post("/ensure-default")
async def ensure_default_template(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """确保默认模板存在（初始化时调用）"""
    template_service = StepTemplateService(session)
    template = template_service.ensure_default_template()
    return template_service.get_template(template.id)

