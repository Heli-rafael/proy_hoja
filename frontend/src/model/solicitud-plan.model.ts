import { PlanModel } from "./user.model";

export interface SolicitudCambioPlan {
    id?: number;
    usuario?: number;
    plan_actual?: PlanModel;
    plan_solicitado: PlanModel;
    metodo_pago: string;
    comprobante?: File;
    observacion?: string;
    estado:'PENDIENTE' | 'APROBADA' | 'RECHAZADA';
    creado_en?: string;
}