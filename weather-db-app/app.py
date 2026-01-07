from flask import Flask, render_template, jsonify
import sqlite3
import requests

app = Flask(__name__)
DB_NAME = "weather.db"


# ============================
# DB接続
# ============================
def get_db():
    return sqlite3.connect(DB_NAME)


# ============================
# 初期化：テーブル作成＋地域データ投入
# ============================
def init_db():
    conn = get_db()
    cur = conn.cursor()

    # --- weather テーブル ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS weather (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      area_code TEXT,
      date TEXT,
      weather TEXT,
      temp_min INTEGER,
      temp_max INTEGER
    )
    """)

    # --- area テーブル ---
    cur.execute("""
    CREATE TABLE IF NOT EXISTS area (
      area_code TEXT PRIMARY KEY,
      area_name TEXT
    )
    """)

    # --- 気象庁エリア情報取得 ---
    url = "https://www.jma.go.jp/bosai/common/const/area.json"
    data = requests.get(url).json()
    offices = data["offices"]

    for code, info in offices.items():
        cur.execute("""
        INSERT OR IGNORE INTO area (area_code, area_name)
        VALUES (?, ?)
        """, (code, info["name"]))

    conn.commit()
    conn.close()


# ============================
# 画面
# ============================
@app.route("/")
def index():
    return render_template("index.html")


# ============================
# 地域一覧API（DB → フロント）
# ============================
@app.route("/api/areas")
def get_areas():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT area_code, area_name FROM area ORDER BY area_name")
    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {"code": r[0], "name": r[1]} for r in rows
    ])


# ============================
# 天気取得API（気象庁 → DB → フロント）
# ============================
@app.route("/api/weather/<area_code>")
def fetch_weather(area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    data = requests.get(url).json()

    weather_series = data[0]["timeSeries"][0]
    temp_series = data[1]["timeSeries"][1]

    conn = get_db()
    cur = conn.cursor()

    # 既存データ削除（最新に更新）
    cur.execute("DELETE FROM weather WHERE area_code = ?", (area_code,))

    for i, date in enumerate(weather_series["timeDefines"]):
        weather = weather_series["areas"][0]["weathers"][i]
        min_temp = temp_series["areas"][0]["tempsMin"][i]
        max_temp = temp_series["areas"][0]["tempsMax"][i]

        cur.execute("""
        INSERT INTO weather (area_code, date, weather, temp_min, temp_max)
        VALUES (?, ?, ?, ?, ?)
        """, (
            area_code,
            date[:10],  # YYYY-MM-DD
            weather,
            min_temp,
            max_temp
        ))

    conn.commit()

    # DBから取得（＝日付選択対応）
    cur.execute("""
    SELECT date, weather, temp_min, temp_max
    FROM weather
    WHERE area_code = ?
    ORDER BY date
    """, (area_code,))

    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {
            "date": r[0],
            "weather": r[1],
            "min": r[2],
            "max": r[3]
        } for r in rows
    ])


# ============================
# 起動
# ============================
if __name__ == "__main__":
    init_db()   # ← 重要：最初にDB初期化
    app.run(debug=True)
