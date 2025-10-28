"""
MCP (Model Context Protocol) 服务入口。

使用 fastapi_mcp 将 FastAPI 应用暴露为 MCP 工具，
提供小说转漫画的完整工作流 API。
"""
import asyncio

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_mcp import FastApiMCP
from loguru import logger

from routers import session, actor, memory, reader, file, draw


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    应用生命周期管理。
    
    在应用启动时执行初始化操作，在关闭时执行清理操作。
    """
    # Startup
    logger.info("NovelPanel MCP API 启动中...")
    logger.info("FastAPI 文档: http://127.0.0.1:8000/docs")
    logger.info("MCP 服务端点: http://127.0.0.1:8000/mcp")

    yield

    # Shutdown
    logger.info("NovelPanel MCP API 关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="NovelPanel MCP API",
    description="小说转漫画的 Model Context Protocol API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# 配置 CORS（允许前端访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册所有路由
app.include_router(session.router)
app.include_router(actor.router)
app.include_router(memory.router)
app.include_router(reader.router)
app.include_router(file.router)
app.include_router(draw.router)


@app.get("/", summary="API 根路径")
async def root():
    """
    API 根路径，返回欢迎信息。
    """
    return {
        "message": "Welcome to NovelPanel MCP API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "mcp": "/mcp",
    }


@app.get("/health", summary="健康检查")
async def health_check():
    """
    健康检查接口。
    """
    return {
        "status": "ok",
        "service": "NovelPanel MCP",
    }




# 创建 FastApiMCP 实例并挂载到 FastAPI 应用
# 这会在 /mcp 路径下提供 MCP 服务
mcp = FastApiMCP(app)
mcp.mount_http()  # 使用 mount_http() 方法挂载 HTTP 传输

#
# def main():
#     """
#     启动 MCP 服务。
#
#     使用 uvicorn 运行 FastAPI 应用。
#     MCP 工具会在 /mcp 端点下可用。
#     """
#     uvicorn.run(
#         "mcp:app",
#         host="127.0.0.1",
#         port=8000,
#         reload=True,  # 开发模式下自动重载
#         log_level="info",
#     )
#
#
# if __name__ == "__main__":
#     main()
#
