import { Injectable } from '@angular/core';
import { CanActivate, Router, UrlTree, ActivatedRouteSnapshot } from '@angular/router';
import { map, take } from 'rxjs/operators';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class RoleGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(route: ActivatedRouteSnapshot): Observable<boolean | UrlTree> {

    const allowedRoles = route.data['roles'] as string[]; // 👈 roles permitidos
    const requireStaff = route.data['staff'] as boolean;
    const requireSuperuser = route.data['superuser'] as boolean;

    return this.authService.getCurrentUser().pipe(
      take(1),
      map(user => {

        if (!user) {
          return this.router.createUrlTree(['/login']);
        }

        // 🔥 superuser tiene acceso total
        if (user.is_superuser) {
          return true;
        }

        // 🔥 restricción por superuser
        if (requireSuperuser && !user.is_superuser) {
          return this.router.createUrlTree(['/inicio']);
        }

        // 🔥 restricción por staff
        if (requireStaff && !user.is_staff) {
          return this.router.createUrlTree(['/inicio']);
        }

        // 🔥 restricción por rol (opcional)
        if (allowedRoles && allowedRoles.length > 0) {
          if (!allowedRoles.includes(user.rol)) {
            return this.router.createUrlTree(['/inicio']);
          }
        }

        return true;
      })
    );
  }
}