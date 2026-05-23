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

    private apiUrl = `${ApiConfig.apiUrl}api/usuario/`; // para CRUD general
    private profileUrl = `${ApiConfig.apiUrl}api/me/`;
    private creditsUrl = `${ApiConfig.apiUrl}api/me/creditos/`;

    constructor(
        private http: HttpClient,
        private authService: AuthService
    ) {}

    getProfile(): Observable<any> {
        return this.http.get(this.profileUrl);
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
    editarUsuario(id: number, usuario: User): Observable<User> {
        return this.http.put<User>(`${this.apiUrl}${id}/`, usuario);
    }

    // Eliminar un usuario
    eliminarUsuario(id: number): Observable<void> {
        return this.http.delete<void>(`${this.apiUrl}${id}/`);
    }
    
}