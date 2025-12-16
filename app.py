import os
from flask import Flask, jsonify, render_template_string
import requests
from datetime import datetime

app = Flask(__name__)

FASTAPI_BASE = os.environ.get("FASTAPI_BASE", "http://192.168.1.110:8000")

# ---------------- 방 상태 API ----------------


@app.route("/api/rooms")
def get_rooms():
    try:
        resp = requests.get(f"{FASTAPI_BASE}/api/sensors", timeout=1.5)
        data = resp.json()
    except Exception as e:
        print("센서 서버 호출 오류:", e)
        return jsonify({})

    sensors = data.get("sensors", [])
    rooms = {}

    for s in sensors:
        sensor_id = s.get("sensor_id", "UNKNOWN")

        last = s.get("last_data") or {}
        temp = last.get("temperature") or 0.0
        hum = last.get("humidity") or 0.0
        score = s.get("air_quality_score") or 0.0

        if score >= 70:
            air = "나쁨"
        elif score >= 40:
            air = "보통"
        else:
            air = "좋음"

        updated_ts = 0
        if s.get("last_updated"):
            try:
                dt = datetime.fromisoformat(s["last_updated"])
                updated_ts = int(dt.timestamp())
            except:
                pass

        name = {"ROOM1": "방 1", "ROOM2": "방 2"}.get(sensor_id, sensor_id)

        rooms[sensor_id] = {
            "name": name,
            "temp": round(float(temp), 1),
            "humidity": round(float(hum), 1),
            "air": air,
            "updated_at": updated_ts,
        }

    return jsonify(rooms)


# ---------------- UI ----------------
@app.route("/")
def index():
    html = """
<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8" />
<title>Smart AirBot 모니터링</title>
<meta name="viewport" content="width=device-width, initial-scale=1" />

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

body {
    margin: 0; padding: 0;
    font-family: system-ui;
    background: #0c111b;
    color: var(--text-main);
}

.shell {
    max-width: 1100px;
    padding: 20px;
    margin: auto;
}

.panel {
    background: #111827;
    padding: 16px;
    border-radius: 16px;
    margin-bottom: 20px;
    border: 1px solid rgba(255,255,255,0.05);
}

.panel-header {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 10px;
}

#live-cam {
    width: 100%;
    border-radius: 12px;
    background: black;
}
button {
    margin: 4px;
    padding: 8px 12px;
    background: #1f2937;
    color: white;
    border-radius: 8px;
    border: 1px solid #374151;
    cursor: pointer;
}
button:hover {
    background: #374151;
}
</style>
</head>
<body>
<div class="shell">

    <h1>Smart AirBot - 실시간 공기질 & 카메라 모니터링</h1>

    <!-- 🔵 실시간 카메라 패널 -->
    <div class="panel">
        <div class="panel-header">실시간 카메라 화면</div>
        <img id="live-cam" />
    </div>

    <!-- 🔵 공기질 패널 -->
    <div class="panel">
        <div class="panel-header">공간별 상태</div>
        <div id="room-grid"></div>
    </div>

    <!-- 🔵 수동 주행 패널 -->
    <div class="panel">
        <div class="panel-header">수동 주행 제어</div>

        <div style="margin-bottom:8px;">WebSocket 상태: <span id="ctrl-status">연결 시도 중...</span></div>

        <button onclick="sendControl('w')">▲ 앞으로 (W)</button>
        <button onclick="sendControl('s')">▼ 뒤로 (S)</button>
        <button onclick="sendControl('a')">◀ 왼쪽 (A)</button>
        <button onclick="sendControl('d')">▶ 오른쪽 (D)</button>
        <button onclick="sendControl(' ')">■ 정지 (SPACE)</button>
        <button onclick="sendControl('y')">공청 ON (Y)</button>
        <button onclick="sendControl('n')">공청 OFF (N)</button>
    </div>

</div>

<script>
// ==================================================
// 📌 1) 실시간 카메라 WebSocket 연결 (FastAPI /ws/camera)
// ==================================================
const camWS = new WebSocket("ws://192.168.1.110:8000/ws/camera");

camWS.onmessage = (ev) => {
    document.getElementById("live-cam").src = "data:image/jpeg;base64," + ev.data;
};

// ==================================================
// 📌 2) 공기질 로딩 (Flask → FastAPI /api/sensors 프록시)
// ==================================================
async function loadRooms() {
    const res = await fetch("/api/rooms");
    const data = await res.json();

    let html = "";
    Object.keys(data).forEach(id => {
        const r = data[id];
        html += `
            <div style="margin-bottom:10px;">
                <b>${r.name}</b><br/>
                온도: ${r.temp}℃ / 습도: ${r.humidity}%<br/>
                공기질: ${r.air}<br/>
                업데이트: ${new Date(r.updated_at*1000).toLocaleTimeString()}
            </div>
        `;
    });

    document.getElementById("room-grid").innerHTML = html;
}
setInterval(loadRooms, 1500);
loadRooms();

// ==================================================
// 📌 3) 수동 주행 제어 WebSocket (직접 FastAPI /ws/control 연결)
// ==================================================
let ctrlWS = null;

function setupControlWS() {
    const url = "ws://192.168.1.110:8000/ws/drive";
    console.log("[CONTROL WS] connect to", url);
    ctrlWS = new WebSocket(url);

    ctrlWS.onopen = () => {
        console.log("[CONTROL WS] connected");
        document.getElementById("ctrl-status").innerText = "연결됨";
    };

    ctrlWS.onclose = () => {
        console.log("[CONTROL WS] closed, retrying...");
        document.getElementById("ctrl-status").innerText = "연결 끊김, 재시도 중...";
        setTimeout(setupControlWS, 3000);
    };

    ctrlWS.onerror = (e) => {
        console.log("[CONTROL WS] error:", e);
    };
}

setupControlWS();

function sendControl(cmd) {
    if (!ctrlWS || ctrlWS.readyState !== WebSocket.OPEN) {
        console.log("[CONTROL] WS not ready, cmd ignored:", cmd);
        return;
    }

    console.log("[CONTROL] send:", cmd);

    ctrlWS.send(cmd);
}

</script>

</body>
</html>
"""
    return render_template_string(html)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=False)
