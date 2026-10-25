package oracle.bancario.response;

import java.math.BigDecimal;
import java.util.List;

/** Indicadores del dashboard del panel de transacciones. */
public record TransaccionDashboardResponse(
        Kpis kpis,
        List<Conteo> porEstado,
        List<Conteo> porTipo,
        List<TransaccionResponse> recientes) {

    public record Kpis(
            long total,
            long pendientes,
            long aprobadas,
            long rechazadas,
            BigDecimal montoAprobado,
            BigDecimal montoPendiente) {
    }

    public record Conteo(String etiqueta, long valor, BigDecimal monto) {
    }
}
