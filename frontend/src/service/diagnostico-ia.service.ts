import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DiagnosticoProgreso } from '../model/diagnostico-ia.model';
import { ActividadTratamientoModel } from '../model/actividad-tratamiento';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class DiagnosticoIAService {
  private apiUrl = `${environment.apiUrl}api/diagnostico/`;

  constructor(private http: HttpClient) {}

  // Obtener progreso de un diagnóstico
  getDiagnosticoProgreso(diagnosticoId: number): Observable<DiagnosticoProgreso> {
    return this.http.get<DiagnosticoProgreso>(
    `${this.apiUrl}${diagnosticoId}/progreso/`
  );
  }

  // Actualizar calendario
  actualizarActividad(id: number, data: Partial<ActividadTratamientoModel>) {
    return this.http.patch(
      `${environment.apiUrl}api/actividad-tratamiento/${id}/`,
      data
    );
  }

  // Exportar formatos
  exportDiagnosticosExcel() {
    return this.http.get(
      `${this.apiUrl}export/excel/`,
      { responseType: 'blob' }
    );
  }

  // Exportar todos los diagnosticos en PDF
  exportDiagnosticosPDF() {
    return this.http.get(
      `${this.apiUrl}export/pdf/`,
      { responseType: 'blob' }
    );
  }

  // Exportar un diagnostico en PDF
  exportDiagnosticoPDF(id: number) {
    return this.http.get(
      `${this.apiUrl}export/pdfindividual/${id}/`,
      { responseType: 'blob' }
    );
  }

  // Exportar imagenes
  exportDiagnosticoImagen(id: number) {
  return this.http.get(
    `${this.apiUrl}export/imagenindividual/${id}/`,
    { responseType: 'blob' }
  );
  }
  
}