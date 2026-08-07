import React, { useState } from 'react';
import { Topic, TopicStatus, PlatformOption } from '../types';
import { X, Sparkles, Loader2, Plus } from 'lucide-react';

interface NewTopicModalProps {
  isOpen: boolean;
  initialStatus?: TopicStatus;
  onClose: () => void;
  onAdd: (newTopic: Topic) => void;
}

const PLATFORMS: PlatformOption[] = [
  'X',
  'Reddit',
  'Bilibili',
  'Newsletter',
  'Blog',
  'Xiaohongshu',
  'YouTube',
  'Douyin',
  'Podcast',
];

export const NewTopicModal: React.FC<NewTopicModalProps> = ({
  isOpen,
  initialStatus = 'unselected',
  onClose,
  onAdd,
}) => {
  if (!isOpen) return null;

  const [title, setTitle] = useState('');
  const [status, setStatus] = useState<TopicStatus>(initialStatus);
  const [category, setCategory] = useState('Tech');
  const [platform, setPlatform] = useState<string>('X');
  const [hook, setHook] = useState('');
  const [contentAngles, setContentAngles] = useState('');
  const [scriptOutline, setScriptOutline] = useState('');
  const [tagsInput, setTagsInput] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    const tagsArr = tagsInput
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    const now = new Date();
    const formattedDate = `${now.toLocaleString('default', { month: 'short' })} ${now.getDate()}, ${now.getFullYear()}`;

    const newTopic: Topic = {
      id: Date.now().toString(),
      title: title.trim(),
      status,
      category: category.trim() || 'General',
      platform,
      hook: hook.trim() || 'Draft topic summary...',
      contentAngles: contentAngles.trim(),
      scriptOutline: scriptOutline.trim(),
      tags: tagsArr.length > 0 ? tagsArr : ['Draft'],
      date: formattedDate,
      progress: status === 'in_progress' ? 20 : undefined,
    };

    onAdd(newTopic);
    onClose();
  };

  const handleAIGenerateIdea = async () => {
    setIsGenerating(true);
    try {
      const res = await fetch('/api/gemini/generate-topics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keyword: category || 'Trending',
          platform,
          count: 1,
        }),
      });

      if (!res.ok) throw new Error('API failed');

      const data = await res.json();
      if (data.topics && data.topics.length > 0) {
        const item = data.topics[0];
        setTitle(item.title || '');
        setHook(item.hook || '');
        if (item.category) setCategory(item.category);
        if (item.contentAngles) setContentAngles(item.contentAngles);
        if (item.scriptOutline) setScriptOutline(item.scriptOutline);
        if (item.tags && Array.isArray(item.tags)) setTagsInput(item.tags.join(', '));
      }
    } catch (err) {
      console.error('Error generating AI idea:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 dark:bg-black/75 backdrop-blur-md z-50 flex items-center justify-center p-4 transition-all">
      <div className="bg-white dark:bg-[#131313] rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden relative border border-[#f5ded6] dark:border-[#353534]">
        {/* Header */}
        <div className="p-5 border-b border-[#f5ded6] dark:border-[#353534] flex justify-between items-center bg-[#fff8f6] dark:bg-[#1c1b1b]">
          <h2 className="font-bold text-xl md:text-2xl text-[#251914] dark:text-[#e5e2e1] flex items-center gap-2">
            <Plus className="w-5 h-5 text-[#ff5f00]" />
            New Topic
          </h2>
          <button
            onClick={onClose}
            className="text-[#5b4137] hover:text-[#251914] dark:text-[#e4bfb1] dark:hover:text-white transition-colors p-1 rounded-lg hover:bg-[#f5ded6]/50 dark:hover:bg-[#353534]"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Form Body */}
        <form onSubmit={handleSubmit} className="p-5 overflow-y-auto flex-1 flex flex-col gap-4 scrollbar-hide bg-white dark:bg-[#131313]">
          {/* AI Idea Auto-filler */}
          <div className="bg-[#fff8f6] dark:bg-[#201f1f] p-3.5 rounded-lg border border-[#f8be00]/60 dark:border-[#353534] flex justify-between items-center gap-2">
            <div className="text-xs text-[#251914] dark:text-[#e4bfb1]">
              <span className="font-bold">Need inspiration?</span> Let Gemini write a complete topic draft for you!
            </div>
            <button
              type="button"
              onClick={handleAIGenerateIdea}
              disabled={isGenerating}
              className="bg-[#f8be00] dark:bg-[#ff5f00] hover:bg-[#e0ac00] dark:hover:bg-[#ff5f00]/90 text-[#251914] dark:text-white text-xs font-bold px-3.5 py-1.5 rounded-md flex items-center gap-1.5 transition-all shadow-sm disabled:opacity-50 flex-shrink-0"
            >
              {isGenerating ? (
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
              ) : (
                <Sparkles className="w-3.5 h-3.5 text-[#a63b00] dark:text-white" />
              )}
              {isGenerating ? 'Drafting...' : 'Generate with AI'}
            </button>
          </div>

          {/* Title */}
          <div className="flex flex-col gap-1.5">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Title *
            </label>
            <input
              type="text"
              required
              placeholder="e.g., The Ultimate Guide to Micro-SaaS"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm"
            />
          </div>

          {/* Status, Category & Platform Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="flex flex-col gap-1.5">
              <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
                Target Column
              </label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as TopicStatus)}
                className="w-full px-3 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm"
              >
                <option value="unselected">Unselected Topics</option>
                <option value="selected">Selected Topics</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
                Category
              </label>
              <input
                type="text"
                placeholder="Tech, Productivity, Marketing..."
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm"
              />
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
                Platform
              </label>
              <select
                value={platform}
                onChange={(e) => setPlatform(e.target.value)}
                className="w-full px-3 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm"
              >
                {PLATFORMS.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Hook */}
          <div className="flex flex-col gap-1.5">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Hook / Core Angle
            </label>
            <textarea
              rows={2}
              placeholder="What makes this topic engaging?"
              value={hook}
              onChange={(e) => setHook(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm resize-none"
            />
          </div>

          {/* Content Angles */}
          <div className="flex flex-col gap-1.5">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Content Angles (optional)
            </label>
            <textarea
              rows={2}
              placeholder="- Angle 1&#10;- Angle 2"
              value={contentAngles}
              onChange={(e) => setContentAngles(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm resize-none"
            />
          </div>

          {/* Tags */}
          <div className="flex flex-col gap-1.5">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Tags (comma separated)
            </label>
            <input
              type="text"
              placeholder="AI, SaaS, Design"
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm"
            />
          </div>

          {/* Submit Buttons */}
          <div className="mt-2 flex justify-end gap-2.5 pt-3 border-t border-[#f5ded6] dark:border-[#353534]">
            <button
              type="button"
              onClick={onClose}
              className="text-[#5b4137] dark:text-[#e4bfb1] font-semibold text-sm px-4 py-2 hover:bg-[#f5ded6] dark:hover:bg-[#353534] rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="bg-[#ff5f00] text-white px-5 py-2 rounded-lg font-semibold text-sm border-b-2 border-[#a63b00] shadow-ambient hover:scale-[0.98] active:scale-95 transition-transform"
            >
              Create Topic
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
