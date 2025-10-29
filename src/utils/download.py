"""
下载和 URL 处理工具。

提供通用的文件下载、URL 类型判断等功能。
"""
from pathlib import Path
from urllib.parse import urlparse, unquote

import httpx
import aiofiles
from loguru import logger


def is_local_url(url: str) -> bool:
    """
    判断 URL 是否为本地 file:// URL。
    
    :param url: URL 字符串
    :return: 是否为本地 URL
    """
    parsed = urlparse(url)
    return parsed.scheme == 'file' or not parsed.scheme


def url_to_path(url: str) -> Path | None:
    """
    将 file:// URL 转换为本地路径。
    
    :param url: file:// URL
    :return: 本地路径，如果不是 file:// URL 则返回 None
    """
    if not is_local_url(url):
        return None
    
    parsed = urlparse(url)
    if parsed.scheme == 'file':
        # file:///C:/path/to/file -> C:/path/to/file
        path_str = unquote(parsed.path)
        # Windows 路径处理：移除开头的 '/'
        if path_str.startswith('/') and len(path_str) > 2 and path_str[2] == ':':
            path_str = path_str[1:]
        return Path(path_str)
    else:
        # 相对或绝对路径
        return Path(url)


async def download_file(
    url: str,
    save_path: Path,
    timeout: float = 30.0,
    create_dirs: bool = True
) -> bool:
    """
    异步下载文件。
    
    :param url: 文件 URL
    :param save_path: 保存路径
    :param timeout: 超时时间（秒）
    :param create_dirs: 是否自动创建目录
    :return: 是否下载成功
    """
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.error(f"下载文件失败 [{resp.status_code}]: {url}")
                return False
            
            if create_dirs:
                save_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with aiofiles.open(save_path, 'wb') as f:
                await f.write(resp.content)
            
            logger.debug(f"下载文件成功: {save_path.name}")
            return True
    except (httpx.HTTPError, IOError, OSError) as e:
        logger.error(f"下载文件异常 {url}: {e}")
        return False

