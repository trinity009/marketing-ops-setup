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
  researchSummary: document.getElementById("researchSummary"),
  insightsSummary: document.getElementById("insightsSummary"),
  contentSummary: document.getElementById("contentSummary"),
  researchList: document.getElementById("researchList"),
  insightsList: document.getElementById("insightsList"),
  contentList: document.getElementById("contentList"),
  toggleRawBtn: document.getElementById("toggleRawBtn"),
  guidelineCount: document.getElementById("guidelineCount"),
  templateCount: document.getElementById("templateCount"),
  promptCount: document.getElementById("promptCount"),
  flowRail: document.getElementById("flowRail"),
};

const stageCards = Array.from(document.querySelectorAll(".stage-card"));
let stageAnimationTimer = null;

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

function renderBullets(container, items) {
  container.innerHTML = "";
  if (!items || !items.length) {
    const li = document.createElement("li");
    li.textContent = "No details available yet.";
    container.appendChild(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    container.appendChild(li);
  });
}

function setStageProgress(progressPercent) {
  if (!ids.flowRail) return;
  ids.flowRail.style.setProperty("--flow-progress", `${progressPercent}%`);
}

function resetStageActivation() {
  stageCards.forEach((card) => card.classList.remove("active"));
  setStageProgress(0);
}

function animateStageActivation() {
  if (stageAnimationTimer) {
    window.clearInterval(stageAnimationTimer);
  }
  resetStageActivation();
  const steps = [
    { index: 0, progress: 33 },
    { index: 1, progress: 67 },
    { index: 2, progress: 100 },
  ];
  let pointer = 0;
  stageAnimationTimer = window.setInterval(() => {
    const step = steps[pointer];
    if (!step) {
      window.clearInterval(stageAnimationTimer);
      stageAnimationTimer = null;
      return;
    }
    stageCards[step.index]?.classList.add("active");
    setStageProgress(step.progress);
    pointer += 1;
  }, 260);
}

function activateStagesImmediately() {
  stageCards.forEach((card) => card.classList.add("active"));
  setStageProgress(100);
}

function attachCardTilt() {
  const cards = document.querySelectorAll(".motion-card");
  cards.forEach((card) => {
    card.addEventListener("mousemove", (event) => {
      const rect = card.getBoundingClientRect();
      const x = event.clientX - rect.left;
      const y = event.clientY - rect.top;
      const rotateY = ((x / rect.width) - 0.5) * 4;
      const rotateX = ((y / rect.height) - 0.5) * -4;
      card.style.transform = `perspective(700px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-1px)`;
    });
    card.addEventListener("mouseleave", () => {
      card.style.transform = "perspective(700px) rotateX(0) rotateY(0) translateY(0)";
    });
  });
}

function renderWorkflowResult(rawResultJson, options = {}) {
  const { animate = true } = options;
  let parsed;
  try {
    parsed = JSON.parse(rawResultJson);
  } catch (_error) {
    ids.runOutput.textContent = rawResultJson;
    ids.researchSummary.textContent = "Could not parse research output.";
    ids.insightsSummary.textContent = "Could not parse insights output.";
    ids.contentSummary.textContent = "Could not parse content output.";
    renderBullets(ids.researchList, []);
    renderBullets(ids.insightsList, []);
    renderBullets(ids.contentList, []);
    return;
  }

  const research = parsed.research || {};
  const insights = parsed.insights || {};
  const content = parsed.content || {};

  ids.researchSummary.textContent = research.brand_constraints || "Research stage completed.";
  ids.insightsSummary.textContent = insights.priority_insight || "Insights stage completed.";
  ids.contentSummary.textContent = content.asset_notes || "Content stage completed.";

  renderBullets(ids.researchList, research.research_findings || []);
  renderBullets(ids.insightsList, insights.recommended_test_matrix || []);

  const draftPreview = content.draft_copy
    ? content.draft_copy.split("\n").slice(0, 2).join(" ")
    : "No draft copy generated.";
  renderBullets(ids.contentList, [draftPreview, content.asset_notes || "No asset notes"]);

  ids.runOutput.textContent = JSON.stringify(parsed, null, 2);
  if (animate) {
    animateStageActivation();
  } else {
    activateStagesImmediately();
  }
}

async function refreshLatestWorkflow() {
  try {
    const workflows = await api.get("/api/workflows");
    if (!Array.isArray(workflows) || !workflows.length) {
      resetStageActivation();
      return;
    }
    renderWorkflowResult(workflows[0].result_json, { animate: false });
  } catch (_error) {
    // Keep dashboard usable even if workflow history is unavailable.
  }
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
    ids.guidelineCount.textContent = String(guidelines.length);
    ids.templateCount.textContent = String(templates.length);
    ids.promptCount.textContent = String(prompts.length);
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
    renderWorkflowResult(run.result_json);
    ids.setupMessage.textContent = `Workflow run saved as #${run.id}.`;
  } catch (error) {
    ids.runOutput.textContent = `Workflow failed: ${error.message}`;
  }
});

ids.toggleRawBtn.addEventListener("click", () => {
  ids.runOutput.classList.toggle("hidden");
});

refreshLists();
refreshLatestWorkflow();
attachCardTilt();
