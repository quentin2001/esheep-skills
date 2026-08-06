import React, { useState, useEffect } from 'react';
import { Topic, TopicStatus, SourceType, PlatformOption } from '../types';
import { X, Trash2, ExternalLink, Flame, Bookmark, Lightbulb } from 'lucide-react';

interface EditTopicModalProps {
  topic: Topic | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedTopic: Topic) => void;
  onDelete: (id: string) => void;
}

const PLATFORMS: PlatformOption[] = [
  'Xiaohongshu',
  'Bilibili',
  'Douyin',
  'X',
  'Reddit',
  'YouTube',
  'Newsletter',
  'Blog',
  'Podcast',
];

export const EditTopicModal: React.FC<EditTopicModalProps> = ({
  topic,
  isOpen,
  onClose,
  onSave,
  onDelete,
}) => {
  if (!isOpen || !topic) return null;

  const [title, setTitle] = useState(topic.title);
  const [status, setStatus] = useState<TopicStatus>(topic.status);
  const [sourceType, setSourceType] = useState<SourceType>(topic.source_type || 'original_idea');
  const [category, setCategory] = useState(topic.category);
  const [platform, setPlatform] = useState(topic.platform);
  const [sourceUrl, setSourceUrl] = useState(topic.source_url || '');
  const [hook, setHook] = useState(topic.hook);
  const [contentAngles, setContentAngles] = useState(topic.contentAngles || '');
  const [scriptOutline, setScriptOutline] = useState(topic.scriptOutline || '');
  const [tagsInput, setTagsInput] = useState(topic.tags.join(', '));
  const [progress, setProgress] = useState(topic.progress ?? 60);

  useEffect(() => {
    if (topic) {
      setTitle(topic.title);
      setStatus(topic.status);
      setSourceType(topic.source_type || 'original_idea');
      setCategory(topic.category);
      setPlatform(topic.platform);
      setSourceUrl(topic.source_url || '');
      setHook(topic.hook);
      setContentAngles(topic.contentAngles || '');
      setScriptOutline(topic.scriptOutline || '');
      setTagsInput(topic.tags.join(', '));
      setProgress(topic.progress ?? 60);
    }
  }, [topic]);

  const handleSave = () => {
    const tagsArr = tagsInput
      .split(',')
      .map((t) => t.trim())
      .filter((t) => t.length > 0);

    onSave({
      ...topic,
      title,
      status,
      source_type: sourceType,
      category,
      platform,
      source_url: sourceUrl,
      hook,
      contentAngles,
      scriptOutline,
      tags: tagsArr,
      progress: status === 'in_progress' ? progress : undefined,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black/60 dark:bg-black/75 backdrop-blur-md z-50 flex items-center justify-center p-4 transition-all">
      <div className="bg-white dark:bg-[#131313] rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden relative border border-[#f5ded6] dark:border-[#353534]">
        {/* Header */}
        <div className="p-5 border-b border-[#f5ded6] dark:border-[#353534] flex justify-between items-center bg-[#fff8f6] dark:bg-[#1c1b1b]">
          <div className="flex items-center gap-2">
            <h2 className="font-bold text-xl md:text-2xl text-[#251914] dark:text-[#e5e2e1]">
              Edit Topic Details
            </h2>
          </div>
          <button
            onClick={onClose}
            className="text-[#5b4137] hover:text-[#251914] dark:text-[#e4bfb1] dark:hover:text-white transition-colors p-1 rounded-lg hover:bg-[#f5ded6]/50 dark:hover:bg-[#353534]"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Scrollable Form Content */}
        <div className="p-5 overflow-y-auto flex-1 flex flex-col gap-4 scrollbar-hide bg-white dark:bg-[#131313]">
          {/* Title Input */}
          <div className="flex flex-col gap-1.5">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Topic Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm font-medium"
            />
          </div>

          {/* Status, Source Type, Category & Platform Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
            <div className="flex flex-col gap-1.5">
              <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
                Status
              </label>
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as TopicStatus)}
                className="w-full px-3 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm"
              >
                <option value="unselected">Unselected</option>
                <option value="selected">Selected</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
                Source Type
              </label>
              <select
                value={sourceType}
                onChange={(e) => setSourceType(e.target.value as SourceType)}
                className="w-full px-3 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm"
              >
                <option value="hotlist">🔥 热榜新闻 (hotlist)</option>
                <option value="social_fav">📕 平台对标 (social_fav)</option>
                <option value="original_idea">💡 灵光一现 (original_idea)</option>
              </select>
            </div>

            <div className="flex flex-col gap-1.5">
              <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
                Category
              </label>
              <input
                type="text"
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

          {/* Source URL Field */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between items-center">
              <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
                Source URL
              </label>
              {sourceUrl && (
                <a
                  href={sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-[#ff5f00] hover:underline text-xs font-bold flex items-center gap-1"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  <span>Open Link</span>
                </a>
              )}
            </div>
            <input
              type="text"
              value={sourceUrl}
              onChange={(e) => setSourceUrl(e.target.value)}
              placeholder="https://..."
              className="w-full px-3.5 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm"
            />
          </div>

          {/* Progress Slider if In Progress */}
          {status === 'in_progress' && (
            <div className="flex flex-col gap-1.5 bg-[#ffe9e2] dark:bg-[#201f1f] p-3 rounded-lg border border-[#f5ded6] dark:border-[#353534]">
              <div className="flex justify-between text-xs font-semibold text-[#251914] dark:text-[#e5e2e1]">
                <span>Progress Percentage</span>
                <span className="text-[#ff5f00] font-bold">{progress}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                step={5}
                value={progress}
                onChange={(e) => setProgress(Number(e.target.value))}
                className="w-full accent-[#ff5f00] cursor-pointer"
              />
            </div>
          )}

          {/* Hook Input */}
          <div className="flex flex-col gap-1.5">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Hook / Summary (吸睛黄金点)
            </label>
            <textarea
              rows={2}
              value={hook}
              onChange={(e) => setHook(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm resize-none"
            />
          </div>

          {/* Content Angles */}
          <div className="flex flex-col gap-1.5">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Content Angles (切入视角)
            </label>
            <textarea
              rows={3}
              value={contentAngles}
              onChange={(e) => setContentAngles(e.target.value)}
              placeholder="- Key perspective 1&#10;- Key perspective 2"
              className="w-full px-3.5 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm resize-none"
            />
          </div>

          {/* Script Outline */}
          <div className="flex flex-col gap-1.5">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Script Outline (脚本大纲)
            </label>
            <textarea
              rows={4}
              value={scriptOutline}
              onChange={(e) => setScriptOutline(e.target.value)}
              placeholder="1. Intro&#10;2. Main Point&#10;3. CTA"
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
              value={tagsInput}
              onChange={(e) => setTagsInput(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-[#f5ded6] dark:border-[#353534] flex justify-between items-center bg-[#fff8f6] dark:bg-[#1c1b1b]">
          <button
            type="button"
            onClick={() => {
              onDelete(topic.id);
              onClose();
            }}
            className="text-[#ba1a1a] dark:text-[#ffb4ab] font-semibold text-sm hover:bg-[#ffdad6]/50 dark:hover:bg-[#93000a]/30 px-3.5 py-2 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <Trash2 className="w-4 h-4" />
            <span>Delete</span>
          </button>

          <div className="flex gap-2.5">
            <button
              type="button"
              onClick={onClose}
              className="text-[#5b4137] dark:text-[#e4bfb1] font-semibold text-sm px-4 py-2 hover:bg-[#f5ded6] dark:hover:bg-[#353534] rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="bg-[#ff5f00] text-white px-5 py-2 rounded-lg font-semibold text-sm border-b-2 border-[#a63b00] shadow-ambient hover:scale-[0.98] active:scale-95 transition-transform"
            >
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
