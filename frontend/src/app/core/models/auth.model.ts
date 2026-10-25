import { Usuario } from './usuario.model';

export interface LoginRequest {
  usuario: string;
  contrasena: string;
}

export interface RegistroRequest {
  usuario: string;
  contrasena: string;
  nombre: string;
  apellido: string;
  email: string;
  telefono?: string | null;
}

export interface AuthResponse {
  token: string;
  tipo: string;
  expiraEn: string;
  usuario: Usuario;
  permisos: string[];
}

export interface Sesion {
  token: string;
  tipo: string;
  expiraEn: string;
  usuario: Usuario;
  permisos: string[];
}
