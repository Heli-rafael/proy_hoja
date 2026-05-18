import { PlantaModel } from "./planta.model";

export interface DiagnosticoIAModel {
  id?: number;
  usuario: number;
  planta: PlantaModel;
  imagen: string;
  enfermedad_detectada: string;
  severidad: string;
  porcentaje_salud: number;
  confianza_ia: number;
  tratamiento: string;
  como_prevenir: string;
  creado_en?: string | Date;
}