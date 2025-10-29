"""
角色（Character）数据库服务。

提供角色的增删改查操作。
"""
from typing import Optional
from loguru import logger
from sqlmodel import select

from .base import DatabaseSession
from schemas.actor import Character


class CharacterService:
    """
    角色数据库服务（单例模式）。
    
    使用类方法提供统一的 CRUD 接口。
    """
    
    @classmethod
    def create(cls, character: Character) -> Character:
        """
        创建角色。
        
        :param character: 角色对象
        :return: 创建后的角色对象
        """
        with DatabaseSession() as db:
            db.add(character)
            db.flush()
            db.refresh(character)
            logger.info(f"创建角色: {character.name}")
            return character
    
    @classmethod
    def get(cls, character_id: str) -> Optional[Character]:
        """
        根据 character_id 获取角色。
        
        :param character_id: 角色ID
        :return: 角色对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            character = db.get(Character, character_id)
            if character:
                logger.debug(f"获取角色: {character_id}")
            else:
                logger.warning(f"角色不存在: {character_id}")
            return character
    
    @classmethod
    def list(cls, limit: Optional[int] = None, offset: int = 0) -> list[Character]:
        """
        获取角色列表。
        
        :param limit: 返回数量限制（None 表示无限制）
        :param offset: 跳过的记录数
        :return: 角色列表
        """
        with DatabaseSession() as db:
            statement = select(Character).offset(offset)
            if limit is not None:
                statement = statement.limit(limit)
            
            characters = db.exec(statement).all()
            logger.debug(f"获取角色列表: {len(characters)} 条")
            return list(characters)
    
    @classmethod
    def update(cls, character_id: str, **kwargs) -> Optional[Character]:
        """
        更新角色。
        
        :param character_id: 角色ID
        :param kwargs: 要更新的字段
        :return: 更新后的角色对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            character = db.get(Character, character_id)
            if not character:
                logger.warning(f"角色不存在，无法更新: {character_id}")
                return None
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(character, key):
                    setattr(character, key, value)
            
            db.add(character)
            db.flush()
            db.refresh(character)
            logger.info(f"更新角色: {character_id}")
            return character
    
    @classmethod
    def delete(cls, character_id: str) -> bool:
        """
        删除角色。
        
        :param character_id: 角色ID
        :return: 是否删除成功
        """
        with DatabaseSession() as db:
            character = db.get(Character, character_id)
            if not character:
                logger.warning(f"角色不存在，无法删除: {character_id}")
                return False
            
            db.delete(character)
            logger.info(f"删除角色: {character_id}")
            return True

