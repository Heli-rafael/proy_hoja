import { Injectable } from "@angular/core";
import { CanActivate, Router, UrlTree, ActivatedRouteSnapshot } from '@angular/router';
import { map, take, switchMap } from 'rxjs/operators';
import { Observable, of } from 'rxjs';
import { AuthService } from "./auth.service";

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  canActivate(route: ActivatedRouteSnapshot): Observable<boolean | UrlTree> {

    return this.authService.isAuthenticated$.pipe(
      take(1),
      switchMap(isAuth => {

        if (!isAuth) {
          return this.authService.checkAuth();
        }

        return of(true);
      }),
      switchMap(authenticated => {

        if (!authenticated) {
          return of(this.router.createUrlTree(['/auth/login']));
        }

        // Validamos permisos
        return this.authService.getCurrentUser().pipe(
          take(1),
          map(user => {

            const requiresStaff = route.data['requiresStaff'];
            const requiresSuperuser = route.data['requiresSuperuser'];

            // Permite acceso a los demas
            if (!requiresStaff && !requiresSuperuser) {
              return true;
            }

            // Solo superuser
            if (requiresSuperuser) {
              return user?.is_superuser
                ? true
                : this.router.createUrlTree(['/page/chat']);
            }

            // Staff o superuser
            if (requiresStaff) {
              return (user?.is_staff || user?.is_superuser)
                ? true
                : this.router.createUrlTree(['/page/chat']);
            }

            return this.router.createUrlTree(['/page/chat']);
          })
        );
      })
    );
  }
}