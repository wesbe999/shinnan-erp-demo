from pathlib import Path
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/api/communities", tags=["社區資料"])

DATA_DIR = Path("data")
COMMUNITY_FILE = DATA_DIR / "communities.json"


class CommunityPayload(BaseModel):
    name: str
    area: str
    address: str
    ip: str


DEFAULT_COMMUNITIES = [
  {
    "id": 1,
    "name": "A大樓",
    "area": "東區",
    "address": "台南市東區測試路1號",
    "ip": "192.168.10.10"
  },
  {
    "id": 2,
    "name": "B大樓",
    "area": "北區",
    "address": "台南市北區測試路2號",
    "ip": "192.168.10.11"
  },
  {
    "id": 3,
    "name": "C大樓",
    "area": "北台南",
    "address": "台南市北台南測試路3號",
    "ip": "192.168.10.12"
  },
  {
    "id": 4,
    "name": "D大樓",
    "area": "仁德",
    "address": "台南市仁德測試路4號",
    "ip": "192.168.10.13"
  },
  {
    "id": 5,
    "name": "E大樓",
    "area": "永康",
    "address": "台南市永康測試路5號",
    "ip": "192.168.10.14"
  },
  {
    "id": 6,
    "name": "F大樓",
    "area": "安平",
    "address": "台南市安平測試路6號",
    "ip": "192.168.10.15"
  },
  {
    "id": 7,
    "name": "G大樓",
    "area": "南高",
    "address": "台南市南高測試路7號",
    "ip": "192.168.10.16"
  },
  {
    "id": 8,
    "name": "H大樓",
    "area": "北高",
    "address": "台南市北高測試路8號",
    "ip": "192.168.10.17"
  },
  {
    "id": 9,
    "name": "I大樓",
    "area": "東區",
    "address": "台南市東區測試路9號",
    "ip": "192.168.10.18"
  },
  {
    "id": 10,
    "name": "J大樓",
    "area": "北區",
    "address": "台南市北區測試路10號",
    "ip": "192.168.10.19"
  },
  {
    "id": 11,
    "name": "K大樓",
    "area": "北台南",
    "address": "台南市北台南測試路11號",
    "ip": "192.168.10.20"
  },
  {
    "id": 12,
    "name": "L大樓",
    "area": "仁德",
    "address": "台南市仁德測試路12號",
    "ip": "192.168.10.21"
  },
  {
    "id": 13,
    "name": "M大樓",
    "area": "永康",
    "address": "台南市永康測試路13號",
    "ip": "192.168.10.22"
  },
  {
    "id": 14,
    "name": "N大樓",
    "area": "安平",
    "address": "台南市安平測試路14號",
    "ip": "192.168.10.23"
  },
  {
    "id": 15,
    "name": "O大樓",
    "area": "南高",
    "address": "台南市南高測試路15號",
    "ip": "192.168.10.24"
  },
  {
    "id": 16,
    "name": "P大樓",
    "area": "北高",
    "address": "台南市北高測試路16號",
    "ip": "192.168.10.25"
  },
  {
    "id": 17,
    "name": "Q大樓",
    "area": "東區",
    "address": "台南市東區測試路17號",
    "ip": "192.168.10.26"
  },
  {
    "id": 18,
    "name": "R大樓",
    "area": "北區",
    "address": "台南市北區測試路18號",
    "ip": "192.168.10.27"
  },
  {
    "id": 19,
    "name": "S大樓",
    "area": "北台南",
    "address": "台南市北台南測試路19號",
    "ip": "192.168.10.28"
  },
  {
    "id": 20,
    "name": "T大樓",
    "area": "仁德",
    "address": "台南市仁德測試路20號",
    "ip": "192.168.10.29"
  },
  {
    "id": 21,
    "name": "U大樓",
    "area": "永康",
    "address": "台南市永康測試路21號",
    "ip": "192.168.10.30"
  },
  {
    "id": 22,
    "name": "V大樓",
    "area": "安平",
    "address": "台南市安平測試路22號",
    "ip": "192.168.10.31"
  },
  {
    "id": 23,
    "name": "W大樓",
    "area": "南高",
    "address": "台南市南高測試路23號",
    "ip": "192.168.10.32"
  },
  {
    "id": 24,
    "name": "X大樓",
    "area": "北高",
    "address": "台南市北高測試路24號",
    "ip": "192.168.10.33"
  },
  {
    "id": 25,
    "name": "Y大樓",
    "area": "東區",
    "address": "台南市東區測試路25號",
    "ip": "192.168.10.34"
  },
  {
    "id": 26,
    "name": "Z大樓",
    "area": "北區",
    "address": "台南市北區測試路26號",
    "ip": "192.168.10.35"
  }
]


def ensure_data():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not COMMUNITY_FILE.exists():
        import json
        COMMUNITY_FILE.write_text(
            json.dumps(DEFAULT_COMMUNITIES, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_communities():
    ensure_data()
    import json
    return json.loads(COMMUNITY_FILE.read_text(encoding="utf-8"))


def save_communities(data):
    ensure_data()
    import json
    COMMUNITY_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


@router.get("", summary="查詢社區資料")
def list_communities(area: str | None = None):
    data = load_communities()

    if area and area != "全部":
        data = [item for item in data if item.get("area") == area]

    return data


@router.post("", summary="新增社區資料")
def create_community(payload: CommunityPayload):
    data = load_communities()
    next_id = max([item.get("id", 0) for item in data] or [0]) + 1

    item = {
        "id": next_id,
        "name": payload.name,
        "area": payload.area,
        "address": payload.address,
        "ip": payload.ip,
    }

    data.append(item)
    save_communities(data)

    return item


@router.patch("/{community_id}", summary="修改社區資料")
def update_community(community_id: int, payload: CommunityPayload):
    data = load_communities()

    for item in data:
        if item.get("id") == community_id:
            item["name"] = payload.name
            item["area"] = payload.area
            item["address"] = payload.address
            item["ip"] = payload.ip
            save_communities(data)
            return item

    return {"error": "找不到社區資料"}


@router.delete("/{community_id}", summary="刪除社區資料")
def delete_community(community_id: int):
    data = load_communities()
    new_data = [item for item in data if item.get("id") != community_id]
    save_communities(new_data)

    return {
        "status": "ok",
        "deleted_id": community_id,
    }
