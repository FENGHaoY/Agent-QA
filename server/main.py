"""
FastAPI 应用入口。

负责创建应用实例、配置 CORS、注册各业务路由，
并在启动时确保 Chroma 向量库目录与上传目录存在。
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.api import auth, chat, documents, stats, users
from server.core.config import CHROMA_DIR, UPLOAD_DIR


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期钩子：启动时确保所需目录存在。"""
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    yield


# 创建 FastAPI 应用
app = FastAPI(
    title="RAG 企业内部知识库问答 Agent 系统",
    description="基于 LangChain + Qwen + Chroma 的企业知识库问答后端服务",
    version="0.1.0",
    lifespan=lifespan,
)

# 配置跨域，允许前端开发服务器访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", tags=["健康检查"], summary="健康检查")
def health() -> dict:
    """健康检查接口，返回服务状态。"""
    return {"status": "ok"}


# 注册业务路由
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(stats.router)
