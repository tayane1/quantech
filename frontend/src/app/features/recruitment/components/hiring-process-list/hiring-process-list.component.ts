import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { CardComponent } from '../../../../shared/components/card/card.component';

@Component({
  selector: 'app-hiring-process-list',
  standalone: true,
  imports: [CommonModule, CardComponent],
  template: `
    <div class="hiring-process-list">
      <div class="page-header">
        <h1>Processus de recrutement</h1>
      </div>
      <app-card title="Liste des processus">
        <p>Liste des processus de recrutement à implémenter</p>
      </app-card>
    </div>
  `,
  styles: [`
    .hiring-process-list {
      max-width: 1400px;
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
export class HiringProcessListComponent {
  private router = inject(Router);
}

