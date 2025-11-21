import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { EmployeeFormComponent } from '../employee-form/employee-form.component';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { Employee } from '../../../../core/models/employee.model';

@Component({
  selector: 'app-employee-create',
  standalone: true,
  imports: [CommonModule, EmployeeFormComponent, CardComponent],
  template: `
    <div class="employee-create">
      <div class="page-header">
        <h1>Ajouter un employé</h1>
      </div>
      <app-card title="Nouvel employé">
        <app-employee-form (saved)="onSaved($event)" (cancelled)="onCancelled()"></app-employee-form>
      </app-card>
    </div>
  `,
  styles: [`
    .employee-create {
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
export class EmployeeCreateComponent {
  private router = inject(Router);

  onSaved(employee: Employee): void {
    this.router.navigate(['/employee', employee.id]);
  }

  onCancelled(): void {
    this.router.navigate(['/employee']);
  }
}

