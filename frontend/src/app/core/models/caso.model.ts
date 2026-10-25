import { Transaccion } from './transaccion.model';

export type EstadoCaso = 'ABIERTO' | 'EN_REVISION' | 'RESUELTO' | 'CERRADO' | 'RECHAZADO';

export interface Caso {
  id: number;
  numeroCaso: string;
  estado: EstadoCaso | string;
  cuentaOrigenNumero: string | null;
  cuentaDestinoNumero: string | null;
  transaccion: Transaccion;
  creadoEn: string;
  actualizadoEn: string;
}
