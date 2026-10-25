package oracle.bancario.response;

import java.math.BigDecimal;
import java.util.List;

/** Indicadores del dashboard del panel de cuentas. */
public record CuentaDashboardResponse(
        Kpis kpis,
        List<Conteo> porTipo,
        List<CuentaResponse> recientes) {

    public record Kpis(
            long total,
            long activas,
            long inactivas,
            BigDecimal saldoTotal) {
    }

    public record Conteo(String etiqueta, long valor, BigDecimal saldo) {
    }
}
