import { Directive, ElementRef, EventEmitter, HostListener, Output, inject } from '@angular/core';

@Directive({
  selector: '[clickOutside]',
  standalone: true
})
export class ClickOutsideDirective {
  private elementRef = inject(ElementRef);
  
  @Output() clickOutside = new EventEmitter<void>();

  @HostListener('document:click', ['$event.target'])
  onClick(target: EventTarget | null): void {
    if (target instanceof HTMLElement) {
      const clickedInside = this.elementRef.nativeElement.contains(target);
      if (!clickedInside) {
        this.clickOutside.emit();
      }
    }
  }
}

