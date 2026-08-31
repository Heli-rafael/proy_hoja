import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PlanModel, PlanPrecioModel } from '../model/user.model';
import { environment } from '../environments/environment';
import { SolicitudCambioPlan } from '../model/solicitud-plan.model';

@Injectable({
  providedIn: 'root'
})
export class PlanService {

  private apiUrl = `${environment.apiUrl}api/plan/`;
  private apiPrecioUrl = `${environment.apiUrl}api/plan-precio/`;
  private solicitudUrl = `${environment.apiUrl}api/solicitud-plan/`;

  constructor(private http: HttpClient) {}

  /* PLANES */

  getPlanes(): Observable<PlanModel[]> {
    return this.http.get<PlanModel[]>(this.apiUrl);
  }

  getPlanPorId(id: number): Observable<PlanModel> {
    return this.http.get<PlanModel>(`${this.apiUrl}${id}/`);
  }

  agregarPlan(plan: PlanModel): Observable<PlanModel> {
    return this.http.post<PlanModel>(this.apiUrl, plan);
  }

  editarPlan(id: number, plan: PlanModel): Observable<PlanModel> {
    return this.http.put<PlanModel>(`${this.apiUrl}${id}/`, plan);
  }

  eliminarPlan(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }

  enviarSolicitudCambioPlan(formData: FormData): Observable<SolicitudCambioPlan>{
    return this.http.post<SolicitudCambioPlan>(this.solicitudUrl,formData);
  }

  /* PLANES */

  getPrecioPlanes(): Observable<PlanPrecioModel[]> {
    return this.http.get<PlanPrecioModel[]>(this.apiPrecioUrl);
  }


  /* SOLICITUDES DE CAMBIO  */

  obtenerSolicitudActual(): Observable<SolicitudCambioPlan[] | null>{
    return this.http.get<SolicitudCambioPlan[] | null>(`${this.solicitudUrl}`);
  }
}