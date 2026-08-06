let allTopics = [];

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  fetchTopics();

  document.getElementById("theme-toggle-btn").addEventListener("click", toggleTheme);
  document.getElementById("import-btn").addEventListener("click", importFavs);
  document.getElementById("new-topic-btn").addEventListener("click", openNewModal);
  document.getElementById("modal-close").addEventListener("click", closeModal);
  document.getElementById("modal-cancel").addEventListener("click", closeModal);
  document.getElementById("topic-form").addEventListener("submit", saveTopic);
  document.getElementById("delete-btn").addEventListener("click", deleteTopic);
  document.getElementById("search-input").addEventListener("input", filterTopics);
});

function initTheme() {
  const savedTheme = localStorage.getItem("theme") || "dark";
  const html = document.documentElement;
  const themeIcon = document.getElementById("theme-icon");
  if (savedTheme === "light") {
    html.classList.remove("dark");
    html.classList.add("light");
    if (themeIcon) themeIcon.textContent = "dark_mode";
  } else {
    html.classList.remove("light");
    html.classList.add("dark");
    if (themeIcon) themeIcon.textContent = "light_mode";
  }
}

function toggleTheme() {
  const html = document.documentElement;
  const themeIcon = document.getElementById("theme-icon");
  if (html.classList.contains("dark")) {
    html.classList.remove("dark");
    html.classList.add("light");
    localStorage.setItem("theme", "light");
    if (themeIcon) themeIcon.textContent = "dark_mode";
  } else {
    html.classList.remove("light");
    html.classList.add("dark");
    localStorage.setItem("theme", "dark");
    if (themeIcon) themeIcon.textContent = "light_mode";
  }
}

async function fetchTopics() {
  try {
    const res = await fetch("/api/topics");
    allTopics = await res.json();
    renderBoard(allTopics);
  } catch (err) {
    console.error("Failed to fetch topics:", err);
  }
}

function renderBoard(topics) {
  const statuses = ["inbox", "selected", "in_progress", "completed"];
  statuses.forEach(s => {
    const listEl = document.getElementById(`list-${s}`);
    const countEl = document.getElementById(`count-${s}`);
    listEl.innerHTML = "";
    
    const filtered = topics.filter(t => t.status === s);
    countEl.textContent = filtered.length;

    filtered.forEach(item => {
      const card = document.createElement("div");
      const isCompleted = s === "completed";
      const isSelected = s === "selected";
      const isInProgress = s === "in_progress";
      
      let borderClass = "border border-surface-variant hover:border-primary";
      if (isSelected) {
        borderClass = "border-t-4 border-purple-500 border-x border-b border-surface-variant";
      } else if (isInProgress) {
        borderClass = "border-t-4 border-amber-500 border-x border-b border-surface-variant";
      } else if (isCompleted) {
        borderClass = "border border-surface-variant opacity-75";
      }

      card.className = `bg-surface-container-lowest rounded-2xl p-5 shadow-ambient hover:shadow-floating transition-all cursor-grab ${borderClass}`;
      card.draggable = true;
      card.dataset.id = item.id;
      card.ondragstart = (e) => e.dataTransfer.setData("text/plain", item.id);
      card.ondblclick = () => openEditModal(item);

      const dateStr = item.created_at ? item.created_at.split("T")[0] : "";
      const platform = item.source_platform ? item.source_platform.toUpperCase() : "GENERAL";
      const tags = (item.tags || []).map(tag => `<span class="bg-surface-container text-on-surface-variant font-bold text-[11px] px-2 py-0.5 rounded-md uppercase tracking-wider">${escapeHtml(tag)}</span>`).join(" ");

      card.innerHTML = `
        <div class="flex justify-between items-center mb-3">
          <span class="bg-surface-variant text-on-surface font-bold text-xs px-2.5 py-1 rounded-full uppercase tracking-wider">${escapeHtml(item.category || "General")}</span>
          <span class="text-on-surface-variant font-bold text-xs uppercase tracking-wider">${escapeHtml(platform)}</span>
        </div>
        <h3 class="font-bold text-base md:text-lg text-on-surface mb-2 leading-snug tracking-tight ${isCompleted ? 'line-through text-on-surface-variant' : ''}">${escapeHtml(item.title)}</h3>
        ${item.hook ? `<p class="font-medium text-sm text-on-surface-variant mb-4 line-clamp-2 leading-normal">${escapeHtml(item.hook)}</p>` : ''}
        <div class="flex justify-between items-end mt-2 pt-2 border-t border-surface-variant/40">
          <div class="flex flex-wrap gap-1.5">${tags}</div>
          <span class="text-on-surface-variant font-semibold text-xs tracking-wider">${escapeHtml(dateStr)}</span>
        </div>
      `;
      listEl.appendChild(card);
    });
  });
}

function allowDrop(ev) {
  ev.preventDefault();
}

async function drop(ev, newStatus) {
  ev.preventDefault();
  const id = ev.dataTransfer.getData("text/plain");
  if (!id) return;

  const item = allTopics.find(t => t.id === id);
  if (item && item.status !== newStatus) {
    item.status = newStatus;
    renderBoard(allTopics);
    await fetch(`/api/topics/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus })
    });
  }
}

async function importFavs() {
  const btn = document.getElementById("import-btn");
  btn.innerHTML = `<span class="material-symbols-outlined text-lg animate-spin">sync</span><span>Syncing...</span>`;
  try {
    const res = await fetch("/api/import-favs", { method: "POST" });
    const result = await res.json();
    alert(`Successfully imported ${result.imported} new items into Unselected Topics!`);
    fetchTopics();
  } catch (e) {
    alert("Failed to import. Make sure raw favs exist.");
  } finally {
    btn.innerHTML = `<span class="material-symbols-outlined text-lg">sync</span><span>Sync Social Favs</span>`;
  }
}

function openEditModal(topic) {
  document.getElementById("edit-id").value = topic.id;
  document.getElementById("edit-title").value = topic.title || "";
  document.getElementById("edit-status").value = topic.status || "inbox";
  document.getElementById("edit-category").value = topic.category || "";
  document.getElementById("edit-hook").value = topic.hook || "";
  document.getElementById("edit-angles").value = (topic.angles || []).join("\n");
  document.getElementById("edit-outline").value = topic.outline || "";
  document.getElementById("edit-tags").value = (topic.tags || []).join(", ");
  
  document.getElementById("modal-heading").textContent = "Edit Topic";
  document.getElementById("delete-btn").style.display = "block";
  document.getElementById("editModal").classList.remove("hidden");
}

function openNewModal() {
  document.getElementById("edit-id").value = "";
  document.getElementById("topic-form").reset();
  document.getElementById("modal-heading").textContent = "New Topic";
  document.getElementById("delete-btn").style.display = "none";
  document.getElementById("editModal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("editModal").classList.add("hidden");
}

async function saveTopic(e) {
  e.preventDefault();
  const id = document.getElementById("edit-id").value;
  const rawTags = document.getElementById("edit-tags").value;
  const tagsArray = rawTags ? rawTags.split(",").map(t => t.trim()).filter(Boolean) : [];
  
  const payload = {
    title: document.getElementById("edit-title").value,
    status: document.getElementById("edit-status").value,
    category: document.getElementById("edit-category").value,
    hook: document.getElementById("edit-hook").value,
    angles: document.getElementById("edit-angles").value.split("\n").filter(a => a.trim()),
    outline: document.getElementById("edit-outline").value,
    tags: tagsArray
  };

  if (id) {
    await fetch(`/api/topics/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  } else {
    await fetch("/api/topics", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  }
  closeModal();
  fetchTopics();
}

async function deleteTopic() {
  const id = document.getElementById("edit-id").value;
  if (id && confirm("Are you sure you want to delete this topic?")) {
    await fetch(`/api/topics/${id}`, { method: "DELETE" });
    closeModal();
    fetchTopics();
  }
}

function filterTopics(e) {
  const query = e.target.value.toLowerCase();
  const filtered = allTopics.filter(t => 
    (t.title && t.title.toLowerCase().includes(query)) ||
    (t.category && t.category.toLowerCase().includes(query)) ||
    (t.hook && t.hook.toLowerCase().includes(query)) ||
    (t.tags && t.tags.some(tag => tag.toLowerCase().includes(query)))
  );
  renderBoard(filtered);
}

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
