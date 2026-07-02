import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, catchError, map, Observable, of, switchMap, tap } from 'rxjs';
import { MessageService } from 'primeng/api';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiLoginUrl = `${environment.apiUrl}api/login/`;
  private apiGoogleUrl = `${environment.apiUrl}api/google-login/`;
  private apiLogoutUrl = `${environment.apiUrl}api/logout/`;
  private apiMeUrl = `${environment.apiUrl}api/me/`;

  constructor(
    private http: HttpClient,
    private router: Router,
    private messageService: MessageService
  ) {}

  // ========================
  // Login Auth
  // ========================
  login(email: string, password: string): Observable<any> {

    return this.http.post<any>(
      this.apiLoginUrl,
      { email, password },
      { withCredentials: true }
    );
  }

  // ========================
  // Login Google
  // ========================
  googleLogin(token: string): Observable<any> {

    return this.http.post<any>(
      this.apiGoogleUrl,
      { token },
      { withCredentials: true }
    );
  }

  // ========================
  // Login Auth
  // ========================
  logout(): Observable<boolean> {

    return this.http.post<any>(
      this.apiLogoutUrl,
      {},
      { withCredentials: true }
    ).pipe(
      
      tap(() => {
        this.messageService.add({
          severity: 'success',
          summary: 'Hasta pronto',
          detail: 'La sesión se cerró correctamente.',
          icon: 'pi pi-sign-out',
        });
        this.router.navigate(['/auth/login']);
      }),

      map(() => true),
      

      catchError(() => of(false))
    );
  }

  // ========================
  // Verifica Auth
  // ========================
  checkAuth(): Observable<boolean> {
    return this.http.get<any>(
      this.apiMeUrl,
      { withCredentials: true }
    ).pipe(

      map(() => true),

      catchError(() => {
        this.router.navigate(['/auth/login']);
        return of(false);
      })

    );
  }

  // ========================
  // ontiene Usuario
  // ========================
  getCurrentUser(): Observable<any> {

    return this.http.get<any>(
      this.apiMeUrl,
      { withCredentials: true }
    );
  }
}