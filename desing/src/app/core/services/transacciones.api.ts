import { Service, inject } from '@angular/core';
import { Observable } from 'rxjs';
import {
  Transaccion,
  TransaccionActualizarRequest,
  TransaccionCrearRequest,
  TransaccionDashboard,
  TransaccionFiltro,
} from '../models';
import { Api } from './api';

@Service()
export class TransaccionesApi {
  private readonly api = inject(Api);

  listar(filtro: TransaccionFiltro = {}): Observable<Transaccion[]> {
    return this.api.get<Transaccion[]>('/transacciones', { ...filtro });
  }

  crear(peticion: TransaccionCrearRequest): Observable<Transaccion> {
    return this.api.post<Transaccion>('/transacciones', peticion);
  }

  actualizar(id: number, peticion: TransaccionActualizarRequest): Observable<Transaccion> {
    return this.api.put<Transaccion>(`/transacciones/${id}`, peticion);
  }

  eliminar(id: number): Observable<void> {
    return this.api.delete<void>(`/transacciones/${id}`);
  }

  dashboard(): Observable<TransaccionDashboard> {
    return this.api.get<TransaccionDashboard>('/transacciones/dashboard');
  }
}
