import { Service, inject } from '@angular/core';
import { Observable } from 'rxjs';
import {
  CuentaActualizarRequest,
  CuentaBancaria,
  CuentaCrearRequest,
  CuentaDashboard,
} from '../models';
import { Api } from './api';

@Service()
export class CuentasApi {
  private readonly api = inject(Api);

  listar(): Observable<CuentaBancaria[]> {
    return this.api.get<CuentaBancaria[]>('/cuentas');
  }

  obtener(id: number): Observable<CuentaBancaria> {
    return this.api.get<CuentaBancaria>(`/cuentas/${id}`);
  }

  crear(peticion: CuentaCrearRequest): Observable<CuentaBancaria> {
    return this.api.post<CuentaBancaria>('/cuentas', peticion);
  }

  actualizar(id: number, peticion: CuentaActualizarRequest): Observable<CuentaBancaria> {
    return this.api.put<CuentaBancaria>(`/cuentas/${id}`, peticion);
  }

  eliminar(id: number): Observable<void> {
    return this.api.delete<void>(`/cuentas/${id}`);
  }

  cambiarActivo(id: number, activo: boolean): Observable<CuentaBancaria> {
    return this.api.patch<CuentaBancaria>(`/cuentas/${id}/activo`, { activo });
  }

  dashboard(): Observable<CuentaDashboard> {
    return this.api.get<CuentaDashboard>('/cuentas/dashboard');
  }
}
