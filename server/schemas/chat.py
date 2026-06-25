"""问答相关的 Pydantic 模型。"""

from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """问答请求体。"""

    question: str = Field(..., description="用户问题")
    use_web: bool = Field(default=False, description="是否启用 Tavily 联网搜索")
    session_id: str | None = Field(
        default=None, description="前端会话标识，用于维持同一会话的多轮上下文记忆"
    )


class SourceItem(BaseModel):
    """回答引用的来源条目。"""

    title: str  # 来源标题（文档标题或网页标题）
    snippet: str | None = None  # 来源片段
    url: str | None = None  # 网页链接（联网搜索时）


class ChatResponse(BaseModel):
    """问答响应体。"""

    answer: str  # Agent 回答
    sources: list[SourceItem] = []  # 引用来源列表


class ChatSessionOut(BaseModel):
    """会话列表项：一个会话聚合为一条历史栏目。"""

    session_id: str  # 会话标识（兼容历史空值时为 legacy-{id}）
    title: str  # 会话标题（取该会话最早一条问题）
    last_time: datetime  # 该会话最后一次问答时间
    count: int  # 该会话内问答轮数


class ChatMessageOut(BaseModel):
    """会话详情中的单条问答。"""

    id: int
    question: str
    answer: str | None = None
    sources: list[SourceItem] = []
    use_web: int
    create_time: datetime
