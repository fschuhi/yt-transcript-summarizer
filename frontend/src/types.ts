export interface VideoMetadata {
  title: string;
  channel_title: string;
  description: string;
  publish_date: string;
  view_count: number;
  like_count: number;
  comment_count: number;
}

export interface SummarizeResult {
  metadata: VideoMetadata;
  summary: string;
  word_count: number;
}