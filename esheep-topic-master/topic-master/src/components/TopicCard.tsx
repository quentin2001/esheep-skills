import React from 'react';
import { Topic, TopicStatus } from '../types';
import { GripVertical, Flame, Bookmark, Lightbulb, ExternalLink } from 'lucide-react';

interface TopicCardProps {
  topic: Topic;
  onEdit: (topic: Topic, rect?: DOMRect) => void;
  onMoveStatus: (id: string, newStatus: TopicStatus) => void;
  onDragStart: (e: React.DragEvent, id: string) => void;
  onDragEnd: (e: React.DragEvent) => void;
}

export const TopicCard: React.FC<TopicCardProps> = ({
  topic,
  onEdit,
  onMoveStatus,
  onDragStart,
  onDragEnd,
}) => {
  const isCompleted = topic.status === 'completed';
  const isInProgress = topic.status === 'in_progress';
  const isSelected = topic.status === 'selected';

  const renderSourceBadge = () => {
    switch (topic.source_type) {
      case 'hotlist':
        return (
          <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e5e2e1] font-semibold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent flex items-center gap-1">
            <Flame className="w-3 h-3 text-[#ff5f00]" />
            热榜
          </span>
        );
      case 'social_fav':
        return (
          <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e5e2e1] font-semibold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent flex items-center gap-1">
            <Bookmark className="w-3 h-3 text-[#a63b00]" />
            对标
          </span>
        );
      default:
        return (
          <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e5e2e1] font-semibold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent flex items-center gap-1">
            <Lightbulb className="w-3 h-3 text-amber-600 dark:text-amber-400" />
            灵感
          </span>
        );
    }
  };

  const formatPlatform = (p?: string) => {
    if (!p) return 'General';
    if (p.includes('{') || p.includes('name')) {
      if (p.toLowerCase().includes('cloudflare')) return 'Cloudflare Blog';
      return 'AIHot';
    }
    return p;
  };

  return (
    <div
      draggable
      onDragStart={(e) => onDragStart(e, topic.id)}
      onDragEnd={onDragEnd}
      onClick={(e) => onEdit(topic, e.currentTarget.getBoundingClientRect())}
      className={`group relative bg-white dark:bg-[#0e0e0e] rounded-xl p-4 shadow-ambient hover:shadow-floating transition-all duration-200 cursor-grab active:cursor-grabbing border ${
        isSelected
          ? 'border-t-4 border-t-[#ff5f00] border-x-[#f5ded6] border-b-[#f5ded6] dark:border-x-[#353534] dark:border-b-[#353534]'
          : 'border-[#f5ded6] dark:border-[#353534] hover:border-[#f8be00] dark:hover:border-[#ff5f00]/60'
      } ${isCompleted ? 'opacity-80' : ''}`}
    >
      {/* Top badges bar */}
      <div className="flex justify-between items-center mb-2">
        <div className="flex items-center gap-1.5">
          {renderSourceBadge()}
        </div>
        <div className="flex items-center gap-1.5">
          {topic.source_url && (
            <a
              href={topic.source_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="text-[#ff5f00] hover:underline text-xs font-bold flex items-center gap-0.5 mr-1"
            >
              <ExternalLink className="w-3.5 h-3.5" />
              <span>源链接</span>
            </a>
          )}
          <GripVertical className="w-4 h-4 text-[#5b4137]/40 group-hover:text-[#251914] dark:text-[#e4bfb1]/40 dark:group-hover:text-[#e5e2e1] transition-colors" />
        </div>
      </div>

      {/* Card Title */}
      <h3
        className={`font-bold text-lg md:text-xl text-[#251914] dark:text-[#e5e2e1] mb-1.5 line-clamp-2 leading-snug ${
          isCompleted ? 'line-through text-[#5b4137] dark:text-[#e4bfb1]' : ''
        }`}
      >
        {topic.title}
      </h3>

      {/* Progress Bar for In Progress items */}
      {isInProgress && (
        <div className="w-full h-2 bg-[#f5ded6] dark:bg-[#353534] rounded-full my-2.5 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-[#f8be00] to-[#ff5f00] rounded-full transition-all duration-300"
            style={{ width: `${topic.progress ?? 60}%` }}
          />
        </div>
      )}

      {/* Footer: Platform Name and Date */}
      <div className="flex justify-between items-center pt-1.5 border-t border-[#f5ded6]/60 dark:border-[#353534]/60">
        <span className="text-[#5b4137] dark:text-[#e4bfb1] text-xs font-semibold">
          {formatPlatform(topic.platform)}
        </span>
        <span className="text-xs text-[#a63b00] dark:text-[#ab8a7d] whitespace-nowrap font-semibold">
          {topic.date}
        </span>
      </div>
    </div>
  );
};
