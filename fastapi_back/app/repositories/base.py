"""
数据访问层基类

提供通用的CRUD操作，减少重复代码。
符合国内互联网企业级规范。

使用示例:
    class ProjectRepository(BaseRepository[Project]):
        def __init__(self, session: Session):
            super().__init__(session, Project)

        def list_by_user(self, user_id: int) -> List[Project]:
            return list(self.session.exec(
                select(Project).where(Project.user_id == user_id)
            ).all())
"""
from typing import Generic, TypeVar, Optional, List, Type, Dict, Any
from sqlmodel import Session, select, SQLModel
import logging

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """
    数据访问层基类

    提供通用的CRUD操作，子类可以扩展或覆盖这些方法。

    Type Parameters:
        ModelType: SQLModel模型类型

    Attributes:
        session: 数据库会话
        model: 模型类
    """

    def __init__(self, session: Session, model: Type[ModelType]):
        """
        初始化Repository

        Args:
            session: 数据库会话
            model: 模型类
        """
        self.session = session
        self.model = model

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        根据ID获取单个实体

        Args:
            id: 实体ID

        Returns:
            实体对象，不存在则返回None

        Example:
            project = repo.get_by_id(1)
        """
        try:
            return self.session.get(self.model, id)
        except Exception as e:
            logger.error(f"获取{self.model.__name__}失败, id={id}: {e}")
            return None

    def get_by_ids(self, ids: List[int]) -> List[ModelType]:
        """
        根据ID列表获取多个实体

        Args:
            ids: ID列表

        Returns:
            实体列表

        Example:
            projects = repo.get_by_ids([1, 2, 3])
        """
        if not ids:
            return []
        try:
            return list(self.session.exec(
                select(self.model).where(self.model.id.in_(ids))
            ).all())
        except Exception as e:
            logger.error(f"批量获取{self.model.__name__}失败, ids={ids}: {e}")
            return []

    def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """
        获取所有实体

        Args:
            skip: 跳过记录数
            limit: 返回记录数
            order_by: 排序字段

        Returns:
            实体列表

        Example:
            projects = repo.list_all(skip=0, limit=10)
        """
        try:
            query = select(self.model).offset(skip).limit(limit)
            if order_by:
                column = getattr(self.model, order_by, None)
                if column is not None:
                    query = query.order_by(column)
            return list(self.session.exec(query).all())
        except Exception as e:
            logger.error(f"获取{self.model.__name__}列表失败: {e}")
            return []

    def create(self, entity: ModelType) -> ModelType:
        """
        创建实体

        Args:
            entity: 要创建的实体

        Returns:
            创建后的实体（包含ID）

        Example:
            new_project = repo.create(Project(title="新项目"))
        """
        try:
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
            logger.info(f"创建{self.model.__name__}成功, id={entity.id}")
            return entity
        except Exception as e:
            self.session.rollback()
            logger.error(f"创建{self.model.__name__}失败: {e}")
            raise

    def update(self, entity: ModelType, data: Dict[str, Any]) -> ModelType:
        """
        更新实体

        Args:
            entity: 要更新的实体
            data: 更新数据字典

        Returns:
            更新后的实体

        Example:
            project = repo.update(project, {"title": "新标题"})
        """
        try:
            for field, value in data.items():
                if hasattr(entity, field):
                    setattr(entity, field, value)
            self.session.add(entity)
            self.session.commit()
            self.session.refresh(entity)
            logger.info(f"更新{self.model.__name__}成功, id={entity.id}")
            return entity
        except Exception as e:
            self.session.rollback()
            logger.error(f"更新{self.model.__name__}失败, id={entity.id}: {e}")
            raise

    def delete(self, entity: ModelType) -> bool:
        """
        删除实体

        Args:
            entity: 要删除的实体

        Returns:
            是否删除成功

        Example:
            repo.delete(project)
        """
        try:
            self.session.delete(entity)
            self.session.commit()
            logger.info(f"删除{self.model.__name__}成功, id={entity.id}")
            return True
        except Exception as e:
            self.session.rollback()
            logger.error(f"删除{self.model.__name__}失败, id={entity.id}: {e}")
            return False

    def delete_by_id(self, id: int) -> bool:
        """
        根据ID删除实体

        Args:
            id: 实体ID

        Returns:
            是否删除成功

        Example:
            repo.delete_by_id(1)
        """
        entity = self.get_by_id(id)
        if entity is None:
            return False
        return self.delete(entity)

    def exists(self, id: int) -> bool:
        """
        检查实体是否存在

        Args:
            id: 实体ID

        Returns:
            是否存在

        Example:
            if repo.exists(1):
                print("存在")
        """
        return self.get_by_id(id) is not None

    def count(self, **filters) -> int:
        """
        统计实体数量

        Args:
            **filters: 过滤条件

        Returns:
            数量

        Example:
            count = repo.count(status="active")
        """
        try:
            from sqlmodel import func
            query = select(func.count()).select_from(self.model)
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
            result = self.session.exec(query).one()
            return result or 0
        except Exception as e:
            logger.error(f"统计{self.model.__name__}数量失败: {e}")
            return 0

    def find_one(self, **filters) -> Optional[ModelType]:
        """
        根据条件查找单个实体

        Args:
            **filters: 过滤条件

        Returns:
            实体对象，不存在则返回None

        Example:
            user = repo.find_one(username="admin")
        """
        try:
            query = select(self.model)
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
            query = query.limit(1)
            results = self.session.exec(query).all()
            return results[0] if results else None
        except Exception as e:
            logger.error(f"查找{self.model.__name__}失败: {e}")
            return None

    def find_many(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters
    ) -> List[ModelType]:
        """
        根据条件查找多个实体

        Args:
            skip: 跳过记录数
            limit: 返回记录数
            **filters: 过滤条件

        Returns:
            实体列表

        Example:
            projects = repo.find_many(skip=0, limit=10, status="active")
        """
        try:
            query = select(self.model)
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.where(getattr(self.model, field) == value)
            query = query.offset(skip).limit(limit)
            return list(self.session.exec(query).all())
        except Exception as e:
            logger.error(f"查找{self.model.__name__}列表失败: {e}")
            return []
