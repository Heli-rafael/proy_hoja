import { MensajeModel } from "./mensaje.model";
import { DiagnosticoIAModel } from "./diagnostico-ia.model";

export interface ChatModel {
  id?: number;
  usuario: number;
  titulo: string;
  diagnostico: DiagnosticoIAModel;
  mensajes?: MensajeModel[];
  creado_en?: string | Date;
}