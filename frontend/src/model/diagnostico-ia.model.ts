import { PlantaModel } from "./planta.model";

export interface DiagnosticoIAModel {
  id?: number;
  usuario: number;
  planta: PlantaModel;
  imagen: string;
  estado_imagen: string;
  enfermedad_detectada: string;
  severidad: string;
  porcentaje_salud: number;
  confianza_ia: number;
  tratamiento_natural: string;
  tratamiento_quimico: string;
  prevencion: string;
  creado_en?: string | Date;
}