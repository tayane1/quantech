import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-email-templates-list',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="email-templates-list">
      <h1>Modèles d'Email</h1>
      <p>Composant en cours de développement...</p>
    </div>
  `,
  styles: [`
    .email-templates-list {
      padding: 2rem;
    }
  `]
})
export class EmailTemplatesListComponent {}

