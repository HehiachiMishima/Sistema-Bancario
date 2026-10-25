export type TipoTransaccion = 'DEPOSITO' | 'RETIRO' | 'TRANSFERENCIA' | 'PAGO';
export type EstadoTransaccion = 'PENDIENTE' | 'APROBADA' | 'RECHAZADA';

export interface ReglaEvaluada {
  regla: string;
  titulo: string;
  aprobada: boolean;
  detalle: string;
}

export interface Transaccion {
  id: number;
  referencia: string;
  cuentaOrigenId: number | null;
  cuentaOrigenNumero: string | null;
  cuentaOrigenTitular?: string | null;
  cuentaDestinoId: number | null;
  cuentaDestinoNumero: string | null;
  cuentaDestinoTitular?: string | null;
  tipoTransaccion: TipoTransaccion | string;
  monto: number;
  estado: EstadoTransaccion | string;
  saldoOrigenPost: number | null;
  saldoDestinoPost: number | null;
  descripcion: string | null;
  reglas?: ReglaEvaluada[];
  creadoPor: number;
  actualizadoPor: number;
  creadoEn: string;
  actualizadoEn: string;
}

export interface TransaccionCrearRequest {
  cuentaOrigenId?: number | null;
  cuentaDestinoId?: number | null;
  cuentaDestinoNumero?: string | null;
  tipoTransaccion: TipoTransaccion | string;
  monto: number;
  contrasena?: string | null;
  descripcion?: string | null;
}

export interface TransaccionActualizarRequest {
  monto?: number | null;
  estado?: EstadoTransaccion | string;
  descripcion?: string | null;
}

export interface TransaccionFiltro {
  estado?: string;
  tipo?: string;
  cuentaId?: number;
}

export interface TransaccionKpis {
  total: number;
  pendientes: number;
  aprobadas: number;
  rechazadas: number;
  montoAprobado: number;
  montoPendiente: number;
}

export interface TransaccionConteo {
  etiqueta: string;
  valor: number;
  monto: number;
}

export interface TransaccionDashboard {
  kpis: TransaccionKpis;
  porEstado: TransaccionConteo[];
  porTipo: TransaccionConteo[];
  recientes: Transaccion[];
}
