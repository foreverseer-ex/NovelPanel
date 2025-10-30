"""
绘图任务数据库服务。

提供 Job 和 BatchJob 的增删改查操作。
"""
from typing import Optional
from loguru import logger
from sqlmodel import select

from .base import DatabaseSession
from schemas.draw import Job, BatchJob


class JobService:
    """
    Job 数据库服务（单例模式）。
    
    使用类方法提供统一的 CRUD 接口。
    """
    
    @classmethod
    def create(cls, job: Job) -> Job:
        """
        创建任务。
        
        :param job: 任务对象
        :return: 创建后的任务对象
        """
        with DatabaseSession() as db:
            db.add(job)
            db.commit()
            db.refresh(job)
            # 从会话中分离对象，使其可以在会话外使用
            db.expunge(job)
            logger.info(f"创建任务: {job.job_id}")
        return job
    
    @classmethod
    def get(cls, job_id: str) -> Optional[Job]:
        """
        根据 ID 获取任务。
        
        :param job_id: 任务 ID
        :return: 任务对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            job = db.get(Job, job_id)
            if job:
                db.expunge(job)
                logger.debug(f"获取任务: {job_id}")
            else:
                logger.warning(f"任务不存在: {job_id}")
        return job
    
    @classmethod
    def list(cls, limit: Optional[int] = None, offset: int = 0) -> list[Job]:
        """
        获取任务列表。
        
        :param limit: 返回数量限制（None 表示无限制）
        :param offset: 跳过的记录数
        :return: 任务列表
        """
        with DatabaseSession() as db:
            statement = select(Job).offset(offset)
            if limit is not None:
                statement = statement.limit(limit)
            
            jobs = db.exec(statement).all()
            logger.debug(f"获取任务列表: {len(jobs)} 条")
            return list(jobs)
    
    @classmethod
    def delete(cls, job_id: str) -> bool:
        """
        删除任务。
        
        :param job_id: 任务 ID
        :return: 是否删除成功
        """
        with DatabaseSession() as db:
            job = db.get(Job, job_id)
            if not job:
                logger.warning(f"任务不存在，无法删除: {job_id}")
                return False
            
            db.delete(job)
            logger.info(f"删除任务: {job_id}")
            return True


class BatchJobService:
    """
    BatchJob 数据库服务（单例模式）。
    
    使用类方法提供统一的 CRUD 接口。
    """
    
    @classmethod
    def create(cls, batch_job: BatchJob) -> BatchJob:
        """
        创建批次任务。
        
        :param batch_job: 批次任务对象
        :return: 创建后的批次任务对象
        """
        with DatabaseSession() as db:
            db.add(batch_job)
            db.commit()
            db.refresh(batch_job)
            # 从会话中分离对象，使其可以在会话外使用
            db.expunge(batch_job)
            logger.info(f"创建批次任务: {batch_job.batch_id}, 包含 {len(batch_job.job_ids)} 个任务")
        return batch_job
    
    @classmethod
    def get(cls, batch_id: str) -> Optional[BatchJob]:
        """
        根据 ID 获取批次任务。
        
        :param batch_id: 批次 ID
        :return: 批次任务对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            batch_job = db.get(BatchJob, batch_id)
            if batch_job:
                db.expunge(batch_job)
                logger.debug(f"获取批次任务: {batch_id}")
            else:
                logger.warning(f"批次任务不存在: {batch_id}")
        return batch_job
    
    @classmethod
    def list(cls, limit: Optional[int] = None, offset: int = 0) -> list[BatchJob]:
        """
        获取批次任务列表。
        
        :param limit: 返回数量限制（None 表示无限制）
        :param offset: 跳过的记录数
        :return: 批次任务列表
        """
        with DatabaseSession() as db:
            statement = select(BatchJob).offset(offset)
            if limit is not None:
                statement = statement.limit(limit)
            
            batch_jobs = db.exec(statement).all()
            logger.debug(f"获取批次任务列表: {len(batch_jobs)} 条")
            return list(batch_jobs)
    
    @classmethod
    def update(cls, batch_id: str, **kwargs) -> Optional[BatchJob]:
        """
        更新批次任务。
        
        :param batch_id: 批次 ID
        :param kwargs: 要更新的字段
        :return: 更新后的批次任务对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            batch_job = db.get(BatchJob, batch_id)
            if not batch_job:
                logger.warning(f"批次任务不存在，无法更新: {batch_id}")
                return None
            
            # 更新字段
            for key, value in kwargs.items():
                if hasattr(batch_job, key):
                    setattr(batch_job, key, value)
            
            db.add(batch_job)
            db.flush()
            db.refresh(batch_job)
            logger.info(f"更新批次任务: {batch_id}")
            return batch_job
    
    @classmethod
    def add_job(cls, batch_id: str, job_id: str) -> Optional[BatchJob]:
        """
        向批次任务添加任务 ID。
        
        :param batch_id: 批次 ID
        :param job_id: 任务 ID
        :return: 更新后的批次任务对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            batch_job = db.get(BatchJob, batch_id)
            if not batch_job:
                logger.warning(f"批次任务不存在，无法添加任务: {batch_id}")
                return None
            
            if job_id not in batch_job.job_ids:
                batch_job.job_ids.append(job_id)
                db.add(batch_job)
                db.flush()
                db.refresh(batch_job)
                logger.info(f"向批次任务 {batch_id} 添加任务: {job_id}")
            else:
                logger.warning(f"任务 {job_id} 已存在于批次 {batch_id} 中")
            
            return batch_job
    
    @classmethod
    def remove_job(cls, batch_id: str, job_id: str) -> Optional[BatchJob]:
        """
        从批次任务移除任务 ID。
        
        :param batch_id: 批次 ID
        :param job_id: 任务 ID
        :return: 更新后的批次任务对象，如果不存在则返回 None
        """
        with DatabaseSession() as db:
            batch_job = db.get(BatchJob, batch_id)
            if not batch_job:
                logger.warning(f"批次任务不存在，无法移除任务: {batch_id}")
                return None
            
            if job_id in batch_job.job_ids:
                batch_job.job_ids.remove(job_id)
                db.add(batch_job)
                db.flush()
                db.refresh(batch_job)
                logger.info(f"从批次任务 {batch_id} 移除任务: {job_id}")
            else:
                logger.warning(f"任务 {job_id} 不存在于批次 {batch_id} 中")
            
            return batch_job
    
    @classmethod
    def delete(cls, batch_id: str) -> bool:
        """
        删除批次任务。
        
        :param batch_id: 批次 ID
        :return: 是否删除成功
        """
        with DatabaseSession() as db:
            batch_job = db.get(BatchJob, batch_id)
            if not batch_job:
                logger.warning(f"批次任务不存在，无法删除: {batch_id}")
                return False
            
            db.delete(batch_job)
            logger.info(f"删除批次任务: {batch_id}")
            return True

