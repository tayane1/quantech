export interface Message {
  id: number;
  sender: number;
  sender_name?: string;
  sender_email?: string;
  sender_avatar?: string;
  recipient: number;
  recipient_name?: string;
  subject?: string;
  content: string;
  is_read: boolean;
  read_at?: string;
  created_at: string;
  updated_at?: string;
}

export interface Conversation {
  id: number;
  participants: number[];
  participant_names?: string[];
  last_message?: Message;
  unread_count: number;
  updated_at: string;
}

