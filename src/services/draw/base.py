"""
绘图服务基础抽象类。

定义所有绘图服务的统一接口。
"""
from abc import ABC, abstractmethod
from pathlib import Path
from PIL import Image

from schemas.draw import DrawArgs


class AbstractDrawService(ABC):
    """
    绘图服务抽象基类。
    
    定义统一的绘图接口，支持不同的后端（SD-Forge、Civitai 等）。
    """
    
    @abstractmethod
    def draw(self, args: DrawArgs) -> str:
        """
        执行单次绘图。
        
        :param args: 绘图参数
        :return: job_id（任务 ID）
        """
        raise NotImplementedError
    
    @abstractmethod
    def draw_batch(self, args_list: list[DrawArgs]) -> str:
        """
        批量绘图。
        
        :param args_list: 绘图参数列表
        :return: batch_id（批次 ID）
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_batch_status(self, batch_id: str) -> dict[str, bool]:
        """
        获取批次状态。
        
        :param batch_id: 批次 ID
        :return: 字典 {job_id: 是否完成}
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_job_status(self, job_id: str) -> bool:
        """
        获取任务状态。
        
        :param job_id: 任务 ID
        :return: 是否完成
        """
        raise NotImplementedError
    
    @abstractmethod
    def get_image(self, job_id: str) -> Image.Image:
        """
        获取生成的图片。
        
        :param job_id: 任务 ID
        :return: PIL Image 对象
        """
        raise NotImplementedError
    
    @abstractmethod
    def save_image(self, job_id: str, save_path: str | Path) -> None:
        """
        保存生成的图片到文件。
        
        :param job_id: 任务 ID
        :param save_path: 保存路径
        """
        raise NotImplementedError

