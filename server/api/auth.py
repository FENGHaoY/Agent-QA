"""认证相关接口：登录、获取当前用户信息。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.core.deps import get_current_user
from server.core.security import create_access_token, verify_password
from server.models.user import User
from server.schemas.common import ApiResponse
from server.schemas.user import LoginRequest, LoginResponse, UserOut

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=ApiResponse[LoginResponse], summary="用户登录")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> ApiResponse:
    """校验用户名密码，成功后返回 JWT 令牌与用户信息。"""
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or not verify_password(payload.password, user.password):
        raise HTTPException(status_code=400, detail="用户名或密码错误")
    if user.status != 1:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    # 令牌主体存放用户ID
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return ApiResponse.ok(
        LoginResponse(access_token=token, user=UserOut.model_validate(user))
    )


@router.get("/me", response_model=ApiResponse[UserOut], summary="获取当前登录用户")
def me(current_user: User = Depends(get_current_user)) -> ApiResponse:
    """返回当前登录用户的信息。"""
    return ApiResponse.ok(UserOut.model_validate(current_user))
