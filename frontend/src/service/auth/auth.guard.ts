import { Injectable } from '@angular/core';

import {
  ActivatedRouteSnapshot,
  CanActivate,
  Router,
  RouterStateSnapshot
} from '@angular/router';

import { Observable, map } from 'rxjs';

import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  canActivate(): Observable<boolean> {

    return this.authService.checkAuth().pipe(

      map(isAuth => {

        if (!isAuth) {

          this.router.navigate(['/auth/login']);

          return false;
        }

        return true;
      })
    );
  }
}