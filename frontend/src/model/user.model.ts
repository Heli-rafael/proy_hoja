export interface User {
  id: number;
  username: string;
  email: string;
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