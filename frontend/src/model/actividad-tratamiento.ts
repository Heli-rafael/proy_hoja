export interface ActividadTratamientoModel {
  id?: number;

  diagnostico: number;

  actividad: string;
  tipo: string;
  semana: number;
  completada: boolean;
}