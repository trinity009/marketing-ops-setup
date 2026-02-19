const api = {
  get: async (path) => (await fetch(path)).json(),
  post: async (path, payload) =>
    (
      await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
    ).json(),
};

const ids = {
  setupMessage: document.getElementById("setupMessage"),
  guidelineList: document.getElementById("guidelineList"),
  templateList: document.getElementById("templateList"),
  promptList: document.getElementById("promptList"),
  runOutput: document.getElementById("runOutput"),
};

function formDataToObject(form) {
  return Object.fromEntries(new FormData(form).entries());
}

function renderList(container, items, mapper) {
  container.innerHTML = "";
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = mapper(item);
    container.appendChild(li);
  });
}

async function refreshLists() {
  const [guidelines, templates, prompts] = await Promise.all([
    api.get("/api/brand-guidelines"),
    api.get("/api/brief-templates"),
    api.get("/api/prompt-libraries"),
  ]);

  renderList(ids.guidelineList, guidelines, (g) => `#${g.id} ${g.name} | ${g.tone_of_voice}`);
  renderList(ids.templateList, templates, (t) => `#${t.id} ${t.name} | ${t.channel}`);
  renderList(ids.promptList, prompts, (p) => `#${p.id} ${p.name} | ${p.model_type}`);
}

document.getElementById("bootstrapBtn").addEventListener("click", async () => {
  const result = await api.post("/api/setup/bootstrap", {});
  ids.setupMessage.textContent = result.status;
  await refreshLists();
});

document.getElementById("maybellineBootstrapBtn").addEventListener("click", async () => {
  const result = await api.post("/api/setup/bootstrap-maybelline", {});
  ids.setupMessage.textContent = result.status;
  await refreshLists();
});

document.getElementById("guidelineForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  await api.post("/api/brand-guidelines", formDataToObject(event.target));
  event.target.reset();
  await refreshLists();
});

document.getElementById("templateForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  await api.post("/api/brief-templates", formDataToObject(event.target));
  event.target.reset();
  await refreshLists();
});

document.getElementById("promptForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  await api.post("/api/prompt-libraries", formDataToObject(event.target));
  event.target.reset();
  await refreshLists();
});

document.getElementById("runForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = formDataToObject(event.target);
  const run = await api.post("/api/workflows/run", payload);
  ids.runOutput.textContent = run.result_json;
});

refreshLists();
