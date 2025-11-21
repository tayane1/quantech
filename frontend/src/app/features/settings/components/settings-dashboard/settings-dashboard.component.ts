import { Component, OnInit, inject, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { CardComponent } from '../../../../shared/components/card/card.component';
import { LoadingComponent } from '../../../../shared/components/loading/loading.component';
import { SettingsService } from '../../../../core/services/settings.service';
import { CurrencyService } from '../../../../core/services/currency.service';
import { SystemSettings, EmailTemplate, NotificationSettings } from '../../../../core/models/settings.model';

@Component({
  selector: 'app-settings-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule, CardComponent, LoadingComponent],
  templateUrl: './settings-dashboard.component.html',
  styleUrls: ['./settings-dashboard.component.scss']
})
export class SettingsDashboardComponent implements OnInit {
  private settingsService = inject(SettingsService);
  private currencyService = inject(CurrencyService);

  systemSettings = signal<SystemSettings | null>(null);
  emailTemplates = signal<EmailTemplate[]>([]);
  notificationSettings = signal<NotificationSettings[]>([]);
  loading = signal(false);
  saving = signal(false);
  activeTab = signal<'system' | 'email' | 'notifications'>('system');

  // Liste des devises ISO 4217 courantes
  currencies = [
    { code: 'XOF', name: 'Franc CFA (BCEAO) - Afrique de l\'Ouest' },
    { code: 'XAF', name: 'Franc CFA (BEAC) - Afrique Centrale' },
    { code: 'EUR', name: 'Euro' },
    { code: 'USD', name: 'Dollar US' },
    { code: 'GBP', name: 'Livre Sterling' },
    { code: 'JPY', name: 'Yen Japonais' },
    { code: 'CNY', name: 'Yuan Chinois' },
    { code: 'NGN', name: 'Naira Nigérian' },
    { code: 'GHS', name: 'Cedi Ghanéen' },
    { code: 'KES', name: 'Shilling Kenyan' },
    { code: 'ZAR', name: 'Rand Sud-Africain' },
    { code: 'EGP', name: 'Livre Égyptienne' },
    { code: 'MAD', name: 'Dirham Marocain' },
    { code: 'TND', name: 'Dinar Tunisien' },
    { code: 'DZD', name: 'Dinar Algérien' },
    { code: 'XPF', name: 'Franc CFP (Pacifique)' },
    { code: 'CHF', name: 'Franc Suisse' },
    { code: 'CAD', name: 'Dollar Canadien' },
    { code: 'AUD', name: 'Dollar Australien' },
    { code: 'BRL', name: 'Real Brésilien' },
    { code: 'INR', name: 'Roupie Indienne' },
    { code: 'RUB', name: 'Rouble Russe' },
    { code: 'TRY', name: 'Livre Turque' },
    { code: 'AED', name: 'Dirham Émirati' },
    { code: 'SAR', name: 'Riyal Saoudien' }
  ];

  ngOnInit(): void {
    this.loadSystemSettings();
    this.loadEmailTemplates();
    this.loadNotificationSettings();
  }

  loadSystemSettings(): void {
    this.loading.set(true);
    this.settingsService.getSystemSettings().subscribe({
      next: (settings) => {
        this.systemSettings.set(settings);
        this.loading.set(false);
      },
      error: (err) => {
        console.error('Error loading system settings:', err);
        this.loading.set(false);
      }
    });
  }

  loadEmailTemplates(): void {
    this.settingsService.getEmailTemplates().subscribe({
      next: (response) => {
        if (response && response.results && Array.isArray(response.results)) {
          this.emailTemplates.set(response.results.slice(0, 5)); // Afficher les 5 premiers
        } else {
          this.emailTemplates.set([]);
        }
      },
      error: (err) => {
        console.error('Error loading email templates:', err);
        this.emailTemplates.set([]);
      }
    });
  }

  loadNotificationSettings(): void {
    this.settingsService.getNotificationSettings().subscribe({
      next: (response) => {
        if (response && response.results && Array.isArray(response.results)) {
          this.notificationSettings.set(response.results);
        } else {
          this.notificationSettings.set([]);
        }
      },
      error: (err) => {
        console.error('Error loading notification settings:', err);
        this.notificationSettings.set([]);
      }
    });
  }

  saveSystemSettings(): void {
    const settings = this.systemSettings();
    if (!settings) return;

    this.saving.set(true);
    this.settingsService.updateSystemSettings(settings).subscribe({
      next: (updated) => {
        this.systemSettings.set(updated);
        // Réinitialiser le cache de devise pour que la nouvelle devise soit utilisée
        this.currencyService.clearCache();
        this.saving.set(false);
        alert('Paramètres sauvegardés avec succès');
      },
      error: (err) => {
        console.error('Error saving system settings:', err);
        this.saving.set(false);
        alert('Erreur lors de la sauvegarde');
      }
    });
  }

  resetSystemSettings(): void {
    if (confirm('Êtes-vous sûr de vouloir réinitialiser les paramètres système ?')) {
      this.saving.set(true);
      this.settingsService.resetSystemSettings().subscribe({
        next: (settings) => {
          this.systemSettings.set(settings);
          this.saving.set(false);
          alert('Paramètres réinitialisés avec succès');
        },
        error: (err) => {
          console.error('Error resetting system settings:', err);
          this.saving.set(false);
          alert('Erreur lors de la réinitialisation');
        }
      });
    }
  }

  setActiveTab(tab: 'system' | 'email' | 'notifications'): void {
    this.activeTab.set(tab);
  }

  toggleNotificationSetting(setting: NotificationSettings): void {
    const action = setting.enabled 
      ? this.settingsService.disableNotificationSetting(setting.id)
      : this.settingsService.enableNotificationSetting(setting.id);

    action.subscribe({
      next: (updated) => {
        this.notificationSettings.update(settings => 
          settings.map(s => s.id === updated.id ? updated : s)
        );
      },
      error: (err) => {
        console.error('Error toggling notification setting:', err);
        alert('Erreur lors de la modification');
      }
    });
  }
}
