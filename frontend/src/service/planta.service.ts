import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PlantaModel } from '../model/planta.model';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PlantaService {
  private apiUrl = `${environment.apiUrl}api/planta/`;

  constructor(private http: HttpClient) {}

  getPlantas(): Observable<PlantaModel[]> {
    return this.http.get<PlantaModel[]>(this.apiUrl);
  }

  getPlantaPorId(id: number): Observable<PlantaModel> {
    return this.http.get<PlantaModel>(`${this.apiUrl}${id}/`);
  }

  agregarPlanta(planta: FormData | PlantaModel): Observable<PlantaModel> {
    return this.http.post<PlantaModel>(this.apiUrl, planta);
  }

  editarPlanta(id: number, planta: FormData | PlantaModel): Observable<PlantaModel> {
    return this.http.put<PlantaModel>(`${this.apiUrl}${id}/`, planta);
  }

  eliminarPlanta(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }

  // Este método enviará la imagen y el backend responderá con el Chat creado
  subirImagen(file: File): Observable<any> {
    const formData = new FormData();
    formData.append('imagen', file);
    // Si el backend necesita el nombre, lo mandamos genérico
    formData.append('nombre', 'Nueva captura'); 
    
    return this.http.post<any>(this.apiUrl, formData);
  }
}