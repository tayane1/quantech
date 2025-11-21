import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { CardComponent } from '../../../../shared/components/card/card.component';

@Component({
  selector: 'app-hiring-process-edit',
  standalone: true,
  imports: [CommonModule, CardComponent],
  template: `
    <div class="hiring-process-edit">
      <div class="page-header">
        <h1>Modifier le processus</h1>
      </div>
      <app-card title="Modifier processus">
        <p>Formulaire d'édition de processus à implémenter</p>
      </app-card>
    </div>
  `,
  styles: [`
    .hiring-process-edit {
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
    }
    .page-header {
      margin-bottom: 30px;
      h1 {
        margin: 0;
        font-size: 2rem;
        color: #333;
      }
    }
  `]
})
export class HiringProcessEditComponent {
  private router = inject(Router);
}

