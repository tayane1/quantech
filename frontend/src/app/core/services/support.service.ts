import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { SupportTicket, SupportCategory, TicketComment, TicketAttachment } from '../models/support.model';

export interface TicketListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: SupportTicket[];
}

export interface CategoryListResponse {
  count: number;
  results: SupportCategory[];
}

@Injectable({
  providedIn: 'root'
})
export class SupportService {
  private api = inject(ApiService);

  // Support Categories
  getCategories(params?: { active?: boolean }): Observable<CategoryListResponse> {
    return this.api.get<CategoryListResponse>('support/support-categories/', params);
  }

  getCategory(id: number): Observable<SupportCategory> {
    return this.api.get<SupportCategory>(`support/support-categories/${id}/`);
  }

  // Support Tickets
  getTickets(params?: {
    status?: string;
    priority?: string;
    category?: number;
    assigned_to?: number;
    page?: number;
    page_size?: number;
  }): Observable<TicketListResponse> {
    return this.api.get<TicketListResponse>('support/support-tickets/', params);
  }

  getTicket(id: number): Observable<SupportTicket> {
    return this.api.get<SupportTicket>(`support/support-tickets/${id}/`);
  }

  createTicket(data: {
    title: string;
    description: string;
    category: number;
    priority?: 'low' | 'medium' | 'high' | 'urgent';
  }): Observable<SupportTicket> {
    return this.api.post<SupportTicket>('support/support-tickets/', data);
  }

  updateTicket(id: number, data: Partial<SupportTicket>): Observable<SupportTicket> {
    return this.api.patch<SupportTicket>(`support/support-tickets/${id}/`, data);
  }

  deleteTicket(id: number): Observable<void> {
    return this.api.delete<void>(`support/support-tickets/${id}/`);
  }

  // Ticket Actions
  assignTicket(id: number, assignedTo: number): Observable<SupportTicket> {
    return this.api.post<SupportTicket>(`support/support-tickets/${id}/assign/`, { assigned_to: assignedTo });
  }

  resolveTicket(id: number, satisfactionRating?: number, feedback?: string): Observable<SupportTicket> {
    return this.api.post<SupportTicket>(`support/support-tickets/${id}/resolve/`, {
      satisfaction_rating: satisfactionRating,
      satisfaction_feedback: feedback
    });
  }

  closeTicket(id: number): Observable<SupportTicket> {
    return this.api.post<SupportTicket>(`support/support-tickets/${id}/close/`, {});
  }

  reopenTicket(id: number): Observable<SupportTicket> {
    return this.api.post<SupportTicket>(`support/support-tickets/${id}/reopen/`, {});
  }

  getMyTickets(): Observable<SupportTicket[]> {
    return this.api.get<SupportTicket[]>('support/support-tickets/my-tickets/');
  }

  getAssignedToMe(): Observable<SupportTicket[]> {
    return this.api.get<SupportTicket[]>('support/support-tickets/assigned-to-me/');
  }

  getOpenTickets(): Observable<SupportTicket[]> {
    return this.api.get<SupportTicket[]>('support/support-tickets/open/');
  }

  getTicketStatistics(): Observable<any> {
    return this.api.get<any>('support/support-tickets/statistics/');
  }

  // Ticket Comments
  getTicketComments(ticketId: number): Observable<{ results: TicketComment[] }> {
    return this.api.get<{ results: TicketComment[] }>(`support/ticket-comments/by-ticket/${ticketId}/`);
  }

  addComment(ticketId: number, content: string, isInternal: boolean = false): Observable<TicketComment> {
    return this.api.post<TicketComment>('support/ticket-comments/', {
      ticket: ticketId,
      content,
      is_internal: isInternal
    });
  }

  updateComment(id: number, content: string): Observable<TicketComment> {
    return this.api.patch<TicketComment>(`support/ticket-comments/${id}/`, { content });
  }

  deleteComment(id: number): Observable<void> {
    return this.api.delete<void>(`support/ticket-comments/${id}/`);
  }

  // Ticket Attachments
  getTicketAttachments(ticketId: number): Observable<{ results: TicketAttachment[] }> {
    return this.api.get<{ results: TicketAttachment[] }>(`support/ticket-attachments/by-ticket/${ticketId}/`);
  }

  uploadAttachment(ticketId: number, file: File): Observable<TicketAttachment> {
    const formData = new FormData();
    formData.append('ticket', ticketId.toString());
    formData.append('file', file);
    return this.api.post<TicketAttachment>('support/ticket-attachments/', formData);
  }

  deleteAttachment(id: number): Observable<void> {
    return this.api.delete<void>(`support/ticket-attachments/${id}/`);
  }
}

