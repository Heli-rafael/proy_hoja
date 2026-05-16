import { MensajeModel } from "./mensaje.model";

export interface ChatModel {
  id?: number;
  usuario: number;
  titulo: string;
  diagnostico: number; // ID del DiagnosticoIA relacionado
  mensajes?: MensajeModel[]; // Opcional, para cuando traes el chat con sus mensajes
  creado_en?: Date;
}