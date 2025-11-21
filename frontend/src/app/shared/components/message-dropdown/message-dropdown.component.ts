import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { MessageService } from '../../../core/services/message.service';
import { Message, Conversation } from '../../../core/models/message.model';
import { DateUtil } from '../../../core/utils/date.util';
import { LoadingComponent } from '../loading/loading.component';
import { ClickOutsideDirective } from '../../directives/click-outside.directive';

@Component({
  selector: 'app-message-dropdown',
  standalone: true,
  imports: [CommonModule, RouterModule, LoadingComponent, ClickOutsideDirective],
  templateUrl: './message-dropdown.component.html',
  styleUrls: ['./message-dropdown.component.scss']
})
export class MessageDropdownComponent implements OnInit {
  private messageService = inject(MessageService);
  private router = inject(Router);

  conversations = signal<Conversation[]>([]);
  unreadCount = signal<number>(0);
  loading = signal(false);
  showDropdown = signal(false);

  ngOnInit(): void {
    this.loadConversations();
  }

  toggleDropdown(): void {
    this.showDropdown.update(value => !value);
    if (this.showDropdown()) {
      this.loadConversations();
    }
  }

  closeDropdown(): void {
    this.showDropdown.set(false);
  }

  loadConversations(): void {
    this.loading.set(true);
    this.messageService.getConversations({ limit: 10 }).subscribe({
      next: (response) => {
        this.conversations.set(response.results || []);
        this.unreadCount.set(
          response.results?.reduce((sum, conv) => sum + (conv.unread_count || 0), 0) || 0
        );
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading conversations:', error);
        this.conversations.set([]);
        this.unreadCount.set(0);
        this.loading.set(false);
      }
    });
  }

  handleConversationClick(conversation: Conversation): void {
    this.router.navigate(['/messages', conversation.id]);
    this.closeDropdown();
  }

  getRelativeTime(date: string): string {
    return DateUtil.getRelativeTime(date);
  }

  getUserInitials(name?: string): string {
    if (!name) return '?';
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }
    return name[0].toUpperCase();
  }
}

