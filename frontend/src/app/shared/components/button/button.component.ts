import { Component, Input, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      [type]="type"
      [disabled]="disabled || loading"
      [class]="buttonClass"
      (click)="onClick()"
    >
      <span *ngIf="loading" class="spinner-small"></span>
      <ng-content></ng-content>
    </button>
  `,
  styles: [`
    button {
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 6px;
      font-size: 1rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
      justify-content: center;
    }

    button:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .btn-primary {
      background-color: #dc3545;
      color: white;
    }

    .btn-primary:hover:not(:disabled) {
      background-color: #c82333;
    }

    .btn-secondary {
      background-color: #6c757d;
      color: white;
    }

    .btn-secondary:hover:not(:disabled) {
      background-color: #5a6268;
    }

    .btn-outline {
      background-color: transparent;
      border: 1px solid #dc3545;
      color: #dc3545;
    }

    .btn-outline:hover:not(:disabled) {
      background-color: #dc3545;
      color: white;
    }

    .spinner-small {
      width: 16px;
      height: 16px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top: 2px solid white;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      0% { transform: rotate(0deg); }
      100% { transform: rotate(360deg); }
    }
  `]
})
export class ButtonComponent {
  @Input() type: 'button' | 'submit' | 'reset' = 'button';
  @Input() variant: 'primary' | 'secondary' | 'outline' = 'primary';
  @Input() disabled = false;
  @Input() loading = false;
  @Output() clicked = new EventEmitter<void>();

  get buttonClass(): string {
    return `btn-${this.variant}`;
  }

  onClick(): void {
    if (!this.disabled && !this.loading) {
      this.clicked.emit();
    }
  }
}

