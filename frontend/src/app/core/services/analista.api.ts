import { Service, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { AnalistaDashboard, Caso, Transaccion, TransaccionFiltro } from '../models';
import { Api } from './api';

@Service()
export class AnalistaApi {
  private readonly api = inject(Api);

  transacciones(filtro: TransaccionFiltro = {}): Observable<Transaccion[]> {
    return this.api.get<Transaccion[]>('/analista/transacciones', {
      estado: filtro.estado,
      tipo: filtro.tipo,
    });
  }

  casos(estado?: string): Observable<Caso[]> {
    return this.api.get<Caso[]>('/analista/casos', { estado });
  }

  dashboard(): Observable<AnalistaDashboard> {
    return this.api.get<AnalistaDashboard>('/analista/dashboard');
  }
}
