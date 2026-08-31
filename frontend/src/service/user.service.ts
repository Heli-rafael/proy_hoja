import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { HttpHeaders } from '@angular/common/http';
import { User } from '../model/user.model';
import { AuthService } from './auth/auth.service';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class UserService {

    private profileUrl = `${environment.apiUrl}api/me/`;
    private apiUrl = `${environment.apiUrl}api/usuario/`;
    private planUrl = `${environment.apiUrl}api/plan/`;
    private creditsUrl = `${environment.apiUrl}api/me/creditos/`;

    constructor(
        private http: HttpClient,
        private authService: AuthService
    ) {}

    getProfile(): Observable<any> {
        return this.http.get(this.profileUrl);
    }

    getPlan(): Observable<any> {
        return this.http.get(this.planUrl);
    }

    getCreditos(): Observable<any> {
        return this.http.get(this.creditsUrl);
    }


    // Actualizar un usuario existente
    editarUsuario(id: number, datos: FormData) {
        return this.http.patch<User>(
            `${this.apiUrl}${id}/`,
            datos
        );
    }

    cambiarPassword(data: any): Observable<any> {
        return this.http.post(`${environment.apiUrl}api/me/password/`, data);
    }

}