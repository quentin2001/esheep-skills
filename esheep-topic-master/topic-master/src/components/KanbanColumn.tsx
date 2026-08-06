import React, { useState } from 'react';
import { Topic, TopicStatus } from '../types';
import { TopicCard } from './TopicCard';
import { Plus } from 'lucide-react';

interface KanbanColumnProps {
  title: string;
  status: TopicStatus;
  count: number;
  topics: Topic[];
  borderStyle: string;
  onEditTopic: (topic: Topic) => void;
  onMoveStatus: (id: string, newStatus: TopicStatus) => void;
  onDropTopic: (topicId: string, newStatus: TopicStatus) => void;
}

export const KanbanColumn: React.FC<KanbanColumnProps> = ({
  title,
  status,
  count,
  topics,
  borderStyle,
  onEditTopic,
  onMoveStatus,
  onDropTopic,
}) => {
  const [isDragOver, setIsDragOver] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    if (!isDragOver) setIsDragOver(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const topicId = e.dataTransfer.getData('text/plain');
    if (topicId) {
      onDropTopic(topicId, status);
    }
  };

  const handleDragStart = (e: React.DragEvent, id: string) => {
    e.dataTransfer.setData('text/plain', id);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragEnd = (_e: React.DragEvent) => {
    setIsDragOver(false);
  };

  return (
    <div className="w-full flex flex-col gap-4">
      {/* Column Header */}
      <div
        className={`flex justify-between items-center bg-[#ffe9e2] dark:bg-[#201f1f] px-4 py-3 rounded-lg shadow-sm ${borderStyle}`}
      >
        <h2 className="font-bold text-lg md:text-xl text-[#251914] dark:text-[#e5e2e1] tracking-tight">
          {title}
        </h2>
        <div className="flex items-center gap-2">
          <span className="bg-[#fff8f6] dark:bg-[#2a2a2a] text-[#5b4137] dark:text-[#e4bfb1] font-bold text-xs px-2.5 py-1 rounded-full border border-[#f5ded6] dark:border-transparent">
            {count}
          </span>
        </div>
      </div>

      {/* Droppable Card List */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`flex flex-col gap-4 overflow-y-auto scrollbar-hide pb-8 min-h-[300px] p-1 rounded-xl transition-colors duration-200 ${
          isDragOver
            ? 'bg-amber-500/10 dark:bg-[#ff5f00]/15 ring-2 ring-[#ff5f00] ring-dashed'
            : ''
        }`}
      >
        {topics.map((topic) => (
          <TopicCard
            key={topic.id}
            topic={topic}
            onEdit={onEditTopic}
            onMoveStatus={onMoveStatus}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          />
        ))}

        {topics.length === 0 && (
          <div className="border-2 border-dashed border-surface-variant dark:border-[#353534] rounded-xl p-6 text-center text-on-surface-variant/60 dark:text-[#e4bfb1]/50 text-sm">
            Drag cards here
          </div>
        )}
      </div>
    </div>
  );
};
