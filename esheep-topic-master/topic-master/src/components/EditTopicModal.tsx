import React, { useState, useEffect } from 'react';
import { Topic, SourceType } from '../types';
import { X, Trash2, ExternalLink, Flame, Bookmark, Lightbulb } from 'lucide-react';

interface EditTopicModalProps {
  topic: Topic | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedTopic: Topic) => void;
  onDelete: (id: string) => void;
}

export const EditTopicModal: React.FC<EditTopicModalProps> = ({
  topic,
  isOpen,
  onClose,
  onSave,
  onDelete,
}) => {
  if (!isOpen || !topic) return null;

  const [title, setTitle] = useState(topic.title);
  const [sourceUrl, setSourceUrl] = useState(topic.source_url || '');

  // Combine Hook, Content Angles, Script Outline, and Tags into one single unified text content field
  const combineDetails = (t: Topic): string => {
    const parts: string[] = [];
    if (t.hook) parts.push(t.hook);
    if (t.contentAngles) parts.push(`【切入视角】\n${t.contentAngles}`);
    if (t.scriptOutline) parts.push(`【脚本大纲】\n${t.scriptOutline}`);
    if (t.tags && t.tags.length > 0) parts.push(`【标签】\n${t.tags.join(', ')}`);
    return parts.join('\n\n');
  };

  const [details, setDetails] = useState(combineDetails(topic));

  useEffect(() => {
    if (topic) {
      setTitle(topic.title);
      setSourceUrl(topic.source_url || '');
      setDetails(combineDetails(topic));
    }
  }, [topic]);

  const handleSave = () => {
    onSave({
      ...topic,
      title,
      source_url: sourceUrl,
      hook: details, // Save unified content into hook/details
    });
    onClose();
  };

  const renderSourceTypeLabel = (sourceType?: SourceType) => {
    switch (sourceType) {
      case 'hotlist':
        return (
          <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e4bfb1] font-semibold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent flex items-center gap-1">
            <Flame className="w-3.5 h-3.5 text-[#ff5f00]" />
            热榜新闻
          </span>
        );
      case 'social_fav':
        return (
          <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e4bfb1] font-semibold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent flex items-center gap-1">
            <Bookmark className="w-3.5 h-3.5 text-[#a63b00]" />
            平台对标
          </span>
        );
      default:
        return (
          <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e4bfb1] font-semibold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent flex items-center gap-1">
            <Lightbulb className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
            灵光一现
          </span>
        );
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 dark:bg-black/75 backdrop-blur-md z-50 flex items-center justify-center p-4 transition-all">
      <div className="bg-white dark:bg-[#131313] rounded-xl shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden relative border border-[#f5ded6] dark:border-[#353534]">
        {/* Header */}
        <div className="p-5 border-b border-[#f5ded6] dark:border-[#353534] flex justify-between items-center bg-[#fff8f6] dark:bg-[#1c1b1b]">
          <div className="flex items-center gap-3">
            <h2 className="font-bold text-xl md:text-2xl text-[#251914] dark:text-[#e5e2e1]">
              Edit Topic
            </h2>
            {renderSourceTypeLabel(topic.source_type)}
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
          {/* Read-Only Metadata Bar (Platform & Created Date) */}
          <div className="flex justify-between items-center bg-[#fff8f6] dark:bg-[#201f1f] px-3.5 py-2.5 rounded-lg border border-[#f5ded6] dark:border-[#353534] text-xs font-semibold text-[#5b4137] dark:text-[#e4bfb1]">
            <span>来源平台: <strong className="text-[#ff5f00] dark:text-[#ffb599]">{topic.platform || 'General'}</strong></span>
            <span>创建时间: {topic.date || 'Today'}</span>
          </div>

          {/* Title Input */}
          <div className="flex flex-col gap-1.5">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Topic Title (选题标题)
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3.5 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm font-medium"
            />
          </div>

          {/* Source URL Field */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between items-center">
              <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
                Source URL (原始链接)
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

          {/* Single Unified Content/Notes Textarea */}
          <div className="flex flex-col gap-1.5 flex-1">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Topic Details & Notes (Hook / 视角 / 大纲 / 笔记)
            </label>
            <textarea
              rows={8}
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              placeholder="在此记录选题的 Hook 吸睛点、切入视角与大纲笔记..."
              className="w-full px-3.5 py-2.5 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm leading-relaxed resize-none"
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
