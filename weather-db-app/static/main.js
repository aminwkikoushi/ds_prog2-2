const areaSelect = document.getElementById("areaSelect");
const dateSelect = document.getElementById("dateSelect");
const forecastDiv = document.getElementById("forecast");

let currentWeatherData = [];

// ============================
// エリア一覧取得（DB → Flask API）
// ============================
fetch("/api/areas")
  .then(res => res.json())
  .then(data => {
    data.forEach(area => {
      const option = document.createElement("option");
      option.value = area.code;
      option.textContent = area.name;
      areaSelect.appendChild(option);
    });
  });


// ============================
// 地域選択時：天気取得 + 日付範囲設定
// ============================
areaSelect.addEventListener("change", () => {
  const code = areaSelect.value;
  if (!code) return;

  fetch(`/api/weather/${code}`)
    .then(res => res.json())
    .then(data => {
      currentWeatherData = data;

      // ★ ここが重要：選べる日付を制限
      const dates = data.map(d => d.date);
      dateSelect.min = dates[0];
      dateSelect.max = dates[dates.length - 1];
      dateSelect.value = "";

      renderForecast(data);
    });
});


// ============================
// 日付選択時：該当日のみ表示
// ============================
dateSelect.addEventListener("change", () => {
  const selectedDate = dateSelect.value;

  const filtered = currentWeatherData.filter(
    d => d.date === selectedDate
  );

  renderForecast(filtered);
});


// ============================
// 表示処理
// ============================
function renderForecast(data) {
  forecastDiv.innerHTML = "";

  if (data.length === 0) {
    forecastDiv.innerHTML = "<p>該当するデータがありません</p>";
    return;
  }

  data.forEach(d => {
    const div = document.createElement("div");
    div.className = "card";

    const icon = getWeatherIcon(d.weather);

    div.innerHTML = `
      <h3>${d.date}</h3>
      <div class="icon">${icon}</div>
      <p>${d.weather}</p>
      <p class="temp">
        <span class="min">${d.min ?? "-"}℃</span> /
        <span class="max">${d.max ?? "-"}℃</span>
      </p>
    `;

    forecastDiv.appendChild(div);
  });
}


// ============================
// 天気アイコン
// ============================
function getWeatherIcon(text) {
  if (text.includes("晴")) return "☀️";
  if (text.includes("曇")) return "☁️";
  if (text.includes("雨")) return "☔️";
  if (text.includes("雪")) return "❄️";
  return "🌤️";
}
