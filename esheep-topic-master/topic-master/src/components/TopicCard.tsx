import React from 'react';
import { Topic, TopicStatus } from '../types';
import { GripVertical, Flame, Bookmark, Lightbulb, ExternalLink, Trash2 } from 'lucide-react';

interface TopicCardProps {
  topic: Topic;
  onEdit: (topic: Topic, rect?: DOMRect) => void;
  onMoveStatus: (id: string, status: TopicStatus) => void;
  onDelete: (id: string) => void;
  onDragStart?: (e: React.DragEvent, id: string) => void;
  onDragEnd?: (e: React.DragEvent) => void;
}

export const TopicCard: React.FC<TopicCardProps> = ({
  topic,
  onEdit,
  onMoveStatus,
  onDelete,
  onDragStart,
  onDragEnd,
}) => {
  const handleDoubleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    onEdit(topic, rect);
  };

  return (
    <div
      draggable
      onDragStart={(e) => onDragStart && onDragStart(e, topic.id)}
      onDragEnd={(e) => onDragEnd && onDragEnd(e)}
      className="bg-white dark:bg-[#131313] rounded-xl shadow-lg border border-[#f5ded6] dark:border-[#353534] transition-transform hover:scale-[1.02] hover:shadow-xl cursor-grab active:cursor-grabbing"
      onDoubleClick={handleDoubleClick}
    >
      {/* Header */}
      <div className="flex justify-between items-center p-3 border-b border-[#f5ded6] dark:border-[#353534]">
        <div className="flex items-center gap-2">
          {/* Platform Badge */}
          <span className="bg-[#ffe9e2] dark:bg-[#201f1f] text-[#5b4137] dark:text-[#e4bfb1] text-xs font-semibold px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent">
            {topic.platform}
          </span>
          <h3 className="font-bold text-sm text-[#251914] dark:text-[#e5e2e1] truncate max-w-[120px]">
            {topic.title}
          </h3>
        </div>
        {/* Source Link moved to top-right */}
        {topic.source && (
          <a
            href={topic.source}
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#ff5f00] hover:underline text-xs flex items-center gap-1"
          >
            <ExternalLink className="w-3.5 h-3.5" />
            <span>源链接 ↗</span>
          </a>
        )}
      </div>

      {/* Footer */}
      <div className="flex justify-between items-center p-2 text-xs text-[#5b4137] dark:text-[#e4bfb1] bg-[#fff8f6] dark:bg-[#1c1b1b] border-t border-[#f5ded6] dark:border-[#353534]">
        <span>创建时间: {topic.date}</span>
        {/* Actions */}
        <div className="flex gap-2 items-center">
          <button
            onClick={() => onMoveStatus(topic.id, 'selected')}
            className="text-[#5b4137] hover:text-[#251914] dark:text-[#e4bfb1] dark:hover:text-white transition-colors p-1 rounded-lg hover:bg-[#f5ded6]/50 dark:hover:bg-[#353534]"
          >
            <Flame className="w-4 h-4" />
          </button>
          <button
            onClick={() => onDelete(topic.id)}
            className="text-[#ba1a1a] hover:text-[#ff5f00] transition-colors p-1 rounded-lg"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
