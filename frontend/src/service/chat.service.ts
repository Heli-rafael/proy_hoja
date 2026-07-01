import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ApiConfig } from './auth/api.config';
import { Observable } from 'rxjs';
import { ChatModel } from '../model/chat.model';

@Injectable({
  providedIn: 'root'
})
export class ChatService {
  private apiUrl = `${ApiConfig.apiUrl}api/chat/`;

  constructor(private http: HttpClient) {}

  getMisChats(): Observable<ChatModel[]> {
    return this.http.get<ChatModel[]>(this.apiUrl);
  }

  getChatPorId(id: number): Observable<ChatModel> {
    return this.http.get<ChatModel>(`${this.apiUrl}${id}/`);
  }

  crearChat(diagnosticoId: number, titulo: string): Observable<ChatModel> {
    return this.http.post<ChatModel>(this.apiUrl, { diagnostico: diagnosticoId, titulo });
  }

  updateChatTitle(id: number, titulo: string) {
    return this.http.patch(`${this.apiUrl}${id}/`, {
      titulo
    });
  }

  eliminarChat(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}${id}/`);
  }

  // Fijar o des-fijar un chat
  togglePinned(id: number) {
    return this.http.post<ChatModel>(`${this.apiUrl}${id}/fijar/`, {});
  }

  // Exportar formatos
  exportChatsExcel() {
    return this.http.get(
      `${this.apiUrl}export/excel/`,
      { responseType: 'blob' }
    );
  }

}