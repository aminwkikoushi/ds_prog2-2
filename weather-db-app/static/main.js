const btn = document.getElementById("load");
const area = document.getElementById("area");
const forecast = document.getElementById("forecast");

btn.addEventListener("click", () => {
  fetch(`/api/weather/${area.value}`)
    .then(res => res.json())
    .then(data => {
      forecast.innerHTML = "";

      data.forEach(d => {
        const div = document.createElement("div");
        div.innerHTML = `
          <h3>${d.date}</h3>
          <p>${d.weather}</p>
          <p>${d.min}℃ / ${d.max}℃</p>
        `;
        forecast.appendChild(div);
      });
    });
});
