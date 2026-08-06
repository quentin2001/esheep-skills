let allTopics = [];
let themeMode = localStorage.getItem("topic_master_theme_mode") || "system";

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  fetchTopics();
  setupDragAndDrop();

  document.getElementById("theme-toggle-btn").addEventListener("click", cycleTheme);
  document.getElementById("modal-close").addEventListener("click", closeModal);
  document.getElementById("modal-cancel").addEventListener("click", closeModal);
  document.getElementById("topic-form").addEventListener("submit", saveTopic);
  document.getElementById("delete-btn").addEventListener("click", deleteTopic);
});

function initTheme() {
  applyTheme();
  if (themeMode === "system") {
    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", applyTheme);
  }
}

function cycleTheme() {
  if (themeMode === "light") themeMode = "dark";
  else if (themeMode === "dark") themeMode = "system";
  else themeMode = "light";

  localStorage.setItem("topic_master_theme_mode", themeMode);
  applyTheme();
}

function applyTheme() {
  const root = document.documentElement;
  const icon = document.getElementById("theme-icon");
  let isDark = false;

  if (themeMode === "dark") isDark = true;
  else if (themeMode === "light") isDark = false;
  else isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;

  if (isDark) {
    root.classList.add("dark");
    root.classList.remove("light");
    if (icon) icon.textContent = "dark_mode";
  } else {
    root.classList.remove("dark");
    root.classList.add("light");
    if (icon) icon.textContent = "light_mode";
  }
}

async function fetchTopics() {
  try {
    const res = await fetch("/api/topics");
    const data = await res.json();
    if (Array.isArray(data)) {
      allTopics = data.map(t => ({
        id: t.id,
        title: t.title || "",
        category: t.category || "General",
        platform: t.source_platform || t.platform || "Xiaohongshu",
        hook: t.hook || "",
        contentAngles: Array.isArray(t.angles) ? t.angles.join("\n") : (t.angles || ""),
        scriptOutline: Array.isArray(t.outline) ? t.outline.join("\n") : (t.outline || ""),
        tags: t.tags || [],
        date: t.created_at ? t.created_at.split("T")[0] : (t.date || "Today"),
        status: t.status === "inbox" ? "inbox" : t.status,
        source_type: t.source_type || "original_idea",
        source_url: t.source_url || t.url || ""
      }));
      renderBoard();
    }
  } catch (err) {
    console.error("Failed to fetch topics:", err);
  }
}

function renderBoard() {
  const statuses = ["inbox", "selected", "in_progress", "completed"];
  statuses.forEach(s => {
    const listEl = document.getElementById(`list-${s}`);
    const countEl = document.getElementById(`count-${s}`);
    if (!listEl) return;
    listEl.innerHTML = "";

    const filtered = allTopics.filter(t => t.status === s);
    if (countEl) countEl.textContent = filtered.length;

    filtered.forEach(item => {
      const card = document.createElement("div");
      const isCompleted = s === "completed";
      const isSelected = s === "selected";

      let borderClass = "border border-[#f5ded6] dark:border-[#353534]";
      if (isSelected) borderClass = "border-t-4 border-[#ff5f00]";
      if (isCompleted) borderClass += " opacity-75";

      card.className = `bg-white dark:bg-[#1c1b1b] rounded-xl p-4 shadow-ambient hover:shadow-floating transition-all cursor-grab flex flex-col gap-2.5 ${borderClass}`;
      card.draggable = true;
      card.dataset.id = item.id;
      card.ondragstart = (e) => {
        e.dataTransfer.setData("text/plain", item.id);
        e.dataTransfer.effectAllowed = "move";
      };
      card.ondblclick = () => openEditModal(item);

      const dateStr = item.date || "";
      const platform = item.platform ? item.platform.toUpperCase() : "GENERAL";
      
      // Source badge HTML
      let sourceBadge = "";
      if (item.source_type === "hotlist") {
        sourceBadge = `<span class="bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 font-bold text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1"><span class="material-symbols-outlined text-xs">local_fire_department</span>热榜</span>`;
      } else if (item.source_type === "social_fav") {
        sourceBadge = `<span class="bg-rose-100 dark:bg-rose-950/60 text-rose-800 dark:text-rose-300 font-bold text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1"><span class="material-symbols-outlined text-xs">bookmarks</span>对标收藏</span>`;
      } else {
        sourceBadge = `<span class="bg-blue-100 dark:bg-blue-950/60 text-blue-800 dark:text-blue-300 font-bold text-[10px] px-2 py-0.5 rounded-full flex items-center gap-1"><span class="material-symbols-outlined text-xs">lightbulb</span>灵感</span>`;
      }

      // Source URL link button
      const urlLink = item.source_url ? `<a href="${escapeHtml(item.source_url)}" target="_blank" onclick="event.stopPropagation()" class="text-[#ff5f00] hover:underline text-xs flex items-center gap-0.5 font-semibold"><span class="material-symbols-outlined text-xs">open_in_new</span>源链接</a>` : "";

      card.innerHTML = `
        <div class="flex justify-between items-center text-xs">
          <div class="flex items-center gap-1.5">
            <span class="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e4bfb1] font-bold text-[10px] px-2 py-0.5 rounded-md border border-[#f5ded6] dark:border-transparent">${escapeHtml(item.category || "General")}</span>
            ${sourceBadge}
          </div>
          <span class="text-[#8f7065] dark:text-[#a0857b] font-semibold text-[11px]">${escapeHtml(platform)}</span>
        </div>
        <h3 class="font-bold text-base text-[#251914] dark:text-[#e5e2e1] leading-snug ${isCompleted ? 'line-through opacity-70' : ''}">${escapeHtml(item.title)}</h3>
        ${item.hook ? `<p class="text-xs text-[#5b4137] dark:text-[#e4bfb1] line-clamp-2 leading-relaxed bg-[#fff8f6] dark:bg-[#252424] p-2 rounded-lg border border-[#f5ded6] dark:border-transparent">${escapeHtml(item.hook)}</p>` : ''}
        <div class="flex justify-between items-center pt-1 border-t border-[#f5ded6]/60 dark:border-[#353534]/60 mt-1 text-xs">
          ${urlLink ? urlLink : '<div></div>'}
          <span class="text-[#8f7065] dark:text-[#a0857b] text-[10px]">${escapeHtml(dateStr)}</span>
        </div>
      `;
      listEl.appendChild(card);
    });

    if (filtered.length === 0) {
      listEl.innerHTML = `<div class="border-2 border-dashed border-[#f5ded6] dark:border-[#353534] rounded-xl p-6 text-center text-[#5b4137]/60 dark:text-[#e4bfb1]/50 text-xs font-semibold">拖拽卡片至此栏</div>`;
    }
  });
}

function setupDragAndDrop() {
  const containers = document.querySelectorAll(".column-container");
  containers.forEach(container => {
    let dragCounter = 0;
    const status = container.dataset.status;

    container.addEventListener("dragenter", (e) => {
      e.preventDefault();
      dragCounter++;
      if (dragCounter === 1) {
        container.classList.add("bg-[#ff5f00]/5", "dark:bg-[#ff5f00]/10", "border-2", "border-dashed", "border-[#ff5f00]", "scale-[1.01]");
      }
    });

    container.addEventListener("dragover", (e) => {
      e.preventDefault();
      e.dataTransfer.dropEffect = "move";
    });

    container.addEventListener("dragleave", (e) => {
      e.preventDefault();
      dragCounter--;
      if (dragCounter <= 0) {
        dragCounter = 0;
        container.classList.remove("bg-[#ff5f00]/5", "dark:bg-[#ff5f00]/10", "border-2", "border-dashed", "border-[#ff5f00]", "scale-[1.01]");
      }
    });

    container.addEventListener("drop", async (e) => {
      e.preventDefault();
      dragCounter = 0;
      container.classList.remove("bg-[#ff5f00]/5", "dark:bg-[#ff5f00]/10", "border-2", "border-dashed", "border-[#ff5f00]", "scale-[1.01]");

      const topicId = e.dataTransfer.getData("text/plain");
      if (!topicId) return;

      const item = allTopics.find(t => t.id === topicId);
      if (item && item.status !== status) {
        item.status = status;
        renderBoard();
        try {
          await fetch(`/api/topics/${topicId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: status })
          });
        } catch (err) {
          console.error("Failed to update status on server:", err);
        }
      }
    });
  });
}

function openEditModal(topic) {
  document.getElementById("edit-id").value = topic.id;
  document.getElementById("edit-title").value = topic.title || "";
  document.getElementById("edit-status").value = topic.status || "inbox";
  document.getElementById("edit-source-type").value = topic.source_type || "original_idea";
  document.getElementById("edit-category").value = topic.category || "";
  document.getElementById("edit-platform").value = topic.platform || "";
  document.getElementById("edit-hook").value = topic.hook || "";
  document.getElementById("edit-angles").value = topic.contentAngles || "";
  document.getElementById("edit-outline").value = topic.scriptOutline || "";
  document.getElementById("edit-url").value = topic.source_url || "";

  document.getElementById("editModal").classList.remove("hidden");
}

function closeModal() {
  document.getElementById("editModal").classList.add("hidden");
}

async function saveTopic(e) {
  e.preventDefault();
  const id = document.getElementById("edit-id").value;

  const payload = {
    title: document.getElementById("edit-title").value,
    status: document.getElementById("edit-status").value,
    source_type: document.getElementById("edit-source-type").value,
    category: document.getElementById("edit-category").value,
    source_platform: document.getElementById("edit-platform").value,
    hook: document.getElementById("edit-hook").value,
    angles: document.getElementById("edit-angles").value.split("\n").filter(Boolean),
    outline: document.getElementById("edit-outline").value,
    source_url: document.getElementById("edit-url").value
  };

  if (id) {
    await fetch(`/api/topics/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
  }
  closeModal();
  fetchTopics();
}

async function deleteTopic() {
  const id = document.getElementById("edit-id").value;
  if (id && confirm("确定要删除这条选题吗？")) {
    await fetch(`/api/topics/${id}`, { method: "DELETE" });
    closeModal();
    fetchTopics();
  }
}

function escapeHtml(str) {
  return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
