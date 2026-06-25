"""问答历史 ORM 模型。"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from server.core.database import Base


class ChatHistory(Base):
    """问答历史表 t_chat_history，记录每次提问与回答。"""

    __tablename__ = "t_chat_history"

    # 问答记录主键ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="问答记录主键ID")
    # 提问用户ID
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, comment="提问用户ID")
    # 会话ID：同一会话的多轮问答共享，用于按会话聚合历史
    session_id: Mapped[str | None] = mapped_column(
        String(64), index=True, nullable=True, comment="会话ID"
    )
    # 用户问题
    question: Mapped[str] = mapped_column(Text, nullable=False, comment="用户问题")
    # Agent 回答
    answer: Mapped[str | None] = mapped_column(Text, nullable=True, comment="Agent回答")
    # 引用来源（JSON 字符串）
    sources: Mapped[str | None] = mapped_column(Text, nullable=True, comment="引用来源JSON")
    # 是否启用联网搜索：1=是，0=否
    use_web: Mapped[int] = mapped_column(default=0, nullable=False, comment="是否联网")
    # 创建时间
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
