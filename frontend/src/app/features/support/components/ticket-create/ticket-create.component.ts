import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-ticket-create',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="ticket-create">
      <h1>Créer un Ticket</h1>
      <p>Composant en cours de développement...</p>
    </div>
  `,
  styles: [`
    .ticket-create {
      padding: 2rem;
    }
  `]
})
export class TicketCreateComponent {}

