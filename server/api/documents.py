"""文档管理接口（仅管理员可访问）：上传入库、列表、删除。"""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from server.core.config import UPLOAD_DIR
from server.core.database import get_db
from server.core.deps import admin_required
from server.models.document import Document
from server.models.user import User
from server.schemas.common import ApiResponse
from server.schemas.document import DocumentOut
from server.services import rag_service

router = APIRouter(prefix="/api/documents", tags=["文档管理"])

# 允许上传的文件扩展名
ALLOWED_EXTENSIONS = {"pdf", "txt", "md", "docx"}


@router.get("", response_model=ApiResponse[list[DocumentOut]], summary="文档列表")
def list_documents(
    db: Session = Depends(get_db), _: User = Depends(admin_required)
) -> ApiResponse:
    """查询全部知识库文档列表。"""
    docs = db.query(Document).order_by(Document.id.desc()).all()
    return ApiResponse.ok([DocumentOut.model_validate(d) for d in docs])


@router.post("/upload", response_model=ApiResponse[DocumentOut], summary="上传文档并入库")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required),
) -> ApiResponse:
    """
    上传文档：保存到本地 -> 解析切片 -> 写入 Chroma 向量库 -> 记录数据库。
    """
    filename = file.filename or "unknown"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400, detail=f"不支持的文件类型，仅支持：{', '.join(ALLOWED_EXTENSIONS)}"
        )

    # 以 uuid 重命名保存，避免重名覆盖
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_name = f"{uuid.uuid4().hex}.{ext}"
    saved_path = UPLOAD_DIR / saved_name
    content = await file.read()
    saved_path.write_bytes(content)

    # 先落库一条记录（状态默认已入库，失败时再修正）
    doc = Document(
        title=Path(filename).stem,
        filename=filename,
        file_path=str(saved_path),
        file_type=ext,
        file_size=len(content),
        chunk_count=0,
        status=1,
        uploader_id=current_user.id,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    # 解析并写入向量库
    try:
        chunk_count = rag_service.ingest_document(
            doc_id=doc.id, title=doc.title, file_path=str(saved_path), file_type=ext
        )
        doc.chunk_count = chunk_count
        doc.status = 1 if chunk_count > 0 else 0
        db.commit()
        db.refresh(doc)
    except Exception as exc:  # noqa: BLE001 - 入库失败需返回明确提示
        doc.status = 0
        db.commit()
        raise HTTPException(status_code=500, detail=f"文档入库失败：{exc}") from exc

    return ApiResponse.ok(DocumentOut.model_validate(doc), message="上传并入库成功")


@router.delete("/{doc_id}", response_model=ApiResponse[None], summary="删除文档")
def delete_document(
    doc_id: int, db: Session = Depends(get_db), _: User = Depends(admin_required)
) -> ApiResponse:
    """删除文档：移除向量库切片 -> 删除本地文件 -> 删除数据库记录。"""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if doc is None:
        raise HTTPException(status_code=404, detail="文档不存在")

    # 清理向量库
    try:
        rag_service.delete_document_vectors(doc.id)
    except Exception:  # noqa: BLE001 - 向量删除失败不阻塞记录删除
        pass

    # 删除本地文件
    file_path = Path(doc.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except OSError:
            pass

    db.delete(doc)
    db.commit()
    return ApiResponse.ok(message="删除成功")
