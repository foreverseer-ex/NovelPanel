"""
文件管理的路由。

简化设计：只处理小说文件和生成图像的读写。
"""
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse


router = APIRouter(
    prefix="/file",
    tags=["文件管理"],
    responses={404: {"description": "文件不存在"}},
)


# ==================== 小说文件 ====================

@router.put("/novel", summary="上传/保存小说文件")
async def put_novel(
    session_id: str,
    file: UploadFile = File(..., description="小说文件（TXT）")
) -> dict:
    """
    上传/保存小说文件到会话。
    
    Args:
        session_id: 会话ID
        file: 小说文件（TXT格式）
    
    Returns:
        保存结果，包含文件路径等信息
    
    实现要点：
    - 自动检测文本编码
    - 保存到会话目录（如 storage/sessions/{session_id}/novel.txt）
    - 触发小说解析任务
    """
    # TODO: 实现小说文件上传逻辑
    raise NotImplementedError("小说文件上传功能尚未实现")


@router.get("/novel", response_class=FileResponse, summary="获取小说文件")
async def get_novel(session_id: str) -> FileResponse:
    """
    获取会话的小说文件。
    
    Args:
        session_id: 会话ID
    
    Returns:
        小说文件内容
    
    实现要点：
    - 返回会话目录下的小说文件
    - 设置正确的 Content-Type
    """
    # TODO: 实现小说文件获取逻辑
    raise NotImplementedError("小说文件获取功能尚未实现")


# ==================== 生成图像 ====================

@router.put("/image", summary="保存生成的图像")
async def put_image(
    session_id: str,
    line: int,
    file: UploadFile = File(..., description="生成的图像文件")
) -> dict:
    """
    保存生成的图像。
    
    Args:
        session_id: 会话ID
        line: 行号（从0开始）
        file: 图像文件
    
    Returns:
        保存结果，包含文件路径等信息
    
    实现要点：
    - 保存到会话目录（如 storage/sessions/{session_id}/images/{line}.png）
    - 自动创建目录
    - 覆盖同名文件
    """
    # TODO: 实现图像保存逻辑
    raise NotImplementedError("图像保存功能尚未实现")


@router.get("/image", response_class=FileResponse, summary="获取生成的图像")
async def get_image(
    session_id: str,
    line: int
) -> FileResponse:
    """
    获取指定行的生成图像。
    
    Args:
        session_id: 会话ID
        line: 行号（从0开始）
    
    Returns:
        图像文件
    
    实现要点：
    - 返回会话目录下的图像文件
    - 设置正确的 Content-Type
    - 如果文件不存在，返回404
    """
    # TODO: 实现图像获取逻辑
    raise NotImplementedError("图像获取功能尚未实现")
