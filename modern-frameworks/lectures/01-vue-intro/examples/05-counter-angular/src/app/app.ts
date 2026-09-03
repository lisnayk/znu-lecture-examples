import { Component, computed, signal } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <h1>Лічильник — Angular</h1>
    <p class="count">{{ count() }}</p>
    <button (click)="add()">Додати</button>
    <button (click)="clear()">Очистити</button>
    <p>{{ total() }}</p>
    <ul>
      @for (e of entries(); track e) {
        <li>{{ e }}</li>
      }
      @if (entries().length === 0) {
        <li class="empty">поки порожньо</li>
      }
    </ul>
  `,
})
export class App {
  protected readonly count = signal(0);
  protected readonly entries = signal<string[]>([]);
  protected readonly total = computed(
    () => `Записів: ${this.entries().length}`,
  );

  protected add(): void {
    const next = this.count() + 1;
    this.count.set(next);
    this.entries.update((list) => [
      `Запис ${next} о ${new Date().toLocaleTimeString('uk-UA')}`,
      ...list,
    ]);
  }

  protected clear(): void {
    this.count.set(0);
    this.entries.set([]);
  }
}
