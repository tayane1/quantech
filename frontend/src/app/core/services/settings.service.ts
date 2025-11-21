import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { ApiService } from './api.service';
import { SystemSettings, EmailTemplate, NotificationSettings } from '../models/settings.model';

export interface EmailTemplateListResponse {
  count: number;
  results: EmailTemplate[];
}

export interface NotificationSettingsListResponse {
  count: number;
  results: NotificationSettings[];
}

@Injectable({
  providedIn: 'root'
})
export class SettingsService {
  private api = inject(ApiService);

  // System Settings
  getSystemSettings(): Observable<SystemSettings> {
    return this.api.get<SystemSettings>('settings/system-settings/');
  }

  updateSystemSettings(data: Partial<SystemSettings>): Observable<SystemSettings> {
    // SystemSettings est un singleton, le list() retourne directement l'objet unique
    // On récupère l'ID puis on fait un PUT
    return this.api.get<SystemSettings>('settings/system-settings/').pipe(
      switchMap((settings: any) => {
        // Le backend retourne directement l'objet singleton (pas une liste)
        const id = settings.id || (Array.isArray(settings) ? settings[0]?.id : null);
        if (!id) {
          throw new Error('Impossible de récupérer l\'ID des paramètres système');
        }
        return this.api.put<SystemSettings>(`settings/system-settings/${id}/`, data);
      })
    );
  }

  resetSystemSettings(): Observable<SystemSettings> {
    return this.api.post<SystemSettings>('settings/system-settings/reset/', {});
  }

  exportSystemSettings(): Observable<Blob> {
    return this.api.get<Blob>('settings/system-settings/export/');
  }

  // Email Templates
  getEmailTemplates(params?: { 
    template_type?: string;
    is_active?: boolean;
    page?: number;
  }): Observable<EmailTemplateListResponse> {
    return this.api.get<EmailTemplateListResponse>('settings/email-templates/', params);
  }

  getEmailTemplate(id: number): Observable<EmailTemplate> {
    return this.api.get<EmailTemplate>(`settings/email-templates/${id}/`);
  }

  createEmailTemplate(data: {
    name: string;
    subject: string;
    body: string;
    template_type: string;
    is_active?: boolean;
  }): Observable<EmailTemplate> {
    return this.api.post<EmailTemplate>('settings/email-templates/', data);
  }

  updateEmailTemplate(id: number, data: Partial<EmailTemplate>): Observable<EmailTemplate> {
    return this.api.patch<EmailTemplate>(`settings/email-templates/${id}/`, data);
  }

  deleteEmailTemplate(id: number): Observable<void> {
    return this.api.delete<void>(`settings/email-templates/${id}/`);
  }

  activateEmailTemplate(id: number): Observable<EmailTemplate> {
    return this.api.post<EmailTemplate>(`settings/email-templates/${id}/activate/`, {});
  }

  deactivateEmailTemplate(id: number): Observable<EmailTemplate> {
    return this.api.post<EmailTemplate>(`settings/email-templates/${id}/deactivate/`, {});
  }

  duplicateEmailTemplate(id: number): Observable<EmailTemplate> {
    return this.api.post<EmailTemplate>(`settings/email-templates/${id}/duplicate/`, {});
  }

  previewEmailTemplate(id: number, variables?: Record<string, string>): Observable<any> {
    return this.api.get<any>(`settings/email-templates/${id}/preview/`, variables);
  }

  getEmailTemplatesByType(templateType: string): Observable<EmailTemplate[]> {
    return this.api.get<EmailTemplate[]>(`settings/email-templates/by-type/${templateType}/`);
  }

  // Notification Settings
  getNotificationSettings(): Observable<NotificationSettingsListResponse> {
    return this.api.get<NotificationSettingsListResponse>('settings/notification-settings/');
  }

  getNotificationSetting(id: number): Observable<NotificationSettings> {
    return this.api.get<NotificationSettings>(`settings/notification-settings/${id}/`);
  }

  updateNotificationSetting(id: number, data: Partial<NotificationSettings>): Observable<NotificationSettings> {
    return this.api.patch<NotificationSettings>(`settings/notification-settings/${id}/`, data);
  }

  enableNotificationSetting(id: number): Observable<NotificationSettings> {
    return this.api.post<NotificationSettings>(`settings/notification-settings/${id}/enable/`, {});
  }

  disableNotificationSetting(id: number): Observable<NotificationSettings> {
    return this.api.post<NotificationSettings>(`settings/notification-settings/${id}/disable/`, {});
  }

  getActiveNotificationSettings(): Observable<NotificationSettings[]> {
    return this.api.get<NotificationSettings[]>('settings/notification-settings/active/');
  }

  getNotificationSettingsStatistics(): Observable<any> {
    return this.api.get<any>('settings/notification-settings/statistics/');
  }
}

