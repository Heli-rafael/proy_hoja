import { Component, signal } from '@angular/core';
import { AuthService } from '../service/auth/auth.service';
import { ThemeService } from '../service/theme/thema.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  standalone: false,
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');

  constructor(
    private authService: AuthService,
    private themeService: ThemeService
  ) {}

  ngOnInit(): void {
    
    this.themeService.useSystemTheme();

  }

}
