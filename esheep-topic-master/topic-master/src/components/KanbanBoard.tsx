import React from 'react';
import { Topic, TopicStatus } from '../types';
import { KanbanColumn } from './KanbanColumn';

interface KanbanBoardProps {
  topics: Topic[];
  onEditTopic: (topic: Topic) => void;
  onMoveStatus: (id: string, newStatus: TopicStatus) => void;
  onDropTopic: (topicId: string, newStatus: TopicStatus) => void;
}

export const KanbanBoard: React.FC<KanbanBoardProps> = ({
  topics,
  onEditTopic,
  onMoveStatus,
  onDropTopic,
}) => {
  const getTopicsByStatus = (status: TopicStatus) =>
    topics.filter((t) => t.status === status);

  const unselectedList = getTopicsByStatus('unselected');
  const selectedList = getTopicsByStatus('selected');
  const inProgressList = getTopicsByStatus('in_progress');
  const completedList = getTopicsByStatus('completed');

  return (
    <main className="flex-1 overflow-x-auto p-4 md:p-12 scrollbar-hide flex gap-6 h-[calc(100vh-80px)]">
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
