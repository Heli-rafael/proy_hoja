export interface Plan {
  nombre: string;
  creditos_diarios: number;
  descripcion: string;
}

export interface Creditos {
  creditos_diarios: number;
  usados: number;
  restantes: number;
}

export interface User {
  id: number;
  username: string;
  email: string;
  plan: Plan;
  creditos: Creditos;
  password?: string;
  first_name?: string;
  last_name?: string;
  is_active?: boolean;
  estado?: boolean;
  is_staff?: boolean;
  is_superuser?: boolean;
  date_joined?: string;
  rol: string;
  last_login?: Date;
}