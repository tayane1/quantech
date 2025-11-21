export interface SupportCategory {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  tickets_count?: number;
  created_at: string;
  updated_at: string;
}

export interface SupportTicket {
  id: number;
  title: string;
  description: string;
  category: number;
  category_name?: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  created_by: number;
  created_by_name?: string;
  assigned_to?: number;
  assigned_to_name?: string;
  satisfaction_rating?: number;
  satisfaction_feedback?: string;
  comments_count?: number;
  attachments_count?: number;
  created_at: string;
  updated_at: string;
  resolved_at?: string;
  closed_at?: string;
}

export interface TicketComment {
  id: number;
  ticket: number;
  author: number;
  author_name?: string;
  content: string;
  is_internal: boolean;
  created_at: string;
  updated_at: string;
}

export interface TicketAttachment {
  id: number;
  ticket: number;
  uploaded_by: number;
  uploaded_by_name?: string;
  file: string;
  file_name?: string;
  file_size?: number;
  created_at: string;
}

