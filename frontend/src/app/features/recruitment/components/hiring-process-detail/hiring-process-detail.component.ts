import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { CardComponent } from '../../../../shared/components/card/card.component';

@Component({
  selector: 'app-hiring-process-detail',
  standalone: true,
  imports: [CommonModule, CardComponent],
  template: `
    <div class="hiring-process-detail">
      <div class="page-header">
        <h1>Détails du processus</h1>
      </div>
      <app-card title="Détails processus">
        <p>Page de détails du processus à implémenter</p>
      </app-card>
    </div>
  `,
  styles: [`
    .hiring-process-detail {
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
export class HiringProcessDetailComponent {
  private router = inject(Router);
}

