import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { DepartmentService } from '../../services/department.service';
import { Department } from '../../../../core/models/department.model';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { ButtonComponent } from '../../../../shared/components/button/button.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { AuthService } from '../../../../core/services/auth.service';
import { CurrencyService } from '../../../../core/services/currency.service';

@Component({
  selector: 'app-department-list',
  standalone: true,
  imports: [CommonModule, RouterModule, CardComponent, ButtonComponent, LoadingComponent],
  templateUrl: './department-list.component.html',
  styleUrls: ['./department-list.component.scss']
})
export class DepartmentListComponent implements OnInit {
  private departmentService = inject(DepartmentService);
  private authService = inject(AuthService);
  private currencyService = inject(CurrencyService);
  public router = inject(Router); // Public pour accès dans le template

  departments = signal<Department[]>([]);
  loading = signal(true);
  canCreate = signal(false);
  currency = signal<string>('XOF');

  ngOnInit(): void {
    this.checkPermissions();
    this.loadDepartments();
    this.loadCurrency();
  }

  loadCurrency(): void {
    this.currencyService.getCurrency().subscribe({
      next: (currency) => {
        this.currency.set(currency);
      },
      error: () => {
        // En cas d'erreur, utiliser XOF par défaut
        this.currency.set('XOF');
      }
    });
  }

  checkPermissions(): void {
    const user = this.authService.currentUser();
    this.canCreate.set(
      !!user && (user.is_staff || user.role === 'admin' || user.role === 'hr_manager')
    );
  }

  loadDepartments(): void {
    this.loading.set(true);
    this.departmentService.getDepartments().subscribe({
      next: (response) => {
        // Gérer différents formats de réponse : paginée ou tableau direct
        if (response && typeof response === 'object') {
          if (Array.isArray(response)) {
            // Si la réponse est directement un tableau
            this.departments.set(response);
          } else if (response.results && Array.isArray(response.results)) {
            // Si la réponse est paginée avec results
            this.departments.set(response.results);
          } else {
            // Format inattendu - log pour débogage
            console.warn('Unexpected response format for departments:', response);
            this.departments.set([]);
          }
        } else {
          this.departments.set([]);
        }
        this.loading.set(false);
      },
      error: (error) => {
        console.error('Error loading departments:', error);
        // Log plus de détails pour le débogage
        if (error.error) {
          console.error('Error details:', error.error);
        }
        this.departments.set([]);
        this.loading.set(false);
      }
    });
  }

  deleteDepartment(id: number): void {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce département ?')) {
      this.departmentService.deleteDepartment(id).subscribe({
        next: () => {
          this.loadDepartments();
        },
        error: (error) => {
          console.error('Error deleting department:', error);
          alert('Erreur lors de la suppression du département');
        }
      });
    }
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
}
