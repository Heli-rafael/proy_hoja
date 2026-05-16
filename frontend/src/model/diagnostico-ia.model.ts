export type Severidad = 'leve' | 'moderada' | 'grave';

export interface DiagnosticoIAModel {
  id?: number;
  usuario: number; // Generalmente se envía el ID del usuario
  planta: number | null;
  imagen: string;
  enfermedad_detectada: string;
  severidad: Severidad;
  porcentaje_salud: number;
  confianza_ia: number;
  tratamiento: string;
  como_prevenir: string;
  creado_en?: Date;
}