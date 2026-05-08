
    function goBackToEngineeringApp() {
      if (window.history.length > 1) {
        window.history.back();
        return;
      }

      location.href = "/app/engineering";
    }

    const engineeringSchedules = [
      {
            "id": "ENG-202604-001",
            "title": "大樓工設網路施工",
            "building": "東方紐約",
            "type": "網路施工",
            "status": "施工中",
            "dispatchDate": "2026-04-01",
            "surveyDate": "2026-04-02",
            "startDate": "2026-05-02",
            "endDate": "2026-06-15",
            "acceptanceDate": "2026-06-22",
            "duration": "45 天",
            "engineer": "工程一組",
            "note": "主幹光纖進線、弱電箱整理、交換器上架、各樓層網路測線。施工期跨 6/15。"
      },
      {
            "id": "ENG-202604-002",
            "title": "社區攝影機增設工程",
            "building": "仁義新城",
            "type": "攝影機施工",
            "status": "待施工",
            "dispatchDate": "2026-04-03",
            "surveyDate": "2026-04-05",
            "startDate": "2026-05-20",
            "endDate": "2026-05-24",
            "acceptanceDate": "2026-05-31",
            "duration": "5 天",
            "engineer": "工程二組",
            "note": "地下室車道、管理室門口、電梯口新增攝影機。"
      },
      {
            "id": "ENG-202604-003",
            "title": "網路與監視器整合施工",
            "building": "北安御品",
            "type": "網路 + CCTV",
            "status": "待驗收",
            "dispatchDate": "2026-03-25",
            "surveyDate": "2026-03-28",
            "startDate": "2026-05-01",
            "endDate": "2026-05-03",
            "acceptanceDate": "2026-05-10",
            "duration": "3 天",
            "engineer": "工程三組",
            "note": "網路主線已完成，攝影機角度需與管委會確認。"
      },
      {
            "id": "ENG-202604-004",
            "title": "大樓管道與機房改善",
            "building": "永華麗景",
            "type": "工設改善",
            "status": "施工中",
            "dispatchDate": "2026-04-02",
            "surveyDate": "2026-04-04",
            "startDate": "2026-05-04",
            "endDate": "2026-06-05",
            "acceptanceDate": "2026-06-12",
            "duration": "33 天",
            "engineer": "工程一組",
            "note": "機房機櫃重新整理、線路標籤重貼、舊線汰換。"
      },
      {
            "id": "ENG-202604-005",
            "title": "大樓網路設備更換",
            "building": "成功國宅",
            "type": "網路施工",
            "status": "待施工",
            "dispatchDate": "2026-04-10",
            "surveyDate": "2026-04-12",
            "startDate": "2026-06-01",
            "endDate": "2026-06-04",
            "acceptanceDate": "2026-06-11",
            "duration": "4 天",
            "engineer": "工程二組",
            "note": "更換核心交換器、重新整理配線與標籤。"
      },
      {
            "id": "ENG-202604-006",
            "title": "停車場攝影機補點",
            "building": "小北世家",
            "type": "攝影機施工",
            "status": "待施工",
            "dispatchDate": "2026-04-14",
            "surveyDate": "2026-04-18",
            "startDate": "2026-06-10",
            "endDate": "2026-06-13",
            "acceptanceDate": "2026-06-20",
            "duration": "4 天",
            "engineer": "工程三組",
            "note": "地下室 B1/B2 攝影機補點與角度調整。"
      },
      {
            "id": "ENG-202604-007",
            "title": "光纖主幹改善",
            "building": "嘉樂首府",
            "type": "網路施工",
            "status": "已派工未勘場",
            "dispatchDate": "2026-05-01",
            "surveyDate": "",
            "startDate": "",
            "endDate": "",
            "acceptanceDate": "",
            "duration": "未排定",
            "engineer": "工程一組",
            "note": "已派工，尚未安排勘場日期。時間未到不畫勘場 / 施工 / 驗收。"
      },
      {
            "id": "ENG-202604-008",
            "title": "社區弱電箱整理",
            "building": "勝利雅築",
            "type": "工設改善",
            "status": "已勘場待施工",
            "dispatchDate": "2026-04-07",
            "surveyDate": "2026-04-09",
            "startDate": "",
            "endDate": "",
            "acceptanceDate": "",
            "duration": "未排定",
            "engineer": "工程二組",
            "note": "已完成勘場，待公司端排定施工日期。"
      },
      {
            "id": "ENG-202604-009",
            "title": "電梯口攝影機施工",
            "building": "安平國宅",
            "type": "攝影機施工",
            "status": "施工中",
            "dispatchDate": "2026-04-01",
            "surveyDate": "2026-04-03",
            "startDate": "2026-04-29",
            "endDate": "2026-05-06",
            "acceptanceDate": "2026-05-13",
            "duration": "8 天",
            "engineer": "工程三組",
            "note": "電梯口與公共走道攝影機施工。"
      },
      {
            "id": "ENG-202604-010",
            "title": "機房設備移機",
            "building": "中正名門",
            "type": "工設改善",
            "status": "待驗收",
            "dispatchDate": "2026-03-20",
            "surveyDate": "2026-03-25",
            "startDate": "2026-04-25",
            "endDate": "2026-04-30",
            "acceptanceDate": "2026-05-07",
            "duration": "6 天",
            "engineer": "工程一組",
            "note": "機房設備已完成移機，等待管理室驗收。"
      },
      {
            "id": "ENG-202604-011",
            "title": "社區 AP 佈建",
            "building": "仁德家園",
            "type": "網路施工",
            "status": "待施工",
            "dispatchDate": "2026-04-20",
            "surveyDate": "2026-04-22",
            "startDate": "2026-05-28",
            "endDate": "2026-06-08",
            "acceptanceDate": "2026-06-15",
            "duration": "12 天",
            "engineer": "工程二組",
            "note": "公共區域 AP 佈建與漫遊測試。"
      },
      {
            "id": "ENG-202604-012",
            "title": "監控主機更新",
            "building": "長榮新城",
            "type": "攝影機施工",
            "status": "已派工未勘場",
            "dispatchDate": "2026-05-03",
            "surveyDate": "",
            "startDate": "",
            "endDate": "",
            "acceptanceDate": "",
            "duration": "未排定",
            "engineer": "工程三組",
            "note": "已派工，尚未勘場，需確認 NVR 容量與既有線路。"
      },
      {
            "id": "ENG-202604-013",
            "title": "大樓網路幹線重整",
            "building": "東門透天",
            "type": "網路施工",
            "status": "施工中",
            "dispatchDate": "2026-03-28",
            "surveyDate": "2026-04-01",
            "startDate": "2026-04-28",
            "endDate": "2026-05-25",
            "acceptanceDate": "2026-06-01",
            "duration": "28 天",
            "engineer": "工程一組",
            "note": "網路幹線與樓層弱電箱重整。"
      },
      {
            "id": "ENG-202604-014",
            "title": "地下室攝影機線路更新",
            "building": "文化雅苑",
            "type": "攝影機施工",
            "status": "待施工",
            "dispatchDate": "2026-04-15",
            "surveyDate": "2026-04-17",
            "startDate": "2026-06-18",
            "endDate": "2026-06-23",
            "acceptanceDate": "2026-06-30",
            "duration": "6 天",
            "engineer": "工程二組",
            "note": "地下室舊線路更新，需避開住戶停車尖峰。"
      },
      {
            "id": "ENG-202604-015",
            "title": "機櫃與配線標籤工程",
            "building": "新光華廈",
            "type": "工設改善",
            "status": "已完工",
            "dispatchDate": "2026-03-10",
            "surveyDate": "2026-03-15",
            "startDate": "2026-04-15",
            "endDate": "2026-04-18",
            "acceptanceDate": "2026-04-25",
            "duration": "4 天",
            "engineer": "工程三組",
            "note": "已完工，配線標籤與機櫃整理完成。"
      },
      {
            "id": "ENG-202604-016",
            "title": "社區網路升級",
            "building": "海安首席",
            "type": "網路施工",
            "status": "施工中",
            "dispatchDate": "2026-04-05",
            "surveyDate": "2026-04-08",
            "startDate": "2026-05-12",
            "endDate": "2026-06-30",
            "acceptanceDate": "2026-07-07",
            "duration": "50 天",
            "engineer": "工程一組",
            "note": "社區網路升級，施工期跨 6 月底。"
      },
      {
            "id": "ENG-202604-017",
            "title": "公共區域攝影機增設",
            "building": "府前麗景",
            "type": "攝影機施工",
            "status": "已勘場待施工",
            "dispatchDate": "2026-04-25",
            "surveyDate": "2026-04-27",
            "startDate": "",
            "endDate": "",
            "acceptanceDate": "",
            "duration": "未排定",
            "engineer": "工程二組",
            "note": "已勘場，等待管委會確認點位。"
      },
      {
            "id": "ENG-202604-018",
            "title": "大樓弱電管道查修",
            "building": "民生大樓",
            "type": "工設改善",
            "status": "已派工未勘場",
            "dispatchDate": "2026-05-05",
            "surveyDate": "",
            "startDate": "",
            "endDate": "",
            "acceptanceDate": "",
            "duration": "未排定",
            "engineer": "工程三組",
            "note": "已派工但尚未勘場，需先確認管道阻塞位置。"
      },
      {
            "id": "ENG-202604-019",
            "title": "網路設備汰換工程",
            "building": "健康新城",
            "type": "網路施工",
            "status": "待驗收",
            "dispatchDate": "2026-03-30",
            "surveyDate": "2026-04-02",
            "startDate": "2026-04-30",
            "endDate": "2026-05-09",
            "acceptanceDate": "2026-05-16",
            "duration": "10 天",
            "engineer": "工程一組",
            "note": "交換器汰換完成，待驗收測速與交接。"
      },
      {
            "id": "ENG-202604-020",
            "title": "車道攝影機與網路整合",
            "building": "南門御所",
            "type": "網路 + CCTV",
            "status": "待施工",
            "dispatchDate": "2026-04-28",
            "surveyDate": "2026-05-01",
            "startDate": "2026-06-05",
            "endDate": "2026-06-15",
            "acceptanceDate": "2026-06-22",
            "duration": "11 天",
            "engineer": "工程二組",
            "note": "車道攝影機與網路整合，需與管理室確認施工時段。"
      }
];

    let currentProject = null;

    function escapeHtml(value) {
      return String(value == null ? "" : value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }

    function setText(id, value) {
      const box = document.getElementById(id);
      if (box) box.textContent = value;
    }

    function parseDateOnly(value) {
      const raw = String(value || "").trim();
      const parts = raw.split("-");
      if (parts.length !== 3) return null;
      return new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
    }

    function formatMonthDay(date) {
      const mm = String(date.getMonth() + 1).padStart(2, "0");
      const dd = String(date.getDate()).padStart(2, "0");
      return mm + "/" + dd;
    }

    function addDays(date, days) {
      const d = new Date(date.getTime());
      d.setDate(d.getDate() + days);
      return d;
    }

    function clamp(value, min, max) {
      return Math.max(min, Math.min(max, value));
    }

    function getMonthWeekRanges(items) {
      const baseDate = items
        .map(function(item) { return parseDateOnly(item.startDate); })
        .filter(Boolean)
        .sort(function(a, b) { return a - b; })[0] || new Date();

      const year = baseDate.getFullYear();
      const month = baseDate.getMonth();

      const monthStart = new Date(year, month, 1);
      const monthEnd = new Date(year, month + 1, 0);

      const weeks = [];
      let cursor = new Date(monthStart.getTime());
      let index = 1;

      while (cursor <= monthEnd) {
        const start = new Date(cursor.getTime());
        const end = addDays(start, 6);

        if (end > monthEnd) {
          end.setTime(monthEnd.getTime());
        }

        weeks.push({
          index: index,
          label: "第 " + index + " 週",
          rangeLabel: formatMonthDay(start) + "-" + formatMonthDay(end),
          start: start,
          end: end
        });

        cursor = addDays(end, 1);
        index += 1;
      }

      return weeks;
    }

    function getNearestTimelineItems(items) {
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      return items
        .map(function(item) {
          const start = parseDateOnly(item.startDate);
          const end = parseDateOnly(item.endDate);

          let distance = 999999999;

          if (start && end) {
            if (today >= start && today <= end) {
              distance = 0;
            } else if (today < start) {
              distance = start - today;
            } else {
              distance = today - end;
            }
          }

          return {item: item, distance: distance};
        })
        .sort(function(a, b) { return a.distance - b.distance; })
        .slice(0, 2)
        .map(function(x) { return x.item; });
    }

    function getWeekSpanForProject(project, weeks) {
      const start = parseDateOnly(project.startDate);
      const end = parseDateOnly(project.endDate);

      if (!start || !end || !weeks.length) {
        return null;
      }

      let startIndex = -1;
      let endIndex = -1;

      weeks.forEach(function(week, idx) {
        const overlap = start <= week.end && end >= week.start;

        if (overlap) {
          if (startIndex < 0) startIndex = idx;
          endIndex = idx;
        }
      });

      if (startIndex < 0 || endIndex < 0) {
        return null;
      }

      return {
        startIndex: startIndex,
        endIndex: endIndex,
        span: endIndex - startIndex + 1
      };
    }

    function renderEngineeringTimeline() {
      const box = document.getElementById("engineering_timeline");
      if (!box) return;

      while (box.firstChild) {
        box.removeChild(box.firstChild);
      }

      const items = Array.isArray(engineeringSchedules) ? engineeringSchedules : [];

      const notice = document.createElement("div");
      notice.className = "notice";
      notice.textContent = "目前共有 " + String(items.length) + " 件工程排程。詳細橫向時程請點底部「排程」。";

      box.appendChild(notice);
    }

    function createScheduleCard(item) {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "schedule-card";
      button.onclick = function() {
        openProject(String(item.id || ""));
      };

      const head = document.createElement("div");
      head.className = "schedule-head";

      const left = document.createElement("div");

      const title = document.createElement("div");
      title.className = "project-title";
      title.textContent = String(item.building || "-") + " / " + String(item.type || "-");

      const building = document.createElement("div");
      building.className = "project-building";
      building.textContent = String(item.id || "-");

      left.appendChild(title);
      left.appendChild(building);

      const badge = document.createElement("div");
      badge.className = "status-badge " + String(item.status || "");
      badge.textContent = String(item.status || "-");

      head.appendChild(left);
      head.appendChild(badge);

      const meta = document.createElement("div");
      meta.className = "project-meta";

      const metaItems = [
        ["工期", String(item.startDate || "-") + " ～ " + String(item.endDate || "-")],
        ["天數", String(item.duration || "-")],
        ["負責", String(item.engineer || "-")],
        ["狀態", String(item.status || "-")]
      ];

      metaItems.forEach(function(pair) {
        const box = document.createElement("div");
        box.className = "meta-box";
        box.appendChild(document.createTextNode(pair[0]));

        const strong = document.createElement("strong");
        strong.textContent = pair[1];
        box.appendChild(strong);

        meta.appendChild(box);
      });

      const note = document.createElement("div");
      note.className = "project-note";
      note.textContent = String(item.note || "");

      button.appendChild(head);
      button.appendChild(meta);
      button.appendChild(note);

      return button;
    }

    function renderScheduleHome() {
      const list = document.getElementById("schedule_list");
      const items = Array.isArray(engineeringSchedules) ? engineeringSchedules : [];

      setText("summary_total", items.length);

      setText(
        "summary_working",
        items.filter(function(x) {
          return x.status === "施工中";
        }).length
      );

      setText(
        "summary_acceptance",
        items.filter(function(x) {
          return x.status === "待驗收";
        }).length
      );

      renderEngineeringTimeline();

      if (!list) return;

      while (list.firstChild) {
        list.removeChild(list.firstChild);
      }

      if (!items.length) {
        const empty = document.createElement("div");
        empty.className = "notice";
        empty.textContent = "目前沒有工程排程資料。";
        list.appendChild(empty);
        return;
      }

      items.forEach(function(item) {
        list.appendChild(createScheduleCard(item));
      });
    }

    function makeDetailLine(className, textValue) {
      const div = document.createElement("div");
      div.className = className;
      div.textContent = textValue == null ? "" : String(textValue);
      return div;
    }

    function openProject(projectId) {
      const project = engineeringSchedules.find(function(x) {
        return x.id === projectId;
      });

      if (!project) {
        alert("找不到工程資料：" + projectId);
        return;
      }

      currentProject = project;

      const home = document.getElementById("schedule_home");
      const panel = document.getElementById("work_panel");
      const detail = document.getElementById("project_detail");

      if (home) home.style.display = "none";
      if (panel) panel.style.display = "block";

      if (detail) {
        while (detail.firstChild) {
          detail.removeChild(detail.firstChild);
        }

        detail.appendChild(
          makeDetailLine(
            "detail-title",
            String(project.building || "-") + " / " + String(project.type || "-")
          )
        );

        detail.appendChild(
          makeDetailLine(
            "detail-sub",
            String(project.title || "-") + " / " + String(project.status || "-")
          )
        );

        detail.appendChild(
          makeDetailLine(
            "detail-sub",
            "工期：" + String(project.startDate || "-") + " ～ " + String(project.endDate || "-") + " / " + String(project.duration || "-")
          )
        );

        detail.appendChild(
          makeDetailLine(
            "detail-sub",
            "負責：" + String(project.engineer || "-") + " / 編號：" + String(project.id || "-")
          )
        );

        detail.appendChild(
          makeDetailLine(
            "detail-note",
            String(project.note || "")
          )
        );
      }

      window.scrollTo({top: 0, behavior: "smooth"});
    }

    function showScheduleHome() {
      const home = document.getElementById("schedule_home");
      const panel = document.getElementById("work_panel");

      if (panel) panel.style.display = "none";
      if (home) home.style.display = "block";

      currentProject = null;
      renderScheduleHome();
      window.scrollTo({top: 0, behavior: "smooth"});
    }

    function claimCurrentProject() {
      if (!currentProject) {
        alert("請先點選一件工程排程，再執行領用。");
        return;
      }

      const message = [
        String(currentProject.building || "-") + " / " + String(currentProject.title || "-"),
        "已領用工程項目。"
      ].join(String.fromCharCode(10));

      alert(message);
    }

    function completeCurrentProject() {
      if (!currentProject) {
        alert("請先點選一件工程排程，再執行完工。");
        return;
      }

      const message = [
        String(currentProject.building || "-") + " / " + String(currentProject.title || "-"),
        "已送出完工回報。"
      ].join(String.fromCharCode(10));

      alert(message);
    }

    function phaseTodo(name) {
      const projectName = currentProject
        ? String(currentProject.building || "-") + " / " + String(currentProject.title || "-")
        : "未選擇工程";

      const message = [
        projectName,
        String(name || "-") + "：此功能會在下一階段接資料表與回報流程。"
      ].join(String.fromCharCode(10));

      alert(message);
    }

    safeEngineeringHomeInit();
  