import { PlantaModel } from "./planta.model";
import { ActividadTratamientoModel } from "./actividad-tratamiento";

export interface BBoxModel {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

export interface LesionDetectadaModel {
  id: number;
  title: string;
  description: string;
  type: string;
  confidence: number;
  bbox: BBoxModel;
}

export interface DiagnosticoProgreso {
  id: number;
  progreso: number;
  estado_imagen: string;
}

// TRATAMIENTOS
export interface TratamientoProductoModel {
  producto: string;
  dosis: string;
  aplicacion: string;
  frecuencia: string;
}

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

  lesiones_detectadas: LesionDetectadaModel[];

  // JSONField → arrays en Angular
  tratamiento_natural: TratamientoProductoModel[];
  tratamiento_quimico: TratamientoProductoModel[];
  prevencion: string[];

  sintomas_detectados: string[];
  prediccion_evolucion: string[];
  plagas_relacionadas: string[];

  factores_climaticos_favorables: Record<string, any>;

  urgencia: string;
  contagio: string;
  recuperacion: string;
  etapa: string;

  actividades?: ActividadTratamientoModel[];

  creado_en?: string | Date;
  progreso?: number;
}