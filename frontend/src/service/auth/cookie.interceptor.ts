import { Injectable } from '@angular/core';
import {
  HttpInterceptor,
  HttpRequest,
  HttpHandler,
  HttpEvent
} from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable()
export class CsrfInterceptor implements HttpInterceptor {

  private getCookie(name: string): string | null {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) {
      return parts.pop()?.split(';').shift() || null;
    }
    return null;
  }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {

    const csrfToken = this.getCookie('csrftoken');

    let headers = req.headers;

    // Solo para métodos que lo necesitan
    if (csrfToken && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(req.method)) {
      headers = headers.set('X-CSRFToken', csrfToken);
    }

    const clonedReq = req.clone({
      withCredentials: true,
      headers
    });

    return next.handle(clonedReq);
  }
}