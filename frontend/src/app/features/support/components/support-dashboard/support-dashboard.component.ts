import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { SupportService } from '../../../../core/services/support.service';
import { SupportTicket, SupportCategory } from '../../../../core/models/support.model';

@Component({
  selector: 'app-support-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, LoadingComponent],
  templateUrl: './support-dashboard.component.html',
  styleUrls: ['./support-dashboard.component.scss']
})
export class SupportDashboardComponent implements OnInit {
  private supportService = inject(SupportService);

  tickets = signal<SupportTicket[]>([]);
  categories = signal<SupportCategory[]>([]);
  loading = signal(false);
  stats = signal<any>(null);

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.loading.set(true);
    
    // Charger les tickets ouverts
    this.supportService.getOpenTickets().subscribe({
      next: (tickets) => {
        if (tickets && Array.isArray(tickets)) {
          this.tickets.set(tickets.slice(0, 5)); // Afficher les 5 premiers
        } else {
          this.tickets.set([]);
        }
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading tickets:', err);
        this.tickets.set([]);
        this.loading.set(false);
      }
    });

    // Charger les catégories actives
    this.supportService.getCategories({ active: true }).subscribe({
      next: (response) => {
        if (response && response.results && Array.isArray(response.results)) {
          this.categories.set(response.results);
        } else {
          this.categories.set([]);
        }
      },
      error: (err) => {
        console.error('Error loading categories:', err);
        this.categories.set([]);
      }
    });

    // Charger les statistiques
    this.supportService.getTicketStatistics().subscribe({
      next: (stats) => {
        this.stats.set(stats);
      },
      error: (err) => {
        console.error('Error loading statistics:', err);
      }
    });
  }

  getStatusBadgeClass(status: string): string {
    const classes: Record<string, string> = {
      'open': 'badge-success',
      'in_progress': 'badge-warning',
      'resolved': 'badge-info',
      'closed': 'badge-secondary'
    };
    return classes[status] || 'badge-secondary';
  }

  getPriorityBadgeClass(priority: string): string {
    const classes: Record<string, string> = {
      'low': 'badge-secondary',
      'medium': 'badge-info',
      'high': 'badge-warning',
      'urgent': 'badge-danger'
    };
    return classes[priority] || 'badge-secondary';
  }
}
