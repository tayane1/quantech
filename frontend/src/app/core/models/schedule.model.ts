export type SchedulePriority = 'high' | 'medium' | 'low';

export interface Schedule {
  id: number;
  title: string;
  description: string;
  assigned_to: number;
  assigned_to_name?: string;
  assigned_by?: number;
  assigned_by_name?: string;
  priority: SchedulePriority;
  scheduled_date: string;
  completed: boolean;
  completed_date?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateScheduleRequest {
  title: string;
  description: string;
  assigned_to: number;
  assigned_by?: number;
  priority?: SchedulePriority;
  scheduled_date: string;
}

export interface UpdateScheduleRequest extends Partial<CreateScheduleRequest> {
  completed?: boolean;
}

export interface Meeting {
  id: number;
  title: string;
  description: string;
  organizer?: number;
  organizer_name?: string;
  attendees?: number[];
  attendees_names?: string[];
  start_time: string;
  end_time: string;
  location?: string;
  video_conference_link?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateMeetingRequest {
  title: string;
  description: string;
  organizer?: number;
  attendees?: number[];
  start_time: string;
  end_time: string;
  location?: string;
  video_conference_link?: string;
}

export interface UpdateMeetingRequest extends Partial<CreateMeetingRequest> {}

export interface ScheduleStatistics {
  total_tasks: number;
  completed_tasks: number;
  pending_tasks: number;
  overdue_tasks: number;
  tasks_by_priority: Record<SchedulePriority, number>;
  upcoming_meetings: number;
  total_meetings: number;
}

