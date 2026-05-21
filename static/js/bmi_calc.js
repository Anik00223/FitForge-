(function () {
  function category(bmi) {
    if (bmi < 18.5) return ["Underweight", "badge-info"];
    if (bmi < 25) return ["Normal", "badge-success"];
    if (bmi < 30) return ["Overweight", "badge-warning"];
    return ["Obese", "badge-danger"];
  }

  function update() {
    const weightInput = document.getElementById("bmiWeight") || document.querySelector("[name='weight_kg']");
    const heightInput = document.getElementById("bmiHeight") || document.querySelector("[name='height_cm']");
    const valueEl = document.getElementById("bmiValue");
    const categoryEl = document.getElementById("bmiCategory");
    if (!weightInput || !heightInput || !valueEl || !categoryEl) return;

    const weight = Number(weightInput.value);
    const height = Number(heightInput.value);
    if (!weight || !height) {
      valueEl.textContent = "--";
      categoryEl.textContent = "Waiting";
      categoryEl.className = "fit-badge badge-info";
      return;
    }

    const bmi = weight / Math.pow(height / 100, 2);
    const details = category(bmi);
    valueEl.textContent = bmi.toFixed(1);
    categoryEl.textContent = details[0];
    categoryEl.className = "fit-badge " + details[1];
  }

  document.addEventListener("input", update);
  document.addEventListener("DOMContentLoaded", update);
})();
