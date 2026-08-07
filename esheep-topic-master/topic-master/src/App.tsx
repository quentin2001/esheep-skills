import React, { useState, useEffect, useRef } from 'react';
import { Topic, TopicStatus } from './types';
import { INITIAL_TOPICS } from './data/initialTopics';
import { Header } from './components/Header';
import { KanbanBoard } from './components/KanbanBoard';
import { EditTopicModal } from './components/EditTopicModal';
import { Trash2 } from 'lucide-react';

export type ThemeMode = 'light' | 'dark' | 'system';

export default function App() {
  // Load topics from backend API or fallback to localStorage / initial topics
  const [topics, setTopics] = useState<Topic[]>(() => {
    try {
      const saved = localStorage.getItem('topic_master_topics');
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) return parsed;
      }
    } catch (e) {
      console.error('Failed to load saved topics:', e);
    }
    return INITIAL_TOPICS;
  });

  // Theme Mode state (light, dark, system)
  const [themeMode, setThemeMode] = useState<ThemeMode>(() => {
    return (localStorage.getItem('topic_master_theme_mode') as ThemeMode) || 'system';
  });

  // Drag to delete zone state
  const [isDraggingCard, setIsDraggingCard] = useState(false);
  const [isOverDeleteZone, setIsOverDeleteZone] = useState(false);
  const deleteZoneCounter = useRef(0);

  const resetDragState = () => {
    setIsDraggingCard(false);
    setIsOverDeleteZone(false);
    deleteZoneCounter.current = 0;
  };

  useEffect(() => {
    const handleDragStart = () => {
      setIsDraggingCard(true);
    };

    const handleDragEnd = () => {
      resetDragState();
    };

    window.addEventListener('dragstart', handleDragStart);
    window.addEventListener('dragend', handleDragEnd);
    window.addEventListener('drop', handleDragEnd);
    window.addEventListener('mouseup', handleDragEnd);
    return () => {
      window.removeEventListener('dragstart', handleDragStart);
      window.removeEventListener('dragend', handleDragEnd);
      window.removeEventListener('drop', handleDragEnd);
      window.removeEventListener('mouseup', handleDragEnd);
    };
  }, []);

  // Sync theme class on <html> & <body>
  useEffect(() => {
    const root = document.documentElement;
    const applyTheme = () => {
      let isDark = false;
      if (themeMode === 'dark') {
        isDark = true;
      } else if (themeMode === 'light') {
        isDark = false;
      } else {
        isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      }

      if (isDark) {
        root.classList.add('dark');
        root.classList.remove('light');
      } else {
        root.classList.remove('dark');
        root.classList.add('light');
      }
    };

    applyTheme();
    localStorage.setItem('topic_master_theme_mode', themeMode);

    if (themeMode === 'system') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const listener = () => applyTheme();
      mediaQuery.addEventListener('change', listener);
      return () => mediaQuery.removeEventListener('change', listener);
    }
  }, [themeMode]);

  // Fetch initial topics from backend API
  useEffect(() => {
    fetch('/api/topics')
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          const mapped: Topic[] = data.map((t: any) => ({
            id: t.id,
            title: t.title || '',
            category: t.category || 'General',
            platform: t.source_platform || t.platform || 'Xiaohongshu',
            hook: t.hook || '',
            contentAngles: Array.isArray(t.angles) ? t.angles.join('\n') : (t.angles || t.contentAngles || ''),
            scriptOutline: Array.isArray(t.outline) ? t.outline.join('\n') : (t.outline || t.scriptOutline || ''),
            tags: t.tags || [],
            date: t.created_at ? t.created_at.split('T')[0] : (t.date || 'Today'),
            status: t.status === 'inbox' ? 'unselected' : (t.status as TopicStatus),
            progress: t.progress || 0,
            source_type: t.source_type || 'original_idea',
            source_url: t.source_url || t.url || ''
          }));
          setTopics(mapped);
        }
      })
      .catch(err => console.log('Backend topics API not ready, using local state'));
  }, []);

  // Sync topics to backend API & localStorage
  const syncToBackend = (newTopics: Topic[]) => {
    try {
      localStorage.setItem('topic_master_topics', JSON.stringify(newTopics));
      fetch('/api/topics/sync', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTopics.map(t => ({
          id: t.id,
          title: t.title,
          category: t.category,
          source_platform: t.platform,
          hook: t.hook,
          angles: t.contentAngles ? t.contentAngles.split('\n').filter(Boolean) : [],
          outline: t.scriptOutline ? t.scriptOutline.split('\n').filter(Boolean) : [],
          tags: t.tags,
          created_at: t.date,
          status: t.status === 'unselected' ? 'inbox' : t.status,
          progress: t.progress,
          source_type: t.source_type,
          source_url: t.source_url
        })))
      }).catch(err => console.log('Sync to backend error', err));
    } catch (e) {
      console.error('Failed to save topics:', e);
    }
  };

  // Modals state with card bounding rect
  const [editingTarget, setEditingTarget] = useState<{ topic: Topic; rect?: DOMRect } | null>(null);

  // Handlers
  const handleMoveStatus = (id: string, newStatus: TopicStatus) => {
    resetDragState();
    setTopics((prev) => {
      const updated = prev.map((t) => (t.id === id ? { ...t, status: newStatus } : t));
      syncToBackend(updated);
      return updated;
    });
  };

  const handleDropTopic = (topicId: string, newStatus: TopicStatus) => {
    resetDragState();
    handleMoveStatus(topicId, newStatus);
  };

  const handleSaveTopic = (updatedTopic: Topic) => {
    setTopics((prev) => {
      const updated = prev.map((t) => (t.id === updatedTopic.id ? updatedTopic : t));
      syncToBackend(updated);
      return updated;
    });
  };

  const handleDeleteTopic = (id: string) => {
    resetDragState();
    setTopics((prev) => {
      const updated = prev.filter((t) => t.id !== id);
      syncToBackend(updated);
      return updated;
    });
  };

  return (
    <div className="bg-[#FFF9E6] dark:bg-[#131313] text-[#251914] dark:text-[#E5E2E1] min-h-screen flex flex-col font-sans selection:bg-amber-200 dark:selection:bg-amber-900 selection:text-amber-900 transition-colors duration-200 relative">
      {/* Top Header */}
      <Header
        themeMode={themeMode}
        onThemeModeChange={setThemeMode}
      />

      {/* Left Drag to Delete Zone (Positioned BELOW header so Title is never obscured) */}
      {isDraggingCard && (
        <div
          onDragEnter={(e) => {
            e.preventDefault();
            deleteZoneCounter.current += 1;
            if (!isOverDeleteZone) setIsOverDeleteZone(true);
          }}
          onDragOver={(e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
          }}
          onDragLeave={(e) => {
            e.preventDefault();
            deleteZoneCounter.current -= 1;
            if (deleteZoneCounter.current <= 0) {
              deleteZoneCounter.current = 0;
              setIsOverDeleteZone(false);
            }
          }}
          onDrop={(e) => {
            e.preventDefault();
            const topicId = e.dataTransfer.getData('text/plain');
            if (topicId) {
              handleDeleteTopic(topicId);
            }
            resetDragState();
          }}
          className={`fixed left-0 top-[68px] bottom-0 z-30 w-44 md:w-64 flex flex-col items-center justify-center transition-all duration-300 pointer-events-auto ${
            isOverDeleteZone
              ? 'bg-gradient-to-r from-red-500/20 via-red-500/5 to-transparent'
              : 'bg-gradient-to-r from-[#ff5f00]/10 via-[#ff5f00]/2 to-transparent'
          }`}
        >
          {/* Pure Trash Icon (No border, background box, or text) */}
          <div
            className={`pointer-events-none transition-all duration-300 ${
              isOverDeleteZone
                ? 'scale-125 text-red-600 dark:text-red-500 drop-shadow-md'
                : 'scale-100 text-red-500/60 dark:text-red-400/60'
            }`}
          >
            <Trash2 className="w-10 h-10 md:w-12 md:h-12" />
          </div>
        </div>
      )}

      {/* Main Kanban Board */}
      <KanbanBoard
        topics={topics}
        onEditTopic={(t, rect) => setEditingTarget({ topic: t, rect })}
        onMoveStatus={handleMoveStatus}
        onDropTopic={handleDropTopic}
      />

      {/* Inline Floating Expansion Card */}
      <EditTopicModal
        topic={editingTarget?.topic || null}
        cardRect={editingTarget?.rect || null}
        isOpen={Boolean(editingTarget)}
        onClose={() => setEditingTarget(null)}
        onSave={handleSaveTopic}
        onDelete={handleDeleteTopic}
      />
    </div>
  );
}
