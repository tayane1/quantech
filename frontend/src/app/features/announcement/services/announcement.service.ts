import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from '../../../core/services/api.service';
import { Announcement } from '../../../core/models/dashboard.model';

export interface CreateAnnouncementRequest {
  title: string;
  content: string;
  visible_to_all: boolean;
  departments_ids?: number[];
  published?: boolean;
}

export interface AnnouncementListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Announcement[];
}

@Injectable({
  providedIn: 'root'
})
export class AnnouncementService {
  private api = inject(ApiService);

  getAnnouncements(params?: {
    published?: boolean;
    visible_to_all?: boolean;
    search?: string;
    page?: number;
    page_size?: number;
  }): Observable<AnnouncementListResponse> {
    return this.api.get<AnnouncementListResponse>('announcement/announcements/', params);
  }

  getAnnouncement(id: number): Observable<Announcement> {
    return this.api.get<Announcement>(`announcement/announcements/${id}/`);
  }

  getVisibleAnnouncements(params?: { limit?: number }): Observable<AnnouncementListResponse> {
    return this.api.get<AnnouncementListResponse>('announcement/announcements/visible-to-me/', params);
  }

  createAnnouncement(data: CreateAnnouncementRequest): Observable<Announcement> {
    return this.api.post<Announcement>('announcement/announcements/', data);
  }

  updateAnnouncement(id: number, data: Partial<CreateAnnouncementRequest>): Observable<Announcement> {
    return this.api.patch<Announcement>(`announcement/announcements/${id}/`, data);
  }

  deleteAnnouncement(id: number): Observable<void> {
    return this.api.delete<void>(`announcement/announcements/${id}/`);
  }

  publishAnnouncement(id: number): Observable<Announcement> {
    return this.api.post<Announcement>(`announcement/announcements/${id}/publish/`, {});
  }

  unpublishAnnouncement(id: number): Observable<Announcement> {
    return this.api.post<Announcement>(`announcement/announcements/${id}/unpublish/`, {});
  }
}

