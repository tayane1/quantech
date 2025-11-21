import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-ticket-detail',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="ticket-detail">
      <h1>Détails du Ticket</h1>
      <p>Composant en cours de développement...</p>
    </div>
  `,
  styles: [`
    .ticket-detail {
      padding: 2rem;
    }
  `]
})
export class TicketDetailComponent {}

