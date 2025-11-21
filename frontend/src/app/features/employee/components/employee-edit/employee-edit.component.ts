import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { EmployeeFormComponent } from '../employee-form/employee-form.component';
import { EmployeeService } from '../../services/employee.service';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { Employee } from '../../../../core/models/employee.model';

@Component({
  selector: 'app-employee-edit',
  standalone: true,
  imports: [CommonModule, EmployeeFormComponent, CardComponent, LoadingComponent],
  template: `
    <div class="employee-edit">
      <div class="page-header">
        <h1>Modifier l'employé</h1>
      </div>
      <app-loading *ngIf="loading()" message="Chargement..."></app-loading>
      <app-card *ngIf="!loading() && employee()" [title]="'Modifier: ' + (employee()?.full_name || employee()?.first_name + ' ' + employee()?.last_name)">
        <app-employee-form 
          [employee]="employee()!" 
          (saved)="onSaved($event)" 
          (cancelled)="onCancelled()">
        </app-employee-form>
      </app-card>
    </div>
  `,
  styles: [`
    .employee-edit {
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
export class EmployeeEditComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private employeeService = inject(EmployeeService);

  employee = signal<Employee | null>(null);
  loading = signal(true);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadEmployee(+id);
    }
  }

  loadEmployee(id: number): void {
    this.loading.set(true);
    this.employeeService.getEmployee(id).subscribe({
      next: (employee) => {
        this.employee.set(employee);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading employee:', error);
        this.loading.set(false);
        this.router.navigate(['/employee']);
      }
    });
  }

  onSaved(employee: Employee): void {
    this.router.navigate(['/employee', employee.id]);
  }

  onCancelled(): void {
    const id = this.employee()?.id;
    if (id) {
      this.router.navigate(['/employee', id]);
    } else {
      this.router.navigate(['/employee']);
    }
  }
}

