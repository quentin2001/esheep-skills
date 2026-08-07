import React from 'react';
import { Topic, TopicStatus } from '../types';
import { KanbanColumn } from './KanbanColumn';
import { Language, translations } from '../i18n';

interface KanbanBoardProps {
  topics: Topic[];
  isDraggingCard?: boolean;
  isOverDeleteZone?: boolean;
  lang?: Language;
  onEditTopic: (topic: Topic, rect?: DOMRect) => void;
  onMoveStatus: (id: string, newStatus: TopicStatus) => void;
  onDropTopic: (topicId: string, newStatus: TopicStatus) => void;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({
  topics,
  isDraggingCard,
  isOverDeleteZone,
  lang = 'zh',
  onEditTopic,
  onMoveStatus,
  onDropTopic,
}) => {
  const t = translations[lang];

  const getTopicsByStatus = (status: TopicStatus) =>
    topics.filter((t) => t.status === status);

  const unselectedList = getTopicsByStatus('unselected');
  const selectedList = getTopicsByStatus('selected');
  const inProgressList = getTopicsByStatus('in_progress');
  const completedList = getTopicsByStatus('completed');

  return (
    <main
      className={`flex-1 py-6 md:py-8 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-5 md:gap-6 w-full max-w-[1650px] mx-auto items-start transition-all duration-300 ease-out ${
        isDraggingCard
          ? 'pl-24 sm:pl-32 md:pl-40 pr-5 sm:pr-8 md:pr-14'
          : 'px-5 sm:px-8 md:px-14'
      } ${isOverDeleteZone ? 'translate-x-4 md:translate-x-8 scale-[0.99]' : ''}`}
    >
      {/* Column 1: Unselected Topics */}
      <KanbanColumn
        title={t.colUnselected}
        status="unselected"
        count={unselectedList.length}
        topics={unselectedList}
        borderStyle="border-t-4 border-[#e4bfb1] dark:border-[#5b4137]"
        lang={lang}
        onEditTopic={onEditTopic}
        onMoveStatus={onMoveStatus}
        onDropTopic={onDropTopic}
      />

      {/* Column 2: Selected Topics */}
      <KanbanColumn
        title={t.colSelected}
        status="selected"
        count={selectedList.length}
        topics={selectedList}
        borderStyle="border-t-4 border-[#ff5f00] dark:border-[#ff5f00]"
        lang={lang}
        onEditTopic={onEditTopic}
        onMoveStatus={onMoveStatus}
        onDropTopic={onDropTopic}
      />

      {/* Column 3: In Progress */}
      <KanbanColumn
        title={t.colInProgress}
        status="in_progress"
        count={inProgressList.length}
        topics={inProgressList}
        borderStyle="border-t-4 border-[#a63b00] dark:border-[#ffb599]"
        lang={lang}
        onEditTopic={onEditTopic}
        onMoveStatus={onMoveStatus}
        onDropTopic={onDropTopic}
      />

      {/* Column 4: Completed */}
      <KanbanColumn
        title={t.colCompleted}
        status="completed"
        count={completedList.length}
        topics={completedList}
        borderStyle="opacity-75 border-t-4 border-[#8f7065] dark:border-[#353534]"
        lang={lang}
        onEditTopic={onEditTopic}
        onMoveStatus={onMoveStatus}
        onDropTopic={onDropTopic}
      />
    </main>
  );
};
