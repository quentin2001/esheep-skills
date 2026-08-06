import React from 'react';
import { Topic, TopicStatus } from '../types';
import { GripVertical, Sparkles, ChevronRight, ChevronLeft } from 'lucide-react';

interface TopicCardProps {
  topic: Topic;
  onEdit: (topic: Topic) => void;
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

  // Status transitions for quick move buttons
  const getNextStatus = (current: TopicStatus): TopicStatus | null => {
    switch (current) {
      case 'unselected': return 'selected';
      case 'selected': return 'in_progress';
      case 'in_progress': return 'completed';
      default: return null;
    }
  };

  const getPrevStatus = (current: TopicStatus): TopicStatus | null => {
    switch (current) {
      case 'selected': return 'unselected';
      case 'in_progress': return 'selected';
      case 'completed': return 'in_progress';
      default: return null;
    }
  };

  const prevStatus = getPrevStatus(topic.status);
  const nextStatus = getNextStatus(topic.status);

  return (
    <div
      draggable
      onDragStart={(e) => onDragStart(e, topic.id)}
      onDragEnd={onDragEnd}
      onClick={() => onEdit(topic)}
      className={`group relative bg-white dark:bg-[#0e0e0e] rounded-xl p-4 shadow-ambient hover:shadow-floating transition-all duration-200 cursor-grab active:cursor-grabbing border ${
        isSelected
          ? 'border-t-4 border-t-[#ff5f00] border-x-[#f5ded6] border-b-[#f5ded6] dark:border-x-[#353534] dark:border-b-[#353534]'
          : 'border-[#f5ded6] dark:border-[#353534] hover:border-[#f8be00] dark:hover:border-[#ff5f00]/60'
      } ${isCompleted ? 'opacity-80' : ''}`}
    >
      {/* Top badges bar */}
      <div className="flex justify-between items-center mb-2">
        <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#251914] dark:text-[#e5e2e1] font-semibold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent">
          {topic.category || 'General'}
        </span>
        <div className="flex items-center gap-1">
          <span className="text-[#5b4137] dark:text-[#e4bfb1] text-xs font-semibold">
            {topic.platform}
          </span>
          <GripVertical className="w-4 h-4 text-[#5b4137]/40 group-hover:text-[#251914] dark:text-[#e4bfb1]/40 dark:group-hover:text-[#e5e2e1] transition-colors ml-1" />
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

      {/* Hook / Summary */}
      <p className="text-sm text-[#5b4137] dark:text-[#e4bfb1] mb-3 line-clamp-2 leading-relaxed font-normal">
        {topic.hook}
      </p>

      {/* Tags and Date */}
      <div className="flex justify-between items-end pt-1">
        <div className="flex flex-wrap gap-1.5 max-w-[70%]">
          {topic.tags.map((tag, idx) => (
            <span
              key={idx}
              className="bg-[#fff8f6] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e4bfb1] border border-[#f5ded6] dark:border-transparent font-medium text-xs px-2 py-0.5 rounded-md"
            >
              #{tag}
            </span>
          ))}
        </div>
        <span className="text-xs text-[#a63b00] dark:text-[#ab8a7d] whitespace-nowrap font-semibold">
          {topic.date}
        </span>
      </div>

    </div>
  );
};
