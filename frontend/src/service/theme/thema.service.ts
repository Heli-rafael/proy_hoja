import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type Theme = 'light' | 'dark' | 'system';

@Injectable({
  providedIn: 'root'
})
export class ThemeService {

  private mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

  private currentTheme = new BehaviorSubject<'light' | 'dark'>(
    this.mediaQuery.matches ? 'dark' : 'light'
  );

  theme$ = this.currentTheme.asObservable();

  private followSystem = false;

  constructor() {

    this.mediaQuery.addEventListener('change', () => {

      if (this.followSystem) {
        this.applySystemTheme();
      }

    });

  }

  getCurrentTheme(): 'light' | 'dark' {
    return this.currentTheme.value;
  }

  setTheme(theme: Theme): void {

    if (theme === 'system') {

      this.followSystem = true;
      this.applySystemTheme();
      return;

    }

    this.followSystem = false;
    this.applyTheme(theme);

  }

  useSystemTheme(): void {

    this.followSystem = true;
    this.applySystemTheme();

  }

  private applySystemTheme(): void {

    const theme: 'light' | 'dark' =
      this.mediaQuery.matches ? 'dark' : 'light';

    this.applyTheme(theme);

  }

  private applyTheme(theme: 'light' | 'dark'): void {

    document.documentElement.setAttribute('data-theme', theme);

    this.currentTheme.next(theme);

    console.log('Tema aplicado:', theme);

  }

}