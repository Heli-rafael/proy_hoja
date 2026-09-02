import { Component } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { AuthService } from '../../../service/auth/auth.service';
import { MessageService } from 'primeng/api';
import { ProcessingService } from '../../../service/auth/processing.service';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ThemeService } from '../../../service/theme/thema.service';
import { finalize } from 'rxjs/operators';
import { environment } from '../../../environments/environment';

import {
  ElementRef,
  ViewChild
} from '@angular/core';

declare const google: any;

@Component({
  selector: 'app-login',
  standalone: false,
  templateUrl: './login.html',
  styleUrl: './login.css',
  providers: [ProcessingService],
})
export class Login {

  logo = '/AgroVisionAI.png';

  // GOOGLE
  private googleInitialized = false;
  private googleButtonElement?: HTMLDivElement;
  private currentTheme: 'light' | 'dark' = 'light';

  // LOGIN
  loginForm!: FormGroup;

  // VISTA
  view: 'login' | 'register' | 'recovery' = 'login';

  // REGISTRO
  registerForm!: FormGroup;
  recoveryForm!: FormGroup;

  // STEP
  registerStep = 1;
  emailVerified = false;

  recoveryStep = 1;
  recoveryEmailVerified = false;

  // TIEMPO DE VERIFICACION
  verificationSeconds = 300;

  private apiOauth = `${environment.apiOAuthGoogle}`;

  // INTERACCION SESSION
  vistaActual = 0;
  private intervaloVista: ReturnType<typeof setInterval> | null = null;
  private readonly totalVistas = 2;

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

    // FORMULARIO DE REGISTRO
    this.registerForm = this.fb.group({
      email: ['', [
        Validators.required, Validators.email
      ]],

      verificationCode: ['', [
        Validators.required, Validators.minLength(6), Validators.maxLength(6)
      ]],

      nickname: ['', [
        Validators.required, Validators.minLength(3)
      ]],

      name: ['', [
        Validators.required
      ]],

      lastname: ['', [
        Validators.required
      ]],

      phone: ['', [
        Validators.required, Validators.pattern(/^\d{9}$/)
      ]],

      password: ['', [
        Validators.required, Validators.minLength(8)
      ]],

      confirmPassword: ['', [
        Validators.required
      ]]
    });

    // FORMULARIO DE RECUPERACIÓN
    this.recoveryForm = this.fb.group({
      email: ['', [
        Validators.required, Validators.email
      ]],

      verificationCode: ['', [
        Validators.required, Validators.minLength(6), Validators.maxLength(6)
      ]],

      password: ['', [
        Validators.required, Validators.minLength(8)
      ]],

      confirmPassword: ['', [
        Validators.required
      ]]
    });


    // Verificacion
    this.authService.checkAuth().subscribe((isAuth) => {
      if (isAuth) {
        this.router.navigate(['/page/chat']);
      }
    });

    // Tema
    this.themeService.theme$.subscribe(theme => {
      this.currentTheme = theme;
      this.renderGoogleButton();
    });

    this.themeService.useSystemTheme();

    // Redirigir a Register de /Inicio
    this.route.queryParams.subscribe(params => {
      if (params['view'] === 'register') {
          this.openRegister();
      }
    });
    
    // INTERACCION GOOGLE
    this.iniciarCarruselVistas();
  }

  ngOnDestroy(): void {
    this.detenerCarruselVistas();
  }

  onPhoneInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    input.value = input.value.replace(/\D/g, '');
    this.registerForm.get('phone')?.setValue(input.value, {
        emitEvent: false
    });
  }


  // VOLVER
  regresarAtras(){
    this.router.navigate(['/page/inicio']);
  }

  /*=========================================================
          INTERACCION SESSION
  =========================================================*/
  iniciarCarruselVistas(): void {

    this.detenerCarruselVistas();

    this.intervaloVista = setInterval(() => {

      this.vistaActual =
        (this.vistaActual + 1) % this.totalVistas;

    }, 7000);

  }


  detenerCarruselVistas(): void {

    if (this.intervaloVista) {

      clearInterval(this.intervaloVista);

      this.intervaloVista = null;

    }

  }


  vistaSiguiente(): void {

    this.vistaActual =
      (this.vistaActual + 1) % this.totalVistas;

    this.iniciarCarruselVistas();

  }


  vistaAnterior(): void {

    this.vistaActual =
      (this.vistaActual - 1 + this.totalVistas)
      % this.totalVistas;

    this.iniciarCarruselVistas();

  }


  seleccionarVista(index: number): void {

    if (index < 0 || index >= this.totalVistas) {
      return;
    }

    this.vistaActual = index;

    this.iniciarCarruselVistas();

  }

  /*=========================================================
          VERIFICACIONES DE SESSION
  =========================================================*/

  // INICIAR SESIÓN
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
          summary: 'No se pudo iniciar sesión',
          detail: 'El correo o la contraseña son incorrectos.'
        });
      }
    });
  }

  // VALIDAR CAMPO
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

  /*=========================================================
          GOOGLE SESSION
  =========================================================*/

  @ViewChild('googleButton')
    set googleButtonRef(ref: ElementRef<HTMLDivElement> | undefined) {

      if (!ref) {
        return;
      }

      this.googleButtonElement = ref.nativeElement;
      this.initializeGoogle();
    }

  // INICIALIZA GOOGLE IDENTIFY SERVICE
  private initializeGoogle(): void {
    if (!this.googleButtonElement) {
      return;
    }
    if (!google?.accounts?.id) {
      console.error('Google Identity Services no está disponible.');
      return;
    }
    if (!this.googleInitialized) {
      google.accounts.id.initialize({
        client_id: this.apiOauth,
        callback: (response: any) => {
          this.handleGoogleLogin(response);
        }
      });
      this.googleInitialized = true;
    }
    this.renderGoogleButton();
  }

  // DIBUJAR EL BOTON
  private renderGoogleButton(): void {

    if (!this.googleInitialized || !this.googleButtonElement) {
      return;
    }

    this.googleButtonElement.innerHTML = '';

    google.accounts.id.renderButton(
      this.googleButtonElement,
      {
        theme: this.currentTheme === 'dark'
          ? 'filled_black'
          : 'outline',
        size: 'large'
      }
    );
  }
  
  // RENDERIZADO DEL BOTON
  handleGoogleLogin(response: any): void {
    const idToken = response.credential;
    this.authService.googleLogin(idToken).subscribe({
      next: (res) => {
        sessionStorage.setItem('loginWelcome',JSON.stringify(res));
        window.location.reload();
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

  /*=========================================================
          REGISTRO
  =========================================================*/
  
  // TEMPORIZADOR DE VERIFICACIÓN
  private verificationTimer?: ReturnType<typeof setInterval>;

  // TITULO DE PROCESO
  getRegisterTitle(): string {
    switch (this.registerStep) {
      case 1: return 'Crear cuenta';
      case 2: return 'Verifica tu correo';
      case 3: return 'Completa tu perfil';
      case 4: return 'Protege tu cuenta';
      default: return 'Crear cuenta';
    }
  }

  // DESCRIPCION DE PROCESO
  getRegisterDescription(): string {
    switch (this.registerStep) {
      case 1: return 'Comienza ingresando tu correo electrónico.';
      case 2: return 'Ingresa el código de 6 dígitos que enviamos a tu correo.';
      case 3: return 'Cuéntanos un poco sobre ti.';
      case 4: return 'Crea una contraseña segura para proteger tu cuenta.';
      default: return '';
    }
  }

  // INICIAR TEMPORIZADOR
  startVerificationTimer(): void {
    this.stopVerificationTimer();

    this.verificationSeconds = 300;

    this.verificationTimer = setInterval(() => {
      if (this.verificationSeconds > 0) {
        this.verificationSeconds--;
      } else {
        this.stopVerificationTimer();
      }
    }, 1000);
  }

  // DETENER TEMPORIZADOR
  stopVerificationTimer(): void {
    if (this.verificationTimer) {
      clearInterval(this.verificationTimer);
      this.verificationTimer = undefined;
    }
  }

  // FORMATEAR TIEMPO
  formatVerificationTime(): string {
    const minutes = Math.floor(this.verificationSeconds / 60);
    const seconds = this.verificationSeconds % 60;

    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  }

  // ABRIR REGISTRO
  openRegister(): void {
    this.view = 'register';
    this.registerStep = 1;
    this.emailVerified = false;
    this.registerForm.reset();
  }

  // REGRESAR LOGIN
  backToLogin(): void {
    this.stopVerificationTimer();

    this.view = 'login';

    this.registerStep = 1;
    this.emailVerified = false;

    this.recoveryStep = 1;
    this.recoveryEmailVerified = false;

    this.registerForm.reset();
    this.recoveryForm.reset();
  }

  /* STEP REGISTRATION - SEND CODE TO EMAIL */
  continueEmail(): void {

    const emailControl = this.registerForm.get('email');

    if (!emailControl || emailControl.invalid) {
      emailControl?.markAsTouched();
      return;
    }

    // PROGRESO
    if (!this.processing.start()) {
      return;
    }

    const email = emailControl.value;

    this.authService.requestOTP(email, 'register').pipe(
      finalize(() => this.processing.stop())
    ).subscribe({

      next: () => {
        this.registerStep = 2;
        this.startVerificationTimer();
        this.messageService.add({
          severity: 'success',
          summary: 'Código enviado',
          detail: 'Hemos enviado un código de verificación a tu correo.'
        });

      },

      error: (err) => {
        console.error(err);
        this.messageService.add({
          severity: 'error',
          summary: 'No se pudo enviar',
          detail: this.getErrorMessage(err)
        });

      }

    });

  }

  /* STEP REGISTRATION - VERIFY CODE */
  verifyCode(): void {
    const codeControl = this.registerForm.get('verificationCode');

    if (
      !codeControl ||
      codeControl.invalid ||
      this.verificationSeconds <= 0
    ) {
      codeControl?.markAsTouched();
      return;
    }

    if (!this.processing.start()) {
      return;
    }

    const email = this.registerForm.get('email')?.value;
    const code = codeControl.value;

    this.authService.verifyOTP(
      email, code, 'register'
    ).pipe(
      finalize(() => this.processing.stop())
    ).subscribe({

      next: () => {
        this.stopVerificationTimer();
        this.emailVerified = true;
        this.registerStep = 3;
        this.messageService.add({
          severity: 'success',
          summary: 'Correo verificado',
          detail: 'Tu correo ha sido verificado correctamente.'
        });
      },

      error: (err) => {
        console.error(err);
        this.messageService.add({
          severity: 'error',
          summary: 'Código incorrecto',
          detail: err?.error?.detail ||
                  'El código ingresado no es válido.'
        });
      }
    });
  }

  resendVerificationCode(): void {
    const email = this.registerForm.get('email')?.value;
    
    if (!email) {
      return;
    }

    if (!this.processing.start()) {
      return;
    }

    this.authService.requestOTP(
      email, 'register'
    ).pipe(
      finalize(() => this.processing.stop())
    ).subscribe({

      next: () => {
        this.startVerificationTimer();
        this.registerForm
          .get('verificationCode')?.reset();
        this.messageService.add({
          severity: 'success',
          summary: 'Código reenviado',
          detail: 'Hemos enviado un nuevo código a tu correo.'
        });
      },

      error: (err) => {
        console.error(err);
        this.messageService.add({
          severity: 'error',
          summary: 'No se pudo reenviar',
          detail: err?.error?.detail ||
                  'No se pudo enviar un nuevo código.'
        });
      }

    });
  }

  /* STEP REGISTRATION - PROFILE */
  continueProfile(): void {

    const personalControls = [
      'nickname',
      'name',
      'lastname',
      'phone'
    ];

    personalControls.forEach(controlName => {
      this.registerForm
        .get(controlName)
        ?.markAsTouched();
    });

    const invalid = personalControls.some(
      controlName =>
        this.registerForm.get(controlName)?.invalid
    );

    if (invalid) {
      return;
    }

    this.registerStep = 4;
  }

  /* STEP REGISTRATION - PASSWORD */
  getPasswordStrength(): number {
    const password = this.registerForm.get('password')?.value || '';

    if (!password) {
      return 0;
    }

    let strength = 0;

    if (password.length >= 8) {
      strength++;
    }

    if (/[A-Z]/.test(password)) {
      strength++;
    }

    if (/[a-z]/.test(password)) {
      strength++;
    }

    if (/[0-9]/.test(password)) {
      strength++;
    }

    if (/[^A-Za-z0-9]/.test(password)) {
      strength++;
    }

    return Math.min(strength, 4);
  }

  getPasswordStrengthLabel(): string {
    const strength = this.getPasswordStrength();

    switch (strength) {
      case 1:
        return 'Débil';
      case 2:
        return 'Regular';
      case 3:
        return 'Buena';
      case 4:
        return 'Excelente';
      default:
        return '';
    }
  }

  hasMinLength(): boolean {
    const password = this.registerForm.get('password')?.value || '';

    return password.length >= 8;
  }


  /* STEP REGISTRATION - COMPLETE REGISTRATION */
  completeRegister(): void {

    if (!this.emailVerified) {
      return;
    }

    const passwordControl = this.registerForm.get('password');
    const confirmPasswordControl = this.registerForm.get('confirmPassword');

    passwordControl?.markAsTouched();
    confirmPasswordControl?.markAsTouched();

    if ( passwordControl?.invalid || confirmPasswordControl?.invalid) {
      return;
    }

    if (!this.passwordsMatch()) {

      this.messageService.add({
        severity: 'warn',
        summary: 'Contraseñas diferentes',
        detail: 'Las contraseñas ingresadas no coinciden.'
      });

      return;
    }

    if (!this.processing.start()) {
      return;
    }

    const registerData = {
      email: this.registerForm.get('email')?.value,
      password: this.registerForm.get('password')?.value,
      nickname: this.registerForm.get('nickname')?.value,
      name: this.registerForm.get('name')?.value,
      lastname: this.registerForm.get('lastname')?.value,
      phone: this.registerForm.get('phone')?.value
    };


    this.authService.register(registerData).pipe(
      finalize(() => this.processing.stop())
    ).subscribe({
      next: (res) => {
        this.messageService.add({
          severity: 'success',
          summary: 'Cuenta creada',
          detail: 'Tu cuenta fue creada correctamente.'
        });
        
        this.router.navigate(['/page/chat']);
      },
      error: (err) => {
        console.error(err);
        this.messageService.add({
          severity: 'error',
          summary: 'No se pudo crear la cuenta',
          detail: err?.error?.detail ||
                  'Ocurrió un error al crear tu cuenta.'
        });
      }
    });
  }


  /*=========================================================
          RECOVERY
  =========================================================*/
    
  // ABRIR RECUPERACIÓN
  openRecovery(): void {
    this.stopVerificationTimer();
    this.view = 'recovery';
    this.recoveryStep = 1;
    this.recoveryEmailVerified = false;
  }

  // TÍTULO DE RECUPERACIÓN
  getRecoveryTitle(): string {
    switch (this.recoveryStep) {
      case 1: return 'Recupera tu cuenta';
      case 2: return 'Verifica tu correo';
      case 3: return 'Crea una nueva contraseña';
      default: return 'Recupera tu cuenta';
    }
  }

  // DESCRIPCIÓN DE RECUPERACIÓN
  getRecoveryDescription(): string {
    switch (this.recoveryStep) {
      case 1: return 'Ingresa tu correo electrónico para comenzar.';
      case 2: return 'Ingresa el código de 6 dígitos que enviamos a tu correo.';
      case 3: return 'Crea una nueva contraseña segura para tu cuenta.';
      default: return '';
    }
  }

  // VALIDAR CONTRASEÑAS
  private passwordsMatch(): boolean {
    const password = this.registerForm.get('password')?.value;
    const confirmPassword = this.registerForm.get('confirmPassword')?.value;

    return password === confirmPassword;
  }

  // VALIDAR CONTRASEÑAS DE REGISTRO
  get passwordMismatch(): boolean {
    const password = this.registerForm.get('password');
    const confirmPassword = this.registerForm.get('confirmPassword');

    return !!(
      password &&
      confirmPassword &&
      confirmPassword.touched &&
      confirmPassword.value &&
      password.value !== confirmPassword.value
    );
  }

  // SOLICITAR CÓDIGO DE RECUPERACIÓN
  continueRecoveryEmail(): void {
    const emailControl = this.recoveryForm.get('email');

    if (!emailControl || emailControl.invalid) {
      emailControl?.markAsTouched();
      return;
    }

    if (!this.processing.start()) {
      return;
    }

    const email = emailControl.value;

    this.authService.requestOTP(email, 'reset_password').pipe(
      finalize(() => this.processing.stop())
    ).subscribe({
      next: () => {
        this.recoveryStep = 2;
        this.startVerificationTimer();

        this.recoveryForm.get('verificationCode')?.reset();

        this.messageService.add({
          severity: 'success',
          summary: 'Código enviado',
          detail: 'Hemos enviado un código de recuperación a tu correo.'
        });
      },
      error: (err) => {
        console.error(err);

        this.messageService.add({
          severity: 'error',
          summary: 'No se pudo enviar',
          detail: this.getErrorMessage(err)
        });
      }
    });
  }

  // VERIFICAR CÓDIGO DE RECUPERACIÓN
  verifyRecoveryCode(): void {
    const codeControl = this.recoveryForm.get('verificationCode');

    if (!codeControl || codeControl.invalid || this.verificationSeconds <= 0) {
      codeControl?.markAsTouched();
      return;
    }

    if (!this.processing.start()) {
      return;
    }

    const email = this.recoveryForm.get('email')?.value;
    const code = codeControl.value;

    this.authService.verifyOTP(email, code, 'reset_password').pipe(
      finalize(() => this.processing.stop())
    ).subscribe({
      next: (res: any) => {
        this.stopVerificationTimer();
        this.recoveryEmailVerified = true;
        this.recoveryStep = 3;

        this.messageService.add({
          severity: 'success',
          summary: 'Correo verificado',
          detail: 'Ahora puedes crear una nueva contraseña.'
        });
      },
      error: (err) => {
        console.error(err);

        this.messageService.add({
          severity: 'error',
          summary: 'Código incorrecto',
          detail: err?.error?.detail || 'El código ingresado no es válido.'
        });
      }
    });
  }

  // REENVIAR CÓDIGO DE RECUPERACIÓN
  resendRecoveryCode(): void {
    const email = this.recoveryForm.get('email')?.value;

    if (!email) {
      return;
    }

    if (!this.processing.start()) {
      return;
    }

    this.authService.requestOTP(email, 'reset_password').pipe(
      finalize(() => this.processing.stop())
    ).subscribe({
      next: () => {
        this.startVerificationTimer();

        this.recoveryForm.get('verificationCode')?.reset();

        this.messageService.add({
          severity: 'success',
          summary: 'Código reenviado',
          detail: 'Hemos enviado un nuevo código a tu correo.'
        });
      },
      error: (err) => {
        console.error(err);

        this.messageService.add({
          severity: 'error',
          summary: 'No se pudo reenviar',
          detail: err?.error?.detail || 'No se pudo enviar un nuevo código.'
        });
      }
    });
  }

  // VALIDAR CONTRASEÑAS DE RECUPERACIÓN
  get recoveryPasswordMismatch(): boolean {
    const password = this.recoveryForm.get('password');
    const confirmPassword = this.recoveryForm.get('confirmPassword');

    return !!(
      password &&
      confirmPassword &&
      confirmPassword.touched &&
      confirmPassword.value &&
      password.value !== confirmPassword.value
    );
  }

  // CALCULAR SEGURIDAD DE CONTRASEÑA
  getRecoveryPasswordStrength(): number {
    const password = this.recoveryForm.get('password')?.value || '';

    if (!password) {
      return 0;
    }

    let strength = 0;

    if (password.length >= 8) {
      strength++;
    }

    if (/[A-Z]/.test(password)) {
      strength++;
    }

    if (/[a-z]/.test(password)) {
      strength++;
    }

    if (/[0-9]/.test(password)) {
      strength++;
    }

    if (/[^A-Za-z0-9]/.test(password)) {
      strength++;
    }

    return Math.min(strength, 4);
  }

  // ETIQUETA DE SEGURIDAD
  getRecoveryPasswordStrengthLabel(): string {
    const strength = this.getRecoveryPasswordStrength();

    switch (strength) {
      case 1:
        return 'Débil';

      case 2:
        return 'Regular';

      case 3:
        return 'Buena';

      case 4:
        return 'Excelente';

      default:
        return '';
    }
  }

  // VALIDAR LONGITUD DE CONTRASEÑA
  hasRecoveryMinLength(): boolean {
    const password = this.recoveryForm.get('password')?.value || '';
    return password.length >= 8;
  }

  // COMPLETAR RECUPERACIÓN
  completeRecovery(): void {
    if (!this.recoveryEmailVerified) {
      return;
    }

    const passwordControl = this.recoveryForm.get('password');
    const confirmPasswordControl = this.recoveryForm.get('confirmPassword');

    passwordControl?.markAsTouched();
    confirmPasswordControl?.markAsTouched();

    if (passwordControl?.invalid || confirmPasswordControl?.invalid) {
      return;
    }

    if (this.recoveryPasswordMismatch) {
      this.messageService.add({
        severity: 'warn',
        summary: 'Contraseñas diferentes',
        detail: 'Las contraseñas ingresadas no coinciden.'
      });

      return;
    }

    /*
    * AQUÍ irá la llamada al backend
    *
    * authService.resetPassword(...)
    *
    * La agregaremos cuando definamos
    * el endpoint y el token de recuperación.
    */

    this.messageService.add({
      severity: 'info',
      summary: 'Recuperación',
      detail: 'La contraseña está lista para ser actualizada.'
    });
  }

  /*=========================================================
          OBTENER MENSAJE DE ERROR
  =========================================================*/

  private getErrorMessage(err: any): string {
    const error = err?.error;

    if (!error) {
      return 'Ocurrió un error inesperado.';
    }

    // detail
    if (typeof error.detail === 'string') {
      return error.detail;
    }

    // Errores de campos: email, code, purpose, etc.
    for (const key of Object.keys(error)) {
      const value = error[key];

      if (Array.isArray(value) && value.length > 0) {
        return value[0];
      }

      if (typeof value === 'string') {
        return value;
      }
    }

    return 'Ocurrió un error inesperado.';
  }




}

