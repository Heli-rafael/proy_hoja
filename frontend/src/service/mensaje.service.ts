import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { MensajeModel } from '../model/mensaje.model';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class MensajeService {
  private apiUrl = `${environment.apiUrl}api/mensajes/`;

  constructor(private http: HttpClient) {}

  // Obtener mensajes de un chat específico
  getMensajesPorChat(chatId: number): Observable<MensajeModel[]> {
    return this.http.get<MensajeModel[]>(`${this.apiUrl}?chat=${chatId}`);
  }

  // Enviar un nuevo mensaje (normalmente de tipo 'usuario')
  enviarMensaje1(chatId: number, texto: string): Observable<MensajeModel> {
    const payload = {
      chat: chatId,
      texto: texto,
      tipo: 'usuario'
    };
    return this.http.post<MensajeModel>(this.apiUrl, payload);
    
  }

  obtenerMensajes(chatId: number) {
    return this.http.get<any[]>(
      `${this.apiUrl}chats/${chatId}/mensajes/`
    );
  }

  enviarMensaje(data: any) {
    return this.http.post(
      `${this.apiUrl}enviar/`,
      data
    );
  }
}