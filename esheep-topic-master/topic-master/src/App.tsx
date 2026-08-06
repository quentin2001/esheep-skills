import React, { useState, useEffect } from 'react';
import { Topic, TopicStatus } from './types';
import { INITIAL_TOPICS } from './data/initialTopics';
import { Header } from './components/Header';
import { KanbanBoard } from './components/KanbanBoard';
import { EditTopicModal } from './components/EditTopicModal';
import { NewTopicModal } from './components/NewTopicModal';
import { SyncFavsModal } from './components/SyncFavsModal';
import { AIGeneratorModal } from './components/AIGeneratorModal';

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
            progress: t.progress || 0
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
          progress: t.progress
        })))
      }).catch(err => console.log('Sync to backend error', err));
    } catch (e) {
      console.error('Failed to save topics:', e);
    }
  };

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');

  // Extract unique categories
  const categories = Array.from(
    new Set(topics.map((t) => t.category).filter(Boolean))
  );

  // Modals state
  const [editingTopic, setEditingTopic] = useState<Topic | null>(null);
  const [isNewTopicOpen, setIsNewTopicOpen] = useState(false);
  const [newTopicInitialStatus, setNewTopicInitialStatus] = useState<TopicStatus>('unselected');
  const [isSyncModalOpen, setIsSyncModalOpen] = useState(false);
  const [isAIGeneratorOpen, setIsAIGeneratorOpen] = useState(false);

  // Handlers
  const handleMoveStatus = (id: string, newStatus: TopicStatus) => {
    setTopics((prev) => {
      const updated = prev.map((t) => (t.id === id ? { ...t, status: newStatus } : t));
      syncToBackend(updated);
      return updated;
    });
  };

  const handleDropTopic = (topicId: string, newStatus: TopicStatus) => {
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
    setTopics((prev) => {
      const updated = prev.filter((t) => t.id !== id);
      syncToBackend(updated);
      return updated;
    });
  };

  const handleAddTopic = (newTopic: Topic) => {
    setTopics((prev) => {
      const updated = [newTopic, ...prev];
      syncToBackend(updated);
      return updated;
    });
  };

  const handleImportMultipleTopics = (newTopics: Topic[]) => {
    setTopics((prev) => {
      const updated = [...newTopics, ...prev];
      syncToBackend(updated);
      return updated;
    });
  };

  const handleQuickAdd = (status: TopicStatus) => {
    setNewTopicInitialStatus(status);
    setIsNewTopicOpen(true);
  };

  return (
    <div className="bg-[#FFF9E6] dark:bg-[#131313] text-[#251914] dark:text-[#E5E2E1] min-h-screen flex flex-col font-sans selection:bg-amber-200 dark:selection:bg-amber-900 selection:text-amber-900 transition-colors duration-200">
      {/* Top Header */}
      <Header
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        selectedCategory={selectedCategory}
        setSelectedCategory={setSelectedCategory}
        categories={categories}
        isDarkMode={isDarkMode}
        toggleDarkMode={() => setIsDarkMode(!isDarkMode)}
        onOpenSyncModal={() => setIsSyncModalOpen(true)}
        onOpenAIGenerator={() => setIsAIGeneratorOpen(true)}
        onOpenNewTopic={() => {
          setNewTopicInitialStatus('unselected');
          setIsNewTopicOpen(true);
        }}
      />

      {/* Main Kanban Board */}
      <KanbanBoard
        topics={topics}
        searchQuery={searchQuery}
        selectedCategory={selectedCategory}
        onEditTopic={(t) => setEditingTopic(t)}
        onMoveStatus={handleMoveStatus}
        onDropTopic={handleDropTopic}
        onQuickAdd={handleQuickAdd}
      />

      {/* Modals */}
      <EditTopicModal
        topic={editingTopic}
        isOpen={Boolean(editingTopic)}
        onClose={() => setEditingTopic(null)}
        onSave={handleSaveTopic}
        onDelete={handleDeleteTopic}
      />

      <NewTopicModal
        isOpen={isNewTopicOpen}
        initialStatus={newTopicInitialStatus}
        onClose={() => setIsNewTopicOpen(false)}
        onAdd={handleAddTopic}
      />

      <SyncFavsModal
        isOpen={isSyncModalOpen}
        onClose={() => setIsSyncModalOpen(false)}
        onImportFavs={handleImportMultipleTopics}
      />

      <AIGeneratorModal
        isOpen={isAIGeneratorOpen}
        onClose={() => setIsAIGeneratorOpen(false)}
        onAddTopics={handleImportMultipleTopics}
      />
    </div>
  );
}
