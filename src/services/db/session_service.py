"""
会话（Session）数据库服务。

提供会话的增删改查操作。
"""
from typing import Optional
from pathlib import Path
from loguru import logger
from sqlmodel import select

from .base import DatabaseSession
from schemas.session import Session


class SessionService:
    """
    会话数据库服务（单例模式）。
    
    使用类方法提供统一的 CRUD 接口。
    """
    
    @classmethod
    def _init_project_structure(cls, session: Session) -> bool:
        """
        初始化项目文件夹结构。
        
        创建以下目录：
        - images/: 存放生成的图片
        - illustration/: 存放立绘
        
        如果有原始小说文件，会自动解析并存入数据库。
        
        :param session: 会话对象
        :return: 是否初始化成功
        """
        try:
            project_path = Path(session.project_path)
            
            # 创建项目根目录
            project_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建项目目录: {project_path}")
            
            # 创建 images 文件夹（存放生成的图片）
            images_dir = project_path / "images"
            images_dir.mkdir(exist_ok=True)
            logger.info(f"创建 images 目录: {images_dir}")
            
            # 创建 illustration 文件夹（存放立绘）
            illustration_dir = project_path / "illustration"
            illustration_dir.mkdir(exist_ok=True)
            logger.info(f"创建 illustration 目录: {illustration_dir}")
            
            # 如果有小说文件，解析并存入数据库
            if session.novel_path:
                from services.transform import transform_service
                from services.novel_parser import novel_parser
                from .novel_service import NovelContentService
                
                source_file = Path(session.novel_path)
                
                if source_file.exists():
                    # 如果不是 TXT，先转换为 TXT
                    if source_file.suffix.lower() != '.txt':
                        # 创建临时 TXT 文件
                        temp_txt = project_path / "temp_novel.txt"
                        success = transform_service.transform_to_txt(source_file, temp_txt)
                        if not success:
                            logger.warning(f"小说转换失败: {source_file}")
                            return False
                        parse_file = temp_txt
                    else:
                        parse_file = source_file
                    
                    # 解析小说内容
                    novel_contents = novel_parser.parse_file(parse_file, session.session_id)
                    if not novel_contents:
                        logger.warning(f"小说解析失败: {parse_file}")
                        return False
                    
                    # 批量存入数据库
                    NovelContentService.batch_create(novel_contents)
                    logger.success(f"小说解析并存储成功: {len(novel_contents)} 行")
                    
                    # 删除临时文件
                    if source_file.suffix.lower() != '.txt':
                        temp_txt.unlink(missing_ok=True)
                else:
                    logger.warning(f"小说文件不存在: {source_file}")
            
            return True
            
        except Exception as e:
            logger.exception(f"初始化项目结构失败: {e}")
            return False
    
    @classmethod
    def create(cls, session: Session) -> Session:
        """
        创建会话。
        
        执行以下操作：
        1. 初始化项目文件夹结构（images/, illustration/）
        2. 如果有小说文件，解析并存入数据库
        3. 在数据库中创建 session 记录
        4. 更新小说统计信息（总行数、总章节数）
        
        :param session: 会话对象
        :return: 创建后的会话对象（包含自动生成的字段）
        """
        # 初始化项目文件夹结构（包括解析小说）
        if not cls._init_project_structure(session):
            raise RuntimeError(f"初始化项目结构失败: {session.project_path}")
        
        # 在数据库中创建记录
        with DatabaseSession() as db:
            db.add(session)
            db.flush()  # 刷新以获取自动生成的字段
            db.refresh(session)
            db.expunge(session)  # 分离对象，使其可以在 session 外部使用
            logger.info(f"创建会话: {session.session_id}")
        
        # 如果有小说内容，更新统计信息
        if session.novel_path:
            from .novel_service import NovelContentService
            total_lines = NovelContentService.count_by_session(session.session_id)
            total_chapters = NovelContentService.count_chapters(session.session_id)
            
            # 更新 session 的统计信息
            updated_session = cls.update(
                session.session_id,
                total_lines=total_lines,
                total_chapters=total_chapters
            )
            if updated_session:
                session = updated_session
                logger.info(f"更新会话统计: {total_lines} 行, {total_chapters} 章")
        
        return session
    
    @classmethod
    def get(cls, session_id: str) -> Optional[Session]:
        """
        根据 ID 获取会话。
        
        :param session_id: 会话 ID
        :return: 会话对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            session = db.get(Session, session_id)
            if session:
                db.expunge(session)  # 分离对象
                logger.debug(f"获取会话: {session_id}")
            else:
                logger.warning(f"会话不存在: {session_id}")
            return session
    
    @classmethod
    def list(cls, limit: Optional[int] = None, offset: int = 0) -> list[Session]:
        """
        获取会话列表。
        
        :param limit: 返回数量限制（None 表示无限制）
        :param offset: 跳过的记录数
        :return: 会话列表
        """
        with DatabaseSession() as db:
            statement = select(Session).offset(offset)
            if limit is not None:
                statement = statement.limit(limit)
            
            sessions = db.exec(statement).all()
            # 分离所有对象
            for session in sessions:
                db.expunge(session)
            logger.debug(f"获取会话列表: {len(sessions)} 条")
            return list(sessions)
    
    @classmethod
    def update(cls, session_id: str, **kwargs) -> Optional[Session]:
        """
        更新会话。
        
        :param session_id: 会话 ID
        :param kwargs: 要更新的字段
        :return: 更新后的会话对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            session = db.get(Session, session_id)
            if not session:
                logger.warning(f"会话不存在，无法更新: {session_id}")
                return None
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            
            db.add(session)
            db.flush()
            db.refresh(session)
            db.expunge(session)  # 分离对象
            logger.info(f"更新会话: {session_id}")
            return session
    
    @classmethod
    def delete(cls, session_id: str) -> bool:
        """
        删除会话。
        
        同时删除关联的小说内容。
        
        :param session_id: 会话 ID
        :return: 是否删除成功
        """
        # 删除关联的小说内容
        from .novel_service import NovelContentService
        novel_count = NovelContentService.delete_by_session(session_id)
        logger.info(f"删除会话关联的小说内容: {session_id}, 共 {novel_count} 行")
        
        # 删除会话记录
        with DatabaseSession() as db:
            session = db.get(Session, session_id)
            if not session:
                logger.warning(f"会话不存在，无法删除: {session_id}")
                return False
            
            db.delete(session)
            logger.info(f"删除会话: {session_id}")
            return True

