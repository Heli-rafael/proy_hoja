export type TipoMensaje = 'usuario' | 'ia';

export interface MensajeModel {
  id?: number;
  chat: number;
  tipo: TipoMensaje;
  texto: string;
  creado_en?: Date;
}