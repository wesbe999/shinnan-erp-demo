import hashlib as _employee_settings_hashlib
import secrets as _employee_settings_secrets
import json as _employee_settings_json
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from fastapi.responses import RedirectResponse as _EmployeeSettingsHTMLResponse, Response as _EmployeeSettingsResponse
from sqlalchemy import text as _employee_settings_sql_text
from app.db import engine as _employee_settings_engine

import json as _employee_settings_json
from fastapi.responses import HTMLResponse as _EmployeeSettingsHTMLResponse, Response as _EmployeeSettingsResponse
from sqlalchemy import text as _employee_settings_sql_text
from app.db import engine as _employee_settings_engine

import json as _dispatch_app_json
from fastapi.responses import HTMLResponse as _DispatchAppHTMLResponse, Response as _DispatchAppResponse
from sqlalchemy import text as _dispatch_app_sql_text
from app.db import engine as _dispatch_app_engine

import json as _employee_profile_json
from fastapi.responses import Response as _EmployeeProfileResponse
from sqlalchemy import text as _employee_profile_sql_text
from app.db import engine as _employee_profile_engine

import json as _ticket_link_json
from urllib.parse import parse_qs as _ticket_link_parse_qs
from fastapi import Request as _TicketLinkRequest
from fastapi.responses import Response as _TicketLinkResponse, HTMLResponse as _TicketLinkHTMLResponse
from sqlalchemy import text as _ticket_link_sql_text
from app.db import engine as _ticket_link_engine

import hashlib as _emp_hashlib
import secrets as _emp_secrets
from datetime import datetime as _emp_datetime, timedelta as _emp_timedelta
from urllib.parse import parse_qs as _emp_parse_qs, quote as _emp_quote
from fastapi import Request as _EmpRequest
from fastapi.responses import HTMLResponse as _EmpHTMLResponse, RedirectResponse as _EmpRedirectResponse, Response as _EmpResponse
from sqlalchemy import text as _emp_sql_text
from app.db import engine as _emp_engine

import json as _customers_json
from sqlalchemy import text as _customers_sql_text
from fastapi.responses import Response as _CustomersResponse
from app.db import engine as _customers_engine

import json as _managers_json
from sqlalchemy import text as _managers_sql_text
from fastapi.responses import Response as _ManagersResponse
from app.db import engine as _managers_engine

import json as _buildings_json
from sqlalchemy import text as _buildings_sql_text
from fastapi.responses import Response as _BuildingsResponse
from app.db import engine as _buildings_engine

import json as _sales_json
from datetime import datetime as _sales_datetime
from sqlalchemy import text as _sales_sql_text
from fastapi.responses import Response as _SalesResponse
from app.db import engine as _sales_engine

from fastapi import APIRouter, Request, Body
from app.engineer_directory import ENGINEER_DIRECTORY, engineer_names
import json as _json
from pathlib import Path as _Path
import subprocess
import platform
from datetime import datetime, date
from fastapi.responses import HTMLResponse, JSONResponse, Response
from app.services.demo_data import generate_buildings

from app.routes.employee_auth import _employee_current_user_from_request
router = APIRouter(tags=["中文後台頁面"])


# SHINNAN_ADMIN_PAGE_MOVED_TO_ADMIN_DISPATCH_START
# /admin route moved to app/routes/admin_dispatch.py
# SHINNAN_ADMIN_PAGE_MOVED_TO_ADMIN_DISPATCH_END




# XUNNAN_ADMIN_DIRECTORY_DATA_FIXED

BUILDING_STATUS_MEMORY = {}



BUILDING_DIRECTORY = [{'building_no': 'B001', 'name': '維冠大樓', 'area': '東區', 'address': '台南市東區測試路10號', 'management_company': '安信管理', 'active_users': 87, 'total_households': 131, 'ip': '192.168.10.10'}, {'building_no': 'B002', 'name': '東方明珠', 'area': '東區', 'address': '台南市東區測試路20號', 'management_company': '宏達物業', 'active_users': 94, 'total_households': 142, 'ip': '192.168.10.11'}, {'building_no': 'B003', 'name': '文化首府', 'area': '東區', 'address': '台南市東區測試路30號', 'management_company': '永盛管理', 'active_users': 101, 'total_households': 153, 'ip': '192.168.10.12'}, {'building_no': 'B004', 'name': '長榮花園', 'area': '東區', 'address': '台南市東區測試路40號', 'management_company': '大台南物業', 'active_users': 108, 'total_households': 164, 'ip': '192.168.10.13'}, {'building_no': 'B005', 'name': '府城天廈', 'area': '東區', 'address': '台南市東區測試路50號', 'management_company': '南都管理', 'active_users': 115, 'total_households': 175, 'ip': '192.168.10.14'}, {'building_no': 'B006', 'name': '崇明雅築', 'area': '東區', 'address': '台南市東區測試路60號', 'management_company': '安信管理', 'active_users': 122, 'total_households': 186, 'ip': '192.168.10.15'}, {'building_no': 'B007', 'name': '南紡新都心', 'area': '東區', 'address': '台南市東區測試路70號', 'management_company': '宏達物業', 'active_users': 129, 'total_households': 197, 'ip': '192.168.10.16'}, {'building_no': 'B008', 'name': '東寧華廈', 'area': '東區', 'address': '台南市東區測試路80號', 'management_company': '永盛管理', 'active_users': 136, 'total_households': 208, 'ip': '192.168.10.17'}, {'building_no': 'B009', 'name': '青年名門', 'area': '東區', 'address': '台南市東區測試路90號', 'management_company': '大台南物業', 'active_users': 143, 'total_households': 219, 'ip': '192.168.10.18'}, {'building_no': 'B010', 'name': '德光苑', 'area': '東區', 'address': '台南市東區測試路100號', 'management_company': '南都管理', 'active_users': 150, 'total_households': 230, 'ip': '192.168.10.19'}, {'building_no': 'B011', 'name': '成大城', 'area': '北區', 'address': '台南市北區測試路10號', 'management_company': '安信管理', 'active_users': 157, 'total_households': 241, 'ip': '192.168.11.10'}, {'building_no': 'B012', 'name': '北辰大樓', 'area': '北區', 'address': '台南市北區測試路20號', 'management_company': '宏達物業', 'active_users': 164, 'total_households': 252, 'ip': '192.168.11.11'}, {'building_no': 'B013', 'name': '開元華廈', 'area': '北區', 'address': '台南市北區測試路30號', 'management_company': '永盛管理', 'active_users': 171, 'total_households': 263, 'ip': '192.168.11.12'}, {'building_no': 'B014', 'name': '成功國宅', 'area': '北區', 'address': '台南市北區測試路40號', 'management_company': '大台南物業', 'active_users': 178, 'total_households': 274, 'ip': '192.168.11.13'}, {'building_no': 'B015', 'name': '和緯名邸', 'area': '北區', 'address': '台南市北區測試路50號', 'management_company': '南都管理', 'active_users': 185, 'total_households': 285, 'ip': '192.168.11.14'}, {'building_no': 'B016', 'name': '文賢雅苑', 'area': '北區', 'address': '台南市北區測試路60號', 'management_company': '安信管理', 'active_users': 192, 'total_households': 296, 'ip': '192.168.11.15'}, {'building_no': 'B017', 'name': '公園首席', 'area': '北區', 'address': '台南市北區測試路70號', 'management_company': '宏達物業', 'active_users': 199, 'total_households': 127, 'ip': '192.168.11.16'}, {'building_no': 'B018', 'name': '北門新城', 'area': '北區', 'address': '台南市北區測試路80號', 'management_company': '永盛管理', 'active_users': 86, 'total_households': 138, 'ip': '192.168.11.17'}, {'building_no': 'B019', 'name': '小北世家', 'area': '北區', 'address': '台南市北區測試路90號', 'management_company': '大台南物業', 'active_users': 93, 'total_households': 149, 'ip': '192.168.11.18'}, {'building_no': 'B020', 'name': '立人花園', 'area': '北區', 'address': '台南市北區測試路100號', 'management_company': '南都管理', 'active_users': 100, 'total_households': 160, 'ip': '192.168.11.19'}, {'building_no': 'B021', 'name': '海安名邸', 'area': '北台南', 'address': '台南市北台南測試路10號', 'management_company': '安信管理', 'active_users': 107, 'total_households': 171, 'ip': '192.168.12.10'}, {'building_no': 'B022', 'name': '和順天廈', 'area': '北台南', 'address': '台南市北台南測試路20號', 'management_company': '宏達物業', 'active_users': 114, 'total_households': 182, 'ip': '192.168.12.11'}, {'building_no': 'B023', 'name': '安中華城', 'area': '北台南', 'address': '台南市北台南測試路30號', 'management_company': '永盛管理', 'active_users': 121, 'total_households': 193, 'ip': '192.168.12.12'}, {'building_no': 'B024', 'name': '府安麗景', 'area': '北台南', 'address': '台南市北台南測試路40號', 'management_company': '大台南物業', 'active_users': 128, 'total_households': 204, 'ip': '192.168.12.13'}, {'building_no': 'B025', 'name': '國安首席', 'area': '北台南', 'address': '台南市北台南測試路50號', 'management_company': '南都管理', 'active_users': 135, 'total_households': 215, 'ip': '192.168.12.14'}, {'building_no': 'B026', 'name': '安南新境', 'area': '北台南', 'address': '台南市北台南測試路60號', 'management_company': '安信管理', 'active_users': 142, 'total_households': 226, 'ip': '192.168.12.15'}, {'building_no': 'B027', 'name': '北安御品', 'area': '北台南', 'address': '台南市北台南測試路70號', 'management_company': '宏達物業', 'active_users': 149, 'total_households': 237, 'ip': '192.168.12.16'}, {'building_no': 'B028', 'name': '長溪花園', 'area': '北台南', 'address': '台南市北台南測試路80號', 'management_company': '永盛管理', 'active_users': 156, 'total_households': 248, 'ip': '192.168.12.17'}, {'building_no': 'B029', 'name': '怡安雅築', 'area': '北台南', 'address': '台南市北台南測試路90號', 'management_company': '大台南物業', 'active_users': 163, 'total_households': 259, 'ip': '192.168.12.18'}, {'building_no': 'B030', 'name': '本原世家', 'area': '北台南', 'address': '台南市北台南測試路100號', 'management_company': '南都管理', 'active_users': 170, 'total_households': 270, 'ip': '192.168.12.19'}, {'building_no': 'B031', 'name': '仁德帝堡', 'area': '仁德', 'address': '台南市仁德測試路10號', 'management_company': '安信管理', 'active_users': 177, 'total_households': 281, 'ip': '192.168.13.10'}, {'building_no': 'B032', 'name': '中正名門', 'area': '仁德', 'address': '台南市仁德測試路20號', 'management_company': '宏達物業', 'active_users': 184, 'total_households': 292, 'ip': '192.168.13.11'}, {'building_no': 'B033', 'name': '德南華廈', 'area': '仁德', 'address': '台南市仁德測試路30號', 'management_company': '永盛管理', 'active_users': 191, 'total_households': 123, 'ip': '192.168.13.12'}, {'building_no': 'B034', 'name': '嘉藥首府', 'area': '仁德', 'address': '台南市仁德測試路40號', 'management_company': '大台南物業', 'active_users': 198, 'total_households': 134, 'ip': '192.168.13.13'}, {'building_no': 'B035', 'name': '太子雲端', 'area': '仁德', 'address': '台南市仁德測試路50號', 'management_company': '南都管理', 'active_users': 85, 'total_households': 145, 'ip': '192.168.13.14'}, {'building_no': 'B036', 'name': '仁義新城', 'area': '仁德', 'address': '台南市仁德測試路60號', 'management_company': '安信管理', 'active_users': 92, 'total_households': 156, 'ip': '192.168.13.15'}, {'building_no': 'B037', 'name': '文賢大樓', 'area': '仁德', 'address': '台南市仁德測試路70號', 'management_company': '宏達物業', 'active_users': 99, 'total_households': 167, 'ip': '192.168.13.16'}, {'building_no': 'B038', 'name': '保安雅苑', 'area': '仁德', 'address': '台南市仁德測試路80號', 'management_company': '永盛管理', 'active_users': 106, 'total_households': 178, 'ip': '192.168.13.17'}, {'building_no': 'B039', 'name': '仁德首席', 'area': '仁德', 'address': '台南市仁德測試路90號', 'management_company': '大台南物業', 'active_users': 113, 'total_households': 189, 'ip': '192.168.13.18'}, {'building_no': 'B040', 'name': '德崙花園', 'area': '仁德', 'address': '台南市仁德測試路100號', 'management_company': '南都管理', 'active_users': 120, 'total_households': 200, 'ip': '192.168.13.19'}, {'building_no': 'B041', 'name': '永康首府', 'area': '永康', 'address': '台南市永康測試路10號', 'management_company': '安信管理', 'active_users': 127, 'total_households': 211, 'ip': '192.168.14.10'}, {'building_no': 'B042', 'name': '中華世家', 'area': '永康', 'address': '台南市永康測試路20號', 'management_company': '宏達物業', 'active_users': 134, 'total_households': 222, 'ip': '192.168.14.11'}, {'building_no': 'B043', 'name': '復國名邸', 'area': '永康', 'address': '台南市永康測試路30號', 'management_company': '永盛管理', 'active_users': 141, 'total_households': 233, 'ip': '192.168.14.12'}, {'building_no': 'B044', 'name': '大橋新都', 'area': '永康', 'address': '台南市永康測試路40號', 'management_company': '大台南物業', 'active_users': 148, 'total_households': 244, 'ip': '192.168.14.13'}, {'building_no': 'B045', 'name': '崑山華廈', 'area': '永康', 'address': '台南市永康測試路50號', 'management_company': '南都管理', 'active_users': 155, 'total_households': 255, 'ip': '192.168.14.14'}, {'building_no': 'B046', 'name': '鹽行天廈', 'area': '永康', 'address': '台南市永康測試路60號', 'management_company': '安信管理', 'active_users': 162, 'total_households': 266, 'ip': '192.168.14.15'}, {'building_no': 'B047', 'name': '龍埔御品', 'area': '永康', 'address': '台南市永康測試路70號', 'management_company': '宏達物業', 'active_users': 169, 'total_households': 277, 'ip': '192.168.14.16'}, {'building_no': 'B048', 'name': '永大花園', 'area': '永康', 'address': '台南市永康測試路80號', 'management_company': '永盛管理', 'active_users': 176, 'total_households': 288, 'ip': '192.168.14.17'}, {'building_no': 'B049', 'name': '勝利雅築', 'area': '永康', 'address': '台南市永康測試路90號', 'management_company': '大台南物業', 'active_users': 183, 'total_households': 299, 'ip': '192.168.14.18'}, {'building_no': 'B050', 'name': '正強大樓', 'area': '永康', 'address': '台南市永康測試路100號', 'management_company': '南都管理', 'active_users': 190, 'total_households': 130, 'ip': '192.168.14.19'}, {'building_no': 'B051', 'name': '府城海悅', 'area': '安平', 'address': '台南市安平測試路10號', 'management_company': '安信管理', 'active_users': 197, 'total_households': 141, 'ip': '192.168.15.10'}, {'building_no': 'B052', 'name': '安平首席', 'area': '安平', 'address': '台南市安平測試路20號', 'management_company': '宏達物業', 'active_users': 84, 'total_households': 152, 'ip': '192.168.15.11'}, {'building_no': 'B053', 'name': '水岸天廈', 'area': '安平', 'address': '台南市安平測試路30號', 'management_company': '永盛管理', 'active_users': 91, 'total_households': 163, 'ip': '192.168.15.12'}, {'building_no': 'B054', 'name': '永華麗景', 'area': '安平', 'address': '台南市安平測試路40號', 'management_company': '大台南物業', 'active_users': 98, 'total_households': 174, 'ip': '192.168.15.13'}, {'building_no': 'B055', 'name': '健康新城', 'area': '安平', 'address': '台南市安平測試路50號', 'management_company': '南都管理', 'active_users': 105, 'total_households': 185, 'ip': '192.168.15.14'}, {'building_no': 'B056', 'name': '慶平名邸', 'area': '安平', 'address': '台南市安平測試路60號', 'management_company': '安信管理', 'active_users': 112, 'total_households': 196, 'ip': '192.168.15.15'}, {'building_no': 'B057', 'name': '湖美華廈', 'area': '安平', 'address': '台南市安平測試路70號', 'management_company': '宏達物業', 'active_users': 119, 'total_households': 207, 'ip': '192.168.15.16'}, {'building_no': 'B058', 'name': '文平雅苑', 'area': '安平', 'address': '台南市安平測試路80號', 'management_company': '永盛管理', 'active_users': 126, 'total_households': 218, 'ip': '192.168.15.17'}, {'building_no': 'B059', 'name': '國平世家', 'area': '安平', 'address': '台南市安平測試路90號', 'management_company': '大台南物業', 'active_users': 133, 'total_households': 229, 'ip': '192.168.15.18'}, {'building_no': 'B060', 'name': '海景花園', 'area': '安平', 'address': '台南市安平測試路100號', 'management_company': '南都管理', 'active_users': 140, 'total_households': 240, 'ip': '192.168.15.19'}, {'building_no': 'B061', 'name': '鳳山首府', 'area': '南高', 'address': '台南市南高測試路10號', 'management_company': '安信管理', 'active_users': 147, 'total_households': 251, 'ip': '192.168.16.10'}, {'building_no': 'B062', 'name': '五甲名邸', 'area': '南高', 'address': '台南市南高測試路20號', 'management_company': '宏達物業', 'active_users': 154, 'total_households': 262, 'ip': '192.168.16.11'}, {'building_no': 'B063', 'name': '前鎮華廈', 'area': '南高', 'address': '台南市南高測試路30號', 'management_company': '永盛管理', 'active_users': 161, 'total_households': 273, 'ip': '192.168.16.12'}, {'building_no': 'B064', 'name': '瑞隆新城', 'area': '南高', 'address': '台南市南高測試路40號', 'management_company': '大台南物業', 'active_users': 168, 'total_households': 284, 'ip': '192.168.16.13'}, {'building_no': 'B065', 'name': '草衙世家', 'area': '南高', 'address': '台南市南高測試路50號', 'management_company': '南都管理', 'active_users': 175, 'total_households': 295, 'ip': '192.168.16.14'}, {'building_no': 'B066', 'name': '小港天廈', 'area': '南高', 'address': '台南市南高測試路60號', 'management_company': '安信管理', 'active_users': 182, 'total_households': 126, 'ip': '192.168.16.15'}, {'building_no': 'B067', 'name': '桂林雅築', 'area': '南高', 'address': '台南市南高測試路70號', 'management_company': '宏達物業', 'active_users': 189, 'total_households': 137, 'ip': '192.168.16.16'}, {'building_no': 'B068', 'name': '鳳新御品', 'area': '南高', 'address': '台南市南高測試路80號', 'management_company': '永盛管理', 'active_users': 196, 'total_households': 148, 'ip': '192.168.16.17'}, {'building_no': 'B069', 'name': '南高花園', 'area': '南高', 'address': '台南市南高測試路90號', 'management_company': '大台南物業', 'active_users': 83, 'total_households': 159, 'ip': '192.168.16.18'}, {'building_no': 'B070', 'name': '鳳凰大樓', 'area': '南高', 'address': '台南市南高測試路100號', 'management_company': '南都管理', 'active_users': 90, 'total_households': 170, 'ip': '192.168.16.19'}, {'building_no': 'B071', 'name': '左營首府', 'area': '北高', 'address': '台南市北高測試路10號', 'management_company': '安信管理', 'active_users': 97, 'total_households': 181, 'ip': '192.168.17.10'}, {'building_no': 'B072', 'name': '巨蛋名邸', 'area': '北高', 'address': '台南市北高測試路20號', 'management_company': '宏達物業', 'active_users': 104, 'total_households': 192, 'ip': '192.168.17.11'}, {'building_no': 'B073', 'name': '博愛華廈', 'area': '北高', 'address': '台南市北高測試路30號', 'management_company': '永盛管理', 'active_users': 111, 'total_households': 203, 'ip': '192.168.17.12'}, {'building_no': 'B074', 'name': '明誠天廈', 'area': '北高', 'address': '台南市北高測試路40號', 'management_company': '大台南物業', 'active_users': 118, 'total_households': 214, 'ip': '192.168.17.13'}, {'building_no': 'B075', 'name': '自由世家', 'area': '北高', 'address': '台南市北高測試路50號', 'management_company': '南都管理', 'active_users': 125, 'total_households': 225, 'ip': '192.168.17.14'}, {'building_no': 'B076', 'name': '河堤雅苑', 'area': '北高', 'address': '台南市北高測試路60號', 'management_company': '安信管理', 'active_users': 132, 'total_households': 236, 'ip': '192.168.17.15'}, {'building_no': 'B077', 'name': '鼎山花園', 'area': '北高', 'address': '台南市北高測試路70號', 'management_company': '宏達物業', 'active_users': 139, 'total_households': 247, 'ip': '192.168.17.16'}, {'building_no': 'B078', 'name': '高鐵新城', 'area': '北高', 'address': '台南市北高測試路80號', 'management_company': '永盛管理', 'active_users': 146, 'total_households': 258, 'ip': '192.168.17.17'}, {'building_no': 'B079', 'name': '北高御品', 'area': '北高', 'address': '台南市北高測試路90號', 'management_company': '大台南物業', 'active_users': 153, 'total_households': 269, 'ip': '192.168.17.18'}, {'building_no': 'B080', 'name': '文自大樓', 'area': '北高', 'address': '台南市北高測試路100號', 'management_company': '南都管理', 'active_users': 160, 'total_households': 280, 'ip': '192.168.17.19'}]

# XUNNAN_ADMIN_DIRECTORY_ROUTES_FIXED


# Route disabled: /api/admin/engineers is owned by app.routes.admin_dispatch.
def api_admin_engineers():
    safe_engineers = []

    for engineer in ENGINEER_DIRECTORY:
        safe_engineers.append({
            "employee_no": str(engineer.get("employee_no", "")),
            "name": str(engineer.get("name", "")),
            "department": str(engineer.get("department", "")),
        })

    return safe_engineers


# SHINNAN_BUILDINGS_DB_API_HELPER_START
def _buildings_db_init():
    with _buildings_engine.begin() as conn:
        conn.execute(_buildings_sql_text("""
            CREATE TABLE IF NOT EXISTS buildings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_no TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                area TEXT DEFAULT '',
                address TEXT DEFAULT '',
                raw_address TEXT DEFAULT '',
                display_address TEXT DEFAULT '',
                management_company TEXT DEFAULT '',
                management_phone TEXT DEFAULT '',
                manager_name TEXT DEFAULT '',
                manager_phone TEXT DEFAULT '',
                manager_age TEXT DEFAULT '',
                manager_experience TEXT DEFAULT '',
                manager_interest TEXT DEFAULT '',
                visit_time TEXT DEFAULT '',
                committee_time TEXT DEFAULT '',
                resident_meeting_time TEXT DEFAULT '',
                active_users INTEGER DEFAULT 0,
                total_households INTEGER DEFAULT 0,
                ip TEXT DEFAULT '',
                host TEXT DEFAULT '',
                note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))


def _fetch_buildings_from_db():
    _buildings_db_init()

    with _buildings_engine.begin() as conn:
        rows = conn.execute(_buildings_sql_text("""
            SELECT
                building_no,
                name,
                area,
                address,
                raw_address,
                display_address,
                management_company,
                management_phone,
                manager_name,
                manager_phone,
                manager_age,
                manager_experience,
                manager_interest,
                visit_time,
                committee_time,
                resident_meeting_time,
                active_users,
                total_households,
                ip,
                host,
                note
            FROM buildings
            ORDER BY building_no ASC
        """)).mappings().fetchall()

    return [dict(row) for row in rows]
# SHINNAN_BUILDINGS_DB_API_HELPER_END


@router.get("/api/admin/buildings")
def api_admin_buildings():
    buildings = _fetch_buildings_from_db()

    return _BuildingsResponse(
        content=_buildings_json.dumps(buildings, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.get("/api/admin/buildings/status")
def api_admin_building_status():
    offline_building_nos = {"B001", "B014"}
    warning_building_nos = {"B027"}
    items = []

    for building in _fetch_buildings_from_db():
        building_no = building.get("building_no")
        online = building_no not in offline_building_nos
        disconnect_count = 2 if building_no in warning_building_nos else (1 if not online else 0)

        items.append({
            "building_no": building_no,
            "name": building.get("name"),
            "area": building.get("area"),
            "ip": building.get("ip"),
            "online": online,
            "disconnect_count": disconnect_count,
            "status": "離線" if not online else ("異常" if disconnect_count >= 2 else "正常"),
        })

    return JSONResponse(items)


@router.get("/admin/buildings", response_class=HTMLResponse)
def admin_buildings_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>訊南ERP｜大樓名錄</title>
  <style>
    :root {
      --bg: #eef3f9;
      --card: #ffffff;
      --line: #d7e1ef;
      --text: #102348;
      --muted: #64748b;
      --blue: #365ee8;
      --purple: #7c3aed;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Microsoft JhengHei", "Segoe UI", Arial, sans-serif;
    }

    .topbar {
      background: linear-gradient(120deg, #0f766e, #2563eb, #7c3aed);
      color: white;
      padding: 28px 34px;
    }

    .topbar h1 {
      margin: 0;
      font-size: 42px;
      font-weight: 1000;
      letter-spacing: 2px;
    }

    .topbar p {
      margin: 14px 0 0;
      font-size: 20px;
      font-weight: 900;
      opacity: .95;
    }

    .page {
      width: min(1680px, calc(100% - 36px));
      margin: 24px auto 42px;
    }

    .toolbar {
      display: grid;
      grid-template-columns: 150px 150px 220px minmax(420px, 1fr);
      gap: 14px;
      align-items: center;
      margin-bottom: 22px;
    }

    button, select, input {
      font-family: inherit;
      font-size: 18px;
    }

    button {
      border: 0;
      border-radius: 14px;
      padding: 13px 18px;
      color: white;
      font-weight: 1000;
      cursor: pointer;
      background: var(--blue);
    }

    input, select {
      width: 100%;
      height: 52px;
      border: 1px solid #cbd5e1;
      border-radius: 14px;
      padding: 0 16px;
      background: white;
      color: var(--text);
      outline: none;
    }

    .card {
      background: white;
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    }

    .hint {
      color: var(--muted);
      font-size: 14px;
      font-weight: 900;
      margin-bottom: 14px;
    }

    table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0 12px;
    }

    th {
      text-align: left;
      padding: 12px 14px;
      color: #475569;
      font-size: 16px;
      font-weight: 1000;
      white-space: nowrap;
    }

    td {
      background: white;
      border-top: 1px solid var(--line);
      border-bottom: 1px solid var(--line);
      padding: 14px;
      font-size: 17px;
      font-weight: 900;
      vertical-align: middle;
    }

    td:first-child {
      border-left: 1px solid var(--line);
      border-radius: 14px 0 0 14px;
    }

    td:last-child {
      border-right: 1px solid var(--line);
      border-radius: 0 14px 14px 0;
    }

    td[contenteditable="true"] {
      background: #fffdf4;
      cursor: text;
      outline: none;
    }

    td[contenteditable="true"]:focus {
      background: #fff7d6;
      box-shadow: inset 0 0 0 2px #f59e0b;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      border-radius: 999px;
      padding: 7px 14px;
      background: #ede9fe;
      color: #5b21b6;
      font-weight: 1000;
    }

    .btn-small {
      min-width: 100px;
      height: 42px;
      padding: 8px 14px;
      border-radius: 12px;
      font-size: 16px;
    }

    @media (max-width: 900px) {
      .toolbar { grid-template-columns: 1fr; }
      table { min-width: 1100px; }
      .card { overflow-x: auto; }
    }
      /* SHINNAN_BUILDING_AREA_PILL_HORIZONTAL_START */
    .pill {
      display: inline-flex !important;
      flex-direction: row !important;
      align-items: center !important;
      justify-content: center !important;
      min-width: 101px !important;
      height: 42px !important;
      padding: 0 18px !important;
      border-radius: 999px !important;
      background: #ede9fe !important;
      color: #5b21b6 !important;
      font-weight: 1000 !important;
      font-size: 20px !important;
      line-height: 1 !important;
      white-space: nowrap !important;
      word-break: keep-all !important;
      writing-mode: horizontal-tb !important;
    }

    td[data-field="area"] {
      min-width: 110px !important;
      width: 110px !important;
      text-align: center !important;
      white-space: nowrap !important;
      word-break: keep-all !important;
    }

    td[data-field="area"] * {
      white-space: nowrap !important;
      word-break: keep-all !important;
      writing-mode: horizontal-tb !important;
    }
    /* SHINNAN_BUILDING_AREA_PILL_HORIZONTAL_END */
  
    /* SHINNAN_BUILDING_TABLE_WIDTH_V2_START */
    table {
      table-layout: fixed !important;
    }

    th:nth-child(1), td:nth-child(1) { width: 101px !important; }
    th:nth-child(2), td:nth-child(2) { width: 150px !important; }
    th:nth-child(3), td:nth-child(3) { width: 105px !important; }
    th:nth-child(4), td:nth-child(4) { width: 32% !important; }
    th:nth-child(5), td:nth-child(5) { width: 145px !important; }
    th:nth-child(6), td:nth-child(6) { width: 86px !important; text-align: center !important; }
    th:nth-child(7), td:nth-child(7) { width: 86px !important; text-align: center !important; }
    th:nth-child(8), td:nth-child(8) { width: 140px !important; }
    th:nth-child(9), td:nth-child(9) { width: 86px !important; text-align: center !important; }
    th:nth-child(10), td:nth-child(10) { width: 86px !important; text-align: center !important; }

    .btn-small {
      min-width: 68px !important;
      width: 68px !important;
      height: 36px !important;
      padding: 6px 8px !important;
      border-radius: 10px !important;
      font-size: 14px !important;
      white-space: nowrap !important;
    }

    td[data-field="address"] {
      font-size: 18px !important;
      line-height: 1.35 !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
    }

    .modal-mask {
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.58);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 100;
      padding: 20px;
    }

    .modal-mask.active {
      display: flex;
    }

    .modal {
      width: min(920px, 100%);
      background: #ffffff;
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 26px 80px rgba(0,0,0,.32);
    }

    .modal-title {
      font-size: 28px;
      font-weight: 1000;
      margin-bottom: 18px;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
    }

    .field label {
      display: block;
      color: #64748b;
      font-size: 14px;
      font-weight: 1000;
      margin-bottom: 6px;
    }

    .field input,
    .field select {
      width: 100%;
      height: 46px;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      padding: 0 12px;
      font-size: 16px;
    }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 18px;
    }

    .btn-gray {
      background: #64748b !important;
    }

    @media (max-width: 900px) {
      .form-grid {
        grid-template-columns: 1fr;
      }
    }
    /* SHINNAN_BUILDING_TABLE_WIDTH_V2_END */

      /* SHINNAN_BUILDING_COLUMN_WIDTH_FINAL_START */
    table {
      width: 100% !important;
      table-layout: fixed !important;
    }

    /* 編號 */
    th:nth-child(1), td:nth-child(1) {
      width: 70px !important;
    }

    /* 大樓名稱：縮小 */
    th:nth-child(2), td:nth-child(2) {
      width: 125px !important;
    }

    /* 區域 */
    th:nth-child(3), td:nth-child(3) {
      width: 95px !important;
      text-align: center !important;
    }

    /* 地址：加寬，主要空間給地址 */
    th:nth-child(4), td:nth-child(4) {
      width: 34% !important;
      min-width: 360px !important;
    }

    /* 管理公司 */
    th:nth-child(5), td:nth-child(5) {
      width: 120px !important;
    }

    /* 用戶數量 */
    th:nth-child(6), td:nth-child(6) {
      width: 70px !important;
      text-align: center !important;
    }

    /* 住戶總數 */
    th:nth-child(7), td:nth-child(7) {
      width: 70px !important;
      text-align: center !important;
    }

    /* IP */
    th:nth-child(8), td:nth-child(8) {
      width: 135px !important;
    }

    /* 主機 */
    th:nth-child(9), td:nth-child(9) {
      width: 72px !important;
      text-align: center !important;
    }

    /* 選擇 */
    th:nth-child(10), td:nth-child(10) {
      width: 72px !important;
      text-align: center !important;
    }

    .btn-small {
      min-width: 58px !important;
      width: 58px !important;
      height: 34px !important;
      padding: 4px 6px !important;
      border-radius: 9px !important;
      font-size: 13px !important;
      white-space: nowrap !important;
    }

    td[data-field="name"] {
      white-space: normal !important;
      word-break: keep-all !important;
      line-height: 1.35 !important;
    }

    td[data-field="address"] {
      white-space: normal !important;
      word-break: break-word !important;
      overflow-wrap: anywhere !important;
      font-size: 18px !important;
      line-height: 1.35 !important;
    }
    /* SHINNAN_BUILDING_COLUMN_WIDTH_FINAL_END */
      
      
  </style>

<style id="buildings_button_center_fix_v1">
  /* 大樓名錄：所有按鈕文字垂直置中，修正手機/電腦版字體偏下 */
  button,
  .btn,
  .button,
  [role="button"] {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    line-height: 1 !important;
    text-align: center !important;
  }
</style>

<style id="buildings_mobile_cards_v1">
  /* 手機版大樓名錄改成卡片式 */
  @media (max-width: 760px) {
    body {
      overflow-x: hidden !important;
    }

    .wrap,
    main,
    .container,
    .page,
    .content {
      max-width: 100% !important;
      padding-left: 10px !important;
      padding-right: 10px !important;
      box-sizing: border-box !important;
    }

    table {
      width: 100% !important;
      min-width: 0 !important;
      border-collapse: separate !important;
      border-spacing: 0 10px !important;
    }

    table thead {
      display: none !important;
    }

    table tbody {
      display: block !important;
      width: 100% !important;
    }

    table tbody tr {
      display: grid !important;
      grid-template-columns: 1fr 1fr !important;
      gap: 8px 10px !important;
      width: 100% !important;
      margin: 0 0 10px !important;
      padding: 14px !important;
      background: #ffffff !important;
      border: 1px solid #d7e1ef !important;
      border-radius: 18px !important;
      box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08) !important;
      box-sizing: border-box !important;
    }

    table tbody tr td {
      display: block !important;
      width: auto !important;
      min-width: 0 !important;
      max-width: none !important;
      padding: 0 !important;
      border: 0 !important;
      background: transparent !important;
      color: #102348 !important;
      font-size: 14px !important;
      line-height: 1.35 !important;
      font-weight: 900 !important;
      white-space: normal !important;
      word-break: break-word !important;
    }

    table tbody tr td::before {
      content: attr(data-label);
      display: block;
      margin-bottom: 3px;
      color: #64748b;
      font-size: 11px;
      line-height: 1.2;
      font-weight: 1000;
    }

    /* 編號 */
    table tbody tr td:nth-child(1) {
      grid-column: 1 / 2 !important;
      color: #64748b !important;
      font-size: 13px !important;
    }

    /* 大樓名稱 */
    table tbody tr td:nth-child(2) {
      grid-column: 1 / -1 !important;
      font-size: 22px !important;
      font-weight: 1000 !important;
      color: #1d4ed8 !important;
    }

    table tbody tr td:nth-child(2)::before {
      display: none !important;
    }

    /* 區域 */
    table tbody tr td:nth-child(3) {
      grid-column: 1 / 2 !important;
    }

    /* 地址 */
    table tbody tr td:nth-child(4) {
      grid-column: 1 / -1 !important;
      font-size: 15px !important;
    }

    /* 管理公司 */
    table tbody tr td:nth-child(5) {
      grid-column: 1 / 2 !important;
    }

    /* 用戶數量 */
    table tbody tr td:nth-child(6) {
      grid-column: 2 / 3 !important;
    }

    /* 住戶總數 */
    table tbody tr td:nth-child(7) {
      grid-column: 1 / 2 !important;
    }

    /* IP */
    table tbody tr td:nth-child(8) {
      grid-column: 2 / 3 !important;
      font-family: ui-monospace, SFMono-Regular, Consolas, monospace !important;
      font-size: 13px !important;
    }

    /* 主機欄手機先隱藏，避免佔空間 */
    table tbody tr td:nth-child(9) {
      display: none !important;
    }

    /* 選擇按鈕 */
    table tbody tr td:last-child {
      grid-column: 1 / -1 !important;
      margin-top: 4px !important;
    }

    table tbody tr td:last-child button,
    table tbody tr td:last-child a,
    table tbody tr td:last-child .btn {
      width: 100% !important;
      height: 38px !important;
      border-radius: 12px !important;
      font-size: 15px !important;
      font-weight: 1000 !important;
    }

    /* 詳細資料彈窗按鈕也修正置中 */
    .modal button,
    .dialog button,
    .popup button,
    [id*="modal"] button,
    [class*="modal"] button {
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      line-height: 1 !important;
      padding-top: 0 !important;
      padding-bottom: 0 !important;
    }
  }
</style>


<style id="buildings_mobile_hide_select_v1">
  @media (max-width: 760px) {
    table tbody tr td:last-child {
      display: none !important;
    }

    table tbody tr {
      padding-bottom: 14px !important;
    }
  }
</style>


<style id="buildings_sales_new_picker_v1">
  @media (max-width: 760px) {
    body:not(.sales-building-picker) table tbody tr td:last-child {
      display: none !important;
    }

    body.sales-building-picker table tbody tr td:last-child {
      display: block !important;
      grid-column: 1 / -1 !important;
      margin-top: 6px !important;
    }

    body.sales-building-picker table tbody tr td:last-child button,
    body.sales-building-picker table tbody tr td:last-child a,
    body.sales-building-picker table tbody tr td:last-child .btn {
      width: 100% !important;
      height: 40px !important;
      border-radius: 13px !important;
      font-size: 15px !important;
      font-weight: 1000 !important;
      display: inline-flex !important;
      align-items: center !important;
      justify-content: center !important;
      line-height: 1 !important;
    }
  }
</style>

</head>

<body>
  <div class="topbar">
    
<style id="hide_building_host_column_v1">
  /* 大樓名錄列表隱藏「主機」欄位；API 與詳細資料仍保留 */
  table thead tr th:nth-child(9),
  table tbody tr td:nth-child(9) {
    display: none !important;
  }
</style>

<h1>大樓名錄</h1>
    <p>每區 10 棟｜地址 / 管理公司 / 用戶數量 / 住戶總數 / 主機登入 / 選擇大樓</p>
  </div>

  <main class="page">
    <div class="toolbar">
      <button type="button" onclick="location.href='/'">返回上一頁</button>
      <button type="button" id="create_building_button">新增資料</button>

      <select id="area_filter">
        <option value="全部">全部區域</option>
        <option value="東區">東區</option>
        <option value="北區">北區</option>
        <option value="北台南">北台南</option>
        <option value="仁德">仁德</option>
        <option value="永康">永康</option>
        <option value="安平">安平</option>
        <option value="南高">南高</option>
        <option value="北高">北高</option>
        <option value="透天">透天</option>
      </select>

      <input id="keyword" placeholder="搜尋大樓 / 地址 / 管理公司 / IP">
    </div>

    <section class="card">
      <div class="hint">提示：大樓名稱、區域、地址、管理公司、用戶數量、住戶總數、IP 可直接點擊修改。選擇大樓時會帶出「大樓名稱 + 地址」。</div>

      <table>
        <thead>
          <tr>
            <th>編號</th>
            <th>大樓名稱</th>
            <th>區域</th>
            <th>地址</th>
            <th>管理公司</th>
            <th>用戶數量</th>
            <th>住戶總數</th>
            <th>IP</th>
            <th>主機</th>
            <th>選擇</th>
          </tr>
        </thead>
        <tbody id="rows"></tbody>
      </table>
    </section>
  </main>

  <script>
    let buildings = [];
    const STORAGE_KEY = "shinnan_building_directory_overrides_v2";

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function goBackFromBuildings() {
      const params = new URLSearchParams(window.location.search);
      const caller = params.get("caller") || "";

      const pickReturn = localStorage.getItem("xunnan_building_pick_return") || "";
      const backReturn = localStorage.getItem("xunnan_building_back_return") || "";

      if (caller === "sales") {
        localStorage.removeItem("xunnan_building_back_return");
        window.location.href = "/admin/sales";
        return;
      }

      if (caller === "dispatch") {
        localStorage.removeItem("xunnan_building_back_return");
        window.location.href = "/admin";
        return;
      }

      if (backReturn) {
        localStorage.removeItem("xunnan_building_back_return");
        window.location.href = backReturn;
        return;
      }

      if (pickReturn) {
        if (pickReturn.includes("/admin/sales")) {
          window.location.href = "/admin/sales";
          return;
        }

        if (pickReturn.includes("/admin")) {
          window.location.href = "/admin";
          return;
        }
      }

      if (document.referrer) {
        try {
          const ref = new URL(document.referrer);

          if (ref.pathname === "/admin/sales") {
            window.location.href = "/admin/sales";
            return;
          }

          if (ref.pathname === "/admin") {
            window.location.href = "/admin";
            return;
          }

          if (ref.pathname && ref.pathname !== window.location.pathname) {
            history.back();
            return;
          }
        } catch (err) {
          history.back();
          return;
        }
      }

      window.location.href = "/admin";
    }

      if (caller === "dispatch") {
        window.location.href = "/admin";
        return;
      }

      if (returnUrl) {
        if (returnUrl.includes("/admin/sales")) {
          window.location.href = "/admin/sales";
          return;
        }

        if (returnUrl.includes("/admin")) {
          window.location.href = "/admin";
          return;
        }
      }

      if (document.referrer && document.referrer !== window.location.href) {
        history.back();
        return;
      }

      window.location.href = "/admin";
    }

    function loadOverrides() {
      try {
        return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}");
      } catch (e) {
        return {};
      }
    }

    function saveOverride(buildingNo, field, value) {
      const overrides = loadOverrides();
      if (!overrides[buildingNo]) overrides[buildingNo] = {};
      overrides[buildingNo][field] = value;
      localStorage.setItem(STORAGE_KEY, JSON.stringify(overrides));
    }

    function applyOverrides(data) {
      const overrides = loadOverrides();

      return data.map(function (item) {
        if (overrides[item.building_no]) {
          return Object.assign({}, item, overrides[item.building_no]);
        }
        return item;
      });
    }

    async function loadBuildings() {
      const res = await fetch("/api/admin/buildings?ts=" + Date.now());
      const data = await res.json();
      buildings = applyOverrides(data);
      renderRows();
    }

    function getFiltered() {
      const area = document.getElementById("area_filter").value;
      const keyword = document.getElementById("keyword").value.trim().toLowerCase();

      return buildings.filter(function (b) {
        if (area !== "全部" && b.area !== area) return false;
        if (!keyword) return true;

        return [
          b.building_no,
          b.name,
          b.area,
          b.address,
          b.management_company,
          b.ip
        ].join(" ").toLowerCase().includes(keyword);
      });
    }

    function renderRows() {
      const rows = document.getElementById("rows");
      const data = getFiltered();

      rows.innerHTML = data.map(function (b) {
        return `
          <tr data-building-no="${escapeHtml(b.building_no)}">
            <td>${escapeHtml(b.building_no)}</td>
            <td contenteditable="true" data-field="name">${escapeHtml(b.name)}</td>
            <td contenteditable="true" data-field="area"><span class="pill">${escapeHtml(b.area)}</span></td>
            <td contenteditable="true" data-field="address">${escapeHtml(b.address)}</td>
            <td contenteditable="true" data-field="management_company">${escapeHtml(b.management_company)}</td>
            <td contenteditable="true" data-field="active_users">${escapeHtml(b.active_users)}</td>
            <td contenteditable="true" data-field="total_households">${escapeHtml(b.total_households)}</td>
            <td contenteditable="true" data-field="ip">${escapeHtml(b.ip)}</td>
            <td><button class="btn-small" type="button" onclick="hostLogin('${escapeHtml(b.ip)}')">主機登入</button></td>
            <td><button class="btn-small" type="button" onclick="chooseBuilding('${escapeHtml(b.building_no)}')">選擇</button></td>
          </tr>
        `;
      }).join("");

      bindEditableCells();
    }

    function bindEditableCells() {
      document.querySelectorAll("td[contenteditable='true']").forEach(function (cell) {
        cell.addEventListener("blur", function () {
          const tr = cell.closest("tr");
          const buildingNo = tr.dataset.buildingNo;
          const field = cell.dataset.field;
          const value = cell.innerText.trim();

          saveOverride(buildingNo, field, value);

          const item = buildings.find(b => b.building_no === buildingNo);
          if (item) item[field] = value;

          renderRows();
        });

        cell.addEventListener("keydown", function (event) {
          if (event.key === "Enter") {
            event.preventDefault();
            cell.blur();
          }
        });
      });
    }

    function hostLogin(ip) {
      alert("主機登入：" + ip);
    }

    function chooseBuilding(buildingNo) {
      const b = buildings.find(item => item.building_no === buildingNo);
      if (!b) return;

      const fullAddress = `${b.name} ${b.address}`;

      const result = {
        building_no: b.building_no,
        name: b.name,
        area: b.area,
        raw_address: b.address,
        address: fullAddress,
        management_company: b.management_company,
        ip: b.ip
      };

      localStorage.setItem("xunnan_building_pick_result", JSON.stringify(result));
      localStorage.setItem("xunnan_selected_building_no", result.building_no);
      localStorage.setItem("xunnan_selected_building_name", result.name);
      localStorage.setItem("xunnan_selected_building_area", result.area);
      localStorage.setItem("xunnan_selected_building_raw_address", result.raw_address);
      localStorage.setItem("xunnan_selected_building_address", result.address);

      const returnUrl = localStorage.getItem("xunnan_building_pick_return") || "/admin";
      window.location.href = returnUrl;
    }

    document.getElementById("area_filter").addEventListener("change", renderRows);
    document.getElementById("keyword").addEventListener("input", renderRows);

    loadBuildings();
  </script>

  <div id="create_building_modal" class="modal-mask">
    <div class="modal">
      <div class="modal-title">新增大樓資料</div>

      <div class="form-grid">
        <div class="field">
          <label>大樓名稱</label>
          <input id="new_building_name" placeholder="例如 維冠大樓">
        </div>

        <div class="field">
          <label>區域</label>
          <select id="new_building_area">
            <option value="東區">東區</option>
            <option value="北區">北區</option>
            <option value="北台南">北台南</option>
            <option value="仁德">仁德</option>
            <option value="永康">永康</option>
            <option value="安平">安平</option>
            <option value="南高">南高</option>
            <option value="北高">北高</option>
            <option value="透天">透天</option>
          </select>
        </div>

        <div class="field">
          <label>地址</label>
          <input id="new_building_address" placeholder="例如 A棟1F-1">
        </div>

        <div class="field">
          <label>管理公司</label>
          <input id="new_management_company" placeholder="例如 安信管理">
        </div>

        <div class="field">
          <label>用戶數量</label>
          <input id="new_active_users" value="0">
        </div>

        <div class="field">
          <label>住戶總數</label>
          <input id="new_total_households" value="0">
        </div>

        <div class="field">
          <label>IP</label>
          <input id="new_building_ip" placeholder="例如 192.168.10.99">
        </div>
      </div>

      <div class="modal-actions">
        <button type="button" class="btn-gray" id="cancel_create_building_button">取消</button>
        <button type="button" id="save_create_building_button">新增資料</button>
      </div>
    </div>
  </div>


<script>
// SHINNAN_BUILDING_CREATE_DATA_V1
(function () {
  const ADD_STORAGE_KEY = "shinnan_building_directory_additional_v1";

  function loadAdditionalBuildings() {
    try {
      return JSON.parse(localStorage.getItem(ADD_STORAGE_KEY) || "[]");
    } catch (e) {
      return [];
    }
  }

  function saveAdditionalBuildings(items) {
    localStorage.setItem(ADD_STORAGE_KEY, JSON.stringify(items));
  }

  function nextBuildingNo() {
    const additional = loadAdditionalBuildings();
    const nums = [];

    try {
      buildings.forEach(function (b) {
        const m = String(b.building_no || "").match(/^B(\\d+)$/);
        if (m) nums.push(Number(m[1]));
      });
    } catch (e) {}

    additional.forEach(function (b) {
      const m = String(b.building_no || "").match(/^B(\\d+)$/);
      if (m) nums.push(Number(m[1]));
    });

    const next = nums.length ? Math.max(...nums) + 1 : 1;
    return "B" + String(next).padStart(3, "0");
  }

  function openCreateBuildingModal() {
    const modal = document.getElementById("create_building_modal");
    if (modal) modal.classList.add("active");
  }

  function closeCreateBuildingModal() {
    const modal = document.getElementById("create_building_modal");
    if (modal) modal.classList.remove("active");
  }

  function createBuilding() {
    const name = document.getElementById("new_building_name").value.trim();
    const area = document.getElementById("new_building_area").value;
    const address = document.getElementById("new_building_address").value.trim();
    const managementCompany = document.getElementById("new_management_company").value.trim();
    const activeUsers = Number(String(document.getElementById("new_active_users").value || "0").replace(/[^\\d]/g, ""));
    const totalHouseholds = Number(String(document.getElementById("new_total_households").value || "0").replace(/[^\\d]/g, ""));
    const ip = document.getElementById("new_building_ip").value.trim();

    if (!name) {
      alert("請輸入大樓名稱");
      return;
    }

    if (!address) {
      alert("請輸入地址");
      return;
    }

    const item = {
      building_no: nextBuildingNo(),
      name: name,
      area: area,
      address: address,
      display_address: name + " " + address,
      management_company: managementCompany || "未填",
      active_users: activeUsers,
      total_households: totalHouseholds,
      ip: ip || "未設定"
    };

    const additional = loadAdditionalBuildings();
    additional.push(item);
    saveAdditionalBuildings(additional);

    buildings.push(item);

    closeCreateBuildingModal();
    renderRows();

    document.getElementById("new_building_name").value = "";
    document.getElementById("new_building_address").value = "";
    document.getElementById("new_management_company").value = "";
    document.getElementById("new_active_users").value = "0";
    document.getElementById("new_total_households").value = "0";
    document.getElementById("new_building_ip").value = "";

    alert("大樓資料已新增");
  }

  function patchLoadBuildings() {
    if (window.__shinnanBuildingCreatePatched) return;
    window.__shinnanBuildingCreatePatched = true;

    const oldLoadBuildings = window.loadBuildings || loadBuildings;

    window.loadBuildings = async function () {
      const res = await fetch("/api/admin/buildings?ts=" + Date.now());
      const data = await res.json();
      const merged = data.concat(loadAdditionalBuildings());
      buildings = applyOverrides(merged);
      renderRows();
    };
  }

  document.addEventListener("DOMContentLoaded", function () {
    patchLoadBuildings();

    const createButton = document.getElementById("create_building_button");
    const cancelButton = document.getElementById("cancel_create_building_button");
    const saveButton = document.getElementById("save_create_building_button");

    if (createButton) createButton.addEventListener("click", openCreateBuildingModal);
    if (cancelButton) cancelButton.addEventListener("click", closeCreateBuildingModal);
    if (saveButton) saveButton.addEventListener("click", createBuilding);
  });
})();
</script>



<script id="shinnan_buildings_simple_back_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  function goBackFromBuildingsSimple(event) {
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    if (window.history.length > 1) {
      window.history.back();
      return;
    }

    window.location.href = "/admin";
  }

  window.goBackFromBuildings = goBackFromBuildingsSimple;

  function bindBackButtons() {
    Array.from(document.querySelectorAll("button, a")).forEach(function (el) {
      const text = String(el.textContent || "").trim();

      if (text === "返回上一頁" || text === "返回後台" || text === "返回首頁") {
        el.textContent = "返回上一頁";
        el.onclick = goBackFromBuildingsSimple;
        el.addEventListener("click", goBackFromBuildingsSimple, true);
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindBackButtons);
  } else {
    bindBackButtons();
  }

  setTimeout(bindBackButtons, 300);
  setTimeout(bindBackButtons, 800);
})();
</script>


<style id="shinnan_building_detail_modal_style_v1">
  .building-name-link {
    border: 0;
    background: transparent;
    color: #1d4ed8;
    font-size: inherit;
    font-weight: 1000;
    cursor: pointer;
    padding: 0;
    text-align: left;
  }

  .building-name-link:hover {
    text-decoration: underline;
  }

  .building-detail-mask {
    position: fixed;
    inset: 0;
    display: none;
    align-items: center;
    justify-content: center;
    background: rgba(15, 23, 42, 0.58);
    z-index: 9000;
    padding: 20px;
  }

  .building-detail-mask.active {
    display: flex;
  }

  .building-detail-modal {
    width: min(1180px, 96vw);
    max-height: 90vh;
    overflow: auto;
    background: #ffffff;
    border-radius: 22px;
    box-shadow: 0 28px 90px rgba(0,0,0,0.30);
    padding: 20px;
    color: #102348;
    font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
  }

  .building-detail-head {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 14px;
    margin-bottom: 14px;
    border-bottom: 1px solid #dbe7f5;
    padding-bottom: 12px;
  }

  .building-detail-title {
    font-size: 30px;
    font-weight: 1000;
    line-height: 1.2;
  }

  .building-detail-sub {
    margin-top: 6px;
    color: #64748b;
    font-size: 14px;
    font-weight: 800;
  }

  .building-detail-close {
    height: 34px;
    min-width: 78px;
    border: 0;
    border-radius: 10px;
    background: #64748b;
    color: #fff;
    font-size: 15px;
    font-weight: 900;
    cursor: pointer;
  }

  .building-detail-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 12px;
  }

  .building-detail-card {
    border: 1px solid #dbe7f5;
    border-radius: 16px;
    background: #f8fbff;
    padding: 12px;
  }

  .building-detail-card.full {
    grid-column: 1 / -1;
  }

  .building-detail-card.half {
    grid-column: span 2;
  }

  .building-detail-label {
    color: #64748b;
    font-size: 13px;
    font-weight: 900;
    margin-bottom: 5px;
  }

  .building-detail-value {
    color: #102348;
    font-size: 16px;
    font-weight: 1000;
    line-height: 1.45;
    white-space: pre-wrap;
  }

  .building-detail-section {
    grid-column: 1 / -1;
    margin-top: 4px;
    padding: 8px 10px;
    border-radius: 12px;
    background: #eaf2ff;
    color: #24415f;
    font-size: 17px;
    font-weight: 1000;
  }

  @media (max-width: 980px) {
    .building-detail-grid {
      grid-template-columns: repeat(2, minmax(0, 1fr));
    }
  }

  @media (max-width: 640px) {
    .building-detail-grid {
      grid-template-columns: 1fr;
    }

    .building-detail-card.half {
      grid-column: 1 / -1;
    }
  }
</style>

<div id="building_detail_mask" class="building-detail-mask">
  <div class="building-detail-modal">
    <div class="building-detail-head">
      <div>
        <div id="building_detail_title" class="building-detail-title">大樓詳細資料</div>
        <div id="building_detail_sub" class="building-detail-sub"></div>
      </div>
      <button class="building-detail-close" type="button" onclick="window.closeBuildingDetailModal && window.closeBuildingDetailModal()">關閉</button>
    </div>

    <div id="building_detail_body" class="building-detail-grid"></div>
  </div>
</div>

<script id="shinnan_building_detail_modal_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  const BUSINESS_STORAGE_KEY = "shinnan_building_business_records_v1";

  function safeText(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function readJson(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback));
    } catch (err) {
      return fallback;
    }
  }

  function normalizeName(value) {
    return String(value || "").trim();
  }

  function findBusinessRecordForBuilding(building) {
    const records = readJson(BUSINESS_STORAGE_KEY, []);
    const buildingName = normalizeName(building.name || building.building_name);

    if (!Array.isArray(records) || !buildingName) return null;

    return records.find(function (item) {
      return normalizeName(item.building_name) === buildingName;
    }) || null;
  }

  function card(label, value, extraClass) {
    return `
      <div class="building-detail-card ${extraClass || ""}">
        <div class="building-detail-label">${safeText(label)}</div>
        <div class="building-detail-value">${safeText(value || "-")}</div>
      </div>
    `;
  }

  function section(title) {
    return `<div class="building-detail-section">${safeText(title)}</div>`;
  }

  window.closeBuildingDetailModal = function () {
    const mask = document.getElementById("building_detail_mask");
    if (mask) mask.classList.remove("active");
  };

  window.openBuildingDetailModal = function (building) {
    building = building || {};

    const record = findBusinessRecordForBuilding(building) || {};
    const title = document.getElementById("building_detail_title");
    const sub = document.getElementById("building_detail_sub");
    const body = document.getElementById("building_detail_body");
    const mask = document.getElementById("building_detail_mask");

    if (!body || !mask) return;

    const buildingName = building.name || building.building_name || record.building_name || "未命名大樓";

    if (title) title.textContent = buildingName;
    if (sub) {
      sub.textContent =
        "區域：" + (building.area || record.area || "-") +
        "｜地址：" + (building.raw_address || building.address || "-");
    }

    body.innerHTML = [
      section("大樓基本資料"),
      card("編號", building.building_no || building.no || ""),
      card("區域", building.area || record.area || ""),
      card("地址", building.raw_address || building.address || ""),
      card("管理公司", building.management_company || record.management_company || ""),
      card("用戶數量", building.active_users ?? building.user_count ?? ""),
      card("住戶總數", building.total_households ?? building.households ?? ""),
      card("IP", building.ip || ""),
      card("主機", building.host || building.main_host || ""),

      section("管理室／總幹事"),
      card("管理室電話", record.management_phone || ""),
      card("總幹事姓名", record.manager_name || ""),
      card("總幹事電話", record.manager_phone || ""),
      card("總幹事年齡", record.manager_age ? record.manager_age + " 歲" : ""),
      card("總幹事資歷", record.manager_experience || ""),
      card("總幹事興趣", record.manager_interest || ""),
      card("可拜訪時段", record.visit_time || ""),
      card("管理室資訊／注意事項", record.management_note || "", "full"),

      section("會議／合約"),
      card("委員會時間", record.committee_time || ""),
      card("住戶大會時間", record.resident_meeting_time || ""),
      card("合約狀態", record.contract_status || ""),
      card("合約到期日", record.contract_end_date || ""),

      section("業務資訊"),
      card("業務類型", record.business_type || ""),
      card("目前狀態", record.status || ""),
      card("負責業務", record.owner || ""),
      card("下次拜訪", record.next_visit || ""),
      card("業務事件", record.event_type && record.event_type !== "無" ? record.event_type + "｜" + (record.event_status || "") : ""),
      card("事件安排日期", record.event_schedule_date || ""),
      card("回饋項目", record.feedback_type && record.feedback_type !== "無" ? record.feedback_type + "｜" + (record.feedback_status || "") : ""),
      card("業務紀錄／拜訪結果", record.business_note || "", "full")
    ].join("");

    mask.classList.add("active");
  };

  function bindExistingBuildingNameCells() {
    const rows = Array.from(document.querySelectorAll("tbody tr"));

    rows.forEach(function (row) {
      const cells = row.querySelectorAll("td");
      if (cells.length < 2) return;

      const nameCell = cells[1];
      if (nameCell.querySelector(".building-name-link")) return;

      const name = nameCell.textContent.trim();
      if (!name) return;

      const building = {
        building_no: cells[0] ? cells[0].textContent.trim() : "",
        name: name,
        area: cells[2] ? cells[2].textContent.trim() : "",
        address: cells[3] ? cells[3].textContent.trim() : "",
        raw_address: cells[3] ? cells[3].textContent.trim() : "",
        management_company: cells[4] ? cells[4].textContent.trim() : "",
        active_users: cells[5] ? cells[5].textContent.trim() : "",
        total_households: cells[6] ? cells[6].textContent.trim() : "",
        ip: cells[7] ? cells[7].textContent.trim() : "",
        host: cells[8] ? cells[8].textContent.trim() : ""
      };

      nameCell.innerHTML = "";
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "building-name-link";
      btn.textContent = name;
      btn.onclick = function () {
        window.openBuildingDetailModal(building);
      };
      nameCell.appendChild(btn);
    });
  }

  document.addEventListener("click", function (event) {
    const mask = document.getElementById("building_detail_mask");
    if (event.target === mask) {
      window.closeBuildingDetailModal();
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bindExistingBuildingNameCells);
  } else {
    bindExistingBuildingNameCells();
  }

  setTimeout(bindExistingBuildingNameCells, 500);
  setTimeout(bindExistingBuildingNameCells, 1000);
})();
</script>

<script id="shinnan_buildings_render_recovery_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  const ADD_STORAGE_KEY = "shinnan_building_directory_additional_v1";
  const OVERRIDE_STORAGE_KEY = "shinnan_building_directory_overrides_v1";

  function safeText(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function readJson(key, fallback) {
    try {
      return JSON.parse(localStorage.getItem(key) || JSON.stringify(fallback));
    } catch (err) {
      return fallback;
    }
  }

  function getAreaFilter() {
    const el = document.getElementById("area_filter");
    return el ? el.value : "全部";
  }

  function getKeyword() {
    const el = document.getElementById("keyword");
    return el ? el.value.trim().toLowerCase() : "";
  }

  function getRowsBox() {
    return (
      document.getElementById("building_rows") ||
      document.getElementById("building_table_body") ||
      document.querySelector("tbody")
    );
  }

  function normalizeBuilding(item) {
    const name = item.name || item.building_name || "";
    const rawAddress = item.raw_address || item.address || item.display_address || "";

    return {
      building_no: item.building_no || item.no || "",
      name: name,
      area: item.area || "",
      address: rawAddress,
      raw_address: rawAddress,
      management_company: item.management_company || "",
      active_users: item.active_users ?? item.user_count ?? "",
      total_households: item.total_households ?? item.households ?? "",
      ip: item.ip || "",
      host: item.host || item.main_host || ""
    };
  }

  function mergeData(apiData) {
    const additional = readJson(ADD_STORAGE_KEY, []);
    const overrides = readJson(OVERRIDE_STORAGE_KEY, {});

    let data = Array.isArray(apiData) ? apiData.slice() : [];

    if (Array.isArray(additional) && additional.length) {
      data = data.concat(additional);
    }

    data = data.map(function (item) {
      const normalized = normalizeBuilding(item);
      const override = overrides[normalized.building_no] || {};
      return Object.assign({}, normalized, override);
    });

    return data;
  }

  function filteredBuildings(data) {
    const area = getAreaFilter();
    const keyword = getKeyword();

    return data.filter(function (b) {
      if (area !== "全部" && b.area !== area) return false;

      if (!keyword) return true;

      const hay = [
        b.building_no,
        b.name,
        b.area,
        b.address,
        b.management_company,
        b.active_users,
        b.total_households,
        b.ip,
        b.host
      ].join(" ").toLowerCase();

      return hay.includes(keyword);
    });
  }

  function chooseBuildingRecovery(b) {
    const result = {
      building_no: b.building_no || "",
      name: b.name || "",
      area: b.area || "",
      address: b.name && b.address ? b.name + " " + b.address : (b.address || ""),
      raw_address: b.address || "",
      management_company: b.management_company || "",
      ip: b.ip || ""
    };

    localStorage.setItem("xunnan_building_pick_result", JSON.stringify(result));
    localStorage.setItem("xunnan_selected_building_no", result.building_no);
    localStorage.setItem("xunnan_selected_building_name", result.name);
    localStorage.setItem("xunnan_selected_building_area", result.area);
    localStorage.setItem("xunnan_selected_building_raw_address", result.raw_address);
    localStorage.setItem("xunnan_selected_building_address", result.address);

    const returnUrl = localStorage.getItem("xunnan_building_pick_return");

    if (returnUrl) {
      window.location.href = returnUrl;
      return;
    }

    const params = new URLSearchParams(window.location.search);
    const caller = params.get("caller") || "";

    if (caller === "sales") {
      window.location.href = "/admin/sales?open_sales_modal=1&from_building_pick=1&caller=sales";
      return;
    }

    window.location.href = "/admin?open_create=1&from_building_pick=1";
  }

  window.__shinnanBuildingChooseRecovery = chooseBuildingRecovery;

  function renderBuildingsRecovery(data) {
    const rows = getRowsBox();
    if (!rows) return;

    const filtered = filteredBuildings(data);

    if (!filtered.length) {
      rows.innerHTML = '<tr><td colspan="10">目前沒有符合條件的大樓資料。</td></tr>';
      return;
    }

    rows.innerHTML = filtered.map(function (b, index) {
      const encoded = encodeURIComponent(JSON.stringify(b));

      return `
        <tr>
          <td>${safeText(b.building_no)}</td>
          <td>
            <button
              class="building-name-link"
              type="button"
              onclick="window.openBuildingDetailModal && window.openBuildingDetailModal(JSON.parse(decodeURIComponent('${encoded}')))"
            >${safeText(b.name)}</button>
          </td>
          <td>${safeText(b.area)}</td>
          <td>${safeText(b.address)}</td>
          <td>${safeText(b.management_company)}</td>
          <td>${safeText(b.active_users)}</td>
          <td>${safeText(b.total_households)}</td>
          <td>${safeText(b.ip)}</td>
          <td>${safeText(b.host || "-")}</td>
          <td>
            <button
              class="btn-blue"
              type="button"
              onclick="window.__shinnanBuildingChooseRecovery(JSON.parse(decodeURIComponent('${encoded}')))"
            >選擇</button>
          </td>
        </tr>
      `;
    }).join("");
  }

  async function loadBuildingsRecovery() {
    try {
      const res = await fetch("/api/admin/buildings?ts=" + Date.now(), {cache: "no-store"});
      const apiData = await res.json();
      const data = mergeData(apiData);

      window.__shinnanBuildingsRecoveryData = data;
      renderBuildingsRecovery(data);
    } catch (err) {
      console.error("大樓名錄救援渲染失敗", err);

      const rows = getRowsBox();
      if (rows) {
        rows.innerHTML = '<tr><td colspan="10">大樓資料讀取失敗，請查看瀏覽器 Console。</td></tr>';
      }
    }
  }

  function bindRecoveryFilters() {
    const area = document.getElementById("area_filter");
    const keyword = document.getElementById("keyword");

    if (area) {
      area.onchange = function () {
        renderBuildingsRecovery(window.__shinnanBuildingsRecoveryData || []);
      };
    }

    if (keyword) {
      keyword.oninput = function () {
        renderBuildingsRecovery(window.__shinnanBuildingsRecoveryData || []);
      };
    }
  }

  function startRecovery() {
    bindRecoveryFilters();
    loadBuildingsRecovery();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startRecovery);
  } else {
    startRecovery();
  }

  setTimeout(startRecovery, 500);
})();
</script>



<script id="buildings_mobile_cards_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  function applyBuildingMobileLabels() {
    const tables = Array.from(document.querySelectorAll("table"));
    if (!tables.length) return;

    tables.forEach(function (table) {
      const headers = Array.from(table.querySelectorAll("thead th")).map(function (th) {
        return (th.textContent || "").trim();
      });

      if (!headers.length) {
        // 若沒有表頭，就用目前大樓名錄預設欄位
        headers.push("編號", "大樓名稱", "區域", "地址", "管理公司", "用戶數量", "住戶總數", "IP", "主機", "選擇");
      }

      table.querySelectorAll("tbody tr").forEach(function (tr) {
        Array.from(tr.children).forEach(function (td, index) {
          if (!td.getAttribute("data-label")) {
            td.setAttribute("data-label", headers[index] || "");
          }
        });
      });
    });
  }

  function fixButtonVerticalCenter() {
    document.querySelectorAll("button, .btn, .button, [role='button']").forEach(function (btn) {
      btn.style.display = "inline-flex";
      btn.style.alignItems = "center";
      btn.style.justifyContent = "center";
      btn.style.lineHeight = "1";
    });
  }

  function applyAll() {
    applyBuildingMobileLabels();
    fixButtonVerticalCenter();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyAll);
  } else {
    applyAll();
  }

  setTimeout(applyAll, 300);
  setTimeout(applyAll, 900);

  const observer = new MutationObserver(function () {
    setTimeout(applyAll, 0);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
})();
</script>


<script id="buildings_sales_new_picker_v1">
(function () {
  if (!location.pathname.includes("/admin/buildings")) return;

  const params = new URLSearchParams(location.search);
  const isPicker = params.get("pick") === "sales_new";

  if (isPicker) {
    document.body.classList.add("sales-building-picker");
    document.title = "選擇大樓｜訊南 ERP";
  }

  function pickUrl(buildingNo, buildingName) {
    return "/app/sales/new?building_no=" +
      encodeURIComponent(buildingNo || "") +
      "&building_name=" +
      encodeURIComponent(buildingName || "") +
      "&ts=" + Date.now();
  }

  function applySalesNewPicker() {
    if (!isPicker) return;

    document.querySelectorAll("table tbody tr").forEach(function (tr) {
      const cells = Array.from(tr.children);

      if (cells.length < 2) return;

      const buildingNo = (cells[0].textContent || "").trim();
      const buildingName = (cells[1].textContent || "").trim();

      const last = cells[cells.length - 1];
      if (!last) return;

      last.innerHTML = "";

      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = "選擇此大樓";
      btn.onclick = function () {
        location.href = pickUrl(buildingNo, buildingName);
      };

      last.appendChild(btn);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applySalesNewPicker);
  } else {
    applySalesNewPicker();
  }

  setTimeout(applySalesNewPicker, 300);
  setTimeout(applySalesNewPicker, 900);

  const observer = new MutationObserver(function () {
    setTimeout(applySalesNewPicker, 0);
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true
  });
})();

</script>

<script id="shinnan_dispatch_recovery_render_v1">
(function () {
  function esc(v) {
    return String(v == null ? "" : v)
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function setDebug(text) {
    var box = document.getElementById("dispatch_recovery_debug_box");
    if (!box) {
      box = document.createElement("div");
      box.id = "dispatch_recovery_debug_box";
      box.style.cssText = "display:none;";
      var anchor = document.querySelector(".stats-grid") || document.getElementById("list") || document.body.firstChild;
      if (anchor && anchor.parentNode) {
        anchor.parentNode.insertBefore(box, anchor);
      } else {
        document.body.insertBefore(box, document.body.firstChild);
      }
    }
    box.textContent = text;
  }

  function isActive(item) {
    var s = String(item.status || "");
    return s !== "已完成" && s !== "取消" && s !== "作廢";
  }

  function renderItems(items, user) {
    var list = document.getElementById("list");
    if (!list) {
      setDebug("補救渲染失敗：找不到 #list");
      return;
    }

    document.querySelectorAll(".stat-card .stat-value").forEach(function (el, idx) {
      if (idx === 0) {
        var today = new Date().toISOString().slice(0, 10);
        el.textContent = items.filter(function (x) { return x.appointment_date === today; }).length;
      }
      if (idx === 1) {
        el.textContent = items.filter(function (x) {
          return x.status === "施工中" || x.status === "已領取";
        }).length;
      }
      if (idx === 2) {
        el.textContent = items.length;
      }
    });

    if (!items.length) {
      list.innerHTML = '<div class="empty">目前沒有派工案件。</div>';
      return;
    }

    list.innerHTML = items.map(function (item) {
      return `
        <div class="ticket-card">
          <div class="ticket-title">${esc(item.ticket_no || "-")}｜${esc(item.case_type || "-")}</div>
          <div class="ticket-sub">${esc(item.customer_name || "-")}｜${esc(item.customer_no || "-")}｜${esc(item.building_no || "-")}</div>
          <div class="ticket-grid">
            <div class="info">
              <div class="info-label">狀態</div>
              <div class="info-value">${esc(item.status || "-")}</div>
            </div>
            <div class="info">
              <div class="info-label">預約</div>
              <div class="info-value">${esc(item.appointment_date || "-")} ${esc(item.appointment_time || "")}</div>
            </div>
            <div class="info">
              <div class="info-label">工程師</div>
              <div class="info-value">${esc(item.assigned_engineer || "-")}｜${esc(item.assigned_engineer_staff_code || "-")}</div>
            </div>
            <div class="info">
              <div class="info-label">地址</div>
              <div class="info-value">${esc(item.service_address || "-")}</div>
            </div>
          </div>
        </div>
      `;
    }).join("");
  }

  async function recoveryLoadDispatchTickets() {
    try {
      setDebug("補救讀取：準備抓派工 API");

      var res = await fetch("/api/app/dispatch/tickets?ts=" + Date.now(), {
        cache: "no-store",
        credentials: "same-origin"
      });

      setDebug("補救讀取：HTTP " + res.status);

      if (res.status === 401) {
        setDebug("補救讀取：401，登入已失效");
        location.href = "/employee/login?next=/app/dispatch";
        return;
      }

      if (!res.ok) {
        var txt = await res.text();
        setDebug("補救讀取失敗：HTTP " + res.status);
        var list = document.getElementById("list");
        if (list) list.innerHTML = '<div class="empty">補救讀取失敗：HTTP ' + res.status + '<br>' + esc(txt.slice(0, 300)) + '</div>';
        return;
      }

      var data = await res.json();
      var items = data.items || [];

      setDebug("補救讀取：OK｜使用者：" + ((data.user && data.user.display_name) || "-") + "｜案件：" + items.length);

      renderItems(items, data.user || {});
    } catch (err) {
      var msg = String(err && err.message ? err.message : err);
      setDebug("補救讀取錯誤：" + msg);
      var list = document.getElementById("list");
      if (list) list.innerHTML = '<div class="empty">補救讀取錯誤：<br>' + esc(msg) + '</div>';
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", recoveryLoadDispatchTickets);
  } else {
    recoveryLoadDispatchTickets();
  }

  setTimeout(recoveryLoadDispatchTickets, 800);
})();
</script>

</body>
</html>
"""
# SHINNAN_BUILDINGS_PAGE_RESTORE_END


# SHINNAN_ENGINEERS_PAGE_ROUTE_START
# Route disabled: /admin/engineers is owned by app.routes.admin_dispatch.
def shinnan_admin_engineers_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>工程師名錄｜訊南 ERP</title>
  <style>
    body {
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1180px;
      margin: 0 auto;
      padding: 24px;
    }

    .topbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 18px;
    }

    .toolbar {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 14px;
      flex-wrap: wrap;
    }

    .filter-box {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 15px;
      font-weight: 900;
      color: #334155;
    }

    .filter-box select {
      height: 36px;
      min-width: 180px;
      padding: 0 10px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      background: #ffffff;
      color: #102348;
      font-size: 15px;
      font-weight: 800;
    }

    .count-text {
      color: #64748b;
      font-size: 14px;
      font-weight: 800;
    }

    h1 {
      margin: 0;
      font-size: 30px;
      font-weight: 1000;
      color: #102348;
    }

    .btn-home {
      height: 36px;
      min-width: 88px;
      padding: 0 12px;
      border: 0;
      border-radius: 10px;
      background: #4f7ee8;
      color: #ffffff;
      font-size: 15px;
      font-weight: 900;
      cursor: pointer;
    }

    .card {
      background: #ffffff;
      border: 1px solid #d7e1ef;
      border-radius: 20px;
      box-shadow: 0 14px 40px rgba(15, 23, 42, 0.08);
      overflow: hidden;
    }

    table {
      width: 100%;
      border-collapse: collapse;
    }

    th, td {
      padding: 14px 16px;
      border-bottom: 1px solid #e5edf7;
      text-align: left;
      font-size: 16px;
    }

    th {
      background: #eaf2ff;
      color: #24415f;
      font-weight: 1000;
    }

    tr:last-child td {
      border-bottom: 0;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 84px;
      height: 28px;
      padding: 0 10px;
      border-radius: 999px;
      background: #eef2ff;
      color: #3730a3;
      font-weight: 900;
      font-size: 14px;
    }

    .muted {
      color: #64748b;
      font-size: 14px;
      margin-top: 6px;
    }

    @media (max-width: 720px) {
      .wrap {
        padding: 14px;
      }

      th, td {
        padding: 10px 8px;
        font-size: 14px;
      }

      h1 {
        font-size: 24px;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="topbar">
      <div>
        <h1>工程師名錄</h1>
        <div class="muted">僅顯示工程師編號、姓名與部門，不顯示密碼。</div>
      </div>
      <button class="btn-home" type="button" onclick="goBackFromBuildings()">返回上一頁</button>
    </div>

    <div class="toolbar">
      <div class="filter-box">
        <label for="department_filter">部門篩選</label>
        <select id="department_filter">
          <option value="全部">全部</option>
        </select>
      </div>
      <div class="count-text" id="engineer_count">讀取中...</div>
    </div>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th>員工編號</th>
            <th>姓名</th>
            <th>部門</th>
          </tr>
        </thead>
        <tbody id="engineer_rows">
          <tr><td colspan="3">讀取中...</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <script>
    function escapeHtml(value) {
      return String(value || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    let engineerData = [];

    function populateDepartmentFilter(items) {
      const select = document.getElementById("department_filter");
      if (!select) return;

      const current = select.value || "全部";
      const departments = Array.from(new Set(
        items.map(function (item) {
          return String(item.department || "").trim();
        }).filter(Boolean)
      ));

      select.innerHTML = '<option value="全部">全部</option>' + departments.map(function (dep) {
        return `<option value="${escapeHtml(dep)}">${escapeHtml(dep)}</option>`;
      }).join("");

      if (departments.includes(current)) {
        select.value = current;
      } else {
        select.value = "全部";
      }
    }

    function renderEngineers() {
      const rows = document.getElementById("engineer_rows");
      const count = document.getElementById("engineer_count");
      const department = document.getElementById("department_filter").value || "全部";

      let data = engineerData;

      if (department !== "全部") {
        data = engineerData.filter(function (item) {
          return item.department === department;
        });
      }

      if (count) {
        count.textContent = department === "全部"
          ? "共 " + data.length + " 位工程師"
          : department + "｜共 " + data.length + " 位工程師";
      }

      if (!data.length) {
        rows.innerHTML = "<tr><td colspan='3'>目前沒有符合條件的工程師。</td></tr>";
        return;
      }

      rows.innerHTML = data.map(function (item) {
        return `
          <tr>
            <td>${escapeHtml(item.employee_no)}</td>
            <td><b>${escapeHtml(item.name)}</b></td>
            <td><span class="pill">${escapeHtml(item.department)}</span></td>
          </tr>
        `;
      }).join("");
    }

    async function loadEngineers() {
      const rows = document.getElementById("engineer_rows");

      try {
        const res = await fetch("/api/admin/engineers?ts=" + Date.now(), {cache: "no-store"});
        if (!res.ok) {
          rows.innerHTML = "<tr><td colspan='3'>工程師資料讀取失敗。</td></tr>";
          return;
        }

        const data = await res.json();

        if (!Array.isArray(data) || !data.length) {
          engineerData = [];
          rows.innerHTML = "<tr><td colspan='3'>目前沒有工程師資料。</td></tr>";
          const count = document.getElementById("engineer_count");
          if (count) count.textContent = "共 0 位工程師";
          return;
        }

        engineerData = data;
        populateDepartmentFilter(engineerData);
        renderEngineers();
      } catch (err) {
        rows.innerHTML = "<tr><td colspan='3'>工程師資料讀取錯誤。</td></tr>";
      }
    }

    document.getElementById("department_filter").addEventListener("change", renderEngineers);

    loadEngineers();
  </script>
</body>
</html>
"""
# SHINNAN_ENGINEERS_PAGE_ROUTE_END


# SHINNAN_SALES_PAGE_ROUTE_START
@router.get("/admin/sales", response_class=HTMLResponse, summary="業務管理系統")
def shinnan_admin_sales_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>業務管理系統｜訊南 ERP</title>
  <style>
    :root {
      --bg:#eef3f9;
      --card:#ffffff;
      --line:#d7e1ef;
      --text:#102348;
      --muted:#64748b;
      --blue:#365ee8;
      --green:#16a34a;
      --orange:#ea580c;
      --red:#dc2626;
      --purple:#7c3aed;
      --teal:#0f766e;
    }

    * { box-sizing: border-box; }

    body {
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1460px;
      margin: 0 auto;
      padding: 22px;
    }

    .topbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;
    }

    h1 {
      margin: 0;
      font-size: 32px;
      font-weight: 1000;
    }

    .subtitle {
      margin-top: 6px;
      color: var(--muted);
      font-size: 14px;
      font-weight: 800;
    }

    .actions {
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      justify-content: flex-end;
    }

    button {
      height: 36px;
      border: 0;
      border-radius: 10px;
      padding: 0 14px;
      color: #fff;
      font-size: 15px;
      font-weight: 900;
      cursor: pointer;
    }

    .btn-home { background:#4f7ee8; }
    .btn-green { background:var(--green); }
    .btn-blue { background:var(--blue); }
    .btn-gray { background:#64748b; }
    .btn-orange { background:var(--orange); }
    .btn-purple { background:var(--purple); }

    .stats {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 8px;
      margin-bottom: 10px;
    }

    .stat-card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 14px;
      padding: 8px 12px;
      min-height: 64px;
      box-shadow: 0 8px 20px rgba(15,23,42,.06);
      display: flex;
      flex-direction: column;
      justify-content: center;
    }

    .stat-label {
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
      line-height: 1.25;
      white-space: nowrap;
    }

    .stat-number {
      margin-top: 4px;
      font-size: 24px;
      line-height: 1;
      font-weight: 1000;
    }

    .panel {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 18px;
      padding: 16px;
      box-shadow: 0 12px 34px rgba(15,23,42,.08);
      margin-bottom: 16px;
    }

    .schedule-panel {
      border: 1px solid rgba(37, 99, 235, 0.22);
      background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    }

    .schedule-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
      margin-bottom: 8px;
    }

    .schedule-title {
      font-size: 22px;
      font-weight: 1000;
      color: #102348;
    }

    .schedule-sub {
      color: #64748b;
      font-size: 13px;
      font-weight: 800;
    }

    .schedule-list {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
    }

    .schedule-card {
      border: 1px solid #dbe7f5;
      border-radius: 16px;
      padding: 12px;
      background: #ffffff;
      box-shadow: 0 10px 24px rgba(15,23,42,.06);
    }

    .schedule-card.important {
      border-color: #f59e0b;
      background: #fffbeb;
    }

    .schedule-card-title {
      font-size: 17px;
      font-weight: 1000;
      margin-bottom: 6px;
    }

    .schedule-card-line {
      color: #475569;
      font-size: 13px;
      font-weight: 800;
      line-height: 1.55;
    }

    .schedule-empty {
      padding: 14px;
      border: 1px dashed #cbd5e1;
      border-radius: 14px;
      color: #64748b;
      font-weight: 800;
      background: #f8fafc;
    }

    .check-row {
      display: flex;
      align-items: center;
      gap: 10px;
      min-height: 36px;
      padding: 8px 10px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      background: #f8fafc;
      font-weight: 900;
      color: #334155;
    }

    .check-row input {
      width: 18px !important;
      height: 18px !important;
      min-height: 18px !important;
      padding: 0 !important;
    }

    .filters {
      display: grid;
      grid-template-columns: repeat(6, 1fr);
      gap: 12px;
      align-items: end;
    }

    label {
      display: block;
      margin-bottom: 5px;
      color: #475569;
      font-size: 14px;
      font-weight: 900;
    }

    input, select, textarea {
      width: 100%;
      height: 36px;
      border: 1px solid #cbd5e1;
      border-radius: 10px;
      padding: 0 10px;
      font-size: 15px;
      background: #f8fafc;
      color: var(--text);
    }

    textarea {
      height: 84px;
      padding: 8px 10px;
      resize: vertical;
    }

    table {
      width: 100%;
      border-collapse: collapse;
    }

    th, td {
      padding: 11px 9px;
      border-bottom: 1px solid #e5edf7;
      text-align: left;
      font-size: 14px;
      vertical-align: top;
    }

    th {
      background: #eaf2ff;
      color: #24415f;
      font-weight: 1000;
      white-space: nowrap;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 72px;
      min-height: 24px;
      padding: 3px 9px;
      border-radius: 999px;
      background: #eef2ff;
      color: #3730a3;
      font-size: 13px;
      font-weight: 900;
      white-space: nowrap;
    }

    .pill-green { background:#dcfce7; color:#166534; }
    .pill-orange { background:#ffedd5; color:#9a3412; }
    .pill-blue { background:#dbeafe; color:#1d4ed8; }
    .pill-red { background:#fee2e2; color:#991b1b; }
    .pill-purple { background:#ede9fe; color:#5b21b6; }
    .pill-teal { background:#ccfbf1; color:#115e59; }

    .small-muted {
      color: #64748b;
      font-size: 13px;
      line-height: 1.45;
      margin-top: 3px;
    }

    .modal-mask {
      position: fixed;
      inset: 0;
      display: none;
      align-items: center;
      justify-content: center;
      background: rgba(15,23,42,.58);
      z-index: 6000;
      padding: 20px;
    }

    .modal-mask.active {
      display: flex;
    }

    .modal {
      width: min(1180px, 96vw);
      max-height: 90vh;
      overflow: auto;
      background: #fff;
      border-radius: 20px;
      padding: 18px;
      box-shadow: 0 26px 80px rgba(0,0,0,.28);
    }

    .modal-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 14px;
      font-size: 24px;
      font-weight: 1000;
    }

    .form-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 12px;
    }

    .sales-building-picker-row {
      display: grid;
      grid-template-columns: 1fr 76px;
      gap: 8px;
      align-items: center;
    }

    .sales-building-picker-row button {
      width: 76px;
      padding: 0 8px;
      white-space: nowrap;
    }

    .full { grid-column: 1 / -1; }
    .half { grid-column: span 2; }

    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 14px;
    }

    @media (max-width: 1180px) {
      .stats { grid-template-columns: repeat(5, 1fr); }
      .filters { grid-template-columns: repeat(3, 1fr); }
      .form-grid { grid-template-columns: repeat(2, 1fr); }
      .half { grid-column: 1 / -1; }
      .schedule-list { grid-template-columns: repeat(2, 1fr); }
    }

    @media (max-width: 720px) {
      .wrap { padding: 14px; }
      .stats, .filters, .form-grid { grid-template-columns: 1fr; }
      .schedule-list { grid-template-columns: 1fr; }
      .topbar { align-items: flex-start; flex-direction: column; }
      .actions { justify-content: flex-start; }
      table { min-width: 1100px; }
      .panel { overflow-x: auto; }
    }
  
    

  
    

  
    

  
    

  
    /* SHINNAN_SALES_HEADER_BUTTON_RESTORE_LOGO_MOVE_V4 */
    .sales-unified-header {
      display: grid !important;
      grid-template-columns: minmax(0, 1fr) auto !important;
      align-items: center !important;
      gap: 18px !important;
      padding: 26px 32px !important;
      margin-bottom: 18px !important;
      border-radius: 22px !important;
      border: 1px solid rgba(255,255,255,.34) !important;
      background: linear-gradient(135deg, #3f6471 0%, #365ee8 68%, #7c3aed 100%) !important;
      box-shadow: 0 18px 42px rgba(15,23,42,.14) !important;
      color: #fff !important;
    }

    .sales-title-row {
      display: flex !important;
      align-items: center !important;
      gap: 16px !important;
      min-width: 0 !important;
    }

    .sales-title-logo {
      width: 124px !important;
      height: 94px !important;
      object-fit: contain !important;
      flex: 0 0 auto !important;
      margin: 0 !important;
      transform: translateY(-20px) !important;
      filter: drop-shadow(0 5px 9px rgba(0,0,0,.18)) !important;
      position: relative !important;
      z-index: 1 !important;
    }

    .sales-title-text {
      min-width: 0 !important;
      display: grid !important;
      gap: 8px !important;
      position: relative !important;
      z-index: 2 !important;
    }

    .sales-unified-header h1,
    .sales-unified-header .subtitle {
      text-align: left !important;
    }

    .sales-unified-header .actions {
      justify-content: flex-end !important;
      align-items: center !important;
      margin-left: auto !important;
      justify-self: end !important;
      width: auto !important;
    }
    /* SHINNAN_SALES_TEXT_LEFT_BUTTON_RIGHT_V6_END */

  
    

  
    /* SHINNAN_SALES_MOVE_LOGO_ONLY_V8 */
    .sales-title-row {
      display: flex !important;
      align-items: center !important;
      gap: 24px !important;
      column-gap: 24px !important;
      min-width: 0 !important;
    }

    .sales-title-logo {
      width: 124px !important;
      height: 94px !important;
      object-fit: contain !important;
      flex: 0 0 auto !important;
      margin: 0 !important;
      transform: translate(-42px, -20px) !important;
      filter: drop-shadow(0 5px 9px rgba(0,0,0,.18)) !important;
      position: relative !important;
      z-index: 1 !important;
    }

    .sales-title-text {
      transform: none !important;
    }

    .sales-unified-header .actions {
      justify-content: flex-end !important;
      align-items: center !important;
      margin-left: auto !important;
      justify-self: end !important;
    }
    /* SHINNAN_SALES_MOVE_LOGO_ONLY_V8_END */

  
    /* SHINNAN_SALES_TEXT_TO_LOGO_SH_V9 */
    .sales-title-text {
      transform: translateX(-52px) !important;
    }

    .sales-unified-header h1,
    .sales-unified-header .subtitle {
      text-align: left !important;
    }

    .sales-unified-header .actions {
      justify-content: flex-end !important;
      align-items: center !important;
      margin-left: auto !important;
      justify-self: end !important;
    }
    /* SHINNAN_SALES_TEXT_TO_LOGO_SH_V9_END */

  
    /* SHINNAN_SALES_HEADER_COMPACT_V10 */
    .sales-unified-header {
      min-height: 0 !important;
      padding: 14px 24px !important;
      margin-bottom: 14px !important;
      border-radius: 18px !important;
      grid-template-columns: minmax(0, 1fr) auto !important;
      align-items: center !important;
    }

    .sales-title-row {
      gap: 18px !important;
      column-gap: 18px !important;
      align-items: center !important;
    }

    .sales-title-logo {
      width: 101px !important;
      height: 75px !important;
      transform: translate(-18px, 4px) !important;
    }

    .sales-title-text {
      transform: translateX(-52px) !important;
      gap: 0 !important;
    }

    .sales-unified-header h1 {
      font-size: 30px !important;
      line-height: 1.05 !important;
      margin: 0 !important;
      white-space: nowrap !important;
    }

    .sales-unified-header .subtitle {
      display: none !important;
    }

    .sales-unified-header .actions {
      justify-content: flex-end !important;
      align-items: center !important;
      gap: 8px !important;
      margin-left: auto !important;
      justify-self: end !important;
    }

    .sales-unified-header button {
      height: 32px !important;
      min-height: 32px !important;
      border-radius: 10px !important;
      padding: 0 13px !important;
      font-size: 13px !important;
      font-weight: 900 !important;
      line-height: 1 !important;
    }
    /* SHINNAN_SALES_HEADER_COMPACT_V10_END */

  </style>
<style id="sales_stats_filter_bar_v1">
  /* 統計區改成一欄式快速篩選列 */

  .stats {
    display: flex !important;
    flex-wrap: wrap !important;
    align-items: center !important;
    gap: 8px !important;
    margin: 0 0 10px 0 !important;
    padding: 10px 12px !important;
    border: 1px solid #d7e1ef !important;
    border-radius: 18px !important;
    background: #ffffff !important;
    box-shadow: 0 10px 26px rgba(15, 23, 42, 0.06) !important;
  }

  .stats::before {
    content: "快速篩選";
    display: inline-flex;
    align-items: center;
    height: 30px;
    margin-right: 2px;
    padding: 0 10px;
    border-radius: 999px;
    background: #eaf2ff;
    color: #24415f;
    font-size: 13px;
    font-weight: 1000;
    white-space: nowrap;
  }

  .stat-card {
    min-height: 30px !important;
    height: 30px !important;
    padding: 0 10px !important;
    border-radius: 999px !important;
    border: 1px solid #dbe7f5 !important;
    background: #f8fafc !important;
    box-shadow: none !important;
    display: inline-flex !important;
    flex-direction: row !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    cursor: pointer !important;
    user-select: none !important;
    transition: transform .12s ease, border-color .12s ease, background .12s ease;
    width: auto !important;
  }

  .stat-card:hover {
    transform: translateY(-1px);
    border-color: #365ee8 !important;
    background: #eef4ff !important;
  }

  .stat-card.active {
    border-color: #365ee8 !important;
    background: #365ee8 !important;
    color: #ffffff !important;
  }

  .stat-card.active .stat-label,
  .stat-card.active .stat-number {
    color: #ffffff !important;
  }

  .stat-label {
    color: #475569 !important;
    font-size: 13px !important;
    font-weight: 900 !important;
    line-height: 1 !important;
    white-space: nowrap !important;
  }

  .stat-number {
    margin: 0 !important;
    color: #102348 !important;
    font-size: 16px !important;
    font-weight: 1000 !important;
    line-height: 1 !important;
  }

  .stat-card::after {
    content: "筆";
    color: inherit;
    opacity: .85;
    font-size: 12px;
    font-weight: 900;
  }

  .sales-filter-reset {
    height: 30px;
    border: 1px solid #cbd5e1;
    border-radius: 999px;
    background: #ffffff;
    color: #334155;
    padding: 0 12px;
    font-size: 13px;
    font-weight: 1000;
    cursor: pointer;
  }

  .sales-filter-reset:hover {
    background: #f1f5f9;
  }

  .schedule-panel {
    margin-top: 0 !important;
  }

  @media (max-width: 760px) {
    .stats {
      align-items: stretch !important;
    }

    .stat-card,
    .sales-filter-reset {
      width: 100% !important;
      justify-content: space-between !important;
    }

    .stats::before {
      width: 100%;
      justify-content: center;
    }
  }
</style>
<style id="sales_today_memo_layout_v3">
  /* 今日行程 memo v3：業務欄往左，加入欄位名稱 */

  .schedule-panel {
    padding: 12px 14px !important;
    margin-bottom: 10px !important;
  }

  .schedule-list {
    display: block !important;
  }

  .sales-memo-header,
  .schedule-card {
    display: grid !important;
    grid-template-columns: 80px 210px 90px 260px minmax(520px, 1fr) !important;
    align-items: center !important;
    gap: 10px !important;
  }

  .sales-memo-header {
    margin-bottom: 6px;
    padding: 0 12px;
    color: #64748b;
    font-size: 12px;
    font-weight: 1000;
  }

  .schedule-card {
    min-height: 0 !important;
    padding: 8px 12px !important;
    margin-bottom: 7px !important;
    border-radius: 10px !important;
    box-shadow: none !important;
    border: 1px solid #dbe7f5 !important;
    background: #ffffff !important;
  }

  .schedule-card.important {
    border-color: #f59e0b !important;
    background: #fffaf0 !important;
  }

  .sales-memo-tag {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 64px;
    height: 25px;
    border-radius: 999px;
    padding: 0 8px;
    background: #dbeafe;
    color: #1d4ed8;
    font-size: 13px;
    font-weight: 1000;
  }

  .sales-memo-tag.important {
    background: #fef3c7;
    color: #92400e;
  }

  .sales-memo-building {
    font-size: 17px;
    font-weight: 1000;
    color: #102348;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .sales-memo-owner {
    font-size: 16px;
    font-weight: 1000;
    color: #1e293b;
    white-space: nowrap;
  }

  .sales-memo-contact {
    font-size: 15px;
    font-weight: 900;
    color: #475569;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .sales-memo-action {
    font-size: 15px;
    font-weight: 1000;
    color: #334155;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .schedule-empty {
    padding: 10px 12px !important;
    font-size: 14px !important;
  }

  @media (max-width: 1280px) {
    .sales-memo-header,
    .schedule-card {
      grid-template-columns: 70px 180px 82px 220px minmax(340px, 1fr) !important;
      gap: 8px !important;
    }
  }

  @media (max-width: 900px) {
    .sales-memo-header {
      display: none !important;
    }

    .schedule-card {
      grid-template-columns: 72px 1fr !important;
      gap: 6px 10px !important;
    }

    .sales-memo-owner,
    .sales-memo-contact,
    .sales-memo-action {
      grid-column: 2 / -1;
      white-space: normal;
    }
  }
</style>


<style id="sales_clean_join_api_list_v1">
  /* 業務列表清理：以 JOIN API 回傳資料為準 */

  /* 備註欄已移到下一列，表頭與原本最後一欄隱藏 */
  table thead tr th:last-child {
    display: none !important;
  }

  #sales_rows tr:not(.sales-note-row) td:last-child {
    display: none !important;
  }

  #sales_rows tr.sales-note-row td {
    padding: 0 7px 8px 7px !important;
    border-bottom: 1px solid #e5edf7 !important;
    background: #ffffff !important;
  }

  .sales-note-box {
    margin: 0 !important;
    padding: 7px 10px !important;
    border-radius: 10px !important;
    background: #f8fafc !important;
    border: 1px solid #dbe7f5 !important;
    color: #334155 !important;
    font-size: 13px !important;
    line-height: 1.5 !important;
    white-space: normal !important;
  }

  .sales-note-label {
    display: inline-flex !important;
    align-items: center !important;
    height: 22px !important;
    margin-right: 8px !important;
    padding: 0 8px !important;
    border-radius: 999px !important;
    background: #eaf2ff !important;
    color: #24415f !important;
    font-size: 12px !important;
    font-weight: 1000 !important;
  }

  .sales-note-content {
    font-weight: 800 !important;
  }

  .sales-note-empty {
    color: #94a3b8 !important;
  }

  .sales-manager-link {
    border: 0;
    background: transparent;
    padding: 0;
    color: #1d4ed8;
    font-size: inherit;
    font-weight: 1000;
    cursor: pointer;
    text-align: left;
  }

  .sales-manager-link:hover {
    text-decoration: underline;
  }
</style>


<style id="sales_force_manager_simple_v1">
  /* 業務列表：總幹事欄強制只保留姓名與電話 */

  #sales_rows tr:not(.sales-note-row) td:nth-child(2) {
    min-width: 120px !important;
  }

  #sales_rows tr:not(.sales-note-row) td:nth-child(2) .small-muted:nth-of-type(n+2) {
    display: none !important;
  }

  #sales_rows tr:not(.sales-note-row) td:nth-child(2) .sales-manager-extra {
    display: none !important;
  }

  #sales_rows tr:not(.sales-note-row) td:nth-child(2) {
    line-height: 1.55 !important;
  }

  #sales_rows tr:not(.sales-note-row) td:nth-child(2) button,
  #sales_rows tr:not(.sales-note-row) td:nth-child(2) b {
    display: inline-block !important;
    margin-bottom: 6px !important;
  }
</style>

</head>
<body>
  <div class="wrap">
    <div class="topbar sales-unified-header">
      <div class="sales-title-row">
        <img class="sales-title-logo" src="/erp-static/shinnan_home_logo.png" alt="訊南 Logo">
        <div class="sales-title-text">
          <h1>業務管理系統</h1>
          
        </div>
      </div>
      <div class="actions">
        <button id="sales_btn_home" class="btn-home" type="button">返回首頁</button>
        <button id="sales_btn_back" class="btn-gray" type="button">返回上一頁</button>
        <button id="sales_btn_buildings" class="btn-blue" type="button">大樓名錄</button>
        <button id="sales_btn_managers" class="btn-purple" type="button">總幹事名錄</button>
        <button id="sales_btn_create" class="btn-green" type="button">新增案件</button>
      </div>
    </div>

    <div class="stats">
      <div class="stat-card"><div class="stat-label">新大樓開發中</div><div class="stat-number" id="stat_developing">0</div></div>
      <div class="stat-card"><div class="stat-label">待拜訪大樓</div><div class="stat-number" id="stat_visit">0</div></div>
      <div class="stat-card"><div class="stat-label">合約即將到期</div><div class="stat-number" id="stat_contract_due">0</div></div>
      <div class="stat-card"><div class="stat-label">待處理事件</div><div class="stat-number" id="stat_events">0</div></div>
      <div class="stat-card"><div class="stat-label">待執行回饋</div><div class="stat-number" id="stat_feedback">0</div></div>
      <div class="stat-card"><div class="stat-label">本月拜訪</div><div class="stat-number" id="stat_month_visit">0</div></div>
    </div>

    <div class="panel schedule-panel">
      <div class="schedule-head">
        <div>
          <div class="schedule-title">今日行程</div>
          <div class="schedule-sub">重要行程會固定排在最上方；有拜訪日期或事件日期的案件也會顯示。</div>
        </div>
        <button class="btn-green" type="button" onclick="openCreateSalesModal()">新增行程</button>
      </div>
      <div id="today_schedule_rows" class="schedule-list">
        <div class="schedule-empty">目前沒有今日行程。</div>
      </div>
    </div>

    <div class="panel">
      <div class="filters">
        <div>
          <label>區域</label>
          <select id="filter_area">
            <option value="全部">全部</option>
            <option>東區</option><option>北區</option><option>北台南</option><option>仁德</option>
            <option>永康</option><option>安平</option><option>南高</option><option>北高</option>
          </select>
        </div>
        <div>
          <label>業務類型</label>
          <select id="filter_business_type">
            <option value="全部">全部</option>
            <option>新大樓開發</option>
            <option>舊大樓拜訪</option>
            <option>合約續約</option>
            <option>管理室拜訪</option>
            <option>業務事件</option>
            <option>回饋處理</option>
          </select>
        </div>
        <div>
          <label>目前狀態</label>
          <select id="filter_status">
            <option value="全部">全部</option>
            <option>未接觸</option>
            <option>已接觸</option>
            <option>已拜訪</option>
            <option>已提案</option>
            <option>等管委會</option>
            <option>談約中</option>
            <option>已簽約</option>
            <option>例行維護</option>
            <option>暫緩</option>
            <option>失敗</option>
          </select>
        </div>
        <div>
          <label>合約狀態</label>
          <select id="filter_contract_status">
            <option value="全部">全部</option>
            <option>未簽</option>
            <option>洽談中</option>
            <option>已簽</option>
            <option>即將到期</option>
            <option>已到期</option>
            <option>已續約</option>
            <option>終止</option>
          </select>
        </div>
        <div>
          <label>負責業務</label>
          <select id="filter_owner">
            <option value="全部">全部</option>
            <option>吳文化</option>
            <option>業務一</option>
            <option>業務二</option>
            <option>業務三</option>
          </select>
        </div>
        <div>
          <label>關鍵字</label>
          <input id="filter_keyword" placeholder="大樓、管理公司、窗口、事件">
        </div>
      </div>
    </div>

    <div class="panel">
      <table>
        <thead>
          <tr>
            <th>大樓／管理室</th>
            <th>總幹事</th>
            <th>會議時間</th>
            <th>區域</th>
            <th>業務類型</th>
            <th>目前狀態</th>
            <th>合約</th>
            <th>業務事件</th>
            <th>回饋項目</th>
            <th>下次拜訪</th>
            <th>負責業務</th>
            <th>備註</th>
          </tr>
        </thead>
        <tbody id="sales_rows">
          <tr><td colspan="12">目前沒有資料。</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <div id="sales_modal" class="modal-mask">
    <div class="modal">
      <div class="modal-title">
        <span>新增案件</span>
        <button class="btn-gray" type="button" onclick="closeCreateSalesModal()">關閉</button>
      </div>

      <div class="form-grid">
        <div class="full">
          <label>行程設定</label>
          <label class="check-row">
            <input id="new_important_schedule" type="checkbox">
            重要行程，顯示在今日行程最上方
          </label>
        </div>
        <div>
          <label>大樓名稱</label>
          <div class="sales-building-picker-row">
            <input id="new_building_name" placeholder="尚未選擇大樓">
            <button id="sales_choose_building_button" class="btn-purple" type="button">大樓</button>
          </div>
        </div>
        <div>
          <label>區域</label>
          <select id="new_area">
            <option>東區</option><option>北區</option><option>北台南</option><option>仁德</option>
            <option>永康</option><option>安平</option><option>南高</option><option>北高</option>
          </select>
        </div>
        <div>
          <label>管理公司</label>
          <input id="new_management_company">
        </div>
        <div>
          <label>管理室電話</label>
          <input id="new_management_phone">
        </div>

        <div>
          <label>總幹事姓名</label>
          <input id="new_manager_name" placeholder="總幹事姓名">
        </div>
        <div>
          <label>總幹事電話</label>
          <input id="new_manager_phone" placeholder="總幹事電話">
        </div>
        <div>
          <label>總幹事年齡</label>
          <input id="new_manager_age" type="number" min="0" placeholder="年齡">
        </div>
        <div>
          <label>總幹事資歷</label>
          <input id="new_manager_experience" placeholder="例如 5 年">
        </div>
        <div>
          <label>總幹事興趣</label>
          <input id="new_manager_interest" placeholder="例如 茶、釣魚、運動">
        </div>
        <div>
          <label>可拜訪時段</label>
          <input id="new_visit_time" placeholder="例如 平日 10:00-17:00">
        </div>
        <div>
          <label>委員會時間</label>
          <input id="new_committee_time" placeholder="例如 每月第 2 週三 19:00">
        </div>
        <div>
          <label>住戶大會時間</label>
          <input id="new_resident_meeting_time" placeholder="例如 每年 6 月">
        </div>
        <div>
          <label>業務類型</label>
          <select id="new_business_type">
            <option>新大樓開發</option>
            <option>舊大樓拜訪</option>
            <option>合約續約</option>
            <option>管理室拜訪</option>
            <option>業務事件</option>
            <option>回饋處理</option>
          </select>
        </div>
        <div>
          <label>目前狀態</label>
          <select id="new_status">
            <option>未接觸</option>
            <option>已接觸</option>
            <option>已拜訪</option>
            <option>已提案</option>
            <option>等管委會</option>
            <option>談約中</option>
            <option>已簽約</option>
            <option>例行維護</option>
            <option>暫緩</option>
            <option>失敗</option>
          </select>
        </div>

        <div>
          <label>合約狀態</label>
          <select id="new_contract_status">
            <option>未簽</option>
            <option>洽談中</option>
            <option>已簽</option>
            <option>即將到期</option>
            <option>已到期</option>
            <option>已續約</option>
            <option>終止</option>
          </select>
        </div>
        <div>
          <label>合約到期日</label>
          <input id="new_contract_end_date" type="date">
        </div>
        <div>
          <label>回饋項目</label>
          <select id="new_feedback_type">
            <option>無</option>
            <option>現金回饋</option>
            <option>管理費補助</option>
            <option>活動贊助</option>
            <option>設備贈送</option>
            <option>網路優惠</option>
            <option>其他</option>
          </select>
        </div>
        <div>
          <label>回饋狀態</label>
          <select id="new_feedback_status">
            <option>無</option>
            <option>待確認</option>
            <option>已核准</option>
            <option>已執行</option>
            <option>已結清</option>
            <option>暫停</option>
          </select>
        </div>

        <div>
          <label>事件類型</label>
          <select id="new_event_type">
            <option>無</option>
            <option>管委會要求</option>
            <option>住戶反應</option>
            <option>競爭業者進場</option>
            <option>管理室要求</option>
            <option>社區公告協調</option>
            <option>續約爭議</option>
            <option>設備室協調</option>
            <option>其他</option>
          </select>
        </div>
        <div>
          <label>事件狀態</label>
          <select id="new_event_status">
            <option>無</option>
            <option>待處理</option>
            <option>處理中</option>
            <option>已回覆</option>
            <option>已完成</option>
            <option>暫緩</option>
          </select>
        </div>
        <div>
          <label>事件安排日期</label>
          <input id="new_event_schedule_date" type="date">
        </div>
        <div>
          <label>下次拜訪日期</label>
          <input id="new_next_visit" type="date">
        </div>
        <div>
          <label>負責業務</label>
          <select id="new_owner">
            <option>吳文化</option>
            <option>業務一</option>
            <option>業務二</option>
            <option>業務三</option>
          </select>
        </div>

        <div class="half">
          <label>管理室資訊／注意事項</label>
          <textarea id="new_management_note" placeholder="例如：可拜訪時段、窗口習慣、禁忌事項、是否需主管出面"></textarea>
        </div>
        <div class="half">
          <label>業務紀錄／拜訪結果</label>
          <textarea id="new_business_note" placeholder="例如：拜訪內容、管委會反應、下一步、需追蹤事項"></textarea>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-gray" type="button" onclick="closeCreateSalesModal()">取消</button>
        <button class="btn-green" type="button" onclick="createSalesLead()">建立案件</button>
      </div>
    </div>
  </div>

  <script>
    const STORAGE_KEY = "shinnan_building_business_records_v1";
    var businessRecords = [];

    function byId(id) {
      return document.getElementById(id);
    }

    function escapeHtml(value) {
      return String(value || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function loadBusinessRecords() {
      try {
        const res = await fetch("/api/app/sales/business-records?ts=" + Date.now(), { cache: "no-store" });

        if (!res.ok) {
          console.error("業務資料庫 API 讀取失敗", res.status);
          businessRecords = [];
          return;
        }

        const data = await res.json();

        if (!Array.isArray(data)) {
          console.error("業務資料庫 API 格式錯誤", data);
          businessRecords = [];
          return;
        }

        businessRecords = data;
        console.log("sales main flow loaded from database:", businessRecords.length);
      } catch (e) {
        console.error("loadBusinessRecords database failed", e);
        businessRecords = [];
      }
    }

    function saveBusinessRecords() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(businessRecords));
    }

    function openCreateSalesModal() {
      byId("sales_modal").classList.add("active");
    }

    function closeCreateSalesModal() {
      byId("sales_modal").classList.remove("active");
    }

    function goBuildingsFromSales() {
      localStorage.setItem("xunnan_building_back_return", "/admin/sales");
      window.location.href = "/admin/buildings?caller=sales";
    }

    function goChooseBuildingFromSalesForm() {
      localStorage.setItem("xunnan_building_pick_return", "/admin/sales?open_sales_modal=1&from_building_pick=1&caller=sales");
      window.location.href = "/admin/buildings?select=1&caller=sales";
    }

    function applyPickedBuildingToSalesForm() {
      const params = new URLSearchParams(window.location.search);
      const shouldOpen =
        params.get("open_sales_modal") === "1" ||
        params.get("from_building_pick") === "1" ||
        params.get("caller") === "sales";

      const raw =
        localStorage.getItem("xunnan_building_pick_result") ||
        localStorage.getItem("xunnan_selected_building");

      if (!raw) {
        if (shouldOpen) {
          setTimeout(function () {
            openCreateSalesModal();
          }, 120);
          window.history.replaceState({}, document.title, "/admin/sales");
        }
        return;
      }

      try {
        const building = JSON.parse(raw);

        if (byId("new_building_name")) {
          byId("new_building_name").value = building.name || "";
        }

        if (byId("new_area") && building.area) {
          byId("new_area").value = building.area;
        }

        if (byId("new_management_company") && building.management_company) {
          byId("new_management_company").value = building.management_company;
        }

        if (byId("new_management_note") && building.raw_address) {
          const oldNote = byId("new_management_note").value.trim();
          const addressLine = "大樓地址：" + building.raw_address;
          byId("new_management_note").value = oldNote ? (oldNote + "\\n" + addressLine) : addressLine;
        }

        localStorage.removeItem("xunnan_building_pick_result");
        localStorage.removeItem("xunnan_selected_building");
        localStorage.removeItem("xunnan_selected_building_no");
        localStorage.removeItem("xunnan_selected_building_name");
        localStorage.removeItem("xunnan_selected_building_area");
        localStorage.removeItem("xunnan_selected_building_raw_address");
        localStorage.removeItem("xunnan_selected_building_address");
        localStorage.removeItem("xunnan_building_pick_return");

        setTimeout(function () {
          openCreateSalesModal();
        }, 120);

        if (shouldOpen) {
          window.history.replaceState({}, document.title, "/admin/sales");
        }
      } catch (err) {
        console.warn("業務系統讀取選擇大樓失敗", err);
      }
    }

    function createSalesLead() {
      const buildingName = byId("new_building_name").value.trim();

      if (!buildingName) {
        alert("請輸入大樓名稱");
        return;
      }

      const item = {
        id: Date.now(),
        building_name: buildingName,
        area: byId("new_area").value,
        management_company: byId("new_management_company").value.trim(),
        management_phone: byId("new_management_phone").value.trim(),
        manager_name: byId("new_manager_name").value.trim(),
        manager_phone: byId("new_manager_phone").value.trim(),
        manager_age: byId("new_manager_age").value.trim(),
        manager_experience: byId("new_manager_experience").value.trim(),
        manager_interest: byId("new_manager_interest").value.trim(),
        visit_time: byId("new_visit_time").value.trim(),
        committee_time: byId("new_committee_time").value.trim(),
        resident_meeting_time: byId("new_resident_meeting_time").value.trim(),
        business_type: byId("new_business_type").value,
        status: byId("new_status").value,
        contract_status: byId("new_contract_status").value,
        contract_end_date: byId("new_contract_end_date").value,
        feedback_type: byId("new_feedback_type").value,
        feedback_status: byId("new_feedback_status").value,
        event_type: byId("new_event_type").value,
        event_status: byId("new_event_status").value,
        event_schedule_date: byId("new_event_schedule_date").value,
        important_schedule: byId("new_important_schedule").checked,
        next_visit: byId("new_next_visit").value,
        owner: byId("new_owner").value,
        management_note: byId("new_management_note").value.trim(),
        business_note: byId("new_business_note").value.trim(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      businessRecords.unshift(item);
      saveBusinessRecords();
      closeCreateSalesModal();
      clearCreateForm();
      renderBusinessRecords();
    }

    function clearCreateForm() {
      [
        "new_building_name",
        "new_management_company",
        "new_management_phone",
        "new_manager_name",
        "new_manager_phone",
        "new_manager_age",
        "new_manager_experience",
        "new_manager_interest",
        "new_visit_time",
        "new_committee_time",
        "new_resident_meeting_time",
        "new_contract_end_date",
        "new_event_schedule_date",
        "new_next_visit",
        "new_management_note",
        "new_business_note"
      ].forEach(function (id) {
        byId(id).value = "";
      });

      byId("new_business_type").value = "新大樓開發";
      byId("new_status").value = "未接觸";
      byId("new_contract_status").value = "未簽";
      byId("new_feedback_type").value = "無";
      byId("new_feedback_status").value = "無";
      byId("new_event_type").value = "無";
      byId("new_event_status").value = "無";
      byId("new_important_schedule").checked = false;
    }

    function statusClass(status) {
      if (status === "已簽約" || status === "已簽") return "pill pill-green";
      if (status === "談約中" || status === "已提案" || status === "等管委會") return "pill pill-orange";
      if (status === "失敗" || status === "終止") return "pill pill-red";
      if (status === "例行維護") return "pill pill-teal";
      return "pill pill-blue";
    }

    function contractClass(status) {
      if (status === "已簽" || status === "已續約") return "pill pill-green";
      if (status === "即將到期" || status === "已到期") return "pill pill-orange";
      if (status === "終止") return "pill pill-red";
      return "pill pill-purple";
    }

    function feedbackText(item) {
      if (!item.feedback_type || item.feedback_type === "無") return "-";
      return item.feedback_type + "｜" + (item.feedback_status || "未設定");
    }

    function eventText(item) {
      if (!item.event_type || item.event_type === "無") return "-";
      return item.event_type + "｜" + (item.event_status || "未設定");
    }

    function isContractDueSoon(item) {
      if (!item.contract_end_date) return false;
      if (!["已簽", "即將到期", "已到期"].includes(item.contract_status)) return false;

      const today = new Date();
      const end = new Date(item.contract_end_date + "T00:00:00");
      if (isNaN(end.getTime())) return false;

      const diffDays = Math.ceil((end - today) / 86400000);
      return diffDays <= 60;
    }

    function isThisMonth(dateText) {
      if (!dateText) return false;
      const now = new Date();
      const ym = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0");
      return String(dateText).startsWith(ym);
    }

    function filteredRecords() {
      const area = byId("filter_area").value;
      const businessType = byId("filter_business_type").value;
      const status = byId("filter_status").value;
      const contractStatus = byId("filter_contract_status").value;
      const owner = byId("filter_owner").value;
      const keyword = byId("filter_keyword").value.trim().toLowerCase();

      return businessRecords.filter(function (item) {
        if (area !== "全部" && item.area !== area) return false;
        if (businessType !== "全部" && item.business_type !== businessType) return false;
        if (status !== "全部" && item.status !== status) return false;
        if (contractStatus !== "全部" && item.contract_status !== contractStatus) return false;
        if (owner !== "全部" && item.owner !== owner) return false;

        if (keyword) {
          const hay = [
            item.building_name,
            item.management_company,
            item.management_phone,
            item.manager_name,
            item.manager_phone,
            item.manager_age,
            item.manager_experience,
            item.manager_interest,
            item.committee_time,
            item.resident_meeting_time,
            item.business_type,
            item.status,
            item.contract_status,
            item.feedback_type,
            item.feedback_status,
            item.event_type,
            item.event_status,
            item.event_schedule_date,
            item.important_schedule ? "重要行程" : "",
            item.management_note,
            item.business_note
          ].join(" ").toLowerCase();

          if (!hay.includes(keyword)) return false;
        }

        return true;
      });
    }

    function updateStats() {
      byId("stat_developing").textContent = businessRecords.filter(function (item) {
        return item.business_type === "新大樓開發" && !["已簽約", "失敗", "暫緩"].includes(item.status);
      }).length;

      byId("stat_visit").textContent = businessRecords.filter(function (item) {
        return item.next_visit;
      }).length;

      byId("stat_contract_due").textContent = businessRecords.filter(isContractDueSoon).length;

      byId("stat_events").textContent = businessRecords.filter(function (item) {
        return item.event_type !== "無" && ["待處理", "處理中"].includes(item.event_status);
      }).length;

      byId("stat_feedback").textContent = businessRecords.filter(function (item) {
        return item.feedback_type !== "無" && ["待確認", "已核准"].includes(item.feedback_status);
      }).length;

      byId("stat_month_visit").textContent = businessRecords.filter(function (item) {
        return isThisMonth(item.next_visit);
      }).length;
    }

    function localDateText() {
      const now = new Date();
      return now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0") + "-" + String(now.getDate()).padStart(2, "0");
    }

    function hasActiveEvent(item) {
      if (!item.event_type || item.event_type === "無") return false;
      return ["待處理", "處理中", "已回覆"].includes(item.event_status || "");
    }

    function scheduleReason(item, today) {
      const reasons = [];

      if (item.important_schedule) {
        reasons.push("重要");
      }

      if (item.next_visit === today) {
        reasons.push("今日拜訪");
      } else if (item.next_visit) {
        reasons.push("拜訪：" + item.next_visit);
      }

      if (item.event_schedule_date === today) {
        reasons.push("今日事件");
      } else if (item.event_schedule_date) {
        reasons.push("事件：" + item.event_schedule_date);
      } else if (hasActiveEvent(item)) {
        reasons.push("待處理事件");
      }

      return reasons.join("｜") || "行程";
    }

    function renderTodaySchedule() {
      const box = byId("today_schedule_rows");
      if (!box) return;

      const today = localDateText();

      const items = businessRecords.filter(function (item) {
        return Boolean(item.important_schedule)
          || item.next_visit === today
          || item.event_schedule_date === today
          || hasActiveEvent(item);
      }).sort(function (a, b) {
        const ai = a.important_schedule ? 0 : 1;
        const bi = b.important_schedule ? 0 : 1;
        if (ai !== bi) return ai - bi;

        const ad = a.next_visit || a.event_schedule_date || "9999-12-31";
        const bd = b.next_visit || b.event_schedule_date || "9999-12-31";
        return String(ad).localeCompare(String(bd));
      });

      if (!items.length) {
        box.innerHTML = '<div class="schedule-empty">目前沒有今日行程。</div>';
        return;
      }

      box.innerHTML = items.map(function (item) {
        const cls = item.important_schedule ? "schedule-card important" : "schedule-card";
        return `
          <div class="${cls}">
            <div class="schedule-card-title">${escapeHtml(item.building_name)}</div>
            <div class="schedule-card-line">${escapeHtml(scheduleReason(item, today))}</div>
            <div class="schedule-card-line">區域：${escapeHtml(item.area || "-")}｜負責：${escapeHtml(item.owner || "-")}</div>
            <div class="schedule-card-line">總幹事：${escapeHtml(item.manager_name || "-")}｜${escapeHtml(item.manager_phone || "-")}</div>
            <div class="schedule-card-line">事件：${escapeHtml(eventText(item))}</div>
          </div>
        `;
      }).join("");
    }

    function renderBusinessRecords() {
      const rows = byId("sales_rows");
      const data = filteredRecords();

      updateStats();
      renderTodaySchedule();

      if (!data.length) {
        rows.innerHTML = "<tr><td colspan='12'>目前沒有符合條件的大樓業務紀錄。</td></tr>";
        return;
      }

      rows.innerHTML = data.map(function (item) {
        return `
          <tr>
            <td>
              <b>${escapeHtml(item.building_name)}</b>
              <div class="small-muted">${escapeHtml(item.management_company || "未填管理公司")}</div>
              <div class="small-muted">管理室：${escapeHtml(item.management_phone || "未填電話")}</div>
            </td>
            <td>
              <button class="sales-manager-link" type="button" onclick="openSalesManagerModalByName('${escapeHtml(item.manager_name || "")}')">${escapeHtml(item.manager_name || "未填")}</button>
              <div class="small-muted">${escapeHtml(item.manager_phone || "未填電話")}</div>
              <div class="small-muted">${escapeHtml(item.manager_age ? item.manager_age + " 歲" : "")}${item.manager_experience ? "｜資歷：" + escapeHtml(item.manager_experience) : ""}</div>
            </td>
            <td>
              <div>委員會：${escapeHtml(item.committee_time || "-")}</div>
              <div class="small-muted">住戶大會：${escapeHtml(item.resident_meeting_time || "-")}</div>
            </td>
            <td>${escapeHtml(item.area)}</td>
            <td><span class="pill pill-teal">${escapeHtml(item.business_type)}</span></td>
            <td><span class="${statusClass(item.status)}">${escapeHtml(item.status)}</span></td>
            <td>
              <span class="${contractClass(item.contract_status)}">${escapeHtml(item.contract_status)}</span>
              <div class="small-muted">${escapeHtml(item.contract_end_date || "-")}</div>
            </td>
            <td>${escapeHtml(eventText(item))}</td>
            <td>${escapeHtml(feedbackText(item))}</td>
            <td>${escapeHtml(item.next_visit || "-")}</td>
            <td>${escapeHtml(item.owner)}</td>
            <td>
              <div>${escapeHtml(item.business_note || "-")}</div>
              <div class="small-muted">${escapeHtml(item.management_note || "")}</div>
            </td>
          </tr>
        `;
      }).join("");
    }

    ["filter_area", "filter_business_type", "filter_status", "filter_contract_status", "filter_owner", "filter_keyword"].forEach(function (id) {
      byId(id).addEventListener("input", renderBusinessRecords);
      byId(id).addEventListener("change", renderBusinessRecords);
    });

    async function bootSalesPage() {
      await loadBusinessRecords();
      renderBusinessRecords();
      applyPickedBuildingToSalesForm();

      const debug = document.getElementById("sales_db_debug_count");
      if (debug) {
        debug.textContent = "資料庫已載入 " + businessRecords.length + " 筆業務資料";
      }
    }

    bootSalesPage();
  </script>

  <script id="sales_button_recovery_v1">
    (function () {
      function go(url) {
        window.location.href = url;
      }

      function safeBack() {
        if (document.referrer) {
          try {
            var ref = new URL(document.referrer);
            if (ref.pathname && ref.pathname !== window.location.pathname) {
              history.back();
              return;
            }
          } catch (err) {
            history.back();
            return;
          }
        }
        window.location.href = "/admin";
      }

      function openSalesCreateModalSafe() {
        var modal = document.getElementById("sales_modal");
        if (modal) {
          modal.classList.add("active");
          return;
        }

        if (typeof window.openCreateSalesModal === "function") {
          window.openCreateSalesModal();
          return;
        }

        alert("新增業務案件視窗尚未載入，請重新整理頁面。");
      }

      function bindSalesButtons() {
        var home = document.getElementById("sales_btn_home");
        var back = document.getElementById("sales_btn_back");
        var buildings = document.getElementById("sales_btn_buildings");
        var managers = document.getElementById("sales_btn_managers");
        var create = document.getElementById("sales_btn_create");

        if (home) {
          home.onclick = function () {
            go("/");
          };
        }

        if (back) {
          back.onclick = function () {
            safeBack();
          };
        }

        if (buildings) {
          buildings.onclick = function () {
            localStorage.setItem("xunnan_building_back_return", "/admin/sales");
            go("/admin/buildings?caller=sales");
          };
        }

        if (managers) {
          managers.onclick = function () {
            go("/admin/sales/managers");
          };
        }

        if (create) {
          create.onclick = function () {
            openSalesCreateModalSafe();
          };
        }
      }

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindSalesButtons);
      } else {
        bindSalesButtons();
      }

      setTimeout(bindSalesButtons, 300);
    })();
  </script>


  <script id="sales_building_picker_recovery_v1">
    (function () {
      function openSalesBuildingPicker() {
        localStorage.setItem(
          "xunnan_building_pick_return",
          "/admin/sales?open_sales_modal=1&from_building_pick=1&caller=sales"
        );
        localStorage.setItem("xunnan_building_back_return", "/admin/sales");
        window.location.href = "/admin/buildings?select=1&caller=sales";
      }

      window.goChooseBuildingFromSalesForm = openSalesBuildingPicker;

      function bindSalesBuildingButton() {
        var btn = document.getElementById("sales_choose_building_button");
        if (!btn) return;

        btn.onclick = function (event) {
          event.preventDefault();
          openSalesBuildingPicker();
        };
      }

      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", bindSalesBuildingButton);
      } else {
        bindSalesBuildingButton();
      }

      setTimeout(bindSalesBuildingButton, 300);
      setTimeout(bindSalesBuildingButton, 800);
    })();
  </script>
<script id="sales_stats_filter_bar_v1">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  let quickMode = "all";

  const modeMap = [
    { id: "stat_developing", mode: "developing" },
    { id: "stat_visit", mode: "visit" },
    { id: "stat_contract_due", mode: "contract_due" },
    { id: "stat_events", mode: "events" },
    { id: "stat_feedback", mode: "feedback" },
    { id: "stat_month_visit", mode: "month_visit" }
  ];

  function clearNormalFilters() {
    const ids = [
      "filter_area",
      "filter_business_type",
      "filter_status",
      "filter_contract_status",
      "filter_owner"
    ];

    ids.forEach(function (id) {
      const el = document.getElementById(id);
      if (el) el.value = "全部";
    });

    const keyword = document.getElementById("filter_keyword");
    if (keyword) keyword.value = "";
  }

  function updateActiveStatCards() {
    modeMap.forEach(function (item) {
      const number = document.getElementById(item.id);
      const card = number ? number.closest(".stat-card") : null;
      if (!card) return;

      if (quickMode === item.mode) {
        card.classList.add("active");
      } else {
        card.classList.remove("active");
      }
    });
  }

  function isContractDueSoonLocal(item) {
    if (!item || !item.contract_end_date) return false;
    if (!["已簽", "即將到期", "已到期"].includes(item.contract_status)) return false;

    const today = new Date();
    const end = new Date(item.contract_end_date + "T00:00:00");
    if (isNaN(end.getTime())) return false;

    const diffDays = Math.ceil((end - today) / 86400000);
    return diffDays <= 60;
  }

  function isThisMonthLocal(dateText) {
    if (!dateText) return false;

    const now = new Date();
    const ym = now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0");

    return String(dateText).startsWith(ym);
  }

  function matchQuickMode(item) {
    if (quickMode === "all") return true;

    if (quickMode === "developing") {
      return item.business_type === "新大樓開發" && !["已簽約", "失敗", "暫緩"].includes(item.status);
    }

    if (quickMode === "visit") {
      return Boolean(item.next_visit);
    }

    if (quickMode === "contract_due") {
      return isContractDueSoonLocal(item);
    }

    if (quickMode === "events") {
      return item.event_type !== "無" && ["待處理", "處理中"].includes(item.event_status);
    }

    if (quickMode === "feedback") {
      return item.feedback_type !== "無" && ["待確認", "已核准"].includes(item.feedback_status);
    }

    if (quickMode === "month_visit") {
      return isThisMonthLocal(item.next_visit);
    }

    return true;
  }

  function installQuickFilterWrapper() {
    if (window.__salesQuickFilterInstalled === true) return;
    if (typeof filteredRecords !== "function") return;

    window.__salesOriginalFilteredRecords = filteredRecords;

    filteredRecords = function () {
      const base = window.__salesOriginalFilteredRecords();
      return base.filter(matchQuickMode);
    };

    window.__salesQuickFilterInstalled = true;
  }

  function bindStatClicks() {
    installQuickFilterWrapper();

    modeMap.forEach(function (item) {
      const number = document.getElementById(item.id);
      const card = number ? number.closest(".stat-card") : null;
      if (!card) return;

      card.title = "點擊篩選：" + String(card.textContent || "").trim();

      card.onclick = function () {
        clearNormalFilters();
        quickMode = quickMode === item.mode ? "all" : item.mode;
        updateActiveStatCards();

        if (typeof renderBusinessRecords === "function") {
          renderBusinessRecords();
        }
      };
    });

    const stats = document.querySelector(".stats");
    if (stats && !document.getElementById("sales_filter_reset_btn")) {
      const btn = document.createElement("button");
      btn.id = "sales_filter_reset_btn";
      btn.className = "sales-filter-reset";
      btn.type = "button";
      btn.textContent = "全部";
      btn.onclick = function () {
        quickMode = "all";
        clearNormalFilters();
        updateActiveStatCards();

        if (typeof renderBusinessRecords === "function") {
          renderBusinessRecords();
        }
      };

      stats.appendChild(btn);
    }

    updateActiveStatCards();
  }

  function moveStatsAboveSchedule() {
    const wrap = document.querySelector(".wrap");
    const stats = document.querySelector(".stats");
    const schedule = document.querySelector(".schedule-panel");

    if (!wrap || !stats || !schedule) return;

    if (stats.compareDocumentPosition(schedule) & Node.DOCUMENT_POSITION_PRECEDING) {
      wrap.insertBefore(stats, schedule);
    }
  }

  function bootStatsFilterBar() {
    moveStatsAboveSchedule();
    bindStatClicks();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bootStatsFilterBar);
  } else {
    bootStatsFilterBar();
  }

  setTimeout(bootStatsFilterBar, 300);
  setTimeout(bootStatsFilterBar, 900);
})();
</script>
<div id="sales_manager_modal_sub" class="sales-manager-modal-sub"></div>
      </div>
      <button class="sales-manager-modal-close" type="button" onclick="closeSalesManagerModal()">關閉</button>
    </div>
    <div id="sales_manager_modal_body" class="sales-manager-grid"></div>
  </div>
</div>
<script id="sales_today_memo_layout_v3">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  function safeEscape(value) {
    if (typeof escapeHtml === "function") {
      return escapeHtml(value);
    }

    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function todayText() {
    const d = new Date();
    return d.getFullYear() + "-" + String(d.getMonth() + 1).padStart(2, "0") + "-" + String(d.getDate()).padStart(2, "0");
  }

  function eventActive(item) {
    return item.event_type && item.event_type !== "無" && ["待處理", "處理中", "已回覆"].includes(item.event_status || "");
  }

  function buildActionText(item) {
    const parts = [];

    if (item.event_type && item.event_type !== "無") {
      parts.push(item.event_type);
    }

    if (item.event_status && item.event_status !== "無") {
      parts.push(item.event_status);
    }

    if (item.business_type) {
      parts.push(item.business_type);
    }

    if (item.contract_status === "洽談中" || item.contract_status === "即將到期") {
      parts.push("合約追蹤");
    }

    if (item.feedback_type && item.feedback_type !== "無") {
      parts.push(item.feedback_type);
    }

    if (!parts.length && item.next_visit) {
      parts.push("拜訪管理室");
    }

    return parts.join("｜") || "-";
  }

  function renderTodayScheduleMemoV3() {
    const box = document.getElementById("today_schedule_rows");
    if (!box) return;

    const rows = Array.isArray(window.businessRecords || businessRecords)
      ? (window.businessRecords || businessRecords)
      : [];

    const today = todayText();

    const items = rows.filter(function (item) {
      return Boolean(item.important_schedule)
        || item.next_visit === today
        || item.event_schedule_date === today
        || eventActive(item);
    }).sort(function (a, b) {
      const ai = a.important_schedule ? 0 : 1;
      const bi = b.important_schedule ? 0 : 1;
      if (ai !== bi) return ai - bi;

      const ad = a.next_visit || a.event_schedule_date || "9999-12-31";
      const bd = b.next_visit || b.event_schedule_date || "9999-12-31";
      return String(ad).localeCompare(String(bd));
    });

    if (!items.length) {
      box.innerHTML = '<div class="schedule-empty">目前沒有今日行程。</div>';
      return;
    }

    const header = `
      <div class="sales-memo-header">
        <div>類型</div>
        <div>大樓</div>
        <div>負責業務</div>
        <div>總幹事／電話</div>
        <div>業務行為</div>
      </div>
    `;

    const body = items.map(function (item) {
      const important = Boolean(item.important_schedule);
      const tag = important ? "重要" : "今日";
      const cls = important ? "schedule-card important" : "schedule-card";
      const contact = (item.manager_name || "-") + "｜" + (item.manager_phone || "-");

      return `
        <div class="${cls}">
          <div><span class="sales-memo-tag ${important ? "important" : ""}">${tag}</span></div>
          <div class="sales-memo-building">${safeEscape(item.building_name || "-")}</div>
          <div class="sales-memo-owner">${safeEscape(item.owner || "-")}</div>
          <div class="sales-memo-contact">${safeEscape(contact)}</div>
          <div class="sales-memo-action">${safeEscape(buildActionText(item))}</div>
        </div>
      `;
    }).join("");

    box.innerHTML = header + body;
  }

  const oldRenderBusinessRecords = window.renderBusinessRecords || (typeof renderBusinessRecords === "function" ? renderBusinessRecords : null);

  if (oldRenderBusinessRecords && window.__salesTodayMemoV3Wrapped !== true) {
    window.__salesTodayMemoV3Wrapped = true;

    renderBusinessRecords = function () {
      oldRenderBusinessRecords();
      setTimeout(renderTodayScheduleMemoV3, 0);
    };
  }

  window.renderTodaySchedule = renderTodayScheduleMemoV3;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", renderTodayScheduleMemoV3);
  } else {
    renderTodayScheduleMemoV3();
  }

  setTimeout(renderTodayScheduleMemoV3, 300);
  setTimeout(renderTodayScheduleMemoV3, 900);
})();
</script>


<script id="sales_clean_join_api_list_v1">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  function safeText(value) {
    return String(value || "").trim();
  }

  function normalizeNoteText(value) {
    let raw = safeText(value);

    raw = raw
      .replace(/\\s+/g, " ")
      .replace(/業務工作：/g, "工作：")
      .replace(/負責業務：/g, "負責：")
      .replace(/內容：/g, "內容：")
      .trim();

    return raw || "無備註";
  }

  function findRecordByManagerName(name) {
    name = safeText(name);
    const rows = Array.isArray(window.businessRecords || businessRecords)
      ? (window.businessRecords || businessRecords)
      : [];

    return rows.find(function (item) {
      return safeText(item.manager_name) === name;
    }) || null;
  }

  function openManagerMiniInfo(name) {
    const item = findRecordByManagerName(name);

    if (!item) {
      alert("找不到總幹事資料：" + name);
      return;
    }

    alert(
      "總幹事：" + (item.manager_name || "-") + "\n" +
      "電話：" + (item.manager_phone || "-") + "\n" +
      "管理公司：" + (item.management_company || "-") + "\n" +
      "服務大樓：" + (item.building_name || "-") + "\n" +
      "可拜訪時段：" + (item.visit_time || "-") + "\n" +
      "委員會時間：" + (item.committee_time || "-") + "\n" +
      "住戶大會：" + (item.resident_meeting_time || "-")
    );
  }

  window.openManagerMiniInfo = openManagerMiniInfo;

  function cleanManagerCells() {
    const tbody = document.getElementById("sales_rows");
    if (!tbody) return;

    Array.from(tbody.querySelectorAll("tr")).forEach(function (row) {
      if (row.classList.contains("sales-note-row")) return;

      const cells = row.querySelectorAll("td");
      if (cells.length < 2) return;

      const managerCell = cells[1];

      // 取得姓名
      let name = "";
      const link = managerCell.querySelector(".sales-manager-link");
      const btn = managerCell.querySelector("button");
      const bold = managerCell.querySelector("b");

      if (link) name = link.textContent.trim();
      else if (btn) name = btn.textContent.trim();
      else if (bold) name = bold.textContent.trim();
      else {
        const firstLine = managerCell.textContent.split(/\n/)[0] || "";
        name = firstLine.trim();
      }

      // 取得電話：找第一個像電話的文字
      let phone = "";
      const text = managerCell.textContent || "";
      const phoneMatch = text.match(/09\\d{8}|0\\d{1,2}-\\d{6,8}|未填電話/);
      if (phoneMatch) phone = phoneMatch[0];

      managerCell.innerHTML = `
        <button class="sales-manager-link" type="button" onclick="openManagerMiniInfo('${name.replaceAll("'", "\\'")}')">${name || "未填"}</button>
        <div class="small-muted">${phone || "未填電話"}</div>
      `;
    });
  }

  function rebuildNoteRowsFromBusinessNote() {
    const tbody = document.getElementById("sales_rows");
    if (!tbody) return;

    // 先移除舊備註列
    Array.from(tbody.querySelectorAll("tr.sales-note-row")).forEach(function (row) {
      row.remove();
    });

    const records = Array.isArray(window.businessRecords || businessRecords)
      ? (window.businessRecords || businessRecords)
      : [];

    const dataRows = Array.from(tbody.querySelectorAll("tr")).filter(function (row) {
      return !row.classList.contains("sales-note-row");
    });

    dataRows.forEach(function (row, index) {
      const cells = Array.from(row.children);
      if (!cells.length) return;

      // 空資料列不處理
      if (cells.length === 1 && cells[0].colSpan > 1) return;

      const item = records[index] || {};
      const note = normalizeNoteText(item.business_note || "");

      const visibleCount = cells.filter(function (cell) {
        return window.getComputedStyle(cell).display !== "none";
      }).length;

      const noteRow = document.createElement("tr");
      noteRow.className = "sales-note-row";

      const noteCell = document.createElement("td");
      noteCell.colSpan = Math.max(1, visibleCount);
      noteCell.innerHTML = `
        <div class="sales-note-box">
          <span class="sales-note-label">業務備註</span>
          <span class="sales-note-content">${note}</span>
        </div>
      `;

      noteRow.appendChild(noteCell);
      row.insertAdjacentElement("afterend", noteRow);
    });
  }

  function applyCleanJoinApiList() {
    cleanManagerCells();
    rebuildNoteRowsFromBusinessNote();
  }

  const oldRender = window.renderBusinessRecords || (typeof renderBusinessRecords === "function" ? renderBusinessRecords : null);

  if (oldRender && window.__salesCleanJoinApiListWrapped !== true) {
    window.__salesCleanJoinApiListWrapped = true;

    renderBusinessRecords = function () {
      oldRender();
      setTimeout(applyCleanJoinApiList, 0);
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applyCleanJoinApiList);
  } else {
    applyCleanJoinApiList();
  }

  setTimeout(applyCleanJoinApiList, 300);
  setTimeout(applyCleanJoinApiList, 900);
})();
</script>


<script id="sales_force_manager_simple_v1">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  function extractPhone(text) {
    const match = String(text || "").match(/09\\d{8}|0\\d{1,2}-\\d{6,8}|未填電話/);
    return match ? match[0] : "未填電話";
  }

  function extractName(cell) {
    const link = cell.querySelector(".sales-manager-link");
    if (link) return link.textContent.trim();

    const btn = cell.querySelector("button");
    if (btn) return btn.textContent.trim();

    const bold = cell.querySelector("b");
    if (bold) return bold.textContent.trim();

    const raw = String(cell.textContent || "")
      .split(/\n/)
      .map(x => x.trim())
      .filter(Boolean);

    return raw[0] || "未填";
  }

  function forceManagerSimple() {
    const tbody = document.getElementById("sales_rows");
    if (!tbody) return;

    Array.from(tbody.querySelectorAll("tr")).forEach(function (row) {
      if (row.classList.contains("sales-note-row")) return;

      const cells = row.querySelectorAll("td");
      if (cells.length < 2) return;

      const cell = cells[1];

      if (cell.dataset.managerSimpleDone === "1") return;

      const name = extractName(cell);
      const phone = extractPhone(cell.textContent);

      const safeName = name.replaceAll("'", "\\'");

      cell.innerHTML = `
        <button class="sales-manager-link" type="button" onclick="openManagerMiniInfo('${safeName}')">${name}</button>
        <div class="small-muted">${phone}</div>
      `;

      cell.dataset.managerSimpleDone = "1";
    });
  }

  function resetAndApply() {
    const tbody = document.getElementById("sales_rows");
    if (tbody) {
      Array.from(tbody.querySelectorAll("td[data-manager-simple-done]")).forEach(function (td) {
        delete td.dataset.managerSimpleDone;
      });
    }

    forceManagerSimple();
  }

  const oldRender = window.renderBusinessRecords || (typeof renderBusinessRecords === "function" ? renderBusinessRecords : null);

  if (oldRender && window.__salesForceManagerSimpleWrapped !== true) {
    window.__salesForceManagerSimpleWrapped = true;

    renderBusinessRecords = function () {
      oldRender();
      setTimeout(resetAndApply, 0);
      setTimeout(resetAndApply, 100);
    };
  }

  const observerTarget = document.getElementById("sales_rows");

  if (observerTarget && window.__salesForceManagerSimpleObserver !== true) {
    window.__salesForceManagerSimpleObserver = true;

    const observer = new MutationObserver(function () {
      setTimeout(forceManagerSimple, 0);
    });

    observer.observe(observerTarget, {
      childList: true,
      subtree: true
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", resetAndApply);
  } else {
    resetAndApply();
  }

  setTimeout(resetAndApply, 300);
  setTimeout(resetAndApply, 900);
})();
</script>



<script id="sales_owner_from_employee_profiles_v1">
(function () {
  if (!location.pathname.includes("/admin/sales")) return;

  async function loadSalesOwnersFromEmployeeProfiles() {
    try {
      const res = await fetch("/api/admin/employees?department=" + encodeURIComponent("業務部") + "&ts=" + Date.now(), {
        cache: "no-store"
      });

      if (!res.ok) {
        console.warn("業務人員 API 讀取失敗", res.status);
        return;
      }

      const rows = await res.json();
      const names = rows
        .filter(function (item) {
          return item && item.display_name && item.employment_status !== "離職" && Number(item.app_access || 0) === 1;
        })
        .map(function (item) {
          return item.display_name;
        });

      if (!names.length) {
        console.warn("沒有可用的業務人員資料");
        return;
      }

      const filterOwner = document.getElementById("filter_owner");
      const newOwner = document.getElementById("new_owner");

      if (filterOwner) {
        const oldValue = filterOwner.value || "全部";
        filterOwner.innerHTML =
          '<option value="全部">全部</option>' +
          names.map(function (name) {
            return '<option value="' + escapeAttr(name) + '">' + escapeHtml(name) + '</option>';
          }).join("");

        filterOwner.value = names.includes(oldValue) || oldValue === "全部" ? oldValue : "全部";

        if (typeof renderBusinessRecords === "function") {
          renderBusinessRecords();
        }
      }

      if (newOwner) {
        const oldValue = newOwner.value || "";
        newOwner.innerHTML = names.map(function (name) {
          return '<option value="' + escapeAttr(name) + '">' + escapeHtml(name) + '</option>';
        }).join("");

        newOwner.value = names.includes(oldValue) ? oldValue : names[0];
      }

      window.xunnanSalesOwners = names;
      console.log("業務 owner 已從 employee_profiles 載入", names);
    } catch (err) {
      console.error("業務 owner 載入失敗", err);
    }
  }

  function escapeHtml(v) {
    return String(v ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function escapeAttr(v) {
    return escapeHtml(v);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadSalesOwnersFromEmployeeProfiles);
  } else {
    loadSalesOwnersFromEmployeeProfiles();
  }

  setTimeout(loadSalesOwnersFromEmployeeProfiles, 500);
})();
</script>
</body>
</html>
"""
# SHINNAN_SALES_PAGE_ROUTE_END



# SHINNAN_SALES_MANAGERS_PAGE_ROUTE_START
@router.get("/admin/sales/managers", response_class=HTMLResponse)
def admin_sales_managers_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>總幹事名錄｜訊南 ERP</title>
  <style>
    body {
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1680px;
      margin: 0 auto;
      padding: 22px;
    }

    .hero {
      border-radius: 24px;
      padding: 28px;
      background: linear-gradient(135deg, #2f7b7b, #365ee8, #7c3aed);
      color: #fff;
      box-shadow: 0 20px 60px rgba(15,23,42,.18);
      margin-bottom: 16px;
    }

    h1 {
      margin: 0 0 10px;
      font-size: 44px;
      line-height: 1.1;
      font-weight: 1000;
    }

    .sub {
      font-size: 18px;
      font-weight: 900;
      opacity: .92;
    }

    .toolbar {
      display: grid;
      grid-template-columns: auto auto 220px 1fr;
      gap: 12px;
      align-items: center;
      margin: 16px 0;
    }

    button, select, input {
      height: 42px;
      border-radius: 12px;
      border: 1px solid #cbd5e1;
      font-size: 16px;
      font-weight: 900;
      padding: 0 14px;
      box-sizing: border-box;
    }

    button {
      border: 0;
      background: #365ee8;
      color: #fff;
      cursor: pointer;
    }

    button.gray {
      background: #64748b;
    }

    .card {
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 22px;
      padding: 14px;
      box-shadow: 0 12px 34px rgba(15,23,42,.07);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }

    th {
      background: #eaf2ff;
      color: #203a5f;
      font-size: 15px;
      font-weight: 1000;
      text-align: left;
      padding: 12px 10px;
    }

    td {
      border-bottom: 1px solid #e5edf7;
      padding: 12px 10px;
      font-size: 15px;
      font-weight: 800;
      vertical-align: top;
      line-height: 1.55;
      color: #102348;
    }

    .muted {
      color: #64748b;
      font-size: 13px;
      font-weight: 800;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 2px 10px;
      border-radius: 999px;
      background: #eaf2ff;
      color: #1d4ed8;
      font-size: 13px;
      font-weight: 1000;
    }

    .empty {
      padding: 28px;
      text-align: center;
      color: #64748b;
      font-weight: 900;
    }

    @media (max-width: 900px) {
      .toolbar {
        grid-template-columns: 1fr;
      }

      table {
        min-width: 1100px;
      }

      .card {
        overflow-x: auto;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>總幹事名錄</h1>
      <div class="sub">由 manager_contacts 資料表提供，不再從工程師名錄讀取。</div>
    </section>

    <div class="toolbar">
      <button type="button" onclick="history.back()">返回上一頁</button>
      <button type="button" class="gray" onclick="location.href='/admin/sales'">回業務系統</button>
      <select id="area_filter">
        <option value="全部">全部區域</option>
      </select>
      <input id="keyword_filter" placeholder="搜尋總幹事 / 電話 / 大樓 / 管理公司">
    </div>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th style="width:90px;">編號</th>
            <th style="width:150px;">總幹事</th>
            <th style="width:140px;">電話</th>
            <th style="width:170px;">管理公司</th>
            <th style="width:190px;">服務大樓</th>
            <th style="width:90px;">區域</th>
            <th style="width:120px;">資歷</th>
            <th style="width:170px;">興趣</th>
            <th style="width:180px;">可拜訪時段</th>
            <th>會議資訊</th>
          </tr>
        </thead>
        <tbody id="manager_rows">
          <tr><td colspan="10" class="empty">資料載入中...</td></tr>
        </tbody>
      </table>
    </div>
  </div>

  <script>
    let managerRows = [];

    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function loadManagers() {
      const res = await fetch("/api/admin/sales/managers?ts=" + Date.now(), {cache: "no-store"});

      if (!res.ok) {
        document.getElementById("manager_rows").innerHTML =
          '<tr><td colspan="10" class="empty">總幹事 API 讀取失敗：' + res.status + '</td></tr>';
        return;
      }

      managerRows = await res.json();
      buildAreaFilter();
      renderManagers();
    }

    function buildAreaFilter() {
      const sel = document.getElementById("area_filter");
      const areas = Array.from(new Set(managerRows.map(x => x.area).filter(Boolean))).sort();

      sel.innerHTML = '<option value="全部">全部區域</option>' +
        areas.map(a => '<option value="' + esc(a) + '">' + esc(a) + '</option>').join("");
    }

    function filteredManagers() {
      const area = document.getElementById("area_filter").value;
      const keyword = document.getElementById("keyword_filter").value.trim().toLowerCase();

      return managerRows.filter(function (item) {
        if (area !== "全部" && item.area !== area) return false;

        if (keyword) {
          const hay = [
            item.name,
            item.phone,
            item.management_company,
            item.building_name,
            item.area,
            item.interest,
            item.committee_time,
            item.resident_meeting_time
          ].join(" ").toLowerCase();

          if (!hay.includes(keyword)) return false;
        }

        return true;
      });
    }

    function renderManagers() {
      const box = document.getElementById("manager_rows");
      const rows = filteredManagers();

      if (!rows.length) {
        box.innerHTML = '<tr><td colspan="10" class="empty">沒有符合條件的總幹事資料。</td></tr>';
        return;
      }

      box.innerHTML = rows.map(function (item) {
        return `
          <tr>
            <td>${esc(item.manager_code || "-")}</td>
            <td>
              <b>${esc(item.name || "-")}</b>
              <div class="muted">${esc(item.age || "-")} 歲</div>
            </td>
            <td>${esc(item.phone || "-")}</td>
            <td>${esc(item.management_company || "-")}</td>
            <td>
              <b>${esc(item.building_name || "-")}</b>
              <div class="muted">${esc(item.building_no || "-")}</div>
            </td>
            <td><span class="pill">${esc(item.area || "-")}</span></td>
            <td>${esc(item.experience || "-")}</td>
            <td>${esc(item.interest || "-")}</td>
            <td>${esc(item.visit_time || "-")}</td>
            <td>
              <div>委員會：${esc(item.committee_time || "-")}</div>
              <div class="muted">住戶大會：${esc(item.resident_meeting_time || "-")}</div>
            </td>
          </tr>
        `;
      }).join("");
    }

    document.getElementById("area_filter").addEventListener("change", renderManagers);
    document.getElementById("keyword_filter").addEventListener("input", renderManagers);

    loadManagers();
  </script>
</body>
</html>
"""

# SHINNAN_SALES_MANAGERS_PAGE_ROUTE_END


# SHINNAN_SALES_DEMO_SEED_ROUTE_START_REMOVED_CLEANUP_STEP1_20260502
# This obsolete route block was removed during pages.py cleanup step 1.
# SHINNAN_SALES_DEMO_SEED_ROUTE_END_REMOVED_CLEANUP_STEP1_20260502





# SHINNAN_SALES_WORK_DEMO_SEED_ROUTE_START_REMOVED_CLEANUP_STEP1_20260502
# This obsolete route block was removed during pages.py cleanup step 1.
# SHINNAN_SALES_WORK_DEMO_SEED_ROUTE_END_REMOVED_CLEANUP_STEP1_20260502








# SHINNAN_CUSTOMER_BILLING_DETAIL_START
@router.get("/api/admin/customers/billing", summary="讀取單一客戶帳務資料")
def api_admin_customer_billing(customer_no: str):
    _customer_accounts_db_init()
    _buildings_db_init()
    _customer_billing_tables_init()

    with _customers_engine.begin() as conn:
        row = conn.execute(
            _customers_sql_text("""
                SELECT
                    c.id,
                    c.customer_no,
                    c.customer_name,
                    c.customer_phone,
                    c.customer_type,
                    c.building_no,
                    b.name AS building_name,
                    b.area AS area,
                    b.address AS building_address,
                    c.floor_text,
                    c.room_no,
                    c.service_address,
                    c.service_type,
                    c.package_name,
                    c.monthly_fee,
                    c.install_date,
                    c.contract_status,
                    c.account_status,
                    c.payment_method,
                    c.billing_day,
                    c.arrears_status,
                    c.equipment_no,
                    c.cm_mac,
                    c.ip_address,
                    c.signal_note,
                    c.billing_note,
                    c.service_note,
                    c.created_at,
                    c.updated_at
                FROM customer_accounts c
                LEFT JOIN buildings b ON b.building_no = c.building_no
                WHERE c.customer_no = :customer_no
                LIMIT 1
            """),
            {"customer_no": customer_no},
        ).mappings().first()

    if not row:
        return _CustomersResponse(
            content=_customers_json.dumps({"ok": False, "error": "customer not found"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=404,
        )

    return _CustomersResponse(
        content=_customers_json.dumps({"ok": True, "item": dict(row)}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.get("/admin/customers/billing", response_class=HTMLResponse)
def admin_customer_billing_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>客戶帳務資料｜訊南 ERP</title>
  <style>
    body {
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1180px;
      margin: 0 auto;
      padding: 18px;
    }

    .hero {
      border-radius: 20px;
      padding: 22px;
      background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
      color: #fff;
      margin-bottom: 14px;
      box-shadow: 0 18px 48px rgba(15,23,42,.18);
    }

    h1 {
      margin: 0 0 8px;
      font-size: 36px;
      font-weight: 1000;
    }

    .toolbar {
      display: flex;
      gap: 10px;
      margin-bottom: 14px;
    }

    button {
      height: 36px;
      border: 0;
      border-radius: 10px;
      padding: 0 14px;
      background: #365ee8;
      color: #fff;
      font-size: 14px;
      font-weight: 1000;
      cursor: pointer;
    }

    button.gray {
      background: #64748b;
    }

    .grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 10px;
    }

    .card {
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 16px;
      padding: 14px;
      box-shadow: 0 10px 26px rgba(15,23,42,.06);
    }

    .card.full {
      grid-column: 1 / -1;
    }

    .label {
      color: #64748b;
      font-size: 12px;
      font-weight: 1000;
      margin-bottom: 4px;
    }

    .value {
      color: #102348;
      font-size: 17px;
      font-weight: 1000;
      line-height: 1.45;
      white-space: pre-wrap;
    }

    .muted {
      color: #64748b;
      font-size: 13px;
      font-weight: 800;
      margin-top: 4px;
    }

    @media (max-width: 760px) {
      .grid {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1 id="title">客戶帳務資料</h1>
      <div id="subtitle">資料載入中...</div>
    </section>

    <div class="toolbar">
      <button type="button" onclick="history.back()">返回上一頁</button>
      <button type="button" class="gray" onclick="location.href='/?ts=' + Date.now()">回入口</button>
      <button type="button" onclick="location.href='/admin/customers?ts=' + Date.now()">客人名冊</button>
    </div>

    <div id="content" class="grid"></div>
  </div>

  <script>
    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function card(label, value, extra) {
      return `
        <div class="card ${extra || ""}">
          <div class="label">${esc(label)}</div>
          <div class="value">${esc(value || "-")}</div>
        </div>
      `;
    }

    async function loadBilling() {
      const params = new URLSearchParams(location.search);
      const customerNo = params.get("customer_no") || "";

      if (!customerNo) {
        document.getElementById("content").innerHTML = card("錯誤", "缺少 customer_no", "full");
        return;
      }

      const res = await fetch("/api/admin/customers/billing?customer_no=" + encodeURIComponent(customerNo) + "&ts=" + Date.now(), {cache: "no-store"});

      if (!res.ok) {
        document.getElementById("content").innerHTML = card("錯誤", "讀取失敗：" + res.status, "full");
        return;
      }

      const data = await res.json();
      const item = data.item || {};

      document.getElementById("title").textContent = item.customer_name + "｜帳務資料";
      document.getElementById("subtitle").textContent = item.customer_no + "｜" + item.building_name + "｜" + item.room_no;

      document.getElementById("content").innerHTML = [
        card("客戶編號", item.customer_no),
        card("客戶姓名", item.customer_name),
        card("聯絡電話", item.customer_phone),
        card("大樓", item.building_name + "（" + item.building_no + "）"),
        card("服務地址", item.service_address),
        card("戶別", item.room_no),
        card("服務類型", item.service_type),
        card("方案", item.package_name),
        card("月租費", item.monthly_fee),
        card("帳號狀態", item.account_status),
        card("合約狀態", item.contract_status),
        card("裝機日", item.install_date),
        card("繳費方式", item.payment_method),
        card("帳單日", item.billing_day),
        card("欠費狀態", item.arrears_status),
        card("設備編號", item.equipment_no),
        card("CM MAC", item.cm_mac),
        card("IP", item.ip_address),
        card("訊號備註", item.signal_note || "-", "full"),
        card("帳務備註", item.billing_note || "-", "full"),
        card("服務備註", item.service_note || "-", "full")
      ].join("");
    }

    loadBilling();
  </script>
</body>
</html>
"""
# SHINNAN_CUSTOMER_BILLING_DETAIL_END


@router.get("/admin/customers", response_class=HTMLResponse)
def admin_customers_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>客人名冊｜訊南 ERP</title>
  <style>
    body {
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1760px;
      margin: 0 auto;
      padding: 22px;
    }

    .hero {
      border-radius: 24px;
      padding: 28px;
      background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
      color: #fff;
      box-shadow: 0 20px 60px rgba(15,23,42,.18);
      margin-bottom: 16px;
    }

    h1 {
      margin: 0 0 10px;
      font-size: 44px;
      line-height: 1.1;
      font-weight: 1000;
    }

    .sub {
      font-size: 18px;
      font-weight: 900;
      opacity: .92;
    }

    .toolbar {
      display: grid;
      grid-template-columns: auto auto 220px 220px 220px 1fr auto;
      gap: 10px;
      align-items: center;
      margin: 16px 0;
    }

    button, select, input {
      height: 40px;
      border-radius: 12px;
      border: 1px solid #cbd5e1;
      font-size: 15px;
      font-weight: 900;
      padding: 0 12px;
      box-sizing: border-box;
    }

    button {
      border: 0;
      background: #365ee8;
      color: #fff;
      cursor: pointer;
    }

    button.gray {
      background: #64748b;
    }

    .summary {
      margin-bottom: 10px;
      color: #475569;
      font-size: 14px;
      font-weight: 900;
    }

    .card {
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 22px;
      padding: 14px;
      box-shadow: 0 12px 34px rgba(15,23,42,.07);
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
      min-width: 1500px;
    }

    th {
      background: #eaf2ff;
      color: #203a5f;
      font-size: 14px;
      font-weight: 1000;
      text-align: left;
      padding: 10px 8px;
    }

    td {
      border-bottom: 1px solid #e5edf7;
      padding: 9px 8px;
      font-size: 14px;
      font-weight: 800;
      vertical-align: top;
      line-height: 1.45;
      color: #102348;
    }

    .muted {
      color: #64748b;
      font-size: 12px;
      font-weight: 800;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      min-height: 23px;
      padding: 2px 9px;
      border-radius: 999px;
      background: #eaf2ff;
      color: #1d4ed8;
      font-size: 12px;
      font-weight: 1000;
    }

    .pill.green {
      background: #dcfce7;
      color: #166534;
    }

    .pill.orange {
      background: #ffedd5;
      color: #9a3412;
    }

    .pill.gray {
      background: #f1f5f9;
      color: #475569;
    }

    .pager {
      display: flex;
      justify-content: flex-end;
      align-items: center;
      gap: 8px;
      margin-top: 12px;
      font-weight: 900;
      color: #475569;
    }

    .empty {
      padding: 28px;
      text-align: center;
      color: #64748b;
      font-weight: 900;
    }

    @media (max-width: 1200px) {
      .toolbar {
        grid-template-columns: 1fr 1fr;
      }
    }
  </style>

<style id="customer_page_compact_v2">
  /* 客人名冊：工具列與列表緊湊版 */

  .wrap {
    max-width: 1760px !important;
    padding: 12px !important;
  }

  .hero {
    padding: 16px 20px !important;
    border-radius: 18px !important;
    margin-bottom: 8px !important;
  }

  h1 {
    font-size: 32px !important;
    margin-bottom: 4px !important;
  }

  .sub {
    font-size: 14px !important;
    line-height: 1.35 !important;
  }

  .toolbar {
    display: flex !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    align-items: center !important;
    margin: 8px 0 !important;
  }

  .toolbar button {
    width: auto !important;
    min-width: 78px !important;
    height: 32px !important;
    padding: 0 12px !important;
    border-radius: 9px !important;
    font-size: 13px !important;
    white-space: nowrap !important;
  }

  .toolbar button.gray {
    background: #2f7b7b !important;
  }

  .toolbar select {
    width: auto !important;
    min-width: 106px !important;
    max-width: 145px !important;
    height: 32px !important;
    padding: 0 8px !important;
    border-radius: 9px !important;
    font-size: 13px !important;
  }

  #limit_filter {
    min-width: 110px !important;
    max-width: 128px !important;
  }

  #keyword_filter {
    width: 360px !important;
    min-width: 240px !important;
    max-width: 420px !important;
    height: 32px !important;
    padding: 0 10px !important;
    border-radius: 9px !important;
    font-size: 13px !important;
  }

  .summary {
    margin: 4px 0 6px !important;
    font-size: 12px !important;
  }

  .card {
    padding: 7px !important;
    border-radius: 15px !important;
  }

  table {
    min-width: 1220px !important;
  }

  th {
    padding: 6px 6px !important;
    font-size: 12px !important;
    line-height: 1.2 !important;
    white-space: nowrap !important;
  }

  td {
    padding: 4px 6px !important;
    font-size: 12px !important;
    line-height: 1.22 !important;
    vertical-align: middle !important;
  }

  td b {
    font-size: 12px !important;
    line-height: 1.2 !important;
  }

  .muted {
    font-size: 10px !important;
    line-height: 1.15 !important;
    margin-top: 1px !important;
  }

  .pill {
    min-height: 18px !important;
    padding: 1px 6px !important;
    font-size: 10px !important;
  }

  .pager {
    margin-top: 6px !important;
    gap: 6px !important;
    font-size: 12px !important;
  }

  .pager button {
    height: 28px !important;
    font-size: 12px !important;
  }

  .customer-link {
    color: #1d4ed8 !important;
    font-weight: 1000 !important;
    text-decoration: none !important;
  }

  .customer-link:hover {
    text-decoration: underline !important;
  }

  @media (max-width: 900px) {
    #keyword_filter {
      width: 100% !important;
      max-width: none !important;
    }
  }
</style>

<style id="customer_area_address_layout_v1">
  /* 客人名冊：區域移到第 2 格，大樓縮小，地址加大，列高壓縮 */

  .card {
    padding: 4px !important;
  }

  table {
    min-width: 1320px !important;
  }

  th {
    padding: 4px 5px !important;
    font-size: 12px !important;
    line-height: 1.15 !important;
    white-space: nowrap !important;
  }

  td {
    padding: 3px 5px !important;
    font-size: 12px !important;
    line-height: 1.15 !important;
    height: 30px !important;
    vertical-align: middle !important;
  }

  td b,
  td a {
    font-size: 12px !important;
    line-height: 1.15 !important;
  }

  .muted {
    font-size: 10px !important;
    line-height: 1.1 !important;
    margin-top: 0 !important;
  }

  .pill {
    min-height: 16px !important;
    padding: 0 5px !important;
    font-size: 10px !important;
    line-height: 16px !important;
  }

  .customer-address-cell {
    max-width: 360px !important;
    white-space: normal !important;
    line-height: 1.18 !important;
  }

  .customer-building-cell {
    max-width: 120px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }

  .customer-service-cell {
    max-width: 190px !important;
    white-space: normal !important;
    line-height: 1.18 !important;
  }

  .customer-link {
    color: #1d4ed8 !important;
    font-weight: 1000 !important;
    text-decoration: none !important;
  }

  .customer-link:hover {
    text-decoration: underline !important;
  }
</style>


<style id="customer_address_service_fix_v1">
  /* 客人名冊：地址改為服務地址，戶別欄取消，大樓欄縮小 */

  table {
    min-width: 1180px !important;
  }

  th,
  td {
    padding: 3px 5px !important;
    font-size: 12px !important;
    line-height: 1.15 !important;
    height: 30px !important;
    vertical-align: middle !important;
  }

  .customer-building-cell {
    max-width: 115px !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
  }

  .customer-address-cell {
    min-width: 230px !important;
    max-width: 360px !important;
    white-space: normal !important;
    line-height: 1.18 !important;
    font-weight: 1000 !important;
  }

  .customer-service-cell {
    max-width: 190px !important;
    white-space: normal !important;
    line-height: 1.18 !important;
  }

  .pill {
    min-height: 16px !important;
    padding: 0 5px !important;
    font-size: 10px !important;
    line-height: 16px !important;
  }

  .muted {
    font-size: 10px !important;
    line-height: 1.1 !important;
  }
</style>

</head>
<body>
  <div class="wrap">
    <section class="hero">
      <h1>客人名冊</h1>
      <div class="sub">由 customer_accounts 資料表提供，並透過 building_no 關聯大樓主資料。</div>
    </section>

    <div class="toolbar">
      <button type="button" onclick="history.back()">返回上一頁</button>
      <button type="button" class="gray" onclick="location.href='/?ts=' + Date.now()">回入口</button>

      <select id="area_filter">
        <option value="全部">全部區域</option>
      </select>

      <select id="status_filter">
        <option value="全部">全部狀態</option>
        <option value="啟用中">啟用中</option>
        <option value="待裝機">待裝機</option>
        <option value="暫停">暫停</option>
        <option value="已退租">已退租</option>
      </select>

      <select id="limit_filter">
        <option value="100">每頁 100 筆</option>
        <option value="300" selected>每頁 300 筆</option>
        <option value="500">每頁 500 筆</option>
        <option value="1000">每頁 1000 筆</option>
      </select>

      <input id="keyword_filter" placeholder="搜尋客戶編號 / 姓名 / 電話 / 大樓 / 戶別">

      <button type="button" onclick="reloadCustomers(true)">搜尋</button>
    </div>

    <div id="summary" class="summary">資料載入中...</div>

    <div class="card">
      <table>
        <thead>
          <tr>
            <th style="width:110px;">客戶編號</th>
            <th style="width:150px;">客戶</th>
            <th style="width:150px;">電話</th>
            <th style="width:190px;">大樓</th>
            <th style="width:80px;">區域</th>
            <th style="width:120px;">戶別</th>
            <th style="width:150px;">服務</th>
            <th style="width:90px;">月租</th>
            <th style="width:120px;">狀態</th>
            <th style="width:140px;">帳務</th>
            <th style="width:180px;">設備</th>
            <th>備註</th>
          </tr>
        </thead>
        <tbody id="customer_rows">
          <tr><td colspan="12" class="empty">資料載入中...</td></tr>
        </tbody>
      </table>

      <div class="pager">
        <button type="button" class="gray" onclick="prevPage()">上一頁</button>
        <span id="page_info">第 1 頁</span>
        <button type="button" onclick="nextPage()">下一頁</button>
      </div>
    </div>
  </div>

  <script>
    let currentOffset = 0;
    let currentLimit = 300;
    let currentTotal = 0;
    let areaOptionsBuilt = false;

    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function statusClass(status) {
      if (status === "啟用中") return "green";
      if (status === "待裝機") return "orange";
      return "gray";
    }

    async function buildAreaFilter() {
      if (areaOptionsBuilt) return;

      const res = await fetch("/api/admin/buildings?ts=" + Date.now(), {cache: "no-store"});
      const rows = await res.json();
      const areas = Array.from(new Set(rows.map(x => x.area).filter(Boolean))).sort();
      const sel = document.getElementById("area_filter");

      sel.innerHTML = '<option value="全部">全部區域</option>' +
        areas.map(a => '<option value="' + esc(a) + '">' + esc(a) + '</option>').join("");

      areaOptionsBuilt = true;
    }

    async function reloadCustomers(reset) {
      if (reset) currentOffset = 0;

      currentLimit = Number(document.getElementById("limit_filter").value || 300);

      const params = new URLSearchParams();
      params.set("limit", currentLimit);
      params.set("offset", currentOffset);
      params.set("area", document.getElementById("area_filter").value || "全部");
      params.set("status", document.getElementById("status_filter").value || "全部");
      params.set("q", document.getElementById("keyword_filter").value || "");
      params.set("ts", Date.now());

      const res = await fetch("/api/admin/customers?" + params.toString(), {cache: "no-store"});

      if (!res.ok) {
        document.getElementById("customer_rows").innerHTML =
          '<tr><td colspan="12" class="empty">客人 API 讀取失敗：' + res.status + '</td></tr>';
        return;
      }

      const data = await res.json();
      currentTotal = data.total || 0;

      renderCustomers(data.items || []);
      renderSummary();
    }

    function renderSummary() {
      const page = Math.floor(currentOffset / currentLimit) + 1;
      const start = currentTotal ? currentOffset + 1 : 0;
      const end = Math.min(currentOffset + currentLimit, currentTotal);

      document.getElementById("summary").textContent =
        "共 " + currentTotal + " 筆，目前顯示 " + start + " - " + end + " 筆";

      document.getElementById("page_info").textContent = "第 " + page + " 頁";
    }

    function renderCustomers(rows) {
      const box = document.getElementById("customer_rows");

      if (!rows.length) {
        box.innerHTML = '<tr><td colspan="12" class="empty">沒有符合條件的客戶資料。</td></tr>';
        return;
      }

      box.innerHTML = rows.map(function (item) {
        return `
          <tr>
            <td>${esc(item.customer_no)}</td>
            <td>
              <b>${esc(item.customer_name)}</b>
              <div class="muted">${esc(item.customer_type || "-")}</div>
            </td>
            <td>${esc(item.customer_phone || "-")}</td>
            <td>
              <b>${esc(item.building_name || "-")}</b>
              <div class="muted">${esc(item.building_no || "-")}</div>
            </td>
            <td><span class="pill">${esc(item.area || "-")}</span></td>
            <td>
              ${esc(item.floor_text || "-")}
              <div class="muted">${esc(item.room_no || "-")}</div>
            </td>
            <td>
              <b>${esc(item.service_type || "-")}</b>
              <div class="muted">${esc(item.package_name || "-")}</div>
            </td>
            <td>${esc(item.monthly_fee || 0)}</td>
            <td><span class="pill ${statusClass(item.account_status)}">${esc(item.account_status || "-")}</span></td>
            <td>
              ${esc(item.payment_method || "-")}
              <div class="muted">帳單日：${esc(item.billing_day || "-")}</div>
              <div class="muted">${esc(item.arrears_status || "-")}</div>
            </td>
            <td>
              ${esc(item.equipment_no || "-")}
              <div class="muted">${esc(item.cm_mac || "-")}</div>
            </td>
            <td>
              <div>${esc(item.service_note || "-")}</div>
              <div class="muted">${esc(item.billing_note || "")}</div>
            </td>
          </tr>
        `;
      }).join("");
    }

    function prevPage() {
      currentOffset = Math.max(0, currentOffset - currentLimit);
      reloadCustomers(false);
    }

    function nextPage() {
      if (currentOffset + currentLimit >= currentTotal) return;
      currentOffset += currentLimit;
      reloadCustomers(false);
    }

    document.getElementById("area_filter").addEventListener("change", function () { reloadCustomers(true); });
    document.getElementById("status_filter").addEventListener("change", function () { reloadCustomers(true); });
    document.getElementById("limit_filter").addEventListener("change", function () { reloadCustomers(true); });
    document.getElementById("keyword_filter").addEventListener("keydown", function (event) {
      if (event.key === "Enter") reloadCustomers(true);
    });

    buildAreaFilter().then(function () {
      reloadCustomers(true);
    });
  </script>


<script id="customer_billing_links_v1">
(function () {
  if (!location.pathname.includes("/admin/customers")) return;

  function esc2(v) {
    return String(v ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function billingUrl(customerNo) {
    return "/admin/customers/billing?customer_no=" + encodeURIComponent(customerNo || "");
  }

  window.renderCustomers = function (rows) {
    const box = document.getElementById("customer_rows");

    if (!rows.length) {
      box.innerHTML = '<tr><td colspan="12" class="empty">沒有符合條件的客戶資料。</td></tr>';
      return;
    }

    box.innerHTML = rows.map(function (item) {
      const url = billingUrl(item.customer_no);

      return `
        <tr>
          <td>
            <a class="customer-link" href="${url}">${esc2(item.customer_no)}</a>
          </td>
          <td>
            <a class="customer-link" href="${url}">${esc2(item.customer_name)}</a>
            <div class="muted">${esc2(item.customer_type || "-")}</div>
          </td>
          <td>${esc2(item.customer_phone || "-")}</td>
          <td>
            <a class="customer-link" href="${url}">${esc2(item.building_name || "-")}</a>
            <div class="muted">${esc2(item.building_no || "-")}</div>
          </td>
          <td><span class="pill">${esc2(item.area || "-")}</span></td>
          <td>
            <a class="customer-link" href="${url}">${esc2(item.floor_text || "-")}</a>
            <div class="muted">
              <a class="customer-link" href="${url}">${esc2(item.room_no || "-")}</a>
            </div>
          </td>
          <td>
            <b>${esc2(item.service_type || "-")}</b>
            <div class="muted">${esc2(item.package_name || "-")}</div>
          </td>
          <td>${esc2(item.monthly_fee || 0)}</td>
          <td><span class="pill ${statusClass(item.account_status)}">${esc2(item.account_status || "-")}</span></td>
          <td>
            ${esc2(item.payment_method || "-")}
            <div class="muted">帳單日：${esc2(item.billing_day || "-")}</div>
            <div class="muted">${esc2(item.arrears_status || "-")}</div>
          </td>
          <td>
            ${esc2(item.equipment_no || "-")}
            <div class="muted">${esc2(item.cm_mac || "-")}</div>
          </td>
          <td>
            <div>${esc2(item.service_note || "-")}</div>
            <div class="muted">${esc2(item.billing_note || "")}</div>
          </td>
        </tr>
      `;
    }).join("");
  };
})();
</script>


<script id="customer_area_address_layout_v1">
(function () {
  if (!location.pathname.includes("/admin/customers")) return;

  function esc2(v) {
    return String(v ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function billingUrl(customerNo) {
    return "/admin/customers/billing?customer_no=" + encodeURIComponent(customerNo || "");
  }

  function patchCustomerHeader() {
    const heads = document.querySelectorAll("table thead tr th");
    if (!heads || heads.length < 9) return;

    const labels = [
      "客戶編號",
      "區域",
      "客戶",
      "電話",
      "大樓",
      "地址",
      "戶別",
      "服務",
      "月租",
      "狀態",
      "帳務",
      "備註"
    ];

    heads.forEach(function (th, index) {
      if (labels[index]) th.textContent = labels[index];
    });
  }

  window.renderCustomers = function (rows) {
    const box = document.getElementById("customer_rows");

    patchCustomerHeader();

    if (!rows.length) {
      box.innerHTML = '<tr><td colspan="12" class="empty">沒有符合條件的客戶資料。</td></tr>';
      return;
    }

    box.innerHTML = rows.map(function (item) {
      const url = billingUrl(item.customer_no);
      const address = item.service_address || item.building_address || "-";

      return `
        <tr>
          <td>
            <a class="customer-link" href="${url}">${esc2(item.customer_no)}</a>
          </td>

          <td>
            <span class="pill">${esc2(item.area || "-")}</span>
          </td>

          <td>
            <a class="customer-link" href="${url}">${esc2(item.customer_name)}</a>
            <div class="muted">${esc2(item.customer_type || "-")}</div>
          </td>

          <td>${esc2(item.customer_phone || "-")}</td>

          <td class="customer-building-cell">
            <a class="customer-link" href="${url}">${esc2(item.building_name || "-")}</a>
            <div class="muted">${esc2(item.building_no || "-")}</div>
          </td>

          <td class="customer-address-cell">${esc2(address)}</td>

          <td>
            <a class="customer-link" href="${url}">${esc2(item.room_no || "-")}</a>
          </td>

          <td class="customer-service-cell">
            <b>${esc2(item.service_type || "-")}</b>
            <div class="muted">${esc2(item.package_name || "-")}</div>
          </td>

          <td><b>${esc2(item.monthly_fee || 0)}</b></td>

          <td><span class="pill ${statusClass(item.account_status)}">${esc2(item.account_status || "-")}</span></td>

          <td>
            ${esc2(item.payment_method || "-")}
            <div class="muted">${esc2(item.arrears_status || "-")}</div>
          </td>

          <td>
            <div>${esc2(item.service_note || "-")}</div>
            <div class="muted">${esc2(item.billing_note || "")}</div>
          </td>
        </tr>
      `;
    }).join("");
  };

  patchCustomerHeader();
  setTimeout(patchCustomerHeader, 300);
})();
</script>


<script id="customer_address_service_fix_v1">
(function () {
  if (!location.pathname.includes("/admin/customers")) return;

  function esc3(v) {
    return String(v ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function billingUrl(customerNo) {
    return "/admin/customers/billing?customer_no=" + encodeURIComponent(customerNo || "");
  }

  function patchCustomerHeaderV2() {
    const heads = document.querySelectorAll("table thead tr th");
    if (!heads || heads.length < 8) return;

    const labels = [
      "客戶編號",
      "區域",
      "客戶",
      "電話",
      "大樓",
      "地址",
      "服務",
      "月租",
      "狀態",
      "帳務",
      "備註"
    ];

    heads.forEach(function (th, index) {
      if (labels[index]) th.textContent = labels[index];
    });
  }

  window.renderCustomers = function (rows) {
    const box = document.getElementById("customer_rows");

    patchCustomerHeaderV2();

    if (!rows.length) {
      box.innerHTML = '<tr><td colspan="11" class="empty">沒有符合條件的客戶資料。</td></tr>';
      return;
    }

    box.innerHTML = rows.map(function (item) {
      const url = billingUrl(item.customer_no);

      /*
        重要：
        地址欄只顯示 customer_accounts.service_address。
        不再組合 building_address + room_no。
      */
      const serviceAddress = item.service_address || item.room_no || "-";
      const buildingName = item.building_name || (item.building_no === "HOUSE" ? "透天" : "-");

      return `
        <tr>
          <td>
            <a class="customer-link" href="${url}">${esc3(item.customer_no)}</a>
          </td>

          <td>
            <span class="pill">${esc3(item.area || "-")}</span>
          </td>

          <td>
            <a class="customer-link" href="${url}">${esc3(item.customer_name)}</a>
            <div class="muted">${esc3(item.customer_type || "-")}</div>
          </td>

          <td>${esc3(item.customer_phone || "-")}</td>

          <td class="customer-building-cell">
            <a class="customer-link" href="${url}">${esc3(buildingName)}</a>
            <div class="muted">${esc3(item.building_no || "-")}</div>
          </td>

          <td class="customer-address-cell">
            <a class="customer-link" href="${url}">${esc3(serviceAddress)}</a>
          </td>

          <td class="customer-service-cell">
            <b>${esc3(item.service_type || "-")}</b>
            <div class="muted">${esc3(item.package_name || "-")}</div>
          </td>

          <td><b>${esc3(item.monthly_fee || 0)}</b></td>

          <td><span class="pill ${statusClass(item.account_status)}">${esc3(item.account_status || "-")}</span></td>

          <td>
            ${esc3(item.payment_method || "-")}
            <div class="muted">${esc3(item.arrears_status || "-")}</div>
          </td>

          <td>
            <div>${esc3(item.service_note || "-")}</div>
            <div class="muted">${esc3(item.billing_note || "")}</div>
          </td>
        </tr>
      `;
    }).join("");
  };

  patchCustomerHeaderV2();
  setTimeout(patchCustomerHeaderV2, 300);
})();
</script>


<script id="customer_address_room_only_v1">
(function () {
  if (!location.pathname.includes("/admin/customers")) return;

  function escRoomOnly(v) {
    return String(v ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function billingUrl(customerNo) {
    return "/admin/customers/billing?customer_no=" + encodeURIComponent(customerNo || "");
  }

  function displayAddress(item) {
    if (item.building_no === "HOUSE") {
      return item.service_address || "-";
    }

    return item.service_address || item.room_no || "-";
  }

  window.renderCustomers = function (rows) {
    const box = document.getElementById("customer_rows");

    if (!rows.length) {
      box.innerHTML = '<tr><td colspan="11" class="empty">沒有符合條件的客戶資料。</td></tr>';
      return;
    }

    box.innerHTML = rows.map(function (item) {
      const url = billingUrl(item.customer_no);
      const serviceAddress = displayAddress(item);
      const buildingName = item.building_name || (item.building_no === "HOUSE" ? "透天" : "-");

      return `
        <tr>
          <td>
            <a class="customer-link" href="${url}">${escRoomOnly(item.customer_no)}</a>
          </td>

          <td>
            <span class="pill">${escRoomOnly(item.area || "-")}</span>
          </td>

          <td>
            <a class="customer-link" href="${url}">${escRoomOnly(item.customer_name)}</a>
            <div class="muted">${escRoomOnly(item.customer_type || "-")}</div>
          </td>

          <td>${escRoomOnly(item.customer_phone || "-")}</td>

          <td class="customer-building-cell">
            <a class="customer-link" href="${url}">${escRoomOnly(buildingName)}</a>
            <div class="muted">${escRoomOnly(item.building_no || "-")}</div>
          </td>

          <td class="customer-address-cell">
            <a class="customer-link" href="${url}">${escRoomOnly(serviceAddress)}</a>
          </td>

          <td class="customer-service-cell">
            <b>${escRoomOnly(item.service_type || "-")}</b>
            <div class="muted">${escRoomOnly(item.package_name || "-")}</div>
          </td>

          <td><b>${escRoomOnly(item.monthly_fee || 0)}</b></td>

          <td><span class="pill ${statusClass(item.account_status)}">${escRoomOnly(item.account_status || "-")}</span></td>

          <td>
            ${escRoomOnly(item.payment_method || "-")}
            <div class="muted">${escRoomOnly(item.arrears_status || "-")}</div>
          </td>

          <td>
            <div>${escRoomOnly(item.service_note || "-")}</div>
            <div class="muted">${escRoomOnly(item.billing_note || "")}</div>
          </td>
        </tr>
      `;
    }).join("");
  };
})();
</script>
</body>
</html>
"""



# SHINNAN_CUSTOMER_BILLING_TABLES_HELPER_START
def _customer_billing_tables_init():
    with _customers_engine.begin() as conn:
        conn.execute(_customers_sql_text("""
            CREATE TABLE IF NOT EXISTS billing_service_plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_code TEXT UNIQUE NOT NULL,
                plan_name TEXT NOT NULL,
                plan_label TEXT DEFAULT '',
                monthly_fee INTEGER DEFAULT 0,
                billing_category TEXT DEFAULT '',
                enabled INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(_customers_sql_text("""
            CREATE TABLE IF NOT EXISTS customer_service_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_no TEXT NOT NULL,
                plan_code TEXT NOT NULL,
                enabled INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))
# SHINNAN_CUSTOMER_BILLING_TABLES_HELPER_END


# SHINNAN_CUSTOMER_ACCOUNTS_API_START
def _customer_accounts_db_init():
    with _customers_engine.begin() as conn:
        conn.execute(_customers_sql_text("""
            CREATE TABLE IF NOT EXISTS customer_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_no TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                customer_phone TEXT DEFAULT '',
                customer_type TEXT DEFAULT '',
                building_no TEXT NOT NULL,
                floor_text TEXT DEFAULT '',
                room_no TEXT DEFAULT '',
                service_address TEXT DEFAULT '',
                service_type TEXT DEFAULT '',
                package_name TEXT DEFAULT '',
                monthly_fee INTEGER DEFAULT 0,
                install_date TEXT DEFAULT '',
                contract_status TEXT DEFAULT '',
                account_status TEXT DEFAULT '',
                payment_method TEXT DEFAULT '',
                billing_day INTEGER DEFAULT 0,
                arrears_status TEXT DEFAULT '',
                equipment_no TEXT DEFAULT '',
                cm_mac TEXT DEFAULT '',
                ip_address TEXT DEFAULT '',
                signal_note TEXT DEFAULT '',
                billing_note TEXT DEFAULT '',
                service_note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))


@router.get("/api/admin/customers", summary="讀取客人名冊")
def api_admin_customers(
    q: str = "",
    area: str = "全部",
    building_no: str = "",
    status: str = "全部",
    limit: int = 300,
    offset: int = 0,
):
    _customer_accounts_db_init()
    _buildings_db_init()

    limit = max(1, min(int(limit or 300), 1000))
    offset = max(0, int(offset or 0))

    where = []
    params = {
        "limit": limit,
        "offset": offset,
    }

    if q:
        where.append("""
            (
                c.customer_no LIKE :q OR
                c.customer_name LIKE :q OR
                c.customer_phone LIKE :q OR
                b.name LIKE :q OR
                c.room_no LIKE :q
            )
        """)
        params["q"] = f"%{q}%"

    if area and area != "全部":
        where.append("b.area = :area")
        params["area"] = area

    if building_no:
        where.append("c.building_no = :building_no")
        params["building_no"] = building_no

    if status and status != "全部":
        where.append("c.account_status = :status")
        params["status"] = status

    where_sql = ""
    if where:
        where_sql = "WHERE " + " AND ".join(where)

    with _customers_engine.begin() as conn:
        total = conn.execute(
            _customers_sql_text(f"""
                SELECT COUNT(*)
                FROM customer_accounts c
                LEFT JOIN buildings b ON b.building_no = c.building_no
                {where_sql}
            """),
            params,
        ).scalar()

        rows = conn.execute(
            _customers_sql_text(f"""
                SELECT
                    c.id,
                    c.customer_no,
                    c.customer_name,
                    c.customer_phone,
                    c.customer_type,
                    c.building_no,
                    b.name AS building_name,
                    b.area AS area,
                    b.address AS building_address,
                    c.floor_text,
                    c.room_no,
                    c.service_address,
                    COALESCE(svc.service_type, c.service_type) AS service_type,
                    COALESCE(svc.package_name, c.package_name) AS package_name,
                    COALESCE(svc.monthly_fee, c.monthly_fee) AS monthly_fee,
                    c.install_date,
                    c.contract_status,
                    c.account_status,
                    c.payment_method,
                    c.billing_day,
                    c.arrears_status,
                    c.equipment_no,
                    c.cm_mac,
                    c.ip_address,
                    c.signal_note,
                    c.billing_note,
                    c.service_note,
                    c.created_at,
                    c.updated_at
                FROM customer_accounts c
                LEFT JOIN buildings b ON b.building_no = c.building_no
                LEFT JOIN (
                    SELECT
                        i.customer_no,
                        GROUP_CONCAT(p.plan_name, '＋') AS service_type,
                        GROUP_CONCAT(p.plan_label, '＋') AS package_name,
                        SUM(p.monthly_fee) AS monthly_fee
                    FROM customer_service_items i
                    LEFT JOIN billing_service_plans p ON p.plan_code = i.plan_code
                    WHERE i.enabled = 1
                    GROUP BY i.customer_no
                ) svc ON svc.customer_no = c.customer_no
                {where_sql}
                ORDER BY c.building_no ASC, c.floor_text ASC, c.room_no ASC, c.customer_no ASC
                LIMIT :limit OFFSET :offset
            """),
            params,
        ).mappings().fetchall()

    return _CustomersResponse(
        content=_customers_json.dumps(
            {
                "total": total,
                "limit": limit,
                "offset": offset,
                "items": [dict(row) for row in rows],
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )
# SHINNAN_CUSTOMER_ACCOUNTS_API_END


# SHINNAN_MANAGER_CONTACTS_API_START
def _manager_contacts_db_init():
    with _managers_engine.begin() as conn:
        conn.execute(_managers_sql_text("""
            CREATE TABLE IF NOT EXISTS manager_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manager_code TEXT DEFAULT '',
                name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                age TEXT DEFAULT '',
                management_company TEXT DEFAULT '',
                experience TEXT DEFAULT '',
                interest TEXT DEFAULT '',
                visit_time TEXT DEFAULT '',
                committee_time TEXT DEFAULT '',
                resident_meeting_time TEXT DEFAULT '',
                building_no TEXT DEFAULT '',
                building_name TEXT DEFAULT '',
                area TEXT DEFAULT '',
                note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))


@router.get("/api/admin/sales/managers", summary="讀取總幹事名錄")
def api_admin_sales_managers():
    _manager_contacts_db_init()

    with _managers_engine.begin() as conn:
        rows = conn.execute(_managers_sql_text("""
            SELECT
                manager_code,
                name,
                phone,
                age,
                management_company,
                experience,
                interest,
                visit_time,
                committee_time,
                resident_meeting_time,
                building_no,
                building_name,
                area,
                note
            FROM manager_contacts
            ORDER BY building_no ASC, id ASC
        """)).mappings().fetchall()

    return _ManagersResponse(
        content=_managers_json.dumps([dict(row) for row in rows], ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )
# SHINNAN_MANAGER_CONTACTS_API_END


# SHINNAN_SALES_DB_API_START
def _sales_business_records_init():
    with _sales_engine.begin() as conn:
        conn.execute(_sales_sql_text("""
            CREATE TABLE IF NOT EXISTS sales_business_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                building_no TEXT NOT NULL,
                business_type TEXT DEFAULT '',
                status TEXT DEFAULT '',
                contract_status TEXT DEFAULT '',
                contract_end_date TEXT DEFAULT '',
                feedback_type TEXT DEFAULT '',
                feedback_status TEXT DEFAULT '',
                event_type TEXT DEFAULT '',
                event_status TEXT DEFAULT '',
                event_schedule_date TEXT DEFAULT '',
                important_schedule INTEGER DEFAULT 0,
                next_visit TEXT DEFAULT '',
                owner TEXT DEFAULT '',
                business_note TEXT DEFAULT '',
                demo_type TEXT DEFAULT '',
                created_at TEXT DEFAULT '',
                updated_at TEXT DEFAULT ''
            )
        """))


@router.get("/api/admin/sales/business-records", summary="讀取業務工作資料")
def api_admin_sales_business_records():
    _sales_business_records_init()
    _buildings_db_init()

    with _sales_engine.begin() as conn:
        rows = conn.execute(_sales_sql_text("""
            SELECT
                s.id AS id,
                s.building_no AS building_no,
                b.name AS building_name,
                b.area AS area,
                b.address AS building_address,
                b.management_company AS management_company,
                b.management_phone AS management_phone,
                b.manager_name AS manager_name,
                b.manager_phone AS manager_phone,
                b.manager_age AS manager_age,
                b.manager_experience AS manager_experience,
                b.manager_interest AS manager_interest,
                b.visit_time AS visit_time,
                b.committee_time AS committee_time,
                b.resident_meeting_time AS resident_meeting_time,
                s.business_type AS business_type,
                s.status AS status,
                s.contract_status AS contract_status,
                s.contract_end_date AS contract_end_date,
                s.feedback_type AS feedback_type,
                s.feedback_status AS feedback_status,
                s.event_type AS event_type,
                s.event_status AS event_status,
                s.event_schedule_date AS event_schedule_date,
                s.important_schedule AS important_schedule,
                s.next_visit AS next_visit,
                s.owner AS owner,
                s.business_note AS business_note,
                s.demo_type AS demo_type,
                s.created_at AS created_at,
                s.updated_at AS updated_at
            FROM sales_business_records s
            LEFT JOIN buildings b ON b.building_no = s.building_no
            ORDER BY s.id DESC
        """)).mappings().fetchall()

    records = []

    for row in rows:
        item = dict(row)
        item["important_schedule"] = bool(item.get("important_schedule"))
        item["management_note"] = (
            "大樓地址：" + str(item.get("building_address") or "") + "\\n"
            "管理公司：" + str(item.get("management_company") or "") + "\\n"
            "管理室電話：" + str(item.get("management_phone") or "")
        )
        records.append(item)

    return _SalesResponse(
        content=_sales_json.dumps(records, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )
# SHINNAN_SALES_DB_API_END

# SHINNAN_BILLING_ROUTE_BRIDGE_START_REMOVED_CLEANUP_STEP1_20260502
# This obsolete route block was removed during pages.py cleanup step 1.
# SHINNAN_BILLING_ROUTE_BRIDGE_END_REMOVED_CLEANUP_STEP1_20260502


@router.get("/admin/import", response_class=HTMLResponse)
def admin_import_page(request: Request):
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8">
  <title>資料匯入｜訊南 ERP 系統</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  <style>
    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
      background: #eef3fa;
      color: #102348;
    }

    .hero {
      background: linear-gradient(135deg, #2f7f74, #315eea, #7c3aed);
      color: #ffffff;
      padding: 30px 34px;
      border-radius: 0 0 28px 28px;
      box-shadow: 0 16px 38px rgba(15, 23, 42, 0.18);
    }

    .hero-title {
      font-size: 42px;
      font-weight: 1000;
      letter-spacing: 2px;
      margin-bottom: 10px;
    }

    .hero-subtitle {
      font-size: 20px;
      font-weight: 800;
      opacity: 0.92;
    }

    .page {
      width: min(1480px, calc(100vw - 40px));
      margin: 0 auto;
      padding: 24px 0 40px;
    }

    .toolbar {
      display: flex;
      align-items: center;
      gap: 12px;
      margin: 22px 0;
    }

    .home-button {
      height: 40px;
      border: 0;
      border-radius: 12px;
      background: #4f7ee8;
      color: #ffffff;
      font-size: 16px;
      font-weight: 1000;
      padding: 0 18px;
      cursor: pointer;
      box-shadow: 0 6px 14px rgba(15, 23, 42, 0.12);
    }

    .hint {
      color: #64748b;
      font-size: 15px;
      font-weight: 800;
    }

    .import-grid {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 16px;
      margin-bottom: 20px;
    }

    .import-card {
      background: #ffffff;
      border: 1px solid #d7e1ef;
      border-radius: 22px;
      padding: 20px;
      box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    }

    .import-card-title {
      font-size: 24px;
      font-weight: 1000;
      margin-bottom: 8px;
      color: #102348;
    }

    .import-card-desc {
      color: #64748b;
      font-size: 15px;
      font-weight: 800;
      line-height: 1.55;
      min-height: 94px;
    }

    .format-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      height: 30px;
      padding: 0 12px;
      border-radius: 999px;
      font-size: 14px;
      font-weight: 1000;
      margin-bottom: 14px;
    }

    .excel {
      background: #dcfce7;
      color: #166534;
    }

    .csv {
      background: #e0f2fe;
      color: #075985;
    }

    .json {
      background: #f3e8ff;
      color: #6b21a8;
    }

    .db {
      background: #ffedd5;
      color: #9a3412;
    }

    .import-button {
      width: 100%;
      height: 42px;
      border: 0;
      border-radius: 14px;
      color: #ffffff;
      font-size: 16px;
      font-weight: 1000;
      cursor: pointer;
      margin-top: 14px;
    }

    .btn-excel {
      background: #16a34a;
    }

    .btn-csv {
      background: #0284c7;
    }

    .btn-json {
      background: #7c3aed;
    }

    .btn-db {
      background: #ea580c;
    }

    .panel {
      background: #ffffff;
      border: 1px solid #d7e1ef;
      border-radius: 22px;
      padding: 22px;
      box-shadow: 0 10px 28px rgba(15, 23, 42, 0.08);
    }

    .panel-title {
      font-size: 26px;
      font-weight: 1000;
      margin-bottom: 16px;
    }

    .form-grid {
      display: grid;
      grid-template-columns: 220px 1fr 180px;
      gap: 14px;
      align-items: end;
    }

    label {
      display: block;
      color: #64748b;
      font-size: 14px;
      font-weight: 1000;
      margin-bottom: 6px;
    }

    select,
    input[type="file"] {
      width: 100%;
      height: 42px;
      border: 1px solid #cbd5e1;
      border-radius: 12px;
      background: #ffffff;
      color: #102348;
      padding: 0 12px;
      font-size: 15px;
      font-weight: 900;
      font-family: inherit;
    }

    .preview-button {
      width: 100%;
      height: 42px;
      border: 0;
      border-radius: 12px;
      background: #f97316;
      color: white;
      font-size: 16px;
      font-weight: 1000;
      cursor: pointer;
    }

    .notice-box {
      margin-top: 18px;
      padding: 14px 16px;
      border: 1px dashed #94a3b8;
      border-radius: 16px;
      background: #f8fbff;
      color: #475569;
      font-size: 15px;
      font-weight: 800;
      line-height: 1.6;
    }

    .preview-area {
      margin-top: 18px;
      border: 1px solid #d7e1ef;
      border-radius: 16px;
      overflow: hidden;
      display: none;
    }

    .preview-header {
      background: #f1f5f9;
      padding: 12px 14px;
      font-size: 16px;
      font-weight: 1000;
    }

    .preview-content {
      padding: 14px;
      color: #64748b;
      font-weight: 800;
      line-height: 1.6;
    }

    .warning-box {
      margin-top: 14px;
      padding: 12px 14px;
      border-radius: 14px;
      background: #fff7ed;
      border: 1px solid #fdba74;
      color: #9a3412;
      font-size: 14px;
      font-weight: 900;
      line-height: 1.5;
    }

    @media (max-width: 1180px) {
      .import-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 760px) {
      .import-grid {
        grid-template-columns: 1fr;
      }

      .form-grid {
        grid-template-columns: 1fr;
      }

      .hero-title {
        font-size: 34px;
      }
    }
  </style>
</head>

<body>
  <div class="hero">
    <div class="hero-title">資料匯入</div>
    <div class="hero-subtitle">Excel / CSV / JSON / DB 匯入，先預覽檢查，再寫入訊南 ERP 系統。</div>
  </div>

  <main class="page">
    <div class="toolbar">
      <button type="button" class="home-button" onclick="goBackFromBuildings()">返回上一頁</button>
      <span class="hint">請先選擇匯入格式與資料類型，上傳後先預覽，不會立即寫入資料庫。</span>
    </div>

    <section class="import-grid">
      <div class="import-card">
        <div class="format-badge excel">Excel .xlsx</div>
        <div class="import-card-title">Excel 匯入</div>
        <div class="import-card-desc">
          適合公司日常使用。可匯入客戶、大樓、帳務、派工、人事資料。
        </div>
        <button type="button" class="import-button btn-excel" onclick="selectImportFormat('excel')">選擇 Excel 匯入</button>
      </div>

      <div class="import-card">
        <div class="format-badge csv">CSV .csv</div>
        <div class="import-card-title">CSV 匯入</div>
        <div class="import-card-desc">
          適合大量資料或舊系統匯出。建議使用 UTF-8 with BOM 避免中文亂碼。
        </div>
        <button type="button" class="import-button btn-csv" onclick="selectImportFormat('csv')">選擇 CSV 匯入</button>
      </div>

      <div class="import-card">
        <div class="format-badge json">JSON .json</div>
        <div class="import-card-title">JSON 匯入</div>
        <div class="import-card-desc">
          適合系統串接、API 資料交換、手機端或外部程式自動匯入。
        </div>
        <button type="button" class="import-button btn-json" onclick="selectImportFormat('json')">選擇 JSON 匯入</button>
      </div>

      <div class="import-card">
        <div class="format-badge db">DB / SQL</div>
        <div class="import-card-title">資料庫匯入</div>
        <div class="import-card-desc">
          適合舊電腦或舊系統使用 SQL / SQLite 資料庫時搬移資料。
        </div>
        <button type="button" class="import-button btn-db" onclick="selectImportFormat('db')">選擇 DB 匯入</button>
      </div>
    </section>

    <section class="panel">
      <div class="panel-title">匯入設定</div>

      <div class="form-grid">
        <div>
          <label>匯入資料類型</label>
          <select id="import_type">
            <option value="customers">客戶資料</option>
            <option value="buildings">大樓資料</option>
            <option value="billing">會計資料</option>
            <option value="tickets">派工案件</option>
            <option value="staff">人事資料</option>
            <option value="database">舊系統資料庫</option>
          </select>
        </div>

        <div>
          <label>選擇檔案</label>
          <input id="import_file" type="file" accept=".xlsx,.csv,.json,.db,.sqlite,.sqlite3,.sql">
        </div>

        <div>
          <label>目前格式</label>
          <button type="button" class="preview-button" id="preview_button" onclick="previewImport()">預覽資料</button>
        </div>
      </div>

      <div class="notice-box" id="import_notice">
        目前選擇：Excel 匯入。此頁先建立匯入入口與預覽流程，後續再接正式解析與資料庫寫入。
      </div>

      <div class="warning-box">
        DB / SQL 匯入建議只提供給系統管理者使用。舊系統資料庫通常需要先分析資料表結構，再對應到訊南 ERP 的客戶、大樓、帳務、派工與人事欄位。
      </div>

      <div class="preview-area" id="preview_area">
        <div class="preview-header">預覽結果</div>
        <div class="preview-content" id="preview_content">
          尚未選擇檔案。
        </div>
      </div>
    </section>
  </main>

  <script>
    let currentImportFormat = "excel";

    function selectImportFormat(format) {
      currentImportFormat = format;

      const fileInput = document.getElementById("import_file");
      const notice = document.getElementById("import_notice");

      if (format === "excel") {
        fileInput.accept = ".xlsx";
        notice.textContent = "目前選擇：Excel 匯入。適合公司日常人工整理資料。";
      }

      if (format === "csv") {
        fileInput.accept = ".csv";
        notice.textContent = "目前選擇：CSV 匯入。適合大量資料與舊系統匯出，建議使用 UTF-8 with BOM。";
      }

      if (format === "json") {
        fileInput.accept = ".json";
        notice.textContent = "目前選擇：JSON 匯入。適合 API、外部系統或程式資料交換。";
      }

      if (format === "db") {
        fileInput.accept = ".db,.sqlite,.sqlite3,.sql";
        notice.textContent = "目前選擇：DB / SQL 匯入。適合舊系統資料庫搬移，需先分析資料表結構再匯入。";
      }
    }

    function previewImport() {
      const fileInput = document.getElementById("import_file");
      const type = document.getElementById("import_type").value;
      const previewArea = document.getElementById("preview_area");
      const previewContent = document.getElementById("preview_content");

      previewArea.style.display = "block";

      if (!fileInput.files || !fileInput.files.length) {
        previewContent.textContent = "尚未選擇檔案。";
        return;
      }

      const file = fileInput.files[0];

      previewContent.innerHTML = `
        <div>匯入格式：${currentImportFormat.toUpperCase()}</div>
        <div>資料類型：${type}</div>
        <div>檔案名稱：${file.name}</div>
        <div>檔案大小：${Math.round(file.size / 1024)} KB</div>
        <div style="margin-top:8px;">下一步可接後端解析 API，先檢查欄位，再確認寫入資料庫。</div>
      `;
    }
  </script>
</body>
</html>
    """)

# SHINNAN_TICKET_CUSTOMER_LINK_START
def _ticket_customer_link_db_init():
    with _ticket_link_engine.begin() as conn:
        rows = conn.execute(_ticket_link_sql_text("PRAGMA table_info(tickets)")).fetchall()
        cols = [row[1] for row in rows]

        if "customer_no" not in cols:
            conn.execute(_ticket_link_sql_text("ALTER TABLE tickets ADD COLUMN customer_no TEXT DEFAULT ''"))

        if "building_no" not in cols:
            conn.execute(_ticket_link_sql_text("ALTER TABLE tickets ADD COLUMN building_no TEXT DEFAULT ''"))

        conn.execute(_ticket_link_sql_text("""
            CREATE TABLE IF NOT EXISTS ticket_customer_candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id INTEGER NOT NULL,
                ticket_no TEXT DEFAULT '',
                customer_name TEXT DEFAULT '',
                contact_phone TEXT DEFAULT '',
                service_address TEXT DEFAULT '',
                candidate_customer_no TEXT DEFAULT '',
                candidate_building_no TEXT DEFAULT '',
                match_type TEXT DEFAULT '',
                match_score INTEGER DEFAULT 0,
                review_status TEXT DEFAULT '待人工確認',
                review_note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))


@router.get("/api/admin/ticket-customer-candidates", summary="讀取派工客戶關聯候選")
def api_admin_ticket_customer_candidates(status: str = "待人工確認", q: str = "", limit: int = 200):
    _ticket_customer_link_db_init()

    limit = max(1, min(int(limit or 200), 500))

    where = []
    params = {"limit": limit}

    if status and status != "全部":
        where.append("c.review_status = :status")
        params["status"] = status

    if q:
        where.append("""
            (
                c.ticket_no LIKE :q OR
                c.customer_name LIKE :q OR
                c.contact_phone LIKE :q OR
                c.service_address LIKE :q
            )
        """)
        params["q"] = "%" + q + "%"

    where_sql = ""
    if where:
        where_sql = "WHERE " + " AND ".join(where)

    with _ticket_link_engine.begin() as conn:
        rows = conn.execute(
            _ticket_link_sql_text(f"""
                SELECT
                    c.id AS candidate_id,
                    c.ticket_id,
                    c.ticket_no,
                    c.customer_name,
                    c.contact_phone,
                    c.service_address,
                    c.candidate_customer_no,
                    c.candidate_building_no,
                    c.match_type,
                    c.match_score,
                    c.review_status,
                    c.review_note,
                    t.case_type,
                    t.status AS ticket_status,
                    t.appointment_date,
                    t.appointment_time,
                    t.assigned_engineer,
                    t.customer_no AS linked_customer_no,
                    t.building_no AS linked_building_no
                FROM ticket_customer_candidates c
                LEFT JOIN tickets t ON t.id = c.ticket_id
                {where_sql}
                ORDER BY
                    CASE c.review_status
                        WHEN '待人工確認' THEN 0
                        WHEN '已確認' THEN 1
                        ELSE 2
                    END,
                    c.ticket_id ASC
                LIMIT :limit
            """),
            params,
        ).mappings().fetchall()

    return _TicketLinkResponse(
        content=_ticket_link_json.dumps([dict(row) for row in rows], ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.get("/api/admin/ticket-customer-candidates/search-customers", summary="搜尋客戶供派工關聯")
def api_admin_ticket_customer_search_customers(q: str = "", limit: int = 30):
    _ticket_customer_link_db_init()

    q = (q or "").strip()
    limit = max(1, min(int(limit or 30), 80))

    where_sql = ""
    params = {"limit": limit}

    if q:
        where_sql = """
            WHERE
                c.customer_no LIKE :q OR
                c.customer_name LIKE :q OR
                c.customer_phone LIKE :q OR
                c.service_address LIKE :q OR
                b.name LIKE :q
        """
        params["q"] = "%" + q + "%"

    with _ticket_link_engine.begin() as conn:
        rows = conn.execute(
            _ticket_link_sql_text(f"""
                SELECT
                    c.customer_no,
                    c.customer_name,
                    c.customer_phone,
                    c.customer_type,
                    c.building_no,
                    COALESCE(b.name, CASE WHEN c.building_no = 'HOUSE' THEN '透天' ELSE '' END) AS building_name,
                    COALESCE(b.area, CASE WHEN c.building_no = 'HOUSE' THEN '透天' ELSE '' END) AS area,
                    c.service_address,
                    c.account_status,
                    c.payment_method,
                    c.arrears_status
                FROM customer_accounts c
                LEFT JOIN buildings b ON b.building_no = c.building_no
                {where_sql}
                ORDER BY c.customer_no
                LIMIT :limit
            """),
            params,
        ).mappings().fetchall()

    return _TicketLinkResponse(
        content=_ticket_link_json.dumps([dict(row) for row in rows], ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )


@router.post("/api/admin/ticket-customer-candidates/confirm", summary="確認派工案件關聯客戶")
async def api_admin_ticket_customer_candidates_confirm(request: _TicketLinkRequest):
    _ticket_customer_link_db_init()

    raw = (await request.body()).decode("utf-8")
    form = _ticket_link_parse_qs(raw)

    def val(name, default=""):
        return (form.get(name, [default])[0] or default).strip()

    candidate_id = val("candidate_id")
    customer_no = val("customer_no")
    review_note = val("review_note")

    if not candidate_id or not customer_no:
        return _TicketLinkResponse(
            content=_ticket_link_json.dumps({"ok": False, "error": "缺少 candidate_id 或 customer_no"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    with _ticket_link_engine.begin() as conn:
        candidate = conn.execute(
            _ticket_link_sql_text("""
                SELECT id, ticket_id, ticket_no
                FROM ticket_customer_candidates
                WHERE id = :id
                LIMIT 1
            """),
            {"id": candidate_id},
        ).mappings().first()

        if not candidate:
            return _TicketLinkResponse(
                content=_ticket_link_json.dumps({"ok": False, "error": "找不到候選資料"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=404,
            )

        customer = conn.execute(
            _ticket_link_sql_text("""
                SELECT customer_no, building_no
                FROM customer_accounts
                WHERE customer_no = :customer_no
                LIMIT 1
            """),
            {"customer_no": customer_no},
        ).mappings().first()

        if not customer:
            return _TicketLinkResponse(
                content=_ticket_link_json.dumps({"ok": False, "error": "找不到客戶資料"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=404,
            )

        conn.execute(
            _ticket_link_sql_text("""
                UPDATE tickets
                SET customer_no = :customer_no,
                    building_no = :building_no
                WHERE id = :ticket_id
            """),
            {
                "customer_no": customer["customer_no"],
                "building_no": customer["building_no"],
                "ticket_id": candidate["ticket_id"],
            },
        )

        conn.execute(
            _ticket_link_sql_text("""
                UPDATE ticket_customer_candidates
                SET candidate_customer_no = :customer_no,
                    candidate_building_no = :building_no,
                    match_type = 'manual_confirmed',
                    match_score = 100,
                    review_status = '已確認',
                    review_note = :review_note,
                    updated_at = datetime('now')
                WHERE id = :candidate_id
            """),
            {
                "customer_no": customer["customer_no"],
                "building_no": customer["building_no"],
                "review_note": review_note or "人工確認關聯",
                "candidate_id": candidate_id,
            },
        )

    return _TicketLinkResponse(
        content=_ticket_link_json.dumps({"ok": True}, ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )



@router.post("/api/admin/ticket-customer-candidates/create-customer-and-confirm", summary="由派工資料建立新客戶並綁定")
async def api_admin_ticket_customer_create_customer_and_confirm(request: _TicketLinkRequest):
    _ticket_customer_link_db_init()

    raw = (await request.body()).decode("utf-8")
    form = _ticket_link_parse_qs(raw)

    def val(name, default=""):
        return (form.get(name, [default])[0] or default).strip()

    candidate_id = val("candidate_id")
    review_note = val("review_note", "由派工資料建立新客戶並綁定")

    if not candidate_id:
        return _TicketLinkResponse(
            content=_ticket_link_json.dumps({"ok": False, "error": "缺少 candidate_id"}, ensure_ascii=False),
            media_type="application/json; charset=utf-8",
            status_code=400,
        )

    with _ticket_link_engine.begin() as conn:
        candidate = conn.execute(
            _ticket_link_sql_text("""
                SELECT
                    id,
                    ticket_id,
                    ticket_no,
                    customer_name,
                    contact_phone,
                    service_address
                FROM ticket_customer_candidates
                WHERE id = :id
                LIMIT 1
            """),
            {"id": candidate_id},
        ).mappings().first()

        if not candidate:
            return _TicketLinkResponse(
                content=_ticket_link_json.dumps({"ok": False, "error": "找不到候選資料"}, ensure_ascii=False),
                media_type="application/json; charset=utf-8",
                status_code=404,
            )

        # 產生下一個 customer_no
        last_no = conn.execute(
            _ticket_link_sql_text("""
                SELECT customer_no
                FROM customer_accounts
                WHERE customer_no LIKE 'C%'
                ORDER BY customer_no DESC
                LIMIT 1
            """)
        ).scalar()

        try:
            next_number = int(str(last_no or "C000000")[1:]) + 1
        except Exception:
            next_number = 1

        customer_no = "C" + str(next_number).zfill(6)

        service_address = candidate["service_address"] or ""
        if service_address and not service_address.startswith("透天"):
            service_address = "透天 " + service_address

        conn.execute(
            _ticket_link_sql_text("""
                INSERT INTO customer_accounts (
                    customer_no,
                    customer_name,
                    customer_phone,
                    customer_type,
                    building_no,
                    floor_text,
                    room_no,
                    service_address,
                    service_type,
                    package_name,
                    monthly_fee,
                    install_date,
                    contract_status,
                    account_status,
                    payment_method,
                    billing_day,
                    arrears_status,
                    equipment_no,
                    cm_mac,
                    ip_address,
                    signal_note,
                    billing_note,
                    service_note,
                    created_at,
                    updated_at
                )
                VALUES (
                    :customer_no,
                    :customer_name,
                    :customer_phone,
                    '派工建立',
                    'HOUSE',
                    '',
                    '',
                    :service_address,
                    '',
                    '',
                    0,
                    '',
                    '待確認',
                    '待確認',
                    '',
                    0,
                    '待確認',
                    '',
                    '',
                    '',
                    '',
                    '由派工案件建立，尚未設定帳務服務。',
                    '由派工案件 ' || :ticket_no || ' 建立。',
                    datetime('now'),
                    datetime('now')
                )
            """),
            {
                "customer_no": customer_no,
                "customer_name": candidate["customer_name"] or "未命名客戶",
                "customer_phone": candidate["contact_phone"] or "",
                "service_address": service_address,
                "ticket_no": candidate["ticket_no"] or "",
            },
        )

        conn.execute(
            _ticket_link_sql_text("""
                UPDATE tickets
                SET customer_no = :customer_no,
                    building_no = 'HOUSE'
                WHERE id = :ticket_id
            """),
            {
                "customer_no": customer_no,
                "ticket_id": candidate["ticket_id"],
            },
        )

        conn.execute(
            _ticket_link_sql_text("""
                UPDATE ticket_customer_candidates
                SET candidate_customer_no = :customer_no,
                    candidate_building_no = 'HOUSE',
                    match_type = 'manual_created_customer',
                    match_score = 100,
                    review_status = '已確認',
                    review_note = :review_note,
                    updated_at = datetime('now')
                WHERE id = :candidate_id
            """),
            {
                "customer_no": customer_no,
                "review_note": review_note,
                "candidate_id": candidate_id,
            },
        )

    return _TicketLinkResponse(
        content=_ticket_link_json.dumps(
            {
                "ok": True,
                "customer_no": customer_no,
                "building_no": "HOUSE",
            },
            ensure_ascii=False,
        ),
        media_type="application/json; charset=utf-8",
    )



@router.get("/admin/ticket-customer-link", response_class=_TicketLinkHTMLResponse)
def admin_ticket_customer_link_page():
    return """
<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <title>派工客戶關聯確認｜訊南 ERP</title>
  <style>
    body {
      margin: 0;
      background: #eef3f9;
      color: #102348;
      font-family: "Noto Sans TC", "Microsoft JhengHei", Arial, sans-serif;
    }

    .wrap {
      max-width: 1680px;
      margin: 0 auto;
      padding: 18px;
    }

    .hero {
      border-radius: 22px;
      padding: 22px;
      color: #fff;
      background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
      margin-bottom: 12px;
      box-shadow: 0 16px 44px rgba(15,23,42,.18);
    }

    h1 {
      margin: 0 0 6px;
      font-size: 36px;
      font-weight: 1000;
    }

    .sub {
      font-size: 15px;
      font-weight: 900;
      opacity: .92;
    }

    .toolbar {
      display: grid;
      grid-template-columns: auto auto 160px 1fr auto;
      gap: 8px;
      margin: 12px 0;
      align-items: center;
    }

    button,
    select,
    input {
      height: 34px;
      border-radius: 10px;
      border: 1px solid #cbd5e1;
      padding: 0 10px;
      font-size: 13px;
      font-weight: 900;
      box-sizing: border-box;
    }

    button {
      border: 0;
      background: #365ee8;
      color: #fff;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      line-height: 1;
    }

    button.gray {
      background: #64748b;
    }

    button.green {
      background: #16a34a;
    }

    .summary {
      color: #475569;
      font-size: 13px;
      font-weight: 900;
      margin: 4px 0 10px;
    }

    .list {
      display: grid;
      gap: 10px;
    }

    .card {
      background: #fff;
      border: 1px solid #d7e1ef;
      border-radius: 18px;
      padding: 12px;
      box-shadow: 0 8px 24px rgba(15,23,42,.06);
    }

    .card.done {
      opacity: .72;
      background: #f8fafc;
    }

    .card-head {
      display: grid;
      grid-template-columns: 180px 1fr 160px;
      gap: 10px;
      align-items: start;
    }

    .ticket-no {
      font-size: 16px;
      font-weight: 1000;
      color: #1d4ed8;
    }

    .main-title {
      font-size: 18px;
      font-weight: 1000;
      color: #102348;
    }

    .muted {
      margin-top: 2px;
      color: #64748b;
      font-size: 12px;
      font-weight: 850;
      line-height: 1.45;
    }

    .pill {
      display: inline-flex;
      justify-content: center;
      align-items: center;
      min-height: 24px;
      padding: 2px 10px;
      border-radius: 999px;
      background: #ffedd5;
      color: #9a3412;
      font-size: 12px;
      font-weight: 1000;
    }

    .pill.done {
      background: #dcfce7;
      color: #166534;
    }

    .link-area {
      margin-top: 10px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
    }

    .results {
      margin-top: 8px;
      display: grid;
      gap: 6px;
    }

    .customer-row {
      border: 1px solid #dbe7f5;
      border-radius: 12px;
      padding: 8px;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 8px;
      align-items: center;
      background: #f8fafc;
    }

    .customer-name {
      font-size: 14px;
      font-weight: 1000;
      color: #102348;
    }

    .empty {
      padding: 18px;
      background: #fff;
      border: 1px dashed #cbd5e1;
      border-radius: 16px;
      color: #64748b;
      font-size: 15px;
      font-weight: 1000;
      text-align: center;
    }

    @media (max-width: 760px) {
      .wrap {
        padding: 10px;
      }

      .hero {
        padding: 16px;
      }

      h1 {
        font-size: 28px;
      }

      .toolbar {
        grid-template-columns: 1fr 1fr;
      }

      .toolbar input {
        grid-column: 1 / -1;
      }

      .card-head {
        grid-template-columns: 1fr;
      }

      .link-area {
        grid-template-columns: 1fr;
      }

      .customer-row {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>

<body>
  <div class="wrap">
    <section class="hero">
      <h1>派工客戶關聯確認</h1>
      <div class="sub">只做人工確認，不自動亂接客戶。確認後才寫回 tickets.customer_no / building_no。</div>
    </section>

    <div class="toolbar">
      <button type="button" onclick="history.back()">返回上一頁</button>
      <button type="button" class="gray" onclick="location.href='/?ts=' + Date.now()">回入口</button>

      <select id="status_filter">
        <option value="全部" selected>全部</option>
        <option value="待建立客戶">待建立客戶</option>
        <option value="待人工確認">待人工確認</option>
        <option value="已確認">已確認</option>
      </select>

      <input id="keyword" placeholder="搜尋派工單號 / 客戶名 / 電話 / 地址">

      <button type="button" onclick="loadCandidates()">搜尋</button>
    </div>

    <div id="summary" class="summary">資料載入中...</div>

    <main id="list" class="list"></main>
  </div>

  <script>
    let candidates = [];

    function esc(v) {
      return String(v ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    async function loadCandidates() {
      const params = new URLSearchParams();
      params.set("status", document.getElementById("status_filter").value);
      params.set("q", document.getElementById("keyword").value.trim());
      params.set("ts", Date.now());

      const res = await fetch("/api/admin/ticket-customer-candidates?" + params.toString(), {cache: "no-store"});

      if (!res.ok) {
        document.getElementById("list").innerHTML = '<div class="empty">API 讀取失敗：' + res.status + '</div>';
        return;
      }

      candidates = await res.json();
      renderCandidates();
    }

    function renderCandidates() {
      document.getElementById("summary").textContent = "目前顯示 " + candidates.length + " 筆";

      const box = document.getElementById("list");

      if (!candidates.length) {
        box.innerHTML = '<div class="empty">沒有符合條件的派工案件。</div>';
        return;
      }

      box.innerHTML = candidates.map(function (item) {
        const done = item.review_status === "已確認";

        return `
          <section class="card ${done ? "done" : ""}">
            <div class="card-head">
              <div>
                <div class="ticket-no">${esc(item.ticket_no)}</div>
                <div class="muted">${esc(item.case_type || "-")}｜${esc(item.ticket_status || "-")}</div>
              </div>

              <div>
                <div class="main-title">${esc(item.customer_name || "-")}｜${esc(item.contact_phone || "-")}</div>
                <div class="muted">地址：${esc(item.service_address || "-")}</div>
                <div class="muted">工程師：${esc(item.assigned_engineer || "-")}｜預約：${esc(item.appointment_date || "-")} ${esc(item.appointment_time || "")}</div>
              </div>

              <div>
                <span class="pill ${done ? "done" : ""}">${esc(item.review_status || "-")}</span>
                <div class="muted">目前關聯：${esc(item.linked_customer_no || "未關聯")}</div>
              </div>
            </div>

            ${done ? "" : `
              <div class="link-area">
                <input id="q_${item.candidate_id}" value="${esc(item.customer_name || item.contact_phone || "")}" placeholder="搜尋客戶姓名 / 電話 / 客戶編號 / 地址">
                <button type="button" onclick="searchCustomers(${item.candidate_id})">搜尋客戶</button>
              </div>

              <div id="results_${item.candidate_id}" class="results"></div>
            `}
          </section>
        `;
      }).join("");
    }

    async function searchCustomers(candidateId) {
      const input = document.getElementById("q_" + candidateId);
      const q = input ? input.value.trim() : "";

      const box = document.getElementById("results_" + candidateId);
      box.innerHTML = '<div class="muted">搜尋中...</div>';

      const params = new URLSearchParams();
      params.set("q", q);
      params.set("limit", "20");
      params.set("ts", Date.now());

      const res = await fetch("/api/admin/ticket-customer-candidates/search-customers?" + params.toString(), {cache: "no-store"});

      if (!res.ok) {
        box.innerHTML = '<div class="muted">搜尋失敗：' + res.status + '</div>';
        return;
      }

      const rows = await res.json();

      if (!rows.length) {
        box.innerHTML = `
          <div class="customer-row">
            <div>
              <div class="customer-name">找不到既有客戶</div>
              <div class="muted">可由此派工資料建立一筆新客戶，並直接綁定此派工單。</div>
            </div>
            <button type="button" class="green" onclick="createCustomerAndBind(${candidateId})">建立新客戶並綁定</button>
          </div>
        `;
        return;
      }

      box.innerHTML = rows.map(function (c) {
        return `
          <div class="customer-row">
            <div>
              <div class="customer-name">${esc(c.customer_no)}｜${esc(c.customer_name)}｜${esc(c.customer_phone)}</div>
              <div class="muted">${esc(c.area || "-")}｜${esc(c.building_name || "-")}｜${esc(c.service_address || "-")}</div>
              <div class="muted">狀態：${esc(c.account_status || "-")}｜欠費：${esc(c.arrears_status || "-")}</div>
            </div>

            <button type="button" class="green" onclick="confirmCustomer(${candidateId}, '${esc(c.customer_no)}')">確認綁定</button>
          </div>
        `;
      }).join("");
    }

    async function createCustomerAndBind(candidateId) {
      if (!confirm("確定要由此派工資料建立新客戶，並綁定此派工案件？")) return;

      const body = new URLSearchParams();
      body.set("candidate_id", candidateId);
      body.set("review_note", "由派工資料建立新客戶並綁定");

      const res = await fetch("/api/admin/ticket-customer-candidates/create-customer-and-confirm", {
        method: "POST",
        body: body
      });

      const data = await res.json();

      if (!res.ok || !data.ok) {
        alert(data.error || "建立新客戶失敗");
        return;
      }

      alert("已建立新客戶：" + data.customer_no + "，並完成派工綁定。");
      loadCandidates();
    }


    async function confirmCustomer(candidateId, customerNo) {
      if (!confirm("確定要將此派工案件綁定到客戶 " + customerNo + "？")) return;

      const body = new URLSearchParams();
      body.set("candidate_id", candidateId);
      body.set("customer_no", customerNo);
      body.set("review_note", "人工確認綁定");

      const res = await fetch("/api/admin/ticket-customer-candidates/confirm", {
        method: "POST",
        body: body
      });

      const data = await res.json();

      if (!res.ok || !data.ok) {
        alert(data.error || "確認失敗");
        return;
      }

      alert("已完成綁定");
      loadCandidates();
    }

    document.getElementById("keyword").addEventListener("keydown", function (event) {
      if (event.key === "Enter") loadCandidates();
    });

    document.getElementById("status_filter").addEventListener("change", loadCandidates);

    loadCandidates();
  </script>
</body>
</html>
"""
# SHINNAN_TICKET_CUSTOMER_LINK_END



# SHINNAN_EMPLOYEE_PROFILES_API_START
def _employee_profiles_db_init():
    with _employee_profile_engine.begin() as conn:
        conn.execute(_employee_profile_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT UNIQUE NOT NULL,
                display_name TEXT NOT NULL,
                department TEXT DEFAULT '',
                role TEXT DEFAULT '',
                position_title TEXT DEFAULT '',
                gender TEXT DEFAULT '',
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                employment_status TEXT DEFAULT '在職',
                hire_date TEXT DEFAULT '',
                permission_scope TEXT DEFAULT '',
                app_access INTEGER DEFAULT 1,
                note TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        cols = [row[1] for row in conn.execute(_employee_profile_sql_text("PRAGMA table_info(employee_profiles)")).fetchall()]
        if "gender" not in cols:
            conn.execute(_employee_profile_sql_text("ALTER TABLE employee_profiles ADD COLUMN gender TEXT DEFAULT ''"))


@router.get("/api/admin/employees", summary="讀取員工主檔")
def api_admin_employees(
    department: str = "全部",
    role: str = "全部",
    status: str = "全部",
    q: str = "",
):
    _employee_profiles_db_init()

    where = []
    params = {}

    if department and department != "全部":
        where.append("department = :department")
        params["department"] = department

    if role and role != "全部":
        where.append("role = :role")
        params["role"] = role

    if status and status != "全部":
        where.append("employment_status = :status")
        params["status"] = status

    if q:
        where.append("""
            (
                staff_code LIKE :q OR
                display_name LIKE :q OR
                phone LIKE :q OR
                department LIKE :q OR
                position_title LIKE :q
            )
        """)
        params["q"] = "%" + q + "%"

    where_sql = ""
    if where:
        where_sql = "WHERE " + " AND ".join(where)

    with _employee_profile_engine.begin() as conn:
        rows = conn.execute(
            _employee_profile_sql_text(f"""
                SELECT
                    staff_code,
                    display_name,
                    department,
                    role,
                    position_title,
                    gender,
                    phone,
                    email,
                    employment_status,
                    hire_date,
                    permission_scope,
                    app_access,
                    note,
                    created_at,
                    updated_at
                FROM employee_profiles
                {where_sql}
                ORDER BY
                    CASE department
                        WHEN '管理部' THEN 1
                        WHEN '業務部' THEN 2
                        WHEN '工程部' THEN 3
                        WHEN '維修部' THEN 4
                        WHEN '北高' THEN 5
                        WHEN '南高' THEN 6
                        WHEN '東區' THEN 7
                        WHEN '安平' THEN 8
                        WHEN '北區' THEN 9
                        WHEN '永康' THEN 10
                        WHEN '北台南' THEN 11
                        WHEN '帳務部' THEN 12
                        WHEN '人事部' THEN 13
                        WHEN '客服部' THEN 14
                        WHEN '倉管部' THEN 15
                        WHEN '專案部' THEN 16
                        WHEN '產品部' THEN 17
                        ELSE 99
                    END,
                    staff_code
            """),
            params,
        ).mappings().fetchall()

    return _EmployeeProfileResponse(
        content=_employee_profile_json.dumps([dict(row) for row in rows], ensure_ascii=False),
        media_type="application/json; charset=utf-8",
    )
# SHINNAN_EMPLOYEE_PROFILES_API_END


# SHINNAN_EMPLOYEE_ROSTER_PAGE_START_REMOVED_CLEANUP_STEP1_20260502
# This obsolete route block was removed during pages.py cleanup step 1.
# SHINNAN_EMPLOYEE_ROSTER_PAGE_END_REMOVED_CLEANUP_STEP1_20260502


# SHINNAN_EMPLOYEE_SETTINGS_START

def _calc_annual_leave_days_for_employee_settings(hire_date_text):
    from datetime import date, datetime

    if not hire_date_text:
        return 0

    try:
        hire_date = datetime.strptime(str(hire_date_text)[:10], "%Y-%m-%d").date()
    except Exception:
        return 0

    today = date.today()

    if hire_date > today:
        return 0

    years = today.year - hire_date.year
    if (today.month, today.day) < (hire_date.month, hire_date.day):
        years -= 1

    # 未滿 6 個月
    months = (today.year - hire_date.year) * 12 + today.month - hire_date.month
    if today.day < hire_date.day:
        months -= 1

    if months < 6:
        return 0

    if years < 1:
        return 3
    if years < 2:
        return 7
    if years < 3:
        return 10
    if years < 5:
        return 14
    if years < 10:
        return 15

    return min(30, 15 + (years - 10 + 1))



def _employee_settings_hash_pin(pin, salt):
    return _employee_settings_hashlib.sha256((str(pin) + ":" + str(salt)).encode("utf-8")).hexdigest()


def _employee_settings_db_init():
    with _employee_settings_engine.begin() as conn:
        conn.execute(_employee_settings_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_leave_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT NOT NULL,
                display_name TEXT DEFAULT '',
                department TEXT DEFAULT '',
                period_label TEXT DEFAULT '',
                leave_date TEXT DEFAULT '',
                leave_type TEXT DEFAULT '',
                start_time TEXT DEFAULT '',
                end_time TEXT DEFAULT '',
                proof_required INTEGER DEFAULT 0,
                proof_image_data TEXT DEFAULT '',
                note TEXT DEFAULT '',
                review_status TEXT DEFAULT '待審核',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(_employee_settings_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_rest_month_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT NOT NULL,
                display_name TEXT DEFAULT '',
                department TEXT DEFAULT '',
                year INTEGER NOT NULL,
                month INTEGER NOT NULL,
                required_rest_days REAL DEFAULT 8,
                selected_dates TEXT DEFAULT '[]',
                rest_count REAL DEFAULT 0,
                confirm_incomplete INTEGER DEFAULT 0,
                review_status TEXT DEFAULT '待審核',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(staff_code, year, month)
            )
        """))

        conn.execute(_employee_settings_sql_text("""
            CREATE TABLE IF NOT EXISTS employee_proxy_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_code TEXT UNIQUE NOT NULL,
                display_name TEXT DEFAULT '',
                department TEXT DEFAULT '',
                proxy_one_staff_code TEXT DEFAULT '',
                proxy_one_name TEXT DEFAULT '',
                proxy_two_staff_code TEXT DEFAULT '',
                proxy_two_name TEXT DEFAULT '',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(_employee_settings_sql_text("""
            CREATE TABLE IF NOT EXISTS company_holidays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                holiday_date TEXT UNIQUE NOT NULL,
                title TEXT DEFAULT '國定假日',
                enabled INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """))


def _employee_leave_period_label():
    from datetime import datetime
    now = datetime.now()
    month = now.month
    next_month = month + 1
    if next_month > 12:
        next_month = 1
    return f"{month}-{next_month}月"

















