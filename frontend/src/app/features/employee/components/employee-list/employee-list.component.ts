import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { EmployeeService } from '../../services/employee.service';
import { Employee, EmployeeStatus } from '../../../../core/models/employee.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { AuthService } from '../../../../core/services/auth.service';
import { CurrencyService } from '../../../../core/services/currency.service';
import { getImageUrl } from '../../../../core/utils/image.util';

/**
 * Composant de présentation - Liste des employés
 * Couche Presentation - Gère uniquement l'affichage et les interactions utilisateur
 */
@Component({
  selector: 'app-employee-list',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './employee-list.component.html',
  styleUrls: ['./employee-list.component.scss']
})
export class EmployeeListComponent implements OnInit {
  private employeeService = inject(EmployeeService);
  private authService = inject(AuthService);
  private currencyService = inject(CurrencyService);

  employees = signal<Employee[]>([]);
  loading = signal(true);
  canCreate = signal(false);
  canEdit = signal(false);
  currency = signal<string>('XOF');

  // Filtres
  statusFilter = signal<EmployeeStatus | 'all'>('all');
  searchTerm = signal<string>('');

  ngOnInit(): void {
    this.checkPermissions();
    this.loadCurrency();
    this.loadEmployees();
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
    this.canCreate.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager')
    );
    this.canEdit.set(this.canCreate());
  }

  loadEmployees(params?: any): void {
    this.loading.set(true);
    const queryParams = {
      ...params,
      status: this.statusFilter() !== 'all' ? this.statusFilter() : undefined,
      search: this.searchTerm() || undefined
    };

    this.employeeService.getEmployees(queryParams).subscribe({
      next: (response) => {
        // Gérer différents formats de réponse : paginée ou tableau direct
        if (response && typeof response === 'object') {
          if (Array.isArray(response)) {
            // Si la réponse est directement un tableau
            this.employees.set(response);
          } else if (response.results && Array.isArray(response.results)) {
            // Si la réponse est paginée avec results
            this.employees.set(response.results);
          } else {
            // Format inattendu - log pour débogage
            console.warn('Unexpected response format for employees:', response);
            this.employees.set([]);
          }
        } else {
          this.employees.set([]);
        }
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading employees:', error);
        // Log plus de détails pour le débogage
        if (error.error) {
          console.error('Error details:', error.error);
        }
        this.employees.set([]);
        this.loading.set(false);
      }
    });
  }

  onStatusFilterChange(status: EmployeeStatus | 'all'): void {
    this.statusFilter.set(status);
    this.loadEmployees();
  }

  onSearch(): void {
    this.loadEmployees();
  }

  deleteEmployee(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer cet employé ?')) {
      this.employeeService.deleteEmployee(id).subscribe({
        next: () => {
          this.loadEmployees();
        },
        error: (error) => {
          console.error('Error deleting employee:', error);
          alert('Erreur lors de la suppression de l\'employé');
        }
      });
    }
  }

  formatSalary(salary: number): string {
    // Format avec FCFA au lieu du formatage automatique de devise
    return new Intl.NumberFormat('fr-FR', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(salary) + ' FCFA';
  }

  getStatusBadgeClass(status: EmployeeStatus): string {
    const classes: Record<EmployeeStatus, string> = {
      'active': 'badge-success',
      'on_leave': 'badge-warning',
      'inactive': 'badge-secondary'
    };
    return classes[status] || 'badge-secondary';
  }

  getStatusDisplay(status: EmployeeStatus): string {
    const displays: Record<EmployeeStatus, string> = {
      'active': 'Actif',
      'on_leave': 'En congé',
      'inactive': 'Inactif'
    };
    return displays[status] || status;
  }

  getEmployeeInitials(employee: Employee): string {
    const firstInitial = employee.first_name && employee.first_name.length > 0 ? employee.first_name[0].toUpperCase() : '';
    const lastInitial = employee.last_name && employee.last_name.length > 0 ? employee.last_name[0].toUpperCase() : '';
    return firstInitial + lastInitial || '?';
  }

  getEmployeeImageUrl(employee: Employee): string | null {
    return getImageUrl(employee.profile_picture);
  }
}
