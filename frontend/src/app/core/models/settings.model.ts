export interface SystemSettings {
  id: number;
  company_name: string;
  company_email: string;
  site_name: string;
  maintenance_mode: boolean;
  maintenance_message?: string;
  password_min_length: number;
  password_require_uppercase: boolean;
  password_require_lowercase: boolean;
  password_require_numbers: boolean;
  password_require_special: boolean;
  session_timeout_minutes: number;
  max_login_attempts: number;
  lockout_duration_minutes: number;
  email_enabled: boolean;
  email_host?: string;
  email_port?: number;
  email_use_tls?: boolean;
  email_username?: string;
  enable_email_notifications: boolean;
  enable_sms_notifications: boolean;
  currency: string;
  last_modified_by?: number;
  last_modified_by_name?: string;
  last_modified_at?: string;
  created_at: string;
  updated_at: string;
}

export interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  body: string;
  template_type: string;
  is_active: boolean;
  variables?: string[];
  created_at: string;
  updated_at: string;
}

export interface NotificationSettings {
  id: number;
  name: string;
  description?: string;
  notification_type: string;
  enabled: boolean;
  email_enabled: boolean;
  sms_enabled: boolean;
  in_app_enabled: boolean;
  created_at: string;
  updated_at: string;
}

