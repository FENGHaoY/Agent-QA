"""文档相关的 Pydantic 模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentOut(BaseModel):
    """文档信息输出模型。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    filename: str
    file_type: str
    file_size: int
    chunk_count: int
    status: int
    uploader_id: int | None = None
    create_time: datetime
