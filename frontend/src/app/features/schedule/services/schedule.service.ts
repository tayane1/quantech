import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiService } from '../../../core/services/api.service';
import { 
  Schedule,
  CreateScheduleRequest,
  UpdateScheduleRequest,
  Meeting,
  CreateMeetingRequest,
  UpdateMeetingRequest,
  ScheduleStatistics
} from '../../../core/models/schedule.model';
import { PaginatedResponse } from '../../../core/interfaces/api.interface';
import { normalizeApiResponse } from '../../../core/utils/api.util';

/**
 * Service pour la gestion du planning
 * Couche Application - Gère toutes les opérations CRUD et métier
 */
@Injectable({
  providedIn: 'root'
})
export class ScheduleService {
  private api = inject(ApiService);

  // ============ Schedules (Tasks) ============

  getSchedules(params?: any): Observable<PaginatedResponse<Schedule> | Schedule[]> {
    return this.api.get<PaginatedResponse<Schedule> | Schedule[]>('schedule/tasks/', params);
  }

  getSchedule(id: number): Observable<Schedule> {
    return this.api.get<Schedule>(`schedule/tasks/${id}/`);
  }

  createSchedule(data: CreateScheduleRequest): Observable<Schedule> {
    return this.api.post<Schedule>('schedule/tasks/', data);
  }

  updateSchedule(id: number, data: UpdateScheduleRequest): Observable<Schedule> {
    return this.api.patch<Schedule>(`schedule/tasks/${id}/`, data);
  }

  deleteSchedule(id: number): Observable<void> {
    return this.api.delete<void>(`schedule/tasks/${id}/`);
  }

  getMySchedules(params?: any): Observable<PaginatedResponse<Schedule>> {
    return this.api.get<PaginatedResponse<Schedule>>('schedule/tasks/my-tasks/', params);
  }

  getPendingSchedules(params?: any): Observable<PaginatedResponse<Schedule>> {
    return this.api.get<PaginatedResponse<Schedule>>('schedule/tasks/', { ...params, completed: false });
  }

  getCompletedSchedules(params?: any): Observable<PaginatedResponse<Schedule>> {
    return this.api.get<PaginatedResponse<Schedule>>('schedule/tasks/', { ...params, completed: true });
  }

  // ============ Meetings ============

  getMeetings(params?: any): Observable<PaginatedResponse<Meeting>> {
    return this.api.get<PaginatedResponse<Meeting>>('schedule/meetings/', params);
  }

  getMeeting(id: number): Observable<Meeting> {
    return this.api.get<Meeting>(`schedule/meetings/${id}/`);
  }

  createMeeting(data: CreateMeetingRequest): Observable<Meeting> {
    return this.api.post<Meeting>('schedule/meetings/', data);
  }

  updateMeeting(id: number, data: UpdateMeetingRequest): Observable<Meeting> {
    return this.api.patch<Meeting>(`schedule/meetings/${id}/`, data);
  }

  deleteMeeting(id: number): Observable<void> {
    return this.api.delete<void>(`schedule/meetings/${id}/`);
  }

  getMyMeetings(params?: any): Observable<PaginatedResponse<Meeting>> {
    return this.api.get<PaginatedResponse<Meeting>>('schedule/meetings/my-meetings/', params);
  }

  getUpcomingMeetings(params?: any): Observable<PaginatedResponse<Meeting> | Meeting[]> {
    return this.api.get<PaginatedResponse<Meeting> | Meeting[]>('schedule/meetings/upcoming/', params);
  }

  // ============ Statistics ============

  getStatistics(): Observable<ScheduleStatistics> {
    return this.api.get<ScheduleStatistics>('schedule/statistics/');
  }
}

