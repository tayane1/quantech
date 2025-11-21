import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { DepartmentService } from '../../services/department.service';
import { Department } from '../../../../core/models/department.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { AuthService } from '../../../../core/services/auth.service';
import { CurrencyService } from '../../../../core/services/currency.service';

@Component({
  selector: 'app-department-detail',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './department-detail.component.html',
  styleUrls: ['./department-detail.component.scss']
})
export class DepartmentDetailComponent implements OnInit {
  private route = inject(ActivatedRoute);
  private router = inject(Router);
  private departmentService = inject(DepartmentService);
  private authService = inject(AuthService);
  private currencyService = inject(CurrencyService);

  department = signal<Department | null>(null);
  loading = signal(true);
  canEdit = signal(false);
  currency = signal<string>('XOF');

  ngOnInit(): void {
    this.checkPermissions();
    this.loadCurrency();
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadDepartment(+id);
    }
  }

  loadCurrency(): void {
    this.currencyService.getCurrency().subscribe({
      next: (currency) => {
        this.currency.set(currency);
      },
      error: () => {
        this.currency.set('XOF');
      }
    });
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canEdit.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager')
    );
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

  formatBudget(budget?: number): string {
    if (!budget) return 'N/A';
    // Format avec FCFA au lieu du formatage automatique de devise
    return new Intl.NumberFormat('fr-FR', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(budget) + ' FCFA';
  }

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }
}

