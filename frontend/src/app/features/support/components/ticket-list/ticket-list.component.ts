import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-ticket-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="ticket-list">
      <h1>Liste des Tickets</h1>
      <p>Composant en cours de développement...</p>
    </div>
  `,
  styles: [`
    .ticket-list {
      padding: 2rem;
    }
  `]
})
export class TicketListComponent {}

