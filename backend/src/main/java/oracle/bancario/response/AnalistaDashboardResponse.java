package oracle.bancario.response;

import java.math.BigDecimal;
import java.util.List;

/** Indicadores del panel de analista: movimientos de usuarios y casos. */
public record AnalistaDashboardResponse(
        Kpis kpis,
        List<Conteo> porEstado,
        List<Conteo> porTipo,
        List<TransaccionResponse> recientes,
        List<CasoResponse> casosRecientes) {

    public record Kpis(
            long total,
            long pendientes,
            long aprobadas,
            long rechazadas,
            long casosAbiertos,
            long autoAprobadas,
            BigDecimal montoAprobado,
            BigDecimal montoPendiente) {
    }

    public record Conteo(String etiqueta, long valor, BigDecimal monto) {
    }
}
