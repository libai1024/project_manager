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
from app.api.responses import ApiResponse, success

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=ApiResponse[List[StepTemplateRead]])
async def list_templates(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有模板"""
    template_service = StepTemplateService(session)
    templates = template_service.list_templates(current_user.id)
    return success(templates)


@router.post("/", response_model=ApiResponse[StepTemplateRead])
async def create_template(
    template_data: StepTemplateCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """创建模板"""
    template_service = StepTemplateService(session)
    template = template_service.create_template(template_data, current_user.id)
    return success(template, msg="模板创建成功")


@router.get("/{template_id}", response_model=ApiResponse[StepTemplateRead])
async def get_template(
    template_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """获取模板详情"""
    template_service = StepTemplateService(session)
    template = template_service.get_template(template_id)
    return success(template)


@router.put("/{template_id}", response_model=ApiResponse[StepTemplateRead])
async def update_template(
    template_id: int,
    template_data: StepTemplateUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """更新模板"""
    template_service = StepTemplateService(session)
    template = template_service.update_template(template_id, template_data, current_user.id)
    return success(template, msg="模板更新成功")


@router.delete("/{template_id}", response_model=ApiResponse[None])
async def delete_template(
    template_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """删除模板"""
    template_service = StepTemplateService(session)
    template_service.delete_template(template_id, current_user.id)
    return success(msg="模板删除成功")


@router.post("/ensure-default", response_model=ApiResponse[StepTemplateRead])
async def ensure_default_template(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_active_user)
):
    """确保默认模板存在（初始化时调用）"""
    template_service = StepTemplateService(session)
    template = template_service.ensure_default_template()
    result = template_service.get_template(template.id)
    return success(result)

