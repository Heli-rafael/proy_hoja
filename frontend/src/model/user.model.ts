export interface PlanModel {
  id: number;
  orden: number;
  nombre: string;
  creditos_diarios: number;
  beneficios: string[];
  estado: boolean;
  destacado: boolean;
}

export interface PlanPrecioModel {
  id: number;
  plan: PlanModel;
  periodo: "MENSUAL" | "ANUAL";
  precio: number;
}

export interface PlanCardModel {
  plan: PlanModel;
  precio: PlanPrecioModel;
}

export interface Creditos {
  creditos_diarios: number;
  usados: number;
  restantes: number;
}

export interface Suscripcion {
  inicio: string;
  fin: string;
  dias_restantes: number;
  horas_restantes: number;
  minutos_restantes: number;
}

export interface User {
  id: number;
  autenticacion: string;
  username: string;
  first_name?: string;
  last_name?: string;

  email: string;
  password?: string;

  state?: boolean;
  phone?: string;
  picture?: string;

  plan: PlanModel;
  creditos: Creditos;
  suscripcion?: Suscripcion | null;

  is_active?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
  date_joined?: string;
  last_login?: Date;
}