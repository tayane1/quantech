import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { ApiService } from './api.service';
import { Message, Conversation } from '../models/message.model';

export interface ConversationListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Conversation[];
}

@Injectable({
  providedIn: 'root'
})
export class MessageService {
  private api = inject(ApiService);

  getConversations(params?: {
    limit?: number;
    page?: number;
  }): Observable<ConversationListResponse> {
    // TODO: Remplacer par l'endpoint réel une fois le backend disponible
    // Pour l'instant, on simule une réponse vide
    return this.api.get<ConversationListResponse>('messages/conversations/', params);
  }

  getMessages(conversationId: number, params?: {
    limit?: number;
    page?: number;
  }): Observable<{ count: number; results: Message[] }> {
    return this.api.get<{ count: number; results: Message[] }>(`messages/conversations/${conversationId}/messages/`, params);
  }

  sendMessage(conversationId: number, content: string): Observable<Message> {
    return this.api.post<Message>(`messages/conversations/${conversationId}/messages/`, { content });
  }

  markAsRead(conversationId: number): Observable<void> {
    return this.api.post<void>(`messages/conversations/${conversationId}/mark-read/`, {});
  }
}

