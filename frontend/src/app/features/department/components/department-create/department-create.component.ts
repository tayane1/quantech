import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { DepartmentFormComponent } from '../department-form/department-form.component';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { Department } from '../../../../core/models/department.model';

@Component({
  selector: 'app-department-create',
  standalone: true,
  imports: [CommonModule, DepartmentFormComponent, CardComponent],
  template: `
    <div class="department-create">
      <div class="page-header">
        <h1>Créer un département</h1>
      </div>
      <app-card title="Nouveau département">
        <app-department-form (saved)="onSaved($event)" (cancelled)="onCancelled()"></app-department-form>
      </app-card>
    </div>
  `,
  styles: [`
    .department-create {
      max-width: 800px;
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
export class DepartmentCreateComponent {
  private router = inject(Router);

  onSaved(department: Department): void {
    this.router.navigate(['/department', department.id]);
  }

  onCancelled(): void {
    this.router.navigate(['/department']);
  }
}

