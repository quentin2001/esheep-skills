import React, { useState, useEffect } from 'react';
import { Topic, TopicStatus } from '../types';
import { KanbanColumn } from './KanbanColumn';

interface KanbanBoardProps {
  topics: Topic[];
  isDraggingCard?: boolean;
  isOverDeleteZone?: boolean;
  onEditTopic: (topic: Topic, rect?: DOMRect) => void;
  onMoveStatus: (id: string, newStatus: TopicStatus) => void;
  onDropTopic: (topicId: string, newStatus: TopicStatus) => void;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({
  topics,
  isDraggingCard,
  isOverDeleteZone,
  onEditTopic,
  onMoveStatus,
  onDropTopic,
}) => {
  const [isNarrowScreen, setIsNarrowScreen] = useState(() =>
    typeof window !== 'undefined' ? window.innerWidth < 1024 : false
  );

  useEffect(() => {
    const handleResize = () => {
      setIsNarrowScreen(window.innerWidth < 1024);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Adaptive dodge rule:
  // - Narrow screen (< 1024px): Dodge immediately when dragging card to protect space.
  // - Wide screen (>= 1024px): Dodge ONLY when mouse actually moves into the delete zone!
  const shouldDodge = isNarrowScreen ? Boolean(isDraggingCard) : Boolean(isOverDeleteZone);

  const getTopicsByStatus = (status: TopicStatus) =>
    topics.filter((t) => t.status === status);

  const unselectedList = getTopicsByStatus('unselected');
  const selectedList = getTopicsByStatus('selected');
  const inProgressList = getTopicsByStatus('in_progress');
  const completedList = getTopicsByStatus('completed');

  return (
    <main
      className={`flex-1 py-6 md:py-8 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5 md:gap-6 w-full max-w-[1650px] mx-auto items-start transition-all duration-300 ease-out px-5 sm:px-8 md:px-14 ${
        shouldDodge
          ? 'pl-16 sm:pl-24 md:pl-32 translate-x-2 md:translate-x-4 scale-[0.995]'
          : ''
      }`}
    >
      {/* Column 1: Unselected Topics */}
      <KanbanColumn
        title="Unselected Topics"
        status="unselected"
        count={unselectedList.length}
        topics={unselectedList}
        borderStyle="border-t-4 border-[#e4bfb1] dark:border-[#5b4137]"
        onEditTopic={onEditTopic}
        onMoveStatus={onMoveStatus}
        onDropTopic={onDropTopic}
      />

      {/* Column 2: Selected Topics */}
      <KanbanColumn
        title="Selected Topics"
        status="selected"
        count={selectedList.length}
        topics={selectedList}
        borderStyle="border-t-4 border-[#ff5f00] dark:border-[#ff5f00]"
        onEditTopic={onEditTopic}
        onMoveStatus={onMoveStatus}
        onDropTopic={onDropTopic}
      />

      {/* Column 3: In Progress */}
      <KanbanColumn
        title="In Progress"
        status="in_progress"
        count={inProgressList.length}
        topics={inProgressList}
        borderStyle="border-t-4 border-[#a63b00] dark:border-[#ffb599]"
        onEditTopic={onEditTopic}
        onMoveStatus={onMoveStatus}
        onDropTopic={onDropTopic}
      />

      {/* Column 4: Completed */}
      <KanbanColumn
        title="Completed"
        status="completed"
        count={completedList.length}
        topics={completedList}
        borderStyle="opacity-75 border-t-4 border-[#8f7065] dark:border-[#353534]"
        onEditTopic={onEditTopic}
        onMoveStatus={onMoveStatus}
        onDropTopic={onDropTopic}
      />
    </main>
  );
};
