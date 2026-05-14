from __future__ import annotations

from datetime import date, timedelta
from typing import Any


AREAS: list[str] = [
    "東區",
    "北區",
    "北台南",
    "仁德",
    "永康",
    "安平",
    "高雄",
    "透天",
]


BUILDING_NAMES_BY_AREA: dict[str, list[str]] = {
    "東區": ["維冠大樓", "東方明珠", "文化首府", "長榮花園", "府城天廈", "崇明雅築", "南紡新都心", "東寧華廈", "青年名門", "德光苑"],
    "北區": ["成大城", "北辰大樓", "開元華廈", "成功國宅", "和緯名邸", "文賢雅苑", "公園首席", "北門新城", "小北世家", "立人花園"],
    "北台南": ["海安名邸", "和順天廈", "安中華城", "府安麗景", "國安首席", "安南新境", "北安御品", "長溪花園", "怡安雅築", "本原世家"],
    "仁德": ["仁德帝堡", "中正名門", "德南華廈", "嘉藥首府", "太子雲端", "仁義新城", "文賢大樓", "保安雅苑", "仁德首席", "德崙花園"],
    "永康": ["永康首府", "中華世家", "復國名邸", "大橋新都", "崑山華廈", "鹽行天廈", "龍埔御品", "永大花園", "勝利雅築", "正強大樓"],
    "安平": ["府城海悅", "安平首席", "水岸天廈", "永華麗景", "健康新城", "慶平名邸", "湖美華廈", "文平雅苑", "國平世家", "海景花園"],
    "高雄": ["鳳山首府", "五甲名邸", "前鎮華廈", "瑞隆新城", "草衙世家", "小港天廈", "桂林雅築", "鳳新御品", "左營首府", "巨蛋名邸", "博愛華廈", "明誠天廈", "自由世家", "河堤雅苑", "鼎山花園", "高鐵新城", "高雄花園", "文自大樓"],
    "透天": ["府城透天", "東門透天", "文化透天", "長榮透天", "安南透天", "仁德透天", "永康透天", "安平透天", "高雄透天"],
}


CUSTOMER_NAME_PREFIXES: list[str] = [
    "王大明",
    "林雅婷",
    "陳志豪",
    "黃淑芬",
    "李俊宏",
    "張美玲",
    "吳建國",
    "蔡佩君",
    "劉冠宇",
    "鄭怡君",
]


MANAGEMENT_COMPANIES: list[str] = [
    "安信管理",
    "宏達物業",
    "永盛管理",
    "大台南物業",
    "南都管理",
]


def _pad(value: int, width: int) -> str:
    return str(value).zfill(width)


def _building_unit(index: int) -> str:
    letters = ["A", "B", "C", "D", "E", "F"]
    letter = letters[index % len(letters)]
    floor = (index % 18) + 1
    room = (index % 8) + 1
    return f"{letter}棟{floor}F-{room}"



MANAGER_NAMES: list[str] = [
    "陳志明", "林美玉", "王建國", "黃俊傑", "李承翰",
    "蔡明哲", "鄭雅文", "周柏宇", "許家豪", "高偉倫",
    "沈志強", "葉冠廷", "何明軒", "吳宗憲", "羅啟彰",
    "林華山", "劉德華", "郭富城", "張學友", "黎明",
    "陳柏宇", "林志豪", "王雅婷", "黃國昌", "李佳蓉",
    "蔡宗翰", "鄭惠如", "周俊宏", "許美玲", "高志偉",
    "沈佳穎", "葉建宏", "何淑芬", "吳明哲", "羅家豪",
    "林佩君", "劉冠廷", "郭雅雯", "張志成", "黎淑華",
    "陳冠宇", "林怡君", "王俊傑", "黃雅惠", "李柏翰",
    "蔡宜蓁", "鄭志明", "周雅萍", "許宗憲", "高佩玲",
    "沈建志", "葉佳玲", "何宗霖", "吳雅琪", "羅明宏",
    "林家妤", "劉志偉", "郭淑貞", "張冠霖", "黎佳宏",
    "陳怡如", "林宗翰", "王佩珊", "黃建銘", "李雅雯",
    "蔡柏宏", "鄭佳蓉", "周明哲", "許雅婷", "高俊傑",
    "沈美惠", "葉志豪", "何雅玲", "吳冠廷", "羅惠君",
    "林柏宇", "劉雅惠", "郭志明", "張美玲", "黎冠宇",
    "陳家豪", "林淑芬", "王志強", "黃怡君", "李明宗",
    "蔡雅琪", "鄭柏翰", "周佳穎", "許建國", "高雅雯",
]

MANAGER_INTERESTS: list[str] = [
    "茶葉、登山", "釣魚、棒球", "咖啡、重機", "園藝、書法", "慢跑、旅遊",
    "攝影、露營", "高爾夫、股票", "廟會、地方事務", "美食、唱歌", "自行車、健走",
]

STREET_ADDRESSES_BY_AREA: dict[str, list[str]] = {
    "東區": [
        "台南市東區崇學路120號", "台南市東區東門路二段168號", "台南市東區裕農路356號",
        "台南市東區長榮路一段88號", "台南市東區文化路36號", "台南市東區德光街92號",
        "台南市東區中華東路二段197號", "台南市東區東寧路456號", "台南市東區青年路320號",
        "台南市東區崇明路512號",
    ],
    "北區": [
        "台南市北區公園路15號", "台南市北區成功路238號", "台南市北區開元路268號",
        "台南市北區西門路四段88號", "台南市北區和緯路二段160號", "台南市北區文賢路520號",
        "台南市北區公園南路71號", "台南市北區北門路二段112號", "台南市北區小北路45號",
        "台南市北區立人路70號",
    ],
    "北台南": [
        "台南市安南區海安路三段188號", "台南市安南區安和路一段188號", "台南市安南區安中路一段260號",
        "台南市安南區府安路五段58號", "台南市安南區國安街210號", "台南市安南區安中路二段109號",
        "台南市安南區北安路三段76號", "台南市安南區長溪路二段310號", "台南市安南區怡安路二段88號",
        "台南市安南區本原街一段180號",
    ],
    "仁德": [
        "台南市仁德區中正路二段780號", "台南市仁德區中正路三段120號", "台南市仁德區德南路58號",
        "台南市仁德區保安路一段88號", "台南市仁德區太子路280號", "台南市仁德區仁義路221號",
        "台南市仁德區文賢路一段320號", "台南市仁德區保安路二段156號", "台南市仁德區仁德路92號",
        "台南市仁德區德崙路168號",
    ],
    "永康": [
        "台南市永康區中華路198號", "台南市永康區中華二路260號", "台南市永康區復國一路260號",
        "台南市永康區大橋一街45號", "台南市永康區崑大路155號", "台南市永康區鹽行路88號",
        "台南市永康區龍埔街166號", "台南市永康區永大路二段350號", "台南市永康區勝利街66號",
        "台南市永康區正強街180號",
    ],
    "安平": [
        "台南市安平區永華路二段300號", "台南市安平區健康三街160號", "台南市安平區慶平路520號",
        "台南市安平區建平路99號", "台南市安平區國平路210號", "台南市安平區文平路366號",
        "台南市安平區湖美街80號", "台南市安平區平通路128號", "台南市安平區育平路176號",
        "台南市安平區世平路66號",
    ],
    "高雄": [
        "高雄市鳳山區中山路160號", "高雄市鳳山區五甲二路320號", "高雄市前鎮區瑞隆路430號",
        "高雄市前鎮區草衙二路210號", "高雄市小港區漢民路288號", "高雄市小港區桂林路76號",
        "高雄市鳳山區鳳新路156號", "高雄市鳳山區南正二路88號", "高雄市岡山區岡山路260號",
        "高雄市路竹區中山路720號",
        "高雄市左營區自由二路150號", "高雄市左營區博愛二路777號", "高雄市鼓山區明誠三路88號",
        "高雄市左營區文自路320號", "高雄市楠梓區德民路228號", "高雄市三民區鼎山街360號",
        "高雄市左營區高鐵路105號", "高雄市鼓山區河西一路130號", "高雄市楠梓區藍昌路288號",
        "高雄市三民區明仁路66號",
    ],
    "透天": [
        "台南市東區東門路一段25號", "台南市中西區民生路二段90號", "台南市北區公園路360號",
        "台南市安南區安中路三段88號", "台南市仁德區中山路208號", "台南市永康區中正路188號",
        "台南市安平區平豐路66號", "高雄市鳳山區光遠路220號", "高雄市左營區文川路80號",
        "高雄市楠梓區後昌路150號",
    ],
}


def _management_phone(index: int) -> str:
    return "06-" + str(2200000 + index * 137)


def _manager_phone(index: int) -> str:
    return "09" + str(12000000 + index * 32719)[:8]


def _host_name(index: int) -> str:
    return "主機-" + str(index + 1).zfill(3)


def generate_buildings() -> list[dict[str, Any]]:
    buildings: list[dict[str, Any]] = []
    serial = 1

    for area_index, area in enumerate(AREAS):
        for local_index, name in enumerate(BUILDING_NAMES_BY_AREA[area], start=1):
            buildings.append({
                "building_no": f"B{serial:03d}",
                "name": name,
                "area": area,
                "address": _building_unit(serial - 1),
                "display_address": f"{name} {_building_unit(serial - 1)}",
                "management_company": MANAGEMENT_COMPANIES[(serial - 1) % len(MANAGEMENT_COMPANIES)],
                "active_users": 80 + ((serial * 7) % 120),
                "total_households": 120 + ((serial * 11) % 180),
                "ip": f"192.168.{10 + area_index}.{10 + local_index - 1}",
            })
            serial += 1

    return buildings


def generate_customers() -> list[dict[str, Any]]:
    buildings = generate_buildings()
    customers: list[dict[str, Any]] = []

    for index in range(1, 101):
        building = buildings[(index - 1) % len(buildings)]
        unit = _building_unit(index + 2)

        customers.append({
            "customer_no": f"C{index:05d}",
            "customer_name": CUSTOMER_NAME_PREFIXES[(index - 1) % len(CUSTOMER_NAME_PREFIXES)],
            "phone": "09" + _pad(60000000 + index * 731, 8),
            "area": building["area"],
            "building_no": building["building_no"],
            "building_name": building["name"],
            "building_address": building["address"],
            "install_address": f"{building['name']} {unit}",
            "management_company": building["management_company"],
        })

    return customers


def generate_billing_records() -> list[dict[str, Any]]:
    customers = generate_customers()
    today = date.today()
    records: list[dict[str, Any]] = []

    for index, customer in enumerate(customers, start=1):
        overdue_days = 25 + (index % 18) if index % 6 == 0 else index % 5
        due_date = today - timedelta(days=overdue_days)

        monthly_fee = 1200 + ((index % 5) * 300)
        change_fee = 500 if index % 7 == 0 else 0
        material_fee = 800 if index % 9 == 0 else 0
        total_amount = monthly_fee + change_fee + material_fee

        is_abnormal = overdue_days > 20

        records.append({
            "billing_no": f"R{115000000 + index}",
            "confirm_no": f"CN{114080000 + index}",
            "customer_no": customer["customer_no"],
            "customer_name": customer["customer_name"],
            "phone": customer["phone"],
            "area": customer["area"],
            "building_no": customer["building_no"],
            "building_name": customer["building_name"],
            "install_address": customer["install_address"],
            "year_month": "115" + _pad(((index - 1) % 12) + 1, 2),
            "install_time": (today - timedelta(days=60 + index)).isoformat(),
            "due_date": due_date.isoformat(),
            "overdue_days": overdue_days,
            "monthly_fee": monthly_fee,
            "change_fee": change_fee,
            "material_fee": material_fee,
            "total_amount": total_amount,
            "invoice_type": "收銀機發票" if index % 4 == 0 else "已手開",
            "invoice_no": f"PV{11100000 + index}",
            "payment_status": "繳費異常" if is_abnormal else "繳費正常",
            "notice_label": "異常" if is_abnormal else "正常",
        })

    return records


def generate_dispatch_tickets() -> list[dict[str, Any]]:
    customers = generate_customers()
    case_types = ["裝機", "維修", "退機"]
    engineers = ["E001", "E002", "E003", "E004", "E005"]

    tickets: list[dict[str, Any]] = []

    for index, customer in enumerate(customers[:80], start=1):
        case_type = case_types[(index - 1) % len(case_types)]
        assigned = index % 4 != 0

        tickets.append({
            "ticket_no": f"T{index:05d}",
            "case_type": case_type,
            "customer_no": customer["customer_no"],
            "customer_name": customer["customer_name"],
            "phone": customer["phone"],
            "area": customer["area"],
            "building_no": customer["building_no"],
            "building_name": customer["building_name"],
            "install_address": customer["install_address"],
            "assigned_engineer_no": engineers[(index - 1) % len(engineers)] if assigned else "",
            "dispatch_status": "已派工" if assigned else "未派工",
            "work_status": "已完工" if index % 5 == 0 else "未完工",
        })

    return tickets


def generate_all_demo_data() -> dict[str, Any]:
    return {
        "areas": AREAS,
        "buildings": generate_buildings(),
        "customers": generate_customers(),
        "billing_records": generate_billing_records(),
        "dispatch_tickets": generate_dispatch_tickets(),
    }


# SHINNAN_BUILDING_MASTER_WRAPPER_START
# 大樓主資料補強層：
# 保留原本 generate_buildings() 產生的 90 筆大樓，再補上業務、管理室、總幹事與會議欄位。
_SHINNAN_BASE_GENERATE_BUILDINGS = generate_buildings

_SHINNAN_MANAGER_NAMES = [
    "陳志明", "林美玉", "王建國", "黃俊傑", "李承翰",
    "蔡明哲", "鄭雅文", "周柏宇", "許家豪", "高偉倫",
    "沈志強", "葉冠廷", "何明軒", "吳宗憲", "羅啟彰",
    "林華山", "劉德華", "郭富城", "張學友", "黎明",
    "陳柏宇", "林志豪", "王雅婷", "黃國昌", "李佳蓉",
    "蔡宗翰", "鄭惠如", "周俊宏", "許美玲", "高志偉",
    "沈佳穎", "葉建宏", "何淑芬", "吳明哲", "羅家豪",
    "林佩君", "劉冠廷", "郭雅雯", "張志成", "黎淑華",
    "陳冠宇", "林怡君", "王俊傑", "黃雅惠", "李柏翰",
    "蔡宜蓁", "鄭志明", "周雅萍", "許宗憲", "高佩玲",
    "沈建志", "葉佳玲", "何宗霖", "吳雅琪", "羅明宏",
    "林家妤", "劉志偉", "郭淑貞", "張冠霖", "黎佳宏",
    "陳怡如", "林宗翰", "王佩珊", "黃建銘", "李雅雯",
    "蔡柏宏", "鄭佳蓉", "周明哲", "許雅婷", "高俊傑",
    "沈美惠", "葉志豪", "何雅玲", "吳冠廷", "羅惠君",
    "林柏宇", "劉雅惠", "郭志明", "張美玲", "黎冠宇",
    "陳家豪", "林淑芬", "王志強", "黃怡君", "李明宗",
    "蔡雅琪", "鄭柏翰", "周佳穎", "許建國", "高雅雯",
]

_SHINNAN_MANAGER_INTERESTS = [
    "茶葉、登山", "釣魚、棒球", "咖啡、重機", "園藝、書法", "慢跑、旅遊",
    "攝影、露營", "高爾夫、股票", "廟會、地方事務", "美食、唱歌", "自行車、健走",
]

_SHINNAN_STREET_ADDRESSES_BY_AREA = {
    "東區": [
        "台南市東區崇學路120號", "台南市東區東門路二段168號", "台南市東區裕農路356號",
        "台南市東區長榮路一段88號", "台南市東區文化路36號", "台南市東區德光街92號",
        "台南市東區中華東路二段197號", "台南市東區東寧路456號", "台南市東區青年路320號",
        "台南市東區崇明路512號",
    ],
    "北區": [
        "台南市北區公園路15號", "台南市北區成功路238號", "台南市北區開元路268號",
        "台南市北區西門路四段88號", "台南市北區和緯路二段160號", "台南市北區文賢路520號",
        "台南市北區公園南路71號", "台南市北區北門路二段112號", "台南市北區小北路45號",
        "台南市北區立人路70號",
    ],
    "北台南": [
        "台南市安南區海安路三段188號", "台南市安南區安和路一段188號", "台南市安南區安中路一段260號",
        "台南市安南區府安路五段58號", "台南市安南區國安街210號", "台南市安南區安中路二段109號",
        "台南市安南區北安路三段76號", "台南市安南區長溪路二段310號", "台南市安南區怡安路二段88號",
        "台南市安南區本原街一段180號",
    ],
    "仁德": [
        "台南市仁德區中正路二段780號", "台南市仁德區中正路三段120號", "台南市仁德區德南路58號",
        "台南市仁德區保安路一段88號", "台南市仁德區太子路280號", "台南市仁德區仁義路221號",
        "台南市仁德區文賢路一段320號", "台南市仁德區保安路二段156號", "台南市仁德區仁德路92號",
        "台南市仁德區德崙路168號",
    ],
    "永康": [
        "台南市永康區中華路198號", "台南市永康區中華二路260號", "台南市永康區復國一路260號",
        "台南市永康區大橋一街45號", "台南市永康區崑大路155號", "台南市永康區鹽行路88號",
        "台南市永康區龍埔街166號", "台南市永康區永大路二段350號", "台南市永康區勝利街66號",
        "台南市永康區正強街180號",
    ],
    "安平": [
        "台南市安平區永華路二段300號", "台南市安平區健康三街160號", "台南市安平區慶平路520號",
        "台南市安平區建平路99號", "台南市安平區國平路210號", "台南市安平區文平路366號",
        "台南市安平區湖美街80號", "台南市安平區平通路128號", "台南市安平區育平路176號",
        "台南市安平區世平路66號",
    ],
    "高雄": [
        "高雄市鳳山區中山路160號", "高雄市鳳山區五甲二路320號", "高雄市前鎮區瑞隆路430號",
        "高雄市前鎮區草衙二路210號", "高雄市小港區漢民路288號", "高雄市小港區桂林路76號",
        "高雄市鳳山區鳳新路156號", "高雄市鳳山區南正二路88號", "高雄市岡山區岡山路260號",
        "高雄市路竹區中山路720號",
        "高雄市左營區自由二路150號", "高雄市左營區博愛二路777號", "高雄市鼓山區明誠三路88號",
        "高雄市左營區文自路320號", "高雄市楠梓區德民路228號", "高雄市三民區鼎山街360號",
        "高雄市左營區高鐵路105號", "高雄市鼓山區河西一路130號", "高雄市楠梓區藍昌路288號",
        "高雄市三民區明仁路66號",
    ],
    "透天": [
        "台南市東區東門路一段25號", "台南市中西區民生路二段90號", "台南市北區公園路360號",
        "台南市安南區安中路三段88號", "台南市仁德區中山路208號", "台南市永康區中正路188號",
        "台南市安平區平豐路66號", "高雄市鳳山區光遠路220號", "高雄市左營區文川路80號",
        "高雄市楠梓區後昌路150號",
    ],
}

_SHINNAN_FALLBACK_ADDRESSES = [
    "台南市北區公園路15號",
    "台南市東區崇學路120號",
    "台南市安平區永華路二段300號",
    "台南市永康區中華路198號",
]


def _shinnan_pick_address(area: str, index: int) -> str:
    streets = _SHINNAN_STREET_ADDRESSES_BY_AREA.get(area) or _SHINNAN_FALLBACK_ADDRESSES
    return streets[index % len(streets)]


def _shinnan_management_company(index: int) -> str:
    try:
        return MANAGEMENT_COMPANIES[index % len(MANAGEMENT_COMPANIES)]
    except Exception:
        companies = ["安信物業", "宏盛管理", "大台南物業", "南都管理", "永安管理"]
        return companies[index % len(companies)]


def generate_buildings() -> list[dict[str, Any]]:
    base_rows = _SHINNAN_BASE_GENERATE_BUILDINGS()
    enriched: list[dict[str, Any]] = []

    for index, original in enumerate(base_rows):
        item = dict(original)
        area = str(item.get("area") or "北區")
        address = _shinnan_pick_address(area, index)
        manager_name = _SHINNAN_MANAGER_NAMES[index % len(_SHINNAN_MANAGER_NAMES)]

        item["building_no"] = item.get("building_no") or item.get("no") or f"B{index + 1:03d}"
        item["name"] = item.get("name") or item.get("building_name") or f"測試大樓 {index + 1}"
        item["area"] = area
        item["address"] = address
        item["raw_address"] = address
        item["display_address"] = f"{item['name']}｜{address}"

        item["management_company"] = item.get("management_company") or _shinnan_management_company(index)
        item["management_phone"] = item.get("management_phone") or ("06-" + str(2200000 + index * 137))

        item["manager_name"] = item.get("manager_name") or manager_name
        item["manager_phone"] = item.get("manager_phone") or ("09" + str(12000000 + index * 32719)[:8])
        item["manager_age"] = item.get("manager_age") or (38 + (index % 24))
        item["manager_experience"] = item.get("manager_experience") or f"{3 + (index % 16)} 年"
        item["manager_interest"] = item.get("manager_interest") or _SHINNAN_MANAGER_INTERESTS[index % len(_SHINNAN_MANAGER_INTERESTS)]

        item["visit_time"] = item.get("visit_time") or ["平日 09:00-12:00", "平日 14:00-17:00", "需先電話預約"][index % 3]
        item["committee_time"] = item.get("committee_time") or f"每月第 {(index % 4) + 1} 週{['一', '二', '三', '四', '五'][index % 5]} 19:00"
        item["resident_meeting_time"] = item.get("resident_meeting_time") or f"每年 {(index % 12) + 1} 月"

        item["active_users"] = item.get("active_users") or item.get("user_count") or (80 + (((index + 1) * 7) % 120))
        item["total_households"] = item.get("total_households") or item.get("households") or (120 + (((index + 1) * 11) % 180))
        item["ip"] = item.get("ip") or f"192.168.{10 + (index // 10)}.{10 + (index % 10)}"
        item["host"] = item.get("host") or item.get("main_host") or f"主機-{index + 1:03d}"

        enriched.append(item)

    return enriched
# SHINNAN_BUILDING_MASTER_WRAPPER_END

