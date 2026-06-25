"""
鉴权依赖模块。

提供从请求头解析 JWT、获取当前登录用户，以及管理员权限校验的 FastAPI 依赖。
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.core.security import decode_token
from server.models.user import User

# OAuth2 令牌提取器，tokenUrl 指向登录接口
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """解析令牌并返回当前登录用户，令牌无效或用户被禁用时抛出 401。"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录凭证无效或已过期",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    if user.status != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")
    return user


def admin_required(current_user: User = Depends(get_current_user)) -> User:
    """管理员权限校验依赖，非管理员访问时抛出 403。"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="需要管理员权限"
        )
    return current_user
