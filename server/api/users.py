"""用户管理接口（仅管理员可访问）。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.core.deps import admin_required
from server.core.security import md5_password
from server.models.user import User
from server.schemas.common import ApiResponse
from server.schemas.user import UserCreate, UserOut, UserUpdate

router = APIRouter(prefix="/api/users", tags=["用户管理"], dependencies=[Depends(admin_required)])


@router.get("", response_model=ApiResponse[list[UserOut]], summary="用户列表")
def list_users(db: Session = Depends(get_db)) -> ApiResponse:
    """查询全部用户列表。"""
    users = db.query(User).order_by(User.id.asc()).all()
    return ApiResponse.ok([UserOut.model_validate(u) for u in users])


@router.post("", response_model=ApiResponse[UserOut], summary="新增用户")
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> ApiResponse:
    """新增用户，密码以 MD5 方式加密存储。"""
    exists = db.query(User).filter(User.username == payload.username).first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名已存在")

    user = User(
        username=payload.username,
        password=md5_password(payload.password),
        real_name=payload.real_name,
        role=payload.role,
        status=payload.status,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return ApiResponse.ok(UserOut.model_validate(user), message="新增成功")


@router.put("/{user_id}", response_model=ApiResponse[UserOut], summary="修改用户")
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)) -> ApiResponse:
    """修改用户信息，密码留空则不变。"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    if payload.password:
        user.password = md5_password(payload.password)
    if payload.real_name is not None:
        user.real_name = payload.real_name
    if payload.role is not None:
        user.role = payload.role
    if payload.status is not None:
        user.status = payload.status

    db.commit()
    db.refresh(user)
    return ApiResponse.ok(UserOut.model_validate(user), message="修改成功")


@router.delete("/{user_id}", response_model=ApiResponse[None], summary="删除用户")
def delete_user(user_id: int, db: Session = Depends(get_db)) -> ApiResponse:
    """删除指定用户。"""
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    db.delete(user)
    db.commit()
    return ApiResponse.ok(message="删除成功")
