"""
哈希计算工具。

提供文件哈希计算功能。
"""
import hashlib
from pathlib import Path


def sha256(file_path: Path, buffer_size: int = 65536) -> str:
    """
    以流式方式计算文件的 SHA-256 哈希值。
    
    :param file_path: 文件路径
    :param buffer_size: 读取块大小（字节）
    :return: 十六进制摘要字符串
    """
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        for chunk in iter(lambda: f.read(buffer_size), b""):
            h.update(chunk)
    return h.hexdigest()

