import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../../service/auth/auth.service';
import { MessageService } from 'primeng/api';
import { ProcessingService } from '../../../service/auth/processing.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ThemeService } from '../../../service/theme/thema.service';
import { finalize } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

declare const google: any;

@Component({
  selector: 'app-login',
  standalone: false,
  templateUrl: './login.html',
  styleUrl: './login.css',
  providers: [ProcessingService],
})
export class Login {

  loginForm!: FormGroup;
  private googleInitialized = false;
  logo = '/AgroVisionAI.png';

  private apiOauth = `${environment.apiOAuthGoogle}`;

  constructor(
    public processing: ProcessingService,
    private authService: AuthService,
    private themeService: ThemeService,

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

    // Verificacion
    this.authService.checkAuth().subscribe((isAuth) => {
      if (isAuth) {
        this.router.navigate(['/page/chat']);
      }
    });

    // Tema
    this.themeService.theme$.subscribe(theme => {
      this.renderGoogleButton(theme);
    });

    this.themeService.useSystemTheme();
    
  }

  regresarAtras(){
    this.router.navigate(['/page/inicio']);
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
      next: (res) => {
        this.messageService.add({
          severity: 'success',
          summary: 'Bienvenido',
          detail: `Hola, ${res.username || res.first_name}`,
          icon: 'pi pi-check-circle',
          // Para el tiempo: life: 500000
        });

        this.router.navigate(['/page/chat']);
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
  
  private waitForGoogle(callback: () => void) {
    const interval = setInterval(() => {
      if ((window as any).google?.accounts?.id) {
        clearInterval(interval);
        callback();
      }
    }, 50);
  }

  renderGoogleButton(theme: 'light' | 'dark') {
    const container = document.getElementById('googleButton');
    if (!container) return;

    this.waitForGoogle(() => {
      container.innerHTML = '';

      if (!this.googleInitialized) {
        google.accounts.id.initialize({
          client_id: this.apiOauth,
          callback: (response: any) => this.handleGoogleLogin(response)
        });

        this.googleInitialized = true;
      }

      google.accounts.id.renderButton(container, {
        theme: theme === 'dark' ? 'filled_black' : 'outline',
        size: 'large',
      });
    });
  }
  
  
  handleGoogleLogin(response: any): void {

    const idToken = response.credential;

    this.authService.googleLogin(idToken).subscribe({
      next: (res) => {

        this.messageService.add({
          severity: 'success',
          summary: 'Sesión con Google',
          detail: `Hola, ${res.first_name}`,
          icon: 'pi pi-google',
        });

        this.router.navigate(['/page/chat']);
      },

      error: () => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'No se pudo autenticar'
        });
      }
    });
  }

}

