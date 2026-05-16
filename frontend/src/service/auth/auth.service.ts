import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { BehaviorSubject, catchError, map, Observable, of, switchMap, tap } from 'rxjs';
import { ApiConfig } from './api.config';

@Injectable({
  providedIn: 'root'
})
export class AuthService {

  private apiLoginUrl = `${ApiConfig.apiUrl}api/login/`;
  private apiLogoutUrl = `${ApiConfig.apiUrl}api/logout/`;
  private apiMeUrl = `${ApiConfig.apiUrl}api/me/`;

  // Estado de autenticación centralizado
  private authSubject = new BehaviorSubject<boolean>(false);

  // La versión pública para los componentes
  public isAuthenticated$ = this.authSubject.asObservable();

  // Estado del usuario
  private currentUserSubject = new BehaviorSubject<any>(null);

  // La versión pública para los componentes
  public currentUser$ = this.currentUserSubject.asObservable();

  private isLoggedOut = false;

  constructor(
    private http: HttpClient,
    private router: Router,
  ) {}

  // Login: devuelve true si fue exitoso
  login(email: string, password: string): Observable<boolean> {
    this.isLoggedOut = false; // 👈 importante

    return this.http.post<any>(this.apiLoginUrl, { email, password }).pipe(
      switchMap(() => this.fetchUser()),
      map(user => !!user),
      catchError(() => of(false))
    );
  }

  // Logout: limpia estado y redirige
  logout(): Observable<void> {

    this.isLoggedOut = true;

    return this.http.post<void>(this.apiLogoutUrl, {}).pipe(
      tap(() => this.clearAuth()),
      catchError(err => {
        console.error('Logout fallido', err);
        this.clearAuth();  // limpieza de frontend aunque falle el backend
        return of(undefined);
      })
    );
  }

  checkAuth(): Observable<boolean> {

    if (this.isLoggedOut) {
      return of(false); // Si ya se hizo logout, no intentamos verificar con el backend
    }

    return this.fetchUser().pipe(
      map(user => !!user)
    );
  }

  // Limpia estado de auth
  private clearAuth(): void {
    this.authSubject.next(false);
    this.currentUserSubject.next(null);
    this.router.navigate(['/auth/login']);
  }

  // Datos del usuario
  private fetchUser(): Observable<any> {
    return this.http.get<any>(this.apiMeUrl).pipe(
      tap(user => {
        this.authSubject.next(true);
        this.currentUserSubject.next(user);
      }),
      catchError(() => {
        this.clearAuth();
        return of(null);
      })
    );
  }

  getCurrentUser(): Observable<any> {
    const cached = this.currentUserSubject.value;

    if (cached) {
      return of(cached);
    }

    return this.fetchUser().pipe(
      map(user => user)
    );
  }
}