export interface DashboardMetric {
  id?: number;
  name: string;
  value: number;
  change?: number;
  change_type?: 'increase' | 'decrease';
  period?: string;
  description?: string;
  color?: string;
  icon?: string;
  details?: {
    men?: number;
    women?: number;
    [key: string]: any;
  };
  created_at?: string;
  updated_at?: string;
}

export interface Announcement {
  id: number;
  title: string;
  content: string;
  author?: number;
  author_name?: string;
  author_email?: string;
  published: boolean;
  published_date: string;
  updated_date: string;
  visible_to_all: boolean;
  departments?: number[];
  departments_ids?: number[];
  departments_names?: string[];
  departments_count?: number;
}

export interface Activity {
  id: number;
  user?: number;
  user_name?: string;
  activity_type: string;
  activity_type_display?: string;
  description: string;
  related_position?: number;
  related_position_title?: string;
  related_candidate?: number;
  related_candidate_name?: string;
  related_employee?: number;
  related_employee_name?: string;
  created_at: string;
}

export interface Schedule {
  id: number;
  title: string;
  description?: string;
  assigned_to: number;
  assigned_to_name?: string;
  assigned_by?: number;
  assigned_by_name?: string;
  priority: 'high' | 'medium' | 'low';
  scheduled_date: string;
  completed: boolean;
  completed_date?: string;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: number;
  title: string;
  message: string;
  notification_type: 'info' | 'warning' | 'success' | 'error';
  is_read: boolean;
  read_at?: string;
  related_link?: string;
  created_at: string;
}

