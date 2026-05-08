
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

    function escapeHtml(value) {
      return String(value == null ? "" : value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
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

    function setText(id, value) {
      const box = document.getElementById(id);
      if (box) box.textContent = value;
    }

    function getScheduleWeeks(items) {
      const stageDates = [];

      items.forEach(function(item) {
        const survey = parseDateOnly(item.surveyDate);
        const start = parseDateOnly(item.startDate);
        const end = parseDateOnly(item.endDate);
        const acceptance = parseDateOnly(item.acceptanceDate);

        if (survey) stageDates.push(survey);
        if (start) stageDates.push(start);
        if (end) stageDates.push(end);
        if (acceptance) stageDates.push(acceptance);
      });

      stageDates.sort((a, b) => a - b);

      const first = stageDates[0] || new Date();

      const rangeStart = new Date(first.getFullYear(), first.getMonth(), 1);
      const rangeEnd = new Date(first.getFullYear(), first.getMonth() + 2, 0);

      const weeks = [];
      let cursor = new Date(rangeStart.getTime());
      const monthWeekCounter = {};

      while (cursor <= rangeEnd) {
        const weekStart = new Date(cursor.getTime());
        let weekEnd = addDays(weekStart, 6);

        if (weekEnd > rangeEnd) {
          weekEnd = new Date(rangeEnd.getTime());
        }

        const monthNumber = weekStart.getMonth() + 1;
        monthWeekCounter[monthNumber] = (monthWeekCounter[monthNumber] || 0) + 1;

        weeks.push({
          label: monthNumber + "月第" + monthWeekCounter[monthNumber] + "周",
          rangeLabel: formatMonthDay(weekStart) + "-" + formatMonthDay(weekEnd),
          start: weekStart,
          end: weekEnd
        });

        cursor = addDays(weekEnd, 1);
      }

      return {
        weeks: weeks,
        rangeStart: rangeStart,
        rangeEnd: rangeEnd
      };
    }

    function daysBetween(a, b) {
      return Math.round((b - a) / (1000 * 60 * 60 * 24));
    }

    function clampDate(date, minDate, maxDate) {
      if (date < minDate) return minDate;
      if (date > maxDate) return maxDate;
      return date;
    }

    function projectOverlapsRange(start, end, rangeStart, rangeEnd) {
      if (!start || !end) return false;
      return start <= rangeEnd && end >= rangeStart;
    }

    function buildStageBar(stage, rangeStart, rangeEnd, totalDays) {
      if (!projectOverlapsRange(stage.start, stage.end, rangeStart, rangeEnd)) {
        return "";
      }

      const barStart = clampDate(stage.start, rangeStart, rangeEnd);
      const barEnd = clampDate(stage.end, rangeStart, rangeEnd);

      const startOffset = daysBetween(rangeStart, barStart);
      const endOffset = daysBetween(rangeStart, barEnd);

      const leftPercent = (startOffset / totalDays) * 100;
      const widthPercent = ((endOffset - startOffset + 1) / totalDays) * 100;

      return `
        <div
          class="bar ${escapeHtml(stage.className)}"
          style="left:${leftPercent}%;width:${widthPercent}%;">
        </div>
      `;
    }

    function getProjectStages(item) {
      const stages = [];

      const surveyDate = parseDateOnly(item.surveyDate);
      const constructionStart = parseDateOnly(item.startDate);
      const constructionEnd = parseDateOnly(item.endDate);
      const explicitAcceptanceDate = parseDateOnly(item.acceptanceDate);
      const acceptanceDate = explicitAcceptanceDate || (constructionEnd ? addDays(constructionEnd, 7) : null);

      if (surveyDate) {
        stages.push({
          label: "勘場",
          className: "survey",
          start: surveyDate,
          end: surveyDate
        });
      }

      if (constructionStart && constructionEnd) {
        stages.push({
          label: "施工",
          className: "construction",
          start: constructionStart,
          end: constructionEnd
        });
      }

      if (acceptanceDate) {
        stages.push({
          label: "驗收",
          className: "acceptance",
          start: acceptanceDate,
          end: acceptanceDate
        });
      }

      return stages;
    }

    function renderScheduleTable() {
      const wrap = document.getElementById("schedule_wrap");
      if (!wrap) return;

      const timeline = getScheduleWeeks(engineeringSchedules);
      const weeks = timeline.weeks;
      const rangeStart = timeline.rangeStart;
      const rangeEnd = timeline.rangeEnd;
      const totalDays = daysBetween(rangeStart, rangeEnd) + 1;

      const head = weeks.map(function(week) {
        return `<th>${escapeHtml(week.label)}<br><span style="font-size:8px;color:#64748b;">${escapeHtml(week.rangeLabel)}</span></th>`;
      }).join("");

      const rows = engineeringSchedules.map(function(item) {
        const stages = getProjectStages(item);

        const bars = stages.map(function(stage) {
          return buildStageBar(stage, rangeStart, rangeEnd, totalDays);
        }).join("");

        return `
          <tr>
            <td>
              <div class="building-name">${escapeHtml(item.building)}</div>
              <div class="building-sub">${escapeHtml(item.title)}</div>
            </td>
            <td colspan="${weeks.length}">
              <div class="week-cell">
                ${bars}
              </div>
            </td>
          </tr>
        `;
      }).join("");

      wrap.innerHTML = `
        <table class="schedule-table">
          <thead>
            <tr>
              <th>大樓 / 工程</th>
              ${head}
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>

        <div class="timeline-legend">
          <span class="timeline-legend-item"><span class="timeline-legend-color survey"></span>勘場</span>
          <span class="timeline-legend-item"><span class="timeline-legend-color construction"></span>施工</span>
          <span class="timeline-legend-item"><span class="timeline-legend-color acceptance"></span>驗收</span>
        </div>
      `;
    }

    renderScheduleTable();
  