import { Injectable, inject } from '@angular/core';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';
import { SettingsService } from './settings.service';

@Injectable({
  providedIn: 'root'
})
export class CurrencyService {
  private settingsService = inject(SettingsService);
  private cachedCurrency: string | null = null;

  /**
   * Récupère la devise depuis les paramètres système
   * Utilise un cache pour éviter les appels répétés
   */
  getCurrency(): Observable<string> {
    if (this.cachedCurrency) {
      return of(this.cachedCurrency);
    }

    return this.settingsService.getSystemSettings().pipe(
      map(settings => {
        this.cachedCurrency = settings.currency || 'XOF';
        return this.cachedCurrency;
      }),
      catchError(() => {
        // En cas d'erreur, utiliser XOF par défaut (Côte d'Ivoire)
        this.cachedCurrency = 'XOF';
        return of('XOF');
      })
    );
  }

  /**
   * Formate un montant avec FCFA (Franc CFA)
   */
  formatAmount(amount: number | undefined | null): Observable<string> {
    if (amount === null || amount === undefined) {
      return of('N/A');
    }

    // Toujours afficher en FCFA au lieu du formatage automatique de devise
    const formatted = new Intl.NumberFormat('fr-FR', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount) + ' FCFA';
    
    return of(formatted);
  }

  /**
   * Formate un montant de manière synchrone avec FCFA
   * Utile pour les cas où on ne peut pas utiliser un Observable
   */
  formatAmountSync(amount: number | undefined | null, currency: string = 'XOF'): string {
    if (amount === null || amount === undefined) {
      return 'N/A';
    }

    // Toujours afficher en FCFA au lieu du formatage automatique de devise
    return new Intl.NumberFormat('fr-FR', {
      style: 'decimal',
      minimumFractionDigits: 0,
      maximumFractionDigits: 2
    }).format(amount) + ' FCFA';
  }

  /**
   * Réinitialise le cache (utile après mise à jour des settings)
   */
  clearCache(): void {
    this.cachedCurrency = null;
  }
}

