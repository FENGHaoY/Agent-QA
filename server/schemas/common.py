"""通用响应模型。"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

# 泛型类型变量，用于通用响应的 data 字段
T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """统一接口响应结构。"""

    code: int = 0  # 业务状态码：0=成功，非0=失败
    message: str = "success"  # 提示信息
    data: T | None = None  # 响应数据

    @classmethod
    def ok(cls, data: Any = None, message: str = "success") -> "ApiResponse":
        """构造成功响应。"""
        return cls(code=0, message=message, data=data)

    @classmethod
    def fail(cls, message: str, code: int = 1) -> "ApiResponse":
        """构造失败响应。"""
        return cls(code=code, message=message, data=None)
