import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiConfig } from './auth/api.config';
import { Observable } from 'rxjs';
import { DiagnosticoIAModel } from '../model/diagnostico-ia.model';
import { ActividadTratamientoModel } from '../model/actividad-tratamiento';

@Injectable({
  providedIn: 'root'
})
export class DiagnosticoIAService {
  private apiUrl = `${ApiConfig.apiUrl}api/diagnostico/`;

  constructor(private http: HttpClient) {}

  // Actualizar calendario
  actualizarActividad(id: number, data: Partial<ActividadTratamientoModel>) {
    return this.http.patch(
      `${ApiConfig.apiUrl}api/actividad-tratamiento/${id}/`,
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
}