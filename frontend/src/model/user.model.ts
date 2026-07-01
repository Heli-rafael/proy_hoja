export interface Plan {
  id: number;
  orden: number;
  nombre: string;
  precio: number;
  creditos_diarios: number;
  beneficios: string[];
  estado: boolean;
  destacado: boolean;
}

export interface Creditos {
  creditos_diarios: number;
  usados: number;
  restantes: number;
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

  plan: Plan;
  creditos: Creditos;

  is_active?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
  date_joined?: string;
  last_login?: Date;
}