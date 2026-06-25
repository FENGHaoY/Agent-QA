"""
应用配置模块。

使用 pydantic-settings 从项目根目录的 .env 文件读取配置，
集中管理数据库、JWT、大模型与向量库等参数。
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# 项目根目录（server 的上一级目录）
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# .env 文件路径
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """全局配置类，字段名与 .env 中的键（不区分大小写）对应。"""

    # ===== MySQL 数据库配置 =====
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "123456"
    mysql_db: str = "db_enterprise_ga"

    # ===== JWT 鉴权配置 =====
    jwt_secret_key: str = "rag-qa-enterprise-secret-key-2026"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # ===== DashScope（Qwen）大模型与嵌入配置 =====
    dashscope_api_key: str = ""
    dashscope_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_model: str = "qwen-plus"
    embedding_model: str = "text-embedding-v4"
    # 检索后重排模型（DashScope/Qwen rerank）
    rerank_model: str = "gte-rerank-v2"

    # ===== DeepSeek（查询重写用的小模型）=====
    deepseek_api_key: str = ""
    query_rewrite_model: str = "deepseek-chat"

    # ===== Tavily 联网搜索配置 =====
    tavily_api_key: str = ""

    # ===== MinerU 文档解析配置（precision 模式需要 token）=====
    mineru_token: str = ""

    # 允许 .env 中存在未在此声明的额外键（如 OSS 等）
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """拼接 SQLAlchemy 使用的 MySQL 连接串（PyMySQL 驱动）。"""
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}?charset=utf8mb4"
        )


# 全局唯一配置实例
settings = Settings()

# Chroma 向量库持久化目录
CHROMA_DIR = BASE_DIR / "server" / "chroma_db"
# 上传文件存储目录
UPLOAD_DIR = BASE_DIR / "server" / "uploads"
# 会话短期记忆 SQLite 文件（LangGraph checkpointer 持久化对话状态）
CHAT_MEMORY_DB = BASE_DIR / "server" / "chat_memory.sqlite"
