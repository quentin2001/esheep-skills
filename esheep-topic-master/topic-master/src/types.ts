export type TopicStatus = 'unselected' | 'selected' | 'in_progress' | 'completed';
export type SourceType = 'hotlist' | 'social_fav' | 'original_idea';

export interface Topic {
  id: string;
  title: string;
  category: string;
  platform: string;
  hook: string;
  contentAngles?: string;
  scriptOutline?: string;
  tags: string[];
  date: string;
  status: TopicStatus;
  progress?: number; // 0 - 100 for in_progress
  source_type?: SourceType;
  source_url?: string;
}

export type PlatformOption = 'X' | 'Reddit' | 'Bilibili' | 'Newsletter' | 'Blog' | 'Xiaohongshu' | 'YouTube' | 'Douyin' | 'Podcast';
