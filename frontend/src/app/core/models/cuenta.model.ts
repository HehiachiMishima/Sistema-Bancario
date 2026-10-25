export type TipoCuenta = 'AHORRO' | 'CORRIENTE' | 'EMPRESARIAL';

export interface CuentaBancaria {
  id: number;
  numeroCuenta: string;
  usuarioId: number;
  titular: string;
  tipoCuenta: TipoCuenta | string;
  saldo: number;
  activo: boolean;
  creadoEn: string;
  actualizadoEn: string;
  actualizadoPor: number;
}

export interface CuentaCrearRequest {
  numeroCuenta?: string | null;
  tipoCuenta: TipoCuenta | string;
  saldo?: number | null;
}

export interface CuentaActualizarRequest {
  numeroCuenta?: string | null;
  tipoCuenta?: TipoCuenta | string;
  saldo?: number | null;
}

export interface CuentaKpis {
  total: number;
  activas: number;
  inactivas: number;
  saldoTotal: number;
}

export interface CuentaConteo {
  etiqueta: string;
  valor: number;
  saldo: number;
}

export interface CuentaDashboard {
  kpis: CuentaKpis;
  porTipo: CuentaConteo[];
  recientes: CuentaBancaria[];
}
