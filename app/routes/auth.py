from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["登入驗證"])


class LoginRequest(BaseModel):
    username: str
    password: str


ENGINEERS = [
    {"employee_no": "E001", "password": "1234", "name": "郭富城", "department": "東區"},
    {"employee_no": "E002", "password": "1234", "name": "劉德華", "department": "東區"},
    {"employee_no": "E003", "password": "1234", "name": "黎明", "department": "北區"},
    {"employee_no": "E004", "password": "1234", "name": "張學友", "department": "北區"},
    {"employee_no": "E005", "password": "1234", "name": "吳文化", "department": "北台南"},
    {"employee_no": "E006", "password": "1234", "name": "吳宗憲", "department": "北台南"},
    {"employee_no": "E007", "password": "1234", "name": "羅啟彰", "department": "仁德"},
    {"employee_no": "E008", "password": "1234", "name": "林華山", "department": "仁德"},
    {"employee_no": "E009", "password": "1234", "name": "陳志明", "department": "永康"},
    {"employee_no": "E010", "password": "1234", "name": "王建國", "department": "永康"},
    {"employee_no": "E011", "password": "1234", "name": "李承翰", "department": "安平"},
    {"employee_no": "E012", "password": "1234", "name": "黃俊傑", "department": "安平"},
    {"employee_no": "E013", "password": "1234", "name": "林柏宏", "department": "南高"},
    {"employee_no": "E014", "password": "1234", "name": "鄭雅文", "department": "南高"},
    {"employee_no": "E015", "password": "1234", "name": "蔡明哲", "department": "北高"},
    {"employee_no": "E016", "password": "1234", "name": "周柏宇", "department": "北高"},
    {"employee_no": "E017", "password": "1234", "name": "許家豪", "department": "專案部"},
    {"employee_no": "E018", "password": "1234", "name": "方志遠", "department": "專案部"},
    {"employee_no": "E019", "password": "1234", "name": "高偉倫", "department": "維修部"},
    {"employee_no": "E020", "password": "1234", "name": "沈志強", "department": "維修部"},
    {"employee_no": "E021", "password": "1234", "name": "葉冠廷", "department": "工程部"},
    {"employee_no": "E022", "password": "1234", "name": "何明軒", "department": "工程部"},
]


def normalize_login_text(value: str) -> str:
    return (value or "").strip()


def find_engineer(employee_no: str):
    target = normalize_login_text(employee_no).upper()
    for engineer in ENGINEERS:
        if engineer["employee_no"].upper() == target:
            return engineer
    return None


@router.post("/login")
def login(payload: LoginRequest):
    username = normalize_login_text(payload.username)
    password = normalize_login_text(payload.password)

    if username.lower() == "admin" and password == "1234":
        return {
            "token": "admin-token",
            "role": "admin",
            "username": "admin",
            "display_name": "系統管理員",
            "department": "管理部",
        }

    engineer = find_engineer(username)

    if not engineer or engineer["password"] != password:
        raise HTTPException(status_code=401, detail="工號或密碼錯誤")

    return {
        "token": "engineer-token-" + engineer["employee_no"],
        "role": "engineer",
        "username": engineer["employee_no"],
        "employee_no": engineer["employee_no"],
        "display_name": engineer["name"],
        "department": engineer["department"],
    }


@router.get("/engineers")
def list_engineers():
    return [
        {
            "employee_no": engineer["employee_no"],
            "name": engineer["name"],
            "department": engineer["department"],
        }
        for engineer in ENGINEERS
    ]
