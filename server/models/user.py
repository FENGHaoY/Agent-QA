"""用户 ORM 模型。"""

from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from server.core.database import Base


class User(Base):
    """用户表 t_user，对应系统中的管理员与普通用户。"""

    __tablename__ = "t_user"

    # 用户主键ID
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, comment="用户主键ID")
    # 登录用户名（唯一）
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="登录用户名")
    # 密码（MD5 加密，32 位）
    password: Mapped[str] = mapped_column(String(32), nullable=False, comment="密码（MD5加密）")
    # 真实姓名
    real_name: Mapped[str | None] = mapped_column(String(50), nullable=True, comment="真实姓名")
    # 角色：admin=管理员，user=普通用户
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False, comment="角色")
    # 状态：1=启用，0=禁用
    status: Mapped[int] = mapped_column(default=1, nullable=False, comment="状态：1启用 0禁用")
    # 创建时间
    create_time: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="创建时间"
    )
