import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../../service/auth/auth.service';
import { MessageService } from 'primeng/api';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import { finalize } from 'rxjs/operators';

@Component({
  selector: 'app-login',
  standalone: false,
  templateUrl: './login.html',
  styleUrl: './login.css',
  providers: [ProcessingService],
})
export class Login {
  loginForm!: FormGroup;
  showPassword: boolean = false;

  constructor(
    public processing: ProcessingService,
    private authService: AuthService,
    private fb: FormBuilder,
    private router: Router,
    private route: ActivatedRoute,
    private messageService: MessageService
  ) {}

  ngOnInit() {
    this.loginForm = this.fb.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required]],
    });
  }

  togglePassword() {
    this.showPassword = !this.showPassword;
  }

  onSubmit(): void {
    if (!this.loginForm.valid) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Campos requeridos',
        detail: 'Debes completar todos los campos correctamente.'
      });
      return;
    }

    if (!this.processing.start()) return;

    const { email, password } = this.loginForm.value;

    // Llamamos al servicio de login que usa cookies
    this.authService.login(email, password).pipe(
      finalize(() => this.processing.stop())
    ).subscribe({
      next: (success) => {
        if (success) {
          // Mostrar mensaje de bienvenida
          this.messageService.add({
            severity: 'success',
            summary: 'Bienvenido',
            detail: `Bienvenido ${email}`
          });

          // Redirigir al returnUrl o al inicio
          const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/page/chat';
          this.router.navigate([returnUrl]);
        } else {
          // Error de login
          this.messageService.add({
            severity: 'error',
            summary: 'Error de autenticación',
            detail: 'Correo electrónico o contraseña incorrectos'
          });
        }
      },
      error: (err) => {
        console.error(err);
        this.messageService.add({
          severity: 'error',
          summary: 'Error de autenticación',
          detail: 'Ocurrió un error en el servidor'
        });
      }
    });
  }

  onFieldBlur(field: string): void {
    const control = this.loginForm.get(field);
    if (control && control.invalid && control.touched) {
      this.messageService.clear();
      const errors = control.errors;

      if (field === 'email' && errors?.['email']) {
        this.messageService.add({
          severity: 'warn',
          summary: 'Validación',
          detail: 'El correo ingresado no es válido.'
        });
      }
    }
  }
}import { ProcessingService } from '../../../service/auth/processing.service';

