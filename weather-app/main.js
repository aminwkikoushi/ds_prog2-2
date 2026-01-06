const areaSelect = document.getElementById("areaSelect");
const forecastDiv = document.getElementById("forecast");

/**
 * 天気文からアイコンを返す
 */
function getWeatherIcon(weatherText) {
  if (!weatherText) return "❓";
  if (weatherText.includes("晴")) return "☀️";
  if (weatherText.includes("くもり") || weatherText.includes("曇")) return "☁️";
  if (weatherText.includes("雨")) return "☔️";
  if (weatherText.includes("雪")) return "❄️";
  if (weatherText.includes("雷")) return "⛈️";
  return "❓";
}

/**
 * 地域リスト取得
 */
fetch("https://www.jma.go.jp/bosai/common/const/area.json")
  .then(response => response.json())
  .then(data => {
    const offices = data.offices;

    for (const code in offices) {
      const option = document.createElement("option");
      option.value = code;
      option.textContent = offices[code].name;
      areaSelect.appendChild(option);
    }
  })
  .catch(error => {
    console.error("地域リスト取得エラー:", error);
  });

/**
 * 地域選択時の処理
 */
areaSelect.addEventListener("change", () => {
  const code = areaSelect.value;
  if (!code) return;

  fetch(`https://www.jma.go.jp/bosai/forecast/data/forecast/${code}.json`)
    .then(response => response.json())
    .then(data => {
      const weatherSeries = data[0].timeSeries[0];
      const tempSeries = data[1].timeSeries[1];

      forecastDiv.innerHTML = "";

      weatherSeries.timeDefines.forEach((date, i) => {
        const div = document.createElement("div");
        div.className = "card";

        const weatherText = weatherSeries.areas[0].weathers[i];
        const icon = getWeatherIcon(weatherText);

        const min =
          tempSeries.areas[0].tempsMin[i] !== null
            ? tempSeries.areas[0].tempsMin[i]
            : "-";

        const max =
          tempSeries.areas[0].tempsMax[i] !== null
            ? tempSeries.areas[0].tempsMax[i]
            : "-";

        div.innerHTML = `
          <h3>${date.slice(0, 10)}</h3>
          <p style="font-size: 32px; margin: 8px 0;">${icon}</p>
          <p>${weatherText}</p>
          <p class="temp">
            <span class="min">${min}℃</span> /
            <span class="max">${max}℃</span>
          </p>
        `;

        forecastDiv.appendChild(div);
      });
    })
    .catch(error => {
      console.error("天気予報取得エラー:", error);
    });
});
