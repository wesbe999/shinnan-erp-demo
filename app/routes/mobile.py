from fastapi import APIRouter
from fastapi.responses import RedirectResponse

router = APIRouter(tags=["工程師手機版"])


@router.get("/mobile", summary="舊手機派工頁導向新版派工 APP")
def mobile_page():
    return RedirectResponse(url="/app/dispatch", status_code=307)
