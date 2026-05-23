import { Component, signal } from '@angular/core';
import { AuthService } from '../service/auth/auth.service';
@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  standalone: false,
  styleUrl: './app.css'
})
export class App {
  protected readonly title = signal('frontend');

  constructor(private authService: AuthService) {}

  ngOnInit(): void {

  }

}
