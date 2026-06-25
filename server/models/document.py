"""知识库文档 ORM 模型。"""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from server.core.database import Base


class Document(Base):
    """文档表 t_document，记录上传到知识库的文件元信息。"""

    __tablename__ = "t_document"

    # 文档主键ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="文档主键ID")
    # 文档标题
    title: Mapped[str] = mapped_column(String(255), nullable=False, comment="文档标题")
    # 原始文件名
    filename: Mapped[str] = mapped_column(String(255), nullable=False, comment="原始文件名")
    # 服务器存储路径
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="服务器存储路径")
    # 文件类型：pdf/txt/md/docx
    file_type: Mapped[str] = mapped_column(String(20), nullable=False, comment="文件类型")
    # 文件大小（字节）
    file_size: Mapped[int] = mapped_column(BigInteger, default=0, comment="文件大小（字节）")
    # 切片数量
    chunk_count: Mapped[int] = mapped_column(Integer, default=0, comment="切片数量")
    # 状态：1=已入库，0=处理中/失败
    status: Mapped[int] = mapped_column(default=1, nullable=False, comment="状态：1已入库 0失败")
    # 上传人ID
    uploader_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, comment="上传人ID")
    # 创建时间
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
