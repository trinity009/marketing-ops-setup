const api = {
  get: async (path) => {
    const response = await fetch(path);
    if (!response.ok) {
      throw new Error(`Request failed (${response.status})`);
    }
    return response.json();
  },
  post: async (path, payload) => {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error(`Request failed (${response.status})`);
    }
    return response.json();
  },
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
  if (!items.length) {
    const li = document.createElement("li");
    li.textContent = "No records yet.";
    container.appendChild(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = mapper(item);
    container.appendChild(li);
  });
}

async function refreshLists() {
  try {
    const [guidelines, templates, prompts] = await Promise.all([
      api.get("/api/brand-guidelines"),
      api.get("/api/brief-templates"),
      api.get("/api/prompt-libraries"),
    ]);

    renderList(ids.guidelineList, guidelines, (g) => `#${g.id} ${g.name} | ${g.tone_of_voice}`);
    renderList(ids.templateList, templates, (t) => `#${t.id} ${t.name} | ${t.channel}`);
    renderList(ids.promptList, prompts, (p) => `#${p.id} ${p.name} | ${p.model_type}`);
  } catch (error) {
    ids.setupMessage.textContent = `Could not load records: ${error.message}`;
  }
}

document.getElementById("bootstrapBtn").addEventListener("click", async () => {
  try {
    const result = await api.post("/api/setup/bootstrap", {});
    ids.setupMessage.textContent = `Setup complete: ${result.status}`;
    await refreshLists();
  } catch (error) {
    ids.setupMessage.textContent = `Setup failed: ${error.message}`;
  }
});

document.getElementById("maybellineBootstrapBtn").addEventListener("click", async () => {
  try {
    const result = await api.post("/api/setup/bootstrap-maybelline", {});
    ids.setupMessage.textContent = `Baseline loaded: ${result.status}`;
    await refreshLists();
  } catch (error) {
    ids.setupMessage.textContent = `Baseline load failed: ${error.message}`;
  }
});

document.getElementById("guidelineForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api.post("/api/brand-guidelines", formDataToObject(event.target));
    event.target.reset();
    ids.setupMessage.textContent = "Brand guideline saved.";
    await refreshLists();
  } catch (error) {
    ids.setupMessage.textContent = `Save failed: ${error.message}`;
  }
});

document.getElementById("templateForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api.post("/api/brief-templates", formDataToObject(event.target));
    event.target.reset();
    ids.setupMessage.textContent = "Brief template saved.";
    await refreshLists();
  } catch (error) {
    ids.setupMessage.textContent = `Save failed: ${error.message}`;
  }
});

document.getElementById("promptForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api.post("/api/prompt-libraries", formDataToObject(event.target));
    event.target.reset();
    ids.setupMessage.textContent = "Prompt library item saved.";
    await refreshLists();
  } catch (error) {
    ids.setupMessage.textContent = `Save failed: ${error.message}`;
  }
});

document.getElementById("runForm").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const payload = formDataToObject(event.target);
    const run = await api.post("/api/workflows/run", payload);
    ids.runOutput.textContent = run.result_json;
    ids.setupMessage.textContent = `Workflow run saved as #${run.id}.`;
  } catch (error) {
    ids.runOutput.textContent = `Workflow failed: ${error.message}`;
  }
});

refreshLists();
