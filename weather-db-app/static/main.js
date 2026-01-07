const areaSelect = document.getElementById("areaSelect");
const dateSelect = document.getElementById("dateSelect");
const forecastDiv = document.getElementById("forecast");

let currentWeatherData = [];

// ============================
// エリア一覧取得
// ============================
fetch("/api/areas")
  .then(res => res.json())
  .then(data => {
    data.sort((a, b) => {
      return Number(a.code) - Number(b.code);
    });

    data.forEach(area => {
      const option = document.createElement("option");
      option.value = area.code;
      option.textContent = area.name;
      areaSelect.appendChild(option);
    });
  });


// ============================
// 地域選択時
// ============================
areaSelect.addEventListener("change", () => {
  const code = areaSelect.value;
  if (!code) return;

  fetch(`/api/weather/${code}`)
    .then(res => res.json())
    .then(data => {
      currentWeatherData = data;
      setupDateSelect(data);
      renderForecast(data);
    });
});


// ============================
// 日付セレクト生成
// ============================
function setupDateSelect(data) {
  dateSelect.innerHTML = `<option value="">すべての日付</option>`;

  const dates = [...new Set(data.map(d => d.date))];
  dates.forEach(date => {
    const option = document.createElement("option");
    option.value = date;
    option.textContent = date;
    dateSelect.appendChild(option);
  });
}


// ============================
// 日付選択時
// ============================
dateSelect.addEventListener("change", () => {
  const selectedDate = dateSelect.value;

  if (!selectedDate) {
    renderForecast(currentWeatherData);
    return;
  }

  const filtered = currentWeatherData.filter(d => d.date === selectedDate);
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

    div.innerHTML = `
      <h3>${d.date}</h3>
      <div class="icon">${getWeatherIcon(d.weather)}</div>
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
