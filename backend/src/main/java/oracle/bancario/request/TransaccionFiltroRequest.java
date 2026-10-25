package oracle.bancario.request;

/** Filtros opcionales del listado de movimientos. */
public record TransaccionFiltroRequest(
        String estado,
        String tipo,
        Long cuentaId) {
}
