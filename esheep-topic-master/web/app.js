let allTopics = [];

document.addEventListener("DOMContentLoaded", () => {
  fetchTopics();

  document.getElementById("import-btn").addEventListener("click", importFavs);
  document.getElementById("new-topic-btn").addEventListener("click", openNewModal);
  document.getElementById("modal-close").addEventListener("click", closeModal);
  document.getElementById("modal-cancel").addEventListener("click", closeModal);
  document.getElementById("topic-form").addEventListener("submit", saveTopic);
  document.getElementById("delete-btn").addEventListener("click", deleteTopic);
  document.getElementById("search-input").addEventListener("input", filterTopics);
});

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
      
      let borderClass = "border border-surface-variant hover:border-primary-fixed-dim";
      if (isSelected) {
        borderClass = "border-t-2 border-primary-container border-x border-b border-x-surface-variant border-b-surface-variant";
      }
      if (isCompleted) {
        borderClass += " opacity-75";
      }

      card.className = `bg-surface-container-lowest rounded-xl p-md shadow-ambient hover:shadow-floating transition-all cursor-grab ${borderClass}`;
      card.draggable = true;
      card.dataset.id = item.id;
      card.ondragstart = (e) => e.dataTransfer.setData("text/plain", item.id);
      card.ondblclick = () => openEditModal(item);
      card.onclick = (e) => {
        if (e.detail === 1) {
          // single click delayed or double click edit
        }
      };

      const dateStr = item.created_at ? item.created_at.split("T")[0] : "";
      const platform = item.source_platform ? item.source_platform.toUpperCase() : "GENERAL";
      const tags = (item.tags || []).map(tag => `<span class="bg-surface-container text-on-surface-variant font-label-sm text-label-sm px-2 py-0.5 rounded-md">${escapeHtml(tag)}</span>`).join(" ");

      card.innerHTML = `
        <div class="flex justify-between items-center mb-sm">
          <span class="bg-surface-variant text-on-surface font-label-sm text-label-sm px-2 py-1 rounded-full">${escapeHtml(item.category || "General")}</span>
          <span class="text-on-surface-variant font-label-sm text-label-sm">${escapeHtml(platform)}</span>
        </div>
        <h3 class="font-headline-lg-mobile text-headline-lg-mobile text-on-surface mb-xs line-clamp-2 ${isCompleted ? 'line-through text-on-surface-variant' : ''}">${escapeHtml(item.title)}</h3>
        ${item.hook ? `<p class="font-body-md text-body-md text-on-surface-variant mb-md line-clamp-2">${escapeHtml(item.hook)}</p>` : ''}
        <div class="flex justify-between items-end mt-sm">
          <div class="flex flex-wrap gap-xs">${tags}</div>
          <span class="text-outline font-label-sm text-label-sm">${escapeHtml(dateStr)}</span>
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
  btn.innerHTML = `<span class="material-symbols-outlined animate-spin">sync</span> Syncing...`;
  try {
    const res = await fetch("/api/import-favs", { method: "POST" });
    const result = await res.json();
    alert(`Successfully imported ${result.imported} new items into Unselected Topics!`);
    fetchTopics();
  } catch (e) {
    alert("Failed to import. Make sure raw favs exist.");
  } finally {
    btn.innerHTML = `<span class="material-symbols-outlined">sync</span> Sync Social Favs`;
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
