import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiConfig } from './auth/api.config';
import { Observable } from 'rxjs';
import { DiagnosticoIAModel } from '../model/diagnostico-ia.model';

@Injectable({
  providedIn: 'root'
})
export class DiagnosticoIAService {
  private apiUrl = `${ApiConfig.apiUrl}api/diagnostico/`;

  constructor(private http: HttpClient) {}

  getMisDiagnosticos(): Observable<DiagnosticoIAModel[]> {
    return this.http.get<DiagnosticoIAModel[]>(this.apiUrl);
  }

  getDiagnosticoPorId(id: number): Observable<DiagnosticoIAModel> {
    return this.http.get<DiagnosticoIAModel>(`${this.apiUrl}${id}/`);
  }

  // Se usa FormData para poder enviar el archivo de imagen capturado
  crearDiagnostico(datos: FormData): Observable<DiagnosticoIAModel> {
    return this.http.post<DiagnosticoIAModel>(this.apiUrl, datos);
  }

  eliminarDiagnostico(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }

  getDiagnosticoById(id: number) {
    return this.http.get<any>(`${this.apiUrl}${id}/`);
  }
}