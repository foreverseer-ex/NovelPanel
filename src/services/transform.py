"""
文件转换服务。

将各种格式的小说文件转换为纯文本格式。
使用 LangChain 的文档加载器进行文件解析和转换。
"""
from pathlib import Path
from loguru import logger


class TransformService:
    """
    文件转换服务。
    
    使用 LangChain 的文档加载器支持将多种文件格式转换为纯文本：
    - TXT: 直接读取（UTF-8/GBK 自动检测）
    - PDF: 使用 PyPDFLoader 提取文本
    - DOC/DOCX: 使用 Docx2txtLoader 提取文本
    
    参考文档：
    - PDF: https://python.langchain.ac.cn/docs/how_to/document_loader_pdf/
    - DOCX: https://python.langchain.ac.cn/docs/integrations/document_loaders/microsoft_word/
    """
    
    @staticmethod
    def transform_to_txt(source_path: Path, target_path: Path) -> bool:
        """
        将源文件转换为纯文本文件。
        
        :param source_path: 源文件路径
        :param target_path: 目标文本文件路径
        :return: 是否转换成功
        """
        if not source_path.exists():
            logger.error(f"源文件不存在: {source_path}")
            return False
        
        # 确保目标目录存在
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 根据文件扩展名选择转换方法
        suffix = source_path.suffix.lower()
        
        try:
            if suffix == '.txt':
                return TransformService._convert_txt(source_path, target_path)
            elif suffix == '.pdf':
                return TransformService._convert_pdf(source_path, target_path)
            elif suffix in ['.doc', '.docx']:
                return TransformService._convert_docx(source_path, target_path)
            else:
                logger.warning(f"不支持的文件格式: {suffix}")
                return False
                
        except Exception as e:
            logger.exception(f"文件转换失败: {e}")
            return False
    
    @staticmethod
    def _convert_txt(source_path: Path, target_path: Path) -> bool:
        """
        转换 TXT 文件（直接复制或重新编码）。
        
        :param source_path: 源文件路径
        :param target_path: 目标文件路径
        :return: 是否转换成功
        """
        try:
            # 尝试以 UTF-8 读取
            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # 如果 UTF-8 失败，尝试 GBK
                with open(source_path, 'r', encoding='gbk') as f:
                    content = f.read()
            
            # 写入目标文件（UTF-8）
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.success(f"TXT 文件转换成功: {source_path} -> {target_path}")
            return True
            
        except Exception as e:
            logger.exception(f"TXT 文件转换失败: {e}")
            return False
    
    @staticmethod
    def _convert_pdf(source_path: Path, target_path: Path) -> bool:
        """
        转换 PDF 文件为文本（使用 LangChain 的 PyPDFLoader）。
        
        :param source_path: 源文件路径
        :param target_path: 目标文件路径
        :return: 是否转换成功
        """
        try:
            # 尝试导入 LangChain PDF 加载器
            try:
                from langchain_community.document_loaders import PyPDFLoader
            except ImportError:
                logger.error("PDF 转换需要安装 langchain-community: pip install langchain-community pypdf")
                return False
            
            # 使用 LangChain 加载 PDF
            loader = PyPDFLoader(str(source_path))
            documents = loader.load()
            
            # 提取所有文档的文本内容
            text_content = [doc.page_content for doc in documents]
            content = '\n\n'.join(text_content)
            
            # 写入目标文件
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.success(f"PDF 文件转换成功 (LangChain): {source_path} -> {target_path}, 共 {len(documents)} 页")
            return True
            
        except Exception as e:
            logger.exception(f"PDF 文件转换失败: {e}")
            return False
    
    @staticmethod
    def _convert_docx(source_path: Path, target_path: Path) -> bool:
        """
        转换 DOC/DOCX 文件为文本（使用 LangChain 的 Docx2txtLoader）。
        
        :param source_path: 源文件路径
        :param target_path: 目标文件路径
        :return: 是否转换成功
        """
        try:
            # 尝试导入 LangChain DOCX 加载器
            try:
                from langchain_community.document_loaders import Docx2txtLoader
            except ImportError:
                logger.error("DOCX 转换需要安装 langchain-community: pip install langchain-community docx2txt")
                return False
            
            # 使用 LangChain 加载 DOCX
            loader = Docx2txtLoader(str(source_path))
            documents = loader.load()
            
            # 提取所有文档的文本内容
            text_content = [doc.page_content for doc in documents]
            content = '\n'.join(text_content)
            
            # 写入目标文件
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.success(f"DOCX 文件转换成功 (LangChain): {source_path} -> {target_path}")
            return True
            
        except Exception as e:
            logger.exception(f"DOCX 文件转换失败: {e}")
            return False
    
    @staticmethod
    def get_supported_extensions() -> list[str]:
        """
        获取支持的文件扩展名列表。
        
        :return: 支持的扩展名列表
        """
        return ['.txt', '.pdf', '.doc', '.docx']
    
    @staticmethod
    def is_supported(file_path: Path) -> bool:
        """
        检查文件格式是否支持。
        
        :param file_path: 文件路径
        :return: 是否支持
        """
        return file_path.suffix.lower() in TransformService.get_supported_extensions()


# 全局单例
transform_service = TransformService()

