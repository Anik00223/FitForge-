(function () {
  const form = document.getElementById("plannerForm");
  const loading = document.getElementById("plannerLoading");
  const button = document.getElementById("generatePlanBtn");
  if (form) {
    form.addEventListener("submit", function () {
      if (loading) loading.classList.remove("d-none");
      if (button) {
        button.disabled = true;
        button.textContent = "Forging...";
      }
    });
  }

  const qaForm = document.getElementById("qaForm");
  if (!qaForm) return;

  qaForm.addEventListener("submit", async function (event) {
    event.preventDefault();
    const data = new FormData(qaForm);
    const question = (data.get("question") || "").toString().trim();
    if (!question) return;

    const submit = qaForm.querySelector("button[type='submit']");
    submit.disabled = true;
    submit.textContent = "Asking...";

    try {
      const response = await fetch(qaForm.dataset.url, {
        method: "POST",
        body: data,
        headers: { "X-Requested-With": "XMLHttpRequest" },
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "AI question failed.");

      const wrap = document.getElementById("qaMessages");
      const block = document.createElement("div");
      block.className = "qa-block";
      block.innerHTML = `<strong>Q: ${escapeHtml(payload.question)}</strong><div class="ai-output small-output">${payload.answer}</div>`;
      wrap.prepend(block);
      qaForm.reset();
    } catch (error) {
      alert(error.message);
    } finally {
      submit.disabled = false;
      submit.textContent = "Ask AI";
    }
  });

  function escapeHtml(value) {
    return value.replace(/[&<>"']/g, function (char) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;",
      }[char];
    });
  }
})();
