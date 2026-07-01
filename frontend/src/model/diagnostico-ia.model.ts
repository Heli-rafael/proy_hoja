import { PlantaModel } from "./planta.model";
import { ActividadTratamientoModel } from "./actividad-tratamiento";

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

  // JSONField → arrays en Angular
  tratamiento_natural: string[];
  tratamiento_quimico: string[];
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
}