const FORMATO_SOLES = new Intl.NumberFormat('es-PE', {
  style: 'currency',
  currency: 'PEN',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

/** Formatea un monto en soles (PEN) para las vistas bancarias. */
export function soles(valor: number | null | undefined): string {
  return FORMATO_SOLES.format(valor ?? 0);
}
