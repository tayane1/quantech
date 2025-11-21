import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { DepartmentFormComponent } from '../department-form/department-form.component';
import { DepartmentService } from '../../services/department.service';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { Department } from '../../../../core/models/department.model';

@Component({
  selector: 'app-department-edit',
  standalone: true,
  imports: [CommonModule, DepartmentFormComponent, CardComponent, LoadingComponent],
  template: `
    <div class="department-edit">
      <div class="page-header">
        <h1>Modifier le département</h1>
      </div>
      <app-loading *ngIf="loading()" message="Chargement..."></app-loading>
      <app-card *ngIf="!loading() && department()" [title]="'Modifier: ' + department()?.name">
        <app-department-form 
          [department]="department()!" 
          (saved)="onSaved($event)" 
          (cancelled)="onCancelled()">
        </app-department-form>
      </app-card>
    </div>
  `,
  styles: [`
    .department-edit {
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
export class DepartmentEditComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private departmentService = inject(DepartmentService);

  department = signal<Department | null>(null);
  loading = signal(true);

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadDepartment(+id);
    }
  }

  loadDepartment(id: number): void {
    this.loading.set(true);
    this.departmentService.getDepartment(id).subscribe({
      next: (department) => {
        this.department.set(department);
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading department:', error);
        this.loading.set(false);
        this.router.navigate(['/department']);
      }
    });
  }

  onSaved(department: Department): void {
    this.router.navigate(['/department', department.id]);
  }

  onCancelled(): void {
    const id = this.department()?.id;
    if (id) {
      this.router.navigate(['/department', id]);
    } else {
      this.router.navigate(['/department']);
    }
  }
}

