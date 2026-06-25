"""
安全模块。

提供密码 MD5 加密/校验，以及 JWT 令牌的生成与解析功能。
"""

import hashlib
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from server.core.config import settings


def md5_password(raw_password: str) -> str:
    """对明文密码进行 MD5 加密，返回 32 位小写十六进制字符串。"""
    return hashlib.md5(raw_password.encode("utf-8")).hexdigest()


def verify_password(raw_password: str, encrypted: str) -> bool:
    """校验明文密码与已加密密码是否匹配。"""
    return md5_password(raw_password) == encrypted


def create_access_token(data: dict) -> str:
    """根据传入数据生成 JWT 访问令牌，并附加过期时间。"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict | None:
    """解析 JWT 令牌，成功返回载荷字典，失败返回 None。"""
    try:
        return jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
    except JWTError:
        return None
