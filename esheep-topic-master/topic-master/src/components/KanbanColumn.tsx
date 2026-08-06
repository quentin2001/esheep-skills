import React, { useState, useRef } from 'react';
import { Topic, TopicStatus } from '../types';
import { TopicCard } from './TopicCard';

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
  const dragCounter = useRef(0);

  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current += 1;
    if (dragCounter.current === 1) {
      setIsDragOver(true);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current -= 1;
    if (dragCounter.current <= 0) {
      dragCounter.current = 0;
      setIsDragOver(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    dragCounter.current = 0;
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
    dragCounter.current = 0;
    setIsDragOver(false);
  };

  return (
    <div
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`w-full flex flex-col gap-3.5 p-2.5 rounded-2xl transition-all duration-200 border-2 ${
        isDragOver
          ? 'bg-[#ff5f00]/5 dark:bg-[#ff5f00]/10 border-dashed border-[#ff5f00] shadow-xl scale-[1.01]'
          : 'border-transparent'
      }`}
    >
      {/* Column Header */}
      <div
        className={`flex justify-between items-center bg-[#ffe9e2] dark:bg-[#201f1f] px-4 py-3 rounded-xl shadow-sm ${borderStyle}`}
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
      <div className="flex flex-col gap-3.5 overflow-y-auto pb-6 min-h-[160px] p-0.5">
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

        {/* Dashed Drop Target Placeholder when dragging over */}
        {isDragOver && (
          <div className="w-full h-28 border-2 border-dashed border-[#ff5f00] rounded-xl flex items-center justify-center text-xs font-bold text-[#ff5f00] bg-[#ff5f00]/10 animate-pulse">
            Drop topic here
          </div>
        )}

        {topics.length === 0 && !isDragOver && (
          <div className="border-2 border-dashed border-[#f5ded6] dark:border-[#353534] rounded-xl p-6 text-center text-[#5b4137]/60 dark:text-[#e4bfb1]/50 text-sm">
            Drag cards here
          </div>
        )}
      </div>
    </div>
  );
};
