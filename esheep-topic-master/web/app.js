// esheep-topic-master Web UI Script
document.addEventListener('DOMContentLoaded', () => {
  // State
  let allTopics = [];
  let currentSearchQuery = '';
  let activeModalTopicId = null; // null if creating new, topic ID if editing

  // DOM Elements
  const searchInput = document.getElementById('search-input');
  const importBtn = document.getElementById('import-btn');
  const addBtn = document.getElementById('add-btn');

  // Kanban Containers & Badges
  const columns = {
    inbox: {
      container: document.getElementById('cards-inbox'),
      badge: document.getElementById('count-inbox')
    },
    selected: {
      container: document.getElementById('cards-selected'),
      badge: document.getElementById('count-selected')
    },
    in_progress: {
      container: document.getElementById('cards-in_progress'),
      badge: document.getElementById('count-in_progress')
    },
    completed: {
      container: document.getElementById('cards-completed'),
      badge: document.getElementById('count-completed')
    }
  };

  // Modal Elements
  const modal = document.getElementById('topic-modal');
  const modalHeading = document.getElementById('modal-heading');
  const modalCloseBtn = document.getElementById('modal-close-btn');
  const cancelModalBtn = document.getElementById('cancel-modal-btn');
  const deleteTopicBtn = document.getElementById('delete-topic-btn');
  const topicForm = document.getElementById('topic-form');

  // Toast Container
  const toastContainer = document.getElementById('toast-container');

  // --- Initial Load ---
  fetchTopics();

  // --- Event Listeners ---
  searchInput.addEventListener('input', (e) => {
    currentSearchQuery = e.target.value.trim().toLowerCase();
    renderBoard();
  });

  importBtn.addEventListener('click', handleImportFavs);
  addBtn.addEventListener('click', () => openModal(null));

  modalCloseBtn.addEventListener('click', closeModal);
  cancelModalBtn.addEventListener('click', closeModal);
  deleteTopicBtn.addEventListener('click', handleDeleteTopic);
  topicForm.addEventListener('submit', handleFormSubmit);

  // Close modal when clicking on backdrop
  modal.addEventListener('click', (e) => {
    if (e.target === modal) {
      closeModal();
    }
  });

  // Setup Column Drag and Drop Handlers
  Object.keys(columns).forEach(status => {
    const colElement = document.querySelector(`.kanban-column[data-status="${status}"]`);
    const container = columns[status].container;

    [colElement, container].forEach(target => {
      if (!target) return;

      target.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        container.classList.add('drag-over');
      });

      target.addEventListener('dragenter', (e) => {
        e.preventDefault();
        container.classList.add('drag-over');
      });

      target.addEventListener('dragleave', (e) => {
        // Only remove drag-over if leaving column bounds
        if (!target.contains(e.relatedTarget)) {
          container.classList.remove('drag-over');
        }
      });

      target.addEventListener('drop', (e) => {
        e.preventDefault();
        container.classList.remove('drag-over');
        const topicId = e.dataTransfer.getData('text/plain');
        if (topicId) {
          moveTopicStatus(topicId, status);
        }
      });
    });
  });

  // --- API Functions ---
  async function fetchTopics() {
    try {
      const res = await fetch('/api/topics');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      allTopics = await res.json();
      renderBoard();
    } catch (err) {
      showToast(`加载选题失败: ${err.message}`, 'error');
    }
  }

  async function moveTopicStatus(topicId, newStatus) {
    const topic = allTopics.find(t => t.id === topicId);
    if (!topic || topic.status === newStatus) return;

    const oldStatus = topic.status;
    // Optimistic UI update
    topic.status = newStatus;
    renderBoard();

    try {
      const res = await fetch(`/api/topics/${topicId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: newStatus })
      });

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const updated = await res.json();
      // Update local item with response data
      const idx = allTopics.findIndex(t => t.id === topicId);
      if (idx !== -1) allTopics[idx] = updated;
      
      const statusNames = {
        inbox: '未选中的散落选题',
        selected: '选中的选题',
        in_progress: '正在做的选题',
        completed: '做完的选题'
      };
      showToast(`已移动到 [${statusNames[newStatus] || newStatus}]`, 'success');
      renderBoard();
    } catch (err) {
      // Revert optimistic update
      topic.status = oldStatus;
      renderBoard();
      showToast(`移动失败: ${err.message}`, 'error');
    }
  }

  async function handleImportFavs() {
    importBtn.disabled = true;
    importBtn.innerHTML = '<span class="btn-icon">⏳</span> 正在导入...';

    try {
      const res = await fetch('/api/import-favs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      showToast(`成功导入 ${data.imported || 0} 条社媒收藏！`, 'success');
      await fetchTopics();
    } catch (err) {
      showToast(`导入社媒收藏失败: ${err.message}`, 'error');
    } finally {
      importBtn.disabled = false;
      importBtn.innerHTML = '<span class="btn-icon">🔄</span> 一键导入社媒收藏';
    }
  }

  async function handleFormSubmit(e) {
    e.preventDefault();

    const title = document.getElementById('form-title').value.trim();
    if (!title) {
      showToast('请输入选题标题', 'error');
      return;
    }

    const status = document.getElementById('form-status').value;
    const category = document.getElementById('form-category').value.trim();
    const sourcePlatform = document.getElementById('form-source-platform').value.trim();
    const sourceUrl = document.getElementById('form-source-url').value.trim();
    const hook = document.getElementById('form-hook').value.trim();

    const anglesRaw = document.getElementById('form-angles').value;
    const angles = anglesRaw.split('\n').map(s => s.trim()).filter(Boolean);

    const outlineRaw = document.getElementById('form-outline').value;
    const outline = outlineRaw.split('\n').map(s => s.trim()).filter(Boolean);

    const tagsRaw = document.getElementById('form-tags').value;
    const tags = tagsRaw.split(/[,，\s]+/).map(s => s.trim()).filter(Boolean);

    const payload = {
      title,
      status,
      category,
      source_platform: sourcePlatform,
      source_url: sourceUrl,
      hook,
      angles,
      outline,
      tags
    };

    try {
      if (activeModalTopicId) {
        // Edit Existing
        const res = await fetch(`/api/topics/${activeModalTopicId}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        showToast('选题保存成功', 'success');
      } else {
        // Create New
        const res = await fetch('/api/topics', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        showToast('选题创建成功', 'success');
      }

      closeModal();
      await fetchTopics();
    } catch (err) {
      showToast(`保存失败: ${err.message}`, 'error');
    }
  }

  async function handleDeleteTopic() {
    if (!activeModalTopicId) return;
    if (!confirm('确定要删除该选题吗？此操作无法撤销。')) return;

    try {
      const res = await fetch(`/api/topics/${activeModalTopicId}`, {
        method: 'DELETE'
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      showToast('选题已删除', 'info');
      closeModal();
      await fetchTopics();
    } catch (err) {
      showToast(`删除失败: ${err.message}`, 'error');
    }
  }

  // --- Rendering ---
  function renderBoard() {
    // Filter topics based on search query
    const filtered = allTopics.filter(t => {
      if (!currentSearchQuery) return true;
      const titleMatch = (t.title || '').toLowerCase().includes(currentSearchQuery);
      const categoryMatch = (t.category || '').toLowerCase().includes(currentSearchQuery);
      const hookMatch = (t.hook || '').toLowerCase().includes(currentSearchQuery);
      const platformMatch = (t.source_platform || '').toLowerCase().includes(currentSearchQuery);
      const tagsMatch = Array.isArray(t.tags) && t.tags.some(tag => tag.toLowerCase().includes(currentSearchQuery));
      return titleMatch || categoryMatch || hookMatch || platformMatch || tagsMatch;
    });

    // Group by status
    const grouped = {
      inbox: [],
      selected: [],
      in_progress: [],
      completed: []
    };

    filtered.forEach(t => {
      const st = grouped[t.status] ? t.status : 'inbox';
      grouped[st].push(t);
    });

    // Render each column
    Object.keys(columns).forEach(status => {
      const list = grouped[status] || [];
      const colObj = columns[status];
      colObj.badge.textContent = list.length;
      colObj.container.innerHTML = '';

      if (list.length === 0) {
        colObj.container.innerHTML = `
          <div class="empty-state">
            <span>暂无选题</span>
          </div>
        `;
        return;
      }

      list.forEach(topic => {
        const card = createTopicCard(topic);
        colObj.container.appendChild(card);
      });
    });
  }

  function createTopicCard(topic) {
    const card = document.createElement('div');
    card.className = 'topic-card';
    card.setAttribute('draggable', 'true');
    card.setAttribute('data-id', topic.id);

    // Header (Category & Source)
    let headerHtml = '<div class="card-header-tags">';
    if (topic.category) {
      headerHtml += `<span class="card-category">🏷️ ${escapeHtml(topic.category)}</span>`;
    } else {
      headerHtml += '<span></span>';
    }
    if (topic.source_platform) {
      headerHtml += `<span class="card-source-platform">📱 ${escapeHtml(topic.source_platform)}</span>`;
    }
    headerHtml += '</div>';

    // Title
    const titleHtml = `<h3>${escapeHtml(topic.title)}</h3>`;

    // Hook
    let hookHtml = '';
    if (topic.hook) {
      hookHtml = `<div class="card-hook">💡 ${escapeHtml(topic.hook)}</div>`;
    }

    // Tags
    let tagsHtml = '';
    if (Array.isArray(topic.tags) && topic.tags.length > 0) {
      tagsHtml = '<div class="card-tags">' + 
        topic.tags.map(tag => `<span class="tag-pill">#${escapeHtml(tag)}</span>`).join('') + 
        '</div>';
    }

    // Footer (Date / Angle count / Outline count)
    let footerInfo = [];
    if (Array.isArray(topic.angles) && topic.angles.length > 0) {
      footerInfo.push(`📐 ${topic.angles.length} 个角度`);
    }
    if (Array.isArray(topic.outline) && topic.outline.length > 0) {
      footerInfo.push(`📝 ${topic.outline.length} 点大纲`);
    }
    const updatedTime = topic.updated_at ? new Date(topic.updated_at).toLocaleDateString() : '';
    if (updatedTime) {
      footerInfo.push(`🕒 ${updatedTime}`);
    }

    const footerHtml = `<div class="card-footer"><span>${footerInfo.join(' • ')}</span></div>`;

    card.innerHTML = headerHtml + titleHtml + hookHtml + tagsHtml + footerHtml;

    // Drag Events on Card
    card.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('text/plain', topic.id);
      card.classList.add('dragging');
    });

    card.addEventListener('dragend', () => {
      card.classList.remove('dragging');
    });

    // Click & Double Click to Edit
    card.addEventListener('click', () => {
      openModal(topic.id);
    });

    return card;
  }

  // --- Modal Helpers ---
  function openModal(topicId = null) {
    activeModalTopicId = topicId;

    if (topicId) {
      const topic = allTopics.find(t => t.id === topicId);
      if (!topic) return;

      modalHeading.textContent = '编辑选题';
      document.getElementById('topic-id').value = topic.id;
      document.getElementById('form-title').value = topic.title || '';
      document.getElementById('form-status').value = topic.status || 'inbox';
      document.getElementById('form-category').value = topic.category || '';
      document.getElementById('form-source-platform').value = topic.source_platform || '';
      document.getElementById('form-source-url').value = topic.source_url || '';
      document.getElementById('form-hook').value = topic.hook || '';
      
      document.getElementById('form-angles').value = Array.isArray(topic.angles) 
        ? topic.angles.join('\n') 
        : (topic.angles || '');
        
      document.getElementById('form-outline').value = Array.isArray(topic.outline) 
        ? topic.outline.join('\n') 
        : (topic.outline || '');

      document.getElementById('form-tags').value = Array.isArray(topic.tags) 
        ? topic.tags.join(', ') 
        : (topic.tags || '');

      deleteTopicBtn.classList.remove('hidden');
    } else {
      modalHeading.textContent = '新增选题';
      topicForm.reset();
      document.getElementById('topic-id').value = '';
      document.getElementById('form-status').value = 'inbox';
      deleteTopicBtn.classList.add('hidden');
    }

    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
  }

  function closeModal() {
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    activeModalTopicId = null;
  }

  // --- Toast Notification ---
  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '❌';

    toast.innerHTML = `<span>${icon}</span> <span>${escapeHtml(message)}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  }

  // --- Utility ---
  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});
