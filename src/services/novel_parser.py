"""
小说解析服务。

将小说文本文件解析为章节和段落，并存储到数据库。
"""
import re
from pathlib import Path
from loguru import logger

from schemas.novel import NovelContent


class NovelParser:
    """
    小说解析器。
    
    支持自动识别章节标题，按段落分割内容。
    """
    
    # 章节标题匹配模式
    CHAPTER_PATTERNS = [
        r'^第[0-9零一二三四五六七八九十百千万]+[章节回集]',  # 第X章
        r'^第[0-9]+[章节回集]',  # 第1章
        r'^Chapter\s*\d+',  # Chapter 1
        r'^\d+\.',  # 1.
        r'^序章',  # 序章
        r'^楔子',  # 楔子
        r'^引子',  # 引子
        r'^尾声',  # 尾声
        r'^后记',  # 后记
    ]
    
    @classmethod
    def parse_file(cls, file_path: Path, session_id: str) -> list[NovelContent]:
        """
        解析小说文件并转换为 NovelContent 对象列表。
        
        :param file_path: 小说文件路径
        :param session_id: 会话 ID
        :return: NovelContent 对象列表
        """
        try:
            # 读取文件
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                # 如果 UTF-8 失败，尝试 GBK
                content = file_path.read_text(encoding='gbk')
            
            # 解析文本
            return cls.parse_text(content, session_id)
            
        except Exception as e:
            logger.exception(f"解析小说文件失败: {e}")
            return []
    
    @classmethod
    def parse_text(cls, text: str, session_id: str) -> list[NovelContent]:
        """
        解析小说文本并转换为 NovelContent 对象列表。
        
        :param text: 小说文本
        :param session_id: 会话 ID
        :return: NovelContent 对象列表
        """
        novel_contents = []
        current_chapter = 0
        line_number = 0
        
        # 按行分割
        lines = text.split('\n')
        
        for raw_line in lines:
            # 去除首尾空白
            line = raw_line.strip()
            
            # 跳过空行
            if not line:
                continue
            
            # 检查是否是章节标题
            if cls._is_chapter_title(line):
                current_chapter += 1
                logger.debug(f"检测到章节: 第 {current_chapter} 章 - {line}")
            
            # 创建 NovelContent 对象
            novel_content = NovelContent(
                session_id=session_id,
                chapter=current_chapter,
                line=line_number,
                content=line
            )
            novel_contents.append(novel_content)
            line_number += 1
        
        logger.info(f"解析小说成功: 共 {len(novel_contents)} 行, {current_chapter} 章")
        return novel_contents
    
    @classmethod
    def _is_chapter_title(cls, line: str) -> bool:
        """
        判断一行文本是否是章节标题。
        
        :param line: 文本行
        :return: 是否是章节标题
        """
        for pattern in cls.CHAPTER_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                return True
        return False


# 全局单例
novel_parser = NovelParser()

