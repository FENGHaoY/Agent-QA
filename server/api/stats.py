"""首页统计接口（仅管理员）：提供数据概览与图表数据。"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.core.deps import admin_required
from server.models.chat import ChatHistory
from server.models.document import Document
from server.models.user import User
from server.schemas.common import ApiResponse

router = APIRouter(prefix="/api/stats", tags=["数据统计"], dependencies=[Depends(admin_required)])


@router.get("/overview", response_model=ApiResponse, summary="首页数据总览")
def overview(db: Session = Depends(get_db)) -> ApiResponse:
    """
    返回首页所需的统计数据：

    - 概览卡片：用户数、文档数、问答总数、切片总数；
    - 近 7 天问答趋势（折线图）；
    - 文档类型分布（饼图）；
    - 用户角色分布（饼图）。
    """
    # ===== 概览卡片 =====
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_documents = db.query(func.count(Document.id)).scalar() or 0
    total_chats = db.query(func.count(ChatHistory.id)).scalar() or 0
    total_chunks = db.query(func.coalesce(func.sum(Document.chunk_count), 0)).scalar() or 0

    # ===== 近 7 天问答趋势 =====
    today = datetime.now().date()
    start_date = today - timedelta(days=6)
    rows = (
        db.query(
            func.date(ChatHistory.create_time).label("day"),
            func.count(ChatHistory.id).label("cnt"),
        )
        .filter(ChatHistory.create_time >= datetime.combine(start_date, datetime.min.time()))
        .group_by(func.date(ChatHistory.create_time))
        .all()
    )
    # 将查询结果转为按日期映射，便于补齐缺失日期
    count_map = {str(r.day): r.cnt for r in rows}
    trend_dates: list[str] = []
    trend_counts: list[int] = []
    for i in range(7):
        day = start_date + timedelta(days=i)
        key = day.strftime("%Y-%m-%d")
        trend_dates.append(day.strftime("%m-%d"))
        trend_counts.append(int(count_map.get(key, 0)))

    # ===== 文档类型分布 =====
    type_rows = (
        db.query(Document.file_type, func.count(Document.id))
        .group_by(Document.file_type)
        .all()
    )
    doc_types = [{"name": t or "未知", "value": c} for t, c in type_rows]

    # ===== 用户角色分布 =====
    role_rows = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    role_label = {"admin": "管理员", "user": "普通用户"}
    user_roles = [{"name": role_label.get(r, r), "value": c} for r, c in role_rows]

    data = {
        "cards": {
            "users": total_users,
            "documents": total_documents,
            "chats": total_chats,
            "chunks": int(total_chunks),
        },
        "chat_trend": {"dates": trend_dates, "counts": trend_counts},
        "doc_types": doc_types,
        "user_roles": user_roles,
    }
    return ApiResponse.ok(data)
