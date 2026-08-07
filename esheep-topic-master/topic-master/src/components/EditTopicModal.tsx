import React, { useState, useEffect } from 'react';
import { Topic, SourceType } from '../types';
import { X, Trash2, ExternalLink, Flame, Bookmark, Lightbulb } from 'lucide-react';

interface EditTopicModalProps {
  topic: Topic | null;
  cardRect: DOMRect | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (updatedTopic: Topic) => void;
  onDelete: (id: string) => void;
}

export const EditTopicModal: React.FC<EditTopicModalProps> = ({
  topic,
  cardRect,
  isOpen,
  onClose,
  onSave,
  onDelete,
}) => {
  if (!isOpen || !topic) return null;

  const [title, setTitle] = useState(topic.title);
  const [sourceUrl, setSourceUrl] = useState(topic.source_url || '');

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
      hook: details,
    });
    onClose();
  };

  const renderSourceTypeLabel = (sourceType?: SourceType) => {
    switch (sourceType) {
      case 'hotlist':
        return (
          <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e4bfb1] font-semibold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent flex items-center gap-1">
            <Flame className="w-3.5 h-3.5 text-[#ff5f00]" />
            热榜
          </span>
        );
      case 'social_fav':
        return (
          <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e4bfb1] font-semibold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent flex items-center gap-1">
            <Bookmark className="w-3.5 h-3.5 text-[#a63b00]" />
            对标
          </span>
        );
      default:
        return (
          <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e4bfb1] font-semibold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent flex items-center gap-1">
            <Lightbulb className="w-3.5 h-3.5 text-amber-600 dark:text-amber-400" />
            灵感
          </span>
        );
    }
  };

  // Calculate dynamic inline expansion position to the RIGHT side of the clicked card
  const computeInlineStyle = (): React.CSSProperties => {
    const isMobile = window.innerWidth < 768;
    if (isMobile || !cardRect) {
      return {
        position: 'fixed',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: 'min(92vw, 520px)',
        maxHeight: '88vh',
      };
    }

    const targetWidth = Math.min(520, window.innerWidth - 32);

    // Prefer positioning directly to the RIGHT side of the clicked card
    let left = cardRect.right + 16;
    if (left + targetWidth > window.innerWidth - 16) {
      // Fallback: position to the LEFT side of the card
      left = cardRect.left - targetWidth - 16;
      if (left < 16) {
        left = window.innerWidth - targetWidth - 16;
      }
    }

    let top = Math.max(16, cardRect.top - 8);
    const estimatedHeight = 520;
    if (top + estimatedHeight > window.innerHeight - 16) {
      top = Math.max(16, window.innerHeight - estimatedHeight - 16);
    }

    return {
      position: 'fixed',
      top: `${top}px`,
      left: `${left}px`,
      width: `${targetWidth}px`,
      maxHeight: `calc(100vh - ${top + 16}px)`,
    };
  };

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 bg-black/15 dark:bg-black/35 backdrop-blur-[1px] z-50 transition-opacity duration-300 ease-out"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        style={computeInlineStyle()}
        className="bg-white dark:bg-[#131313] rounded-2xl shadow-floating flex flex-col overflow-hidden relative border-2 border-[#ff5f00] dark:border-[#ff5f00] transition-all duration-300 ease-out origin-top-left animate-in fade-in zoom-in-95"
      >
        {/* Header */}
        <div className="p-4 px-5 border-b border-[#f5ded6] dark:border-[#353534] flex justify-between items-center bg-[#fff8f6] dark:bg-[#1c1b1b]">
          <div className="flex items-center gap-3">
            <h2 className="font-bold text-lg md:text-xl text-[#251914] dark:text-[#e5e2e1]">
              Edit Topic
            </h2>
            {renderSourceTypeLabel(topic.source_type)}
          </div>
          <button
            onClick={onClose}
            className="text-[#5b4137] hover:text-[#251914] dark:text-[#e4bfb1] dark:hover:text-white transition-colors p-1 rounded-lg hover:bg-[#f5ded6]/50 dark:hover:bg-[#353534]"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content Form */}
        <div className="p-4 px-5 overflow-y-auto flex-1 flex flex-col gap-3.5 scrollbar-hide bg-white dark:bg-[#131313]">
          {/* Metadata Bar */}
          <div className="flex justify-between items-center bg-[#fff8f6] dark:bg-[#201f1f] px-3.5 py-2 rounded-lg border border-[#f5ded6] dark:border-[#353534] text-xs font-semibold text-[#5b4137] dark:text-[#e4bfb1]">
            <span>来源平台: <strong className="text-[#ff5f00] dark:text-[#ffb599]">{topic.platform || 'General'}</strong></span>
            <span>创建时间: {topic.date || 'Today'}</span>
          </div>

          {/* Title Input */}
          <div className="flex flex-col gap-1">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              Topic Title (选题标题)
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm font-medium"
            />
          </div>

          {/* Source URL Field */}
          <div className="flex flex-col gap-1">
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
              className="w-full px-3 py-2 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm"
            />
          </div>

          {/* Unified Content/Notes Textarea */}
          <div className="flex flex-col gap-1 flex-1">
            <label className="font-semibold text-xs text-[#5b4137] dark:text-[#e4bfb1]">
              选题思考与笔记 (Notes & Outline)
            </label>
            <textarea
              rows={6}
              value={details}
              onChange={(e) => setDetails(e.target.value)}
              placeholder="在此记录选题的 Hook 吸睛点、切入视角与大纲笔记..."
              className="w-full px-3.5 py-2.5 bg-[#fff8f6] dark:bg-[#0e0e0e] border border-[#e4bfb1] dark:border-[#353534] focus:border-2 focus:border-[#ff5f00] focus:outline-none rounded-lg text-[#251914] dark:text-[#e5e2e1] text-sm leading-relaxed resize-none"
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-3.5 px-4 border-t border-[#f5ded6] dark:border-[#353534] flex justify-between items-center bg-[#fff8f6] dark:bg-[#1c1b1b]">
          <button
            type="button"
            onClick={() => {
              onDelete(topic.id);
              onClose();
            }}
            className="text-[#ba1a1a] dark:text-[#ffb4ab] font-semibold text-xs hover:bg-[#ffdad6]/50 dark:hover:bg-[#93000a]/30 px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Delete</span>
          </button>

          <div className="flex gap-2">
            <button
              type="button"
              onClick={onClose}
              className="text-[#5b4137] dark:text-[#e4bfb1] font-semibold text-xs px-3.5 py-1.5 hover:bg-[#f5ded6] dark:hover:bg-[#353534] rounded-lg transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              onClick={handleSave}
              className="bg-[#ff5f00] text-white px-4 py-1.5 rounded-lg font-semibold text-xs border-b-2 border-[#a63b00] shadow-ambient hover:scale-[0.98] active:scale-95 transition-transform"
            >
              Save Changes
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
