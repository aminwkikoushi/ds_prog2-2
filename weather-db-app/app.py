import sqlite3

conn = sqlite3.connect("weather.db")
cur = conn.cursor()

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

conn.commit()
conn.close()


from flask import Flask, render_template, jsonify
import requests
import sqlite3

app = Flask(__name__)
DB_NAME = "weather.db"


def get_db():
    return sqlite3.connect(DB_NAME)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/weather/<area_code>")
def fetch_weather(area_code):
    url = f"https://www.jma.go.jp/bosai/forecast/data/forecast/{area_code}.json"
    data = requests.get(url).json()

    weather_series = data[0]["timeSeries"][0]
    temp_series = data[1]["timeSeries"][1]

    conn = get_db()
    cur = conn.cursor()

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
            date[:10],
            weather,
            min_temp,
            max_temp
        ))

    conn.commit()

    cur.execute("""
        SELECT date, weather, temp_min, temp_max
        FROM weather
        WHERE area_code = ?
        ORDER BY date
    """, (area_code,))

    rows = cur.fetchall()
    conn.close()

    result = [
        {
            "date": r[0],
            "weather": r[1],
            "min": r[2],
            "max": r[3]
        } for r in rows
    ]

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)

