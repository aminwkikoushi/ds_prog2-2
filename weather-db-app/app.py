from flask import Flask, render_template, jsonify
import sqlite3
import requests
import os

app = Flask(__name__)
DB_NAME = "weather.db"


# ==============================
# DB接続
# ==============================
def get_db():
    return sqlite3.connect(DB_NAME)


# ==============================
# DB初期化
# ==============================
def init_db():
    conn = get_db()
    cur = conn.cursor()

    # エリアテーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS area (
        area_code TEXT PRIMARY KEY,
        area_name TEXT
    )
    """)

    # 天気テーブル
    cur.execute("""
    CREATE TABLE IF NOT EXISTS weather (
        area_code TEXT,
        date TEXT,
        weather TEXT,
        temp_min TEXT,
        temp_max TEXT
    )
    """)

    conn.commit()
    conn.close()


# ==============================
# エリア情報をDBに保存
# ==============================
def init_area_table():
    conn = get_db()
    cur = conn.cursor()

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


# ==============================
# トップページ
# ==============================
@app.route("/")
def index():
    return render_template("index.html")


# ==============================
# エリア一覧API
# ==============================
@app.route("/api/areas")
def get_areas():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT area_code, area_name FROM area")
    rows = cur.fetchall()
    conn.close()

    return jsonify([
        {"code": r[0], "name": r[1]} for r in rows
    ])


# ==============================
# 天気取得API
# ==============================
@app.route("/api/weather/<area_code>")
def get_weather(area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    data = requests.get(url).json()

    weather_series = data[0]["timeSeries"][0]
    temp_series = data[1]["timeSeries"][1]

    conn = get_db()
    cur = conn.cursor()

    # 既存データ削除
    cur.execute("DELETE FROM weather WHERE area_code = ?", (area_code,))

    for i, date in enumerate(weather_series["timeDefines"]):
        weather = weather_series["areas"][0]["weathers"][i]

        min_temp = temp_series["areas"][0]["tempsMin"][i] if temp_series["areas"][0]["tempsMin"] else None
        max_temp = temp_series["areas"][0]["tempsMax"][i] if temp_series["areas"][0]["tempsMax"] else None

        cur.execute("""
        INSERT INTO weather (area_code, date, weather, temp_min, temp_max)
        VALUES (?, ?, ?, ?, ?)
        """, (
            area_code,
            date[:10],
            weather,
            min_temp,
            max_temp
        ))

    conn.commit()

    # DBから取得
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


# ==============================
# 起動時処理
# ==============================
if __name__ == "__main__":
    init_db()
    init_area_table()
    app.run(debug=True)

