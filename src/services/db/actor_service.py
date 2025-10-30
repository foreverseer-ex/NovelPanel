"""
Actor（角色/要素）数据库服务。

提供 Actor 的增删改查操作。
Actor 可以是角色、地点、组织等小说要素。
"""
from typing import Optional
from loguru import logger
from sqlmodel import select

from .base import DatabaseSession
from schemas.actor import Actor, ActorExample


class ActorService:
    """
    Actor 数据库服务（单例模式）。
    
    使用类方法提供统一的 CRUD 接口。
    """
    
    @classmethod
    def create(cls, actor: Actor) -> Actor:
        """
        创建 Actor。
        
        :param actor: Actor 对象
        :return: 创建后的 Actor 对象
        """
        with DatabaseSession() as db:
            db.add(actor)
            db.flush()
            db.refresh(actor)
            db.expunge(actor)
            logger.info(f"创建 Actor: {actor.name}")
            return actor
    
    @classmethod
    def get(cls, actor_id: str) -> Optional[Actor]:
        """
        根据 actor_id 获取 Actor。
        
        :param actor_id: Actor ID
        :return: Actor 对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            actor = db.get(Actor, actor_id)
            if actor:
                db.expunge(actor)
                logger.debug(f"获取 Actor: {actor_id}")
            else:
                logger.warning(f"Actor 不存在: {actor_id}")
            return actor
    
    @classmethod
    def list_by_session(cls, session_id: str, limit: Optional[int] = None, offset: int = 0) -> list[Actor]:
        """
        根据会话ID获取 Actor 列表。
        
        :param session_id: 会话ID
        :param limit: 返回数量限制（None 表示无限制）
        :param offset: 跳过的记录数
        :return: Actor 列表
        """
        with DatabaseSession() as db:
            statement = select(Actor).where(Actor.session_id == session_id).offset(offset)
            if limit is not None:
                statement = statement.limit(limit)
            
            actors = db.exec(statement).all()
            for actor in actors:
                db.expunge(actor)
            logger.debug(f"获取 Actor 列表: {len(actors)} 条")
            return list(actors)
    
    @classmethod
    def update(cls, actor_id: str, **kwargs) -> Optional[Actor]:
        """
        更新 Actor。
        
        :param actor_id: Actor ID
        :param kwargs: 要更新的字段
        :return: 更新后的 Actor 对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            actor = db.get(Actor, actor_id)
            if not actor:
                logger.warning(f"Actor 不存在，无法更新: {actor_id}")
                return None
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(actor, key):
                    setattr(actor, key, value)
            
            db.add(actor)
            db.flush()
            db.refresh(actor)
            db.expunge(actor)
            logger.info(f"更新 Actor: {actor_id}")
            return actor
    
    @classmethod
    def delete(cls, actor_id: str) -> bool:
        """
        删除 Actor。
        
        :param actor_id: Actor ID
        :return: 是否删除成功
        """
        with DatabaseSession() as db:
            actor = db.get(Actor, actor_id)
            if not actor:
                logger.warning(f"Actor 不存在，无法删除: {actor_id}")
                return False
            
            db.delete(actor)
            logger.info(f"删除 Actor: {actor_id}")
            return True
    
    @classmethod
    def add_example(cls, actor_id: str, example: ActorExample) -> Optional[Actor]:
        """
        为 Actor 添加示例图。
        
        :param actor_id: Actor ID
        :param example: ActorExample 对象
        :return: 更新后的 Actor 对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            actor = db.get(Actor, actor_id)
            if not actor:
                logger.warning(f"Actor 不存在，无法添加示例: {actor_id}")
                return None
            
            # 将 ActorExample 转换为字典并添加到 examples 列表
            actor.examples.append(example.model_dump())
            db.add(actor)
            db.flush()
            db.refresh(actor)
            db.expunge(actor)
            logger.info(f"为 Actor 添加示例: {actor_id}, title={example.title}")
            return actor
    
    @classmethod
    def remove_example(cls, actor_id: str, example_index: int) -> Optional[Actor]:
        """
        删除 Actor 的指定示例图。
        
        :param actor_id: Actor ID
        :param example_index: 示例图索引
        :return: 更新后的 Actor 对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            actor = db.get(Actor, actor_id)
            if not actor:
                logger.warning(f"Actor 不存在，无法删除示例: {actor_id}")
                return None
            
            if 0 <= example_index < len(actor.examples):
                removed = actor.examples.pop(example_index)
                db.add(actor)
                db.flush()
                db.refresh(actor)
                db.expunge(actor)
                logger.info(f"删除 Actor 示例: {actor_id}, index={example_index}, title={removed.get('title')}")
                return actor
            else:
                logger.warning(f"示例图索引越界: {actor_id}, index={example_index}")
                return None

