"""用户相关的 Pydantic 模型。"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    """登录请求体。"""

    username: str = Field(..., description="用户名")
    password: str = Field(..., description="明文密码")


class LoginResponse(BaseModel):
    """登录成功响应。"""

    access_token: str  # JWT 访问令牌
    token_type: str = "bearer"  # 令牌类型
    user: "UserOut"  # 用户信息


class UserOut(BaseModel):
    """用户信息输出模型（不含密码）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    real_name: str | None = None
    role: str
    status: int
    create_time: datetime


class UserCreate(BaseModel):
    """创建用户请求体。"""

    username: str = Field(..., max_length=50, description="用户名")
    password: str = Field(default="123456", description="明文密码，默认123456")
    real_name: str | None = Field(default=None, max_length=50, description="真实姓名")
    role: str = Field(default="user", description="角色：admin/user")
    status: int = Field(default=1, description="状态：1启用 0禁用")


class UserUpdate(BaseModel):
    """更新用户请求体（密码可选，留空则不修改）。"""

    password: str | None = Field(default=None, description="新密码，留空不修改")
    real_name: str | None = Field(default=None, max_length=50)
    role: str | None = None
    status: int | None = None


# 解决 LoginResponse 中对 UserOut 的前向引用
LoginResponse.model_rebuild()
