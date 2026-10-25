import { Caso } from './caso.model';
import { Transaccion, TransaccionConteo } from './transaccion.model';

export interface AnalistaKpis {
  total: number;
  pendientes: number;
  aprobadas: number;
  rechazadas: number;
  casosAbiertos: number;
  autoAprobadas: number;
  montoAprobado: number;
  montoPendiente: number;
}

export interface AnalistaDashboard {
  kpis: AnalistaKpis;
  porEstado: TransaccionConteo[];
  porTipo: TransaccionConteo[];
  recientes: Transaccion[];
  casosRecientes: Caso[];
}
