import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiConfig } from './auth/api.config';
import { Observable } from 'rxjs';
import { HttpHeaders } from '@angular/common/http';
import { User } from '../model/user.model';
import { AuthService } from './auth/auth.service';

@Injectable({
  providedIn: 'root'
})
export class UserService {

    private profileUrl = `${ApiConfig.apiUrl}api/me/`;
    private apiUrl = `${ApiConfig.apiUrl}api/usuario/`;
    private planUrl = `${ApiConfig.apiUrl}api/plan/`;
    private creditsUrl = `${ApiConfig.apiUrl}api/me/creditos/`;

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

    // Obtener todos los usuarios
    getUsuarios(): Observable<User[]> {
        return this.http.get<User[]>(this.apiUrl);
    }

    // Obtener un solo usuario por ID
    getUsuarioPorId(id: number): Observable<User> {
        return this.http.get<User>(`${this.apiUrl}${id}/`);
    }

    // Crear nuevo usuario
    agregarUsuario(usuario: User): Observable<User> {
        return this.http.post<User>(this.apiUrl, usuario);
    }

    // Actualizar un usuario existente
    editarUsuario(id: number, datos: FormData) {
        return this.http.patch<User>(
            `${this.apiUrl}${id}/`,
            datos
        );
    }

    cambiarPassword(data: any): Observable<any> {
        return this.http.post(`${ApiConfig.apiUrl}api/me/password/`, data);
    }

    // Eliminar un usuario
    eliminarUsuario(id: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}${id}/`);
    }
    
}