import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-email-template-form',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="email-template-form">
      <h1>Formulaire Modèle d'Email</h1>
      <p>Composant en cours de développement...</p>
    </div>
  `,
  styles: [`
    .email-template-form {
      padding: 2rem;
    }
  `]
})
export class EmailTemplateFormComponent {}

