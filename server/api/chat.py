"""问答接口：知识库问答与历史记录。"""

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from server.core.database import get_db
from server.core.deps import get_current_user
from server.models.chat import ChatHistory
from server.models.user import User
from server.schemas.chat import (
    ChatMessageOut,
    ChatRequest,
    ChatResponse,
    ChatSessionOut,
    SourceItem,
)
from server.schemas.common import ApiResponse
from server.services import agent_service

# 历史记录中 session_id 为空时的兜底分组键（旧数据各自成单条会话）
_LEGACY_GROUP = func.coalesce(ChatHistory.session_id, func.concat("legacy-", ChatHistory.id))

router = APIRouter(prefix="/api/chat", tags=["智能问答"])


@router.post("/ask", response_model=ApiResponse[ChatResponse], summary="知识库问答")
def ask(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """调用问答 Agent 生成回答，并保存问答历史。"""
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    # 会话记忆线程标识：拼接用户ID与前端会话ID，确保用户间记忆相互隔离
    thread_id = f"u{current_user.id}:{payload.session_id}" if payload.session_id else None

    try:
        result = agent_service.answer_question(
            payload.question, use_web=payload.use_web, thread_id=thread_id
        )
    except Exception as exc:  # noqa: BLE001 - 模型调用异常需返回提示
        raise HTTPException(status_code=500, detail=f"问答失败：{exc}") from exc

    sources = [SourceItem(**s) for s in result["sources"]]

    # 保存问答历史
    history = ChatHistory(
        user_id=current_user.id,
        session_id=payload.session_id,
        question=payload.question,
        answer=result["answer"],
        sources=json.dumps(result["sources"], ensure_ascii=False),
        use_web=1 if payload.use_web else 0,
    )
    db.add(history)
    db.commit()

    return ApiResponse.ok(ChatResponse(answer=result["answer"], sources=sources))


@router.get("/sessions", response_model=ApiResponse[list[ChatSessionOut]], summary="我的会话历史列表")
def list_sessions(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ApiResponse:
    """
    按会话聚合返回当前用户的历史：每个会话一项，标题取该会话最早的问题，
    并附带最后一次问答时间与轮数，按最后时间倒序。
    """
    group_key = _LEGACY_GROUP.label("sid")
    rows = (
        db.query(
            group_key,
            func.min(ChatHistory.id).label("first_id"),
            func.max(ChatHistory.create_time).label("last_time"),
            func.count(ChatHistory.id).label("cnt"),
        )
        .filter(ChatHistory.user_id == current_user.id)
        .group_by(group_key)
        .order_by(func.max(ChatHistory.create_time).desc())
        .all()
    )

    # 批量取出每个会话首条记录的问题作为标题
    first_ids = [r.first_id for r in rows]
    title_map: dict[int, str] = {}
    if first_ids:
        for rec in db.query(ChatHistory.id, ChatHistory.question).filter(
            ChatHistory.id.in_(first_ids)
        ):
            title_map[rec.id] = rec.question

    sessions = [
        ChatSessionOut(
            session_id=r.sid,
            title=title_map.get(r.first_id, "（无标题）"),
            last_time=r.last_time,
            count=r.cnt,
        )
        for r in rows
    ]
    return ApiResponse.ok(sessions)


@router.get(
    "/sessions/{session_id}",
    response_model=ApiResponse[list[ChatMessageOut]],
    summary="会话内全部问答",
)
def session_detail(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ApiResponse:
    """按时间正序返回某个会话内的全部问答（含来源），仅限本人会话。"""
    records = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id, _LEGACY_GROUP == session_id)
        .order_by(ChatHistory.id.asc())
        .all()
    )

    messages: list[ChatMessageOut] = []
    for r in records:
        try:
            raw_sources = json.loads(r.sources) if r.sources else []
        except (ValueError, TypeError):
            raw_sources = []
        messages.append(
            ChatMessageOut(
                id=r.id,
                question=r.question,
                answer=r.answer,
                sources=[SourceItem(**s) for s in raw_sources if isinstance(s, dict)],
                use_web=r.use_web,
                create_time=r.create_time,
            )
        )
    return ApiResponse.ok(messages)
