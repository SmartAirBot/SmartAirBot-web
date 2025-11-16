from flask import Flask, jsonify, render_template_string
import random
import time

app = Flask(__name__)

# ----- 방 정보 기본값 -----
rooms = {
    "ROOM1": {"name": "방 1", "temp": 24.0, "humidity": 40.0, "air": "좋음", "updated_at": 0},
    "ROOM2": {"name": "방 2", "temp": 25.0, "humidity": 42.0, "air": "보통", "updated_at": 0},
    "ROOM3": {"name": "방 3", "temp": 23.5, "humidity": 38.0, "air": "좋음", "updated_at": 0},
    "LIVING": {"name": "거실", "temp": 26.0, "humidity": 45.0, "air": "나쁨", "updated_at": 0},
}


# 지금은 센서가 없으니까, 랜덤으로 값 살짝살짝 흔들어주는 함수
def update_mock_data():
    for room_id, room in rooms.items():
        room["temp"] += random.uniform(-0.3, 0.3)
        room["humidity"] += random.uniform(-1, 1)

        # 공기질 상태를 온도/습도랑 상관 없이 랜덤으로 바꿔볼 수도 있음
        air_status = random.choice(["좋음", "보통", "나쁨"])
        room["air"] = air_status

        room["temp"] = round(room["temp"], 1)
        room["humidity"] = round(room["humidity"], 1)
        room["updated_at"] = int(time.time())


# ----- API: 방 데이터 제공 -----
@app.route("/api/rooms")
def get_rooms():
    # 실제에서는 여기서 라즈베리파이에서 받은 최신 데이터를 사용하게 될 것
    update_mock_data()  # 지금은 화면 움직임 보이게 랜덤 업데이트
    return jsonify(rooms)


# ----- 웹페이지 (대시보드) -----
@app.route("/")
def index():
    html = """
    <!doctype html>
    <html lang="ko">
    <head>
        <meta charset="utf-8">
        <title>Smart AirBot · 실내 공기질 모니터링</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            :root {
                --bg: #050816;
                --bg-card: #0b1120;
                --bg-card-soft: #111827;
                --accent: #38bdf8;
                --accent-soft: #0ea5e9;
                --good: #22c55e;
                --normal: #facc15;
                --bad: #f97316;
                --text-main: #f9fafb;
                --text-sub: #9ca3af;
            }

            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                padding: 0;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background: #0c111b;  /* 단색 다크 배경 */
                color: var(--text-main);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
            }

            .shell {
                width: 100%;
                max-width: 1100px;
                padding: 24px 20px 40px;
            }

            .topbar {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 12px;
                margin-bottom: 24px;
            }

            .logo-wrap {
                display: flex;
                align-items: center;
                gap: 10px;
            }

            .logo-icon {
                width: 32px;
                height: 32px;
                border-radius: 12px;
                background: radial-gradient(circle at 20% 20%, #a5b4fc, #38bdf8 40%, #0f172a 80%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                font-weight: 700;
                box-shadow: 0 8px 20px rgba(15, 118, 252, 0.45);
            }

            .logo-text-main {
                font-size: 18px;
                font-weight: 600;
                letter-spacing: 0.02em;
            }

            .logo-text-sub {
                font-size: 12px;
                color: var(--text-sub);
            }

            .status-pill {
                padding: 6px 12px;
                border-radius: 999px;
                border: 1px solid rgba(148, 163, 184, 0.6);
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 0.11em;
                color: var(--text-sub);
                display: inline-flex;
                align-items: center;
                gap: 6px;
                backdrop-filter: blur(10px);
                background: rgba(15, 23, 42, 0.6);
                white-space: nowrap;
            }

            .dot {
                width: 7px;
                height: 7px;
                border-radius: 999px;
                background: #22c55e;
                box-shadow: 0 0 8px rgba(34, 197, 94, 0.8);
            }

            .headline {
                margin-bottom: 18px;
            }

            .headline-title {
                font-size: clamp(20px, 3.2vw, 26px);
                font-weight: 600;
            }

            .headline-desc {
                font-size: clamp(12px, 2.1vw, 13px);
                color: var(--text-sub);
                margin-top: 6px;
            }

            .chips-row {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-bottom: 22px;
            }

            .chip {
                font-size: 11px;
                padding: 6px 10px;
                border-radius: 999px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: var(--text-sub);
                background: #1a2537;   /* 단색 칩 */
            }

            .layout {
                display: grid;
                grid-template-columns: 2.1fr 1.2fr;
                gap: 16px;
            }

            .panel {
                background: #111827;  /* 패널 단색 */
                border-radius: 16px;
                padding: 18px 18px 16px;
                border: 1px solid rgba(255, 255, 255, 0.05);
                box-shadow: 0 4px 16px rgba(0,0,0,0.25);
            }

            .panel-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
                gap: 10px;
            }

            .panel-title {
                font-size: 14px;
                font-weight: 500;
            }

            .panel-sub {
                font-size: 11px;
                color: var(--text-sub);
            }

            .pill-mini {
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 999px;
                background: #0f172a;
                border: 1px solid rgba(148, 163, 184, 0.5);
                color: var(--text-sub);
                white-space: nowrap;
            }

            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
                gap: 12px;
            }

            .card {
                background: #0f172a;  /* 카드 단색 */
                border-radius: 14px;
                padding: 14px 14px 12px;
                border: 1px solid rgba(255, 255, 255, 0.06);
                position: relative;
                overflow: hidden;
                transition: transform 0.18s ease-out, box-shadow 0.18s ease-out, border-color 0.18s;
            }

            .card:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(0,0,0,0.32);
                border-color: rgba(56, 189, 248, 0.7);
            }

            .room-top {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 4px;
                gap: 6px;
            }

            .room-name {
                font-size: 15px;
                font-weight: 500;
            }

            .room-tag {
                font-size: 11px;
                color: var(--text-sub);
            }

            .air-chip {
                font-size: 11px;
                padding: 4px 10px;
                border-radius: 999px;
                display: inline-flex;
                align-items: center;
                gap: 6px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                background: #1a2537; /* 단색 */
            }

            .air-dot {
                width: 8px;
                height: 8px;
                border-radius: 999px;
            }

            .air-good .air-dot {
                background: var(--good);
                box-shadow: 0 0 8px rgba(34, 197, 94, 0.9);
            }
            .air-normal .air-dot {
                background: var(--normal);
                box-shadow: 0 0 8px rgba(250, 204, 21, 0.9);
            }
            .air-bad .air-dot {
                background: var(--bad);
                box-shadow: 0 0 8px rgba(249, 115, 22, 0.9);
            }

            .metrics {
                display: flex;
                gap: 10px;
                margin-top: 10px;
            }

            .metric {
                flex: 1;
                font-size: 12px;
            }

            .metric-label {
                color: var(--text-sub);
                margin-bottom: 4px;
            }

            .metric-main {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 2px;
            }

            .bar-track {
                width: 100%;
                height: 5px;
                border-radius: 999px;
                background: #1e293b;
                overflow: hidden;
            }

            .bar-fill {
                height: 100%;
                border-radius: 999px;
                background: var(--accent-soft);
                transform-origin: left;
                transform: scaleX(0.5);
            }

            .updated-room {
                margin-top: 8px;
                font-size: 11px;
                color: #6b7280;
                text-align: right;
            }

            .side-metrics {
                display: grid;
                gap: 10px;
                font-size: 12px;
            }

            .side-row {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 9px;
                border-radius: 10px;
                background: var(--bg-card-soft);
                border: 1px solid rgba(148, 163, 184, 0.35);
            }

            .side-label {
                color: var(--text-sub);
            }

            .side-value {
                font-weight: 600;
            }

            .side-highlight {
                font-size: 12px;
                margin-top: 10px;
                color: var(--text-sub);
            }

            .time-footer {
                margin-top: 14px;
                font-size: 11px;
                color: #6b7280;
                text-align: right;
            }

            /* ----------------- 모바일 최적화 ----------------- */
            @media (max-width: 720px) {

                body {
                    padding: 0;
                    margin: 0;
                }

                .shell {
                    padding: 14px 12px 24px;
                }

                .topbar {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 6px;
                    margin-bottom: 12px;
                }

                .logo-icon {
                    width: 28px;
                    height: 28px;
                    font-size: 16px;
                }

                .logo-text-main {
                    font-size: 16px;
                }

                .logo-text-sub {
                    font-size: 11px;
                }

                .status-pill {
                    font-size: 10px;
                    padding: 4px 10px;
                }

                .headline {
                    margin-bottom: 12px;
                }

                .headline-title {
                    font-size: 20px;
                    line-height: 1.3;
                }

                .headline-desc {
                    font-size: 12px;
                    line-height: 1.45;
                }

                .chips-row {
                    margin-bottom: 14px;
                    gap: 6px;
                }

                .chip {
                    padding: 4px 8px;
                    font-size: 10px;
                }

                .layout {
                    grid-template-columns: 1fr;
                    gap: 12px;
                }

                .panel {
                    padding: 14px 12px;
                    border-radius: 14px;
                }

                .panel-header {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 4px;
                    margin-bottom: 10px;
                }

                .panel-title {
                    font-size: 13px;
                }

                .panel-sub {
                    font-size: 11px;
                    line-height: 1.4;
                }

                .grid {
                    grid-template-columns: 1fr;
                    gap: 10px;
                }

                .card {
                    padding: 12px 12px;
                    border-radius: 14px;
                }

                .room-top {
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 4px;
                }

                .room-name {
                    font-size: 14px;
                }

                .room-tag {
                    font-size: 10px;
                }

                .air-chip {
                    font-size: 10px;
                    padding: 3px 8px;
                }

                .metrics {
                    margin-top: 8px;
                    gap: 8px;
                }

                .metric-label {
                    font-size: 11px;
                }

                .metric-main {
                    font-size: 15px;
                    margin-bottom: 2px;
                }

                .bar-track {
                    height: 7px;
                }

                .updated-room {
                    font-size: 10px;
                    margin-top: 6px;
                }

                .side-metrics {
                    gap: 8px;
                }

                .side-row {
                    padding: 6px 8px;
                    font-size: 12px;
                }

                .side-label {
                    font-size: 11px;
                }

                .side-value {
                    font-size: 13px;
                    font-weight: 500;
                }

                .side-highlight {
                    font-size: 11px;
                    line-height: 1.4;
                }

                .time-footer {
                    font-size: 10px;
                    text-align: left;
                    margin-top: 8px;
                }
            }
        </style>
    </head>
    <body>
        <div class="shell">
            <div class="topbar">
                <div class="logo-wrap">
                    <div class="logo-icon">A</div>
                    <div>
                        <div class="logo-text-main">Smart AirBot</div>
                    </div>
                </div>
                <div class="status-pill">
                    <span class="dot"></span>
                    LIVE MONITORING
                </div>
            </div>

            <div class="headline">
                <div class="headline-title">집 안 공기의 모든 정보를 한눈에.</div>
                <div class="headline-desc">
                    우리 집 공기 상태를 실시간으로 관리합니다.
                </div>
            </div>

            <div class="chips-row">
                <div class="chip">전체 공간 4곳 모니터링 중</div>
                <div class="chip">온도·습도·공기질 분석</div>
                <div class="chip">자동 상태 판별</div>
            </div>

            <div class="layout">
                <div class="panel">
                    <div class="panel-header">
                        <div>
                            <div class="panel-title">공간별 상태</div>
                            <div class="panel-sub">방마다 현재 상태와 변화를 카드로 확인할 수 있습니다.</div>
                        </div>
                        <div class="pill-mini">ROOM VIEW</div>
                    </div>

                    <div class="grid" id="room-grid">
                        <!-- JS에서 카드 생성 -->
                    </div>
                </div>

                <div class="panel">
                    <div class="panel-header">
                        <div>
                            <div class="panel-title">요약 인사이트</div>
                            <div class="panel-sub">각 방의 평균 값으로 전체 컨디션을 집계합니다.</div>
                        </div>
                        <div class="pill-mini">OVERVIEW</div>
                    </div>

                    <div class="side-metrics" id="summary">
                        <!-- JS에서 요약 생성 -->
                    </div>

                    <div class="time-footer" id="last-updated">마지막 업데이트: -</div>
                </div>
            </div>
        </div>

        <script>
            function getAirClass(air) {
                if (air === "좋음") return "air-chip air-good";
                if (air === "보통") return "air-chip air-normal";
                if (air === "나쁨") return "air-chip air-bad";
                return "air-chip";
            }

            function formatTime(timestamp) {
                if (!timestamp) return "-";
                const date = new Date(timestamp * 1000);
                return date.toLocaleTimeString("ko-KR", {
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit"
                });
            }

            function calcBarWidthTemp(temp) {
                const min = 18;
                const max = 30;
                const clamped = Math.min(max, Math.max(min, temp));
                return ((clamped - min) / (max - min));
            }

            function calcBarWidthHum(h) {
                const min = 20;
                const max = 70;
                const clamped = Math.min(max, Math.max(min, h));
                return ((clamped - min) / (max - min));
            }

            async function loadData() {
                try {
                    const res = await fetch("/api/rooms");
                    const data = await res.json();

                    const container = document.getElementById("room-grid");
                    container.innerHTML = "";

                    let tempSum = 0;
                    let humSum = 0;
                    let count = 0;
                    let good = 0, normal = 0, bad = 0;
                    let latestTs = 0;

                    Object.keys(data).forEach((id) => {
                        const room = data[id];
                        count += 1;
                        tempSum += room.temp;
                        humSum += room.humidity;

                        if (room.air === "좋음") good += 1;
                        else if (room.air === "보통") normal += 1;
                        else if (room.air === "나쁨") bad += 1;

                        if (room.updated_at && room.updated_at > latestTs) {
                            latestTs = room.updated_at;
                        }

                        const card = document.createElement("div");
                        card.className = "card";

                        const airClass = getAirClass(room.air);
                        const tempScale = calcBarWidthTemp(room.temp);
                        const humScale = calcBarWidthHum(room.humidity);

                        card.innerHTML = `
                            <div class="room-top">
                                <div>
                                    <div class="room-name">${room.name}</div>
                                    <div class="room-tag">NODE · ${id}</div>
                                </div>
                                <div class="${airClass}">
                                    <span class="air-dot"></span>
                                    <span>공기질: ${room.air}</span>
                                </div>
                            </div>

                            <div class="metrics">
                                <div class="metric">
                                    <div class="metric-label">온도</div>
                                    <div class="metric-main">${room.temp.toFixed(1)} ℃</div>
                                    <div class="bar-track">
                                        <div class="bar-fill" style="transform: scaleX(${tempScale});"></div>
                                    </div>
                                </div>

                                <div class="metric">
                                    <div class="metric-label">습도</div>
                                    <div class="metric-main">${room.humidity.toFixed(1)} %</div>
                                    <div class="bar-track">
                                        <div class="bar-fill" style="transform: scaleX(${humScale});"></div>
                                    </div>
                                </div>
                            </div>

                            <div class="updated-room">업데이트: ${formatTime(room.updated_at)}</div>
                        `;

                        container.appendChild(card);
                    });

                    const summary = document.getElementById("summary");
                    summary.innerHTML = "";

                    if (count > 0) {
                        const avgTemp = tempSum / count;
                        const avgHum = humSum / count;

                        const rows = [
                            { label: "평균 온도", value: avgTemp.toFixed(1) + " ℃" },
                            { label: "평균 습도", value: avgHum.toFixed(1) + " %" },
                            { label: "공기질 상태", value: `좋음 ${good} · 보통 ${normal} · 나쁨 ${bad}` }
                        ];

                        rows.forEach((row) => {
                            const el = document.createElement("div");
                            el.className = "side-row";
                            el.innerHTML = `
                                <div class="side-label">${row.label}</div>
                                <div class="side-value">${row.value}</div>
                            `;
                            summary.appendChild(el);
                        });

                        const hint = document.createElement("div");
                        hint.className = "side-highlight";
                        summary.appendChild(hint);
                    }

                    const last = document.getElementById("last-updated");
                    last.textContent = "마지막 업데이트: " + (latestTs ? formatTime(latestTs) : "-");

                } catch (err) {
                    console.error("데이터 로드 오류:", err);
                }
            }

            loadData();
            setInterval(loadData, 2000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html)


if __name__ == "__main__":
    app.run(debug=True)
