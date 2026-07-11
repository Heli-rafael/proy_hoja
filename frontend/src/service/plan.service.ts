import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Plan } from '../model/user.model';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class PlanService {

  private apiUrl = `${environment.apiUrl}api/plan/`;

  constructor(private http: HttpClient) {}

  getPlanes(): Observable<Plan[]> {
    return this.http.get<Plan[]>(this.apiUrl);
  }

  getPlanPorId(id: number): Observable<Plan> {
    return this.http.get<Plan>(`${this.apiUrl}${id}/`);
  }

  agregarPlan(plan: Plan): Observable<Plan> {
    return this.http.post<Plan>(this.apiUrl, plan);
  }

  editarPlan(id: number, plan: Plan): Observable<Plan> {
    return this.http.put<Plan>(`${this.apiUrl}${id}/`, plan);
  }

  eliminarPlan(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }
}