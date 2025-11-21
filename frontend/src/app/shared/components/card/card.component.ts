import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-card',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="card" [class.card-colored]="colored" [style.background-color]="backgroundColor">
      <div class="card-header" *ngIf="title || headerActions">
        <h3 *ngIf="title" class="card-title">{{ title }}</h3>
        <div class="card-actions" *ngIf="headerActions">
          <ng-content select="[slot=header-actions]"></ng-content>
        </div>
      </div>
      <div class="card-body">
        <ng-content></ng-content>
      </div>
      <div class="card-footer" *ngIf="footer">
        <ng-content select="[slot=footer]"></ng-content>
      </div>
    </div>
  `,
  styles: [`
    .card {
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      padding: 1.5rem;
      margin-bottom: 1rem;
    }

    .card-colored {
      color: white;
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
      padding-bottom: 1rem;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    .card-colored .card-header {
      border-bottom-color: rgba(255, 255, 255, 0.2);
    }

    .card-title {
      margin: 0;
      font-size: 1.25rem;
      font-weight: 600;
    }

    .card-actions {
      display: flex;
      gap: 0.5rem;
    }

    .card-body {
      min-height: 50px;
    }

    .card-footer {
      margin-top: 1rem;
      padding-top: 1rem;
      border-top: 1px solid rgba(0, 0, 0, 0.1);
    }

    .card-colored .card-footer {
      border-top-color: rgba(255, 255, 255, 0.2);
    }
  `]
})
export class CardComponent {
  @Input() title?: string;
  @Input() colored = false;
  @Input() backgroundColor?: string;
  @Input() headerActions = false;
  @Input() footer = false;
}

