import { PERMISOS } from './permisos';

export interface ModuloPanel {
  id: string;
  nombre: string;
  descripcion: string;
  icono: string;
  ruta: string;
  permiso: string;
}

export interface PanelDef {
  id: string;
  nombre: string;
  descripcion: string;
  icono: string;
  ruta: string;
  permiso: string;
  acento: string;
  modulos: ModuloPanel[];
}

export const PANEL_ADMIN: PanelDef = {
  id: 'admin',
  nombre: 'Administración',
  descripcion: 'Gobierno de identidades, accesos y trazabilidad del sistema.',
  icono: 'shield',
  ruta: '/admin',
  permiso: PERMISOS.PANEL_ADMIN,
  acento: 'brand',
  modulos: [
    {
      id: 'dashboard',
      nombre: 'Dashboard',
      descripcion: 'Resumen operativo del control de accesos.',
      icono: 'dashboard',
      ruta: 'dashboard',
      permiso: PERMISOS.DASHBOARD_ADMIN,
    },
    {
      id: 'usuarios',
      nombre: 'Usuarios',
      descripcion: 'Altas, edición, estado y asignación de roles.',
      icono: 'usuarios',
      ruta: 'usuarios',
      permiso: PERMISOS.VER_USUARIOS,
    },
    {
      id: 'roles',
      nombre: 'Roles',
      descripcion: 'Roles y los permisos que conceden.',
      icono: 'roles',
      ruta: 'roles',
      permiso: PERMISOS.VER_ROLES,
    },
    {
      id: 'permisos',
      nombre: 'Permisos',
      descripcion: 'Catálogo de permisos del sistema.',
      icono: 'permisos',
      ruta: 'permisos',
      permiso: PERMISOS.VER_PERMISOS,
    },
  ],
}

export const PANEL_CUENTAS: PanelDef = {
  id: 'cuentas',
  nombre: 'Cuentas',
  descripcion: 'Apertura y gestión de cuentas bancarias.',
  icono: 'bank',
  ruta: '/cuentas',
  permiso: PERMISOS.PANEL_CUENTAS,
  acento: 'brand',
  modulos: [
    {
      id: 'dashboard',
      nombre: 'Dashboard',
      descripcion: 'Resumen de saldos y cuentas.',
      icono: 'dashboard',
      ruta: 'dashboard',
      permiso: PERMISOS.DASHBOARD_CUENTAS,
    },
    {
      id: 'cuentas',
      nombre: 'Cuentas',
      descripcion: 'Altas, edición y consulta de cuentas.',
      icono: 'wallet',
      ruta: 'cuentas',
      permiso: PERMISOS.VER_CUENTAS,
    },
  ],
};

export const PANEL_TRANSACCIONES: PanelDef = {
  id: 'transacciones',
  nombre: 'Transacciones',
  descripcion: 'Registro y seguimiento de movimientos financieros.',
  icono: 'transfer',
  ruta: '/transacciones',
  permiso: PERMISOS.PANEL_TRANSACCIONES,
  acento: 'accent',
  modulos: [
    {
      id: 'dashboard',
      nombre: 'Dashboard',
      descripcion: 'Resumen de movimientos y estados.',
      icono: 'dashboard',
      ruta: 'dashboard',
      permiso: PERMISOS.DASHBOARD_TRANSACCIONES,
    },
    {
      id: 'movimientos',
      nombre: 'Movimientos',
      descripcion: 'Altas y resolución de transacciones.',
      icono: 'transfer',
      ruta: 'movimientos',
      permiso: PERMISOS.VER_TRANSACCIONES,
    },
  ],
};

export const PANEL_ANALISTA: PanelDef = {
  id: 'analista',
  nombre: 'Analista',
  descripcion: 'Supervisión de movimientos y resolución de casos.',
  icono: 'analytics',
  ruta: '/analista',
  permiso: PERMISOS.PANEL_ANALISTA,
  acento: 'success',
  modulos: [
    {
      id: 'dashboard',
      nombre: 'Dashboard',
      descripcion: 'Resumen de movimientos, casos y aprobaciones automáticas.',
      icono: 'dashboard',
      ruta: 'dashboard',
      permiso: PERMISOS.DASHBOARD_TRANSACCIONES,
    },
    {
      id: 'transacciones',
      nombre: 'Transacciones',
      descripcion: 'Movimientos de todos los usuarios con rol USUARIO.',
      icono: 'transfer',
      ruta: 'transacciones',
      permiso: PERMISOS.VER_TRANSACCIONES,
    },
    {
      id: 'cuentas',
      nombre: 'Cuentas',
      descripcion: 'Consulta, edición y eliminación de las cuentas de todos los usuarios.',
      icono: 'wallet',
      ruta: 'cuentas',
      permiso: PERMISOS.VER_CUENTAS,
    },
    {
      id: 'casos',
      nombre: 'Casos',
      descripcion: 'Transacciones pendientes de revisión y resolución.',
      icono: 'alertTriangle',
      ruta: 'casos',
      permiso: PERMISOS.RESOLVER_CASO,
    },
  ],
};

export const PANELES: PanelDef[] = [PANEL_ADMIN, PANEL_CUENTAS, PANEL_TRANSACCIONES, PANEL_ANALISTA];

export function primerModuloAccesible(panel: PanelDef, permisos: readonly string[]): ModuloPanel | undefined {
  return panel.modulos.find((modulo) => permisos.includes(modulo.permiso));
}

export function tienePermiso(permisos: readonly string[], permiso: string): boolean {
  return permisos.includes(permiso);
}
