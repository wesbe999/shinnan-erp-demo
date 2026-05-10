from __future__ import annotations

import json
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel
from app.config import DATA_DIR

router = APIRouter(tags=["通知"])

DATA_DIR.mkdir(parents=True, exist_ok=True)

NOTICE_FILE = DATA_DIR / "emergency_notices.json"
MAX_NOTICES = 20


class EmergencyNoticeIn(BaseModel):
    message: str | None = None
    notice: str | None = None
    delete_index: int | None = None
    clear_all: bool = False
    clear: bool = False


def _load_notices() -> list[str]:
    if not NOTICE_FILE.exists():
        return []

    try:
        data: Any = json.loads(NOTICE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return []

    if isinstance(data, dict):
        raw = data.get("notices")
        if isinstance(raw, list):
            return [str(x).strip() for x in raw if str(x).strip()]

        old_message = data.get("message") or data.get("notice") or ""
        old_message = str(old_message).strip()
        return [old_message] if old_message else []

    if isinstance(data, list):
        return [str(x).strip() for x in data if str(x).strip()]

    return []


def _save_notices(items: list[str]) -> None:
    clean = [str(x).strip() for x in items if str(x).strip()]
    clean = clean[-MAX_NOTICES:]
    NOTICE_FILE.write_text(
        json.dumps({"notices": clean}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _response(notices: list[str]) -> dict[str, Any]:
    message = "　　｜　　".join(notices)

    return {
        "ok": True,
        "message": message,
        "notice": message,
        "notices": notices,
        "count": len(notices),
    }


@router.get("/api/notices/emergency")
def get_emergency_notice():
    notices = _load_notices()
    return _response(notices)


@router.post("/api/notices/emergency")
def update_emergency_notice(payload: EmergencyNoticeIn):
    notices = _load_notices()

    if payload.clear_all or payload.clear:
        _save_notices([])
        return _response([])

    if payload.delete_index is not None:
        index = payload.delete_index
        if 0 <= index < len(notices):
            notices.pop(index)
            _save_notices(notices)
        return _response(_load_notices())

    text = (payload.message or payload.notice or "").strip()

    if text:
        notices.append(text)
        _save_notices(notices)

    return _response(_load_notices())
