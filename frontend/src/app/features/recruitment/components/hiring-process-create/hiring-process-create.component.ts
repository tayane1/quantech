import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { CardComponent } from '../../../../shared/components/card/card.component';

@Component({
  selector: 'app-hiring-process-create',
  standalone: true,
  imports: [CommonModule, CardComponent],
  template: `
    <div class="hiring-process-create">
      <div class="page-header">
        <h1>Créer un processus</h1>
      </div>
      <app-card title="Nouveau processus">
        <p>Formulaire de création de processus à implémenter</p>
      </app-card>
    </div>
  `,
  styles: [`
    .hiring-process-create {
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
export class HiringProcessCreateComponent {
  private router = inject(Router);
}

