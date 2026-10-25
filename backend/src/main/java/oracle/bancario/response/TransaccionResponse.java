package oracle.bancario.response;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import oracle.bancario.model.CuentaBancaria;
import oracle.bancario.model.Transaccion;

/** Salida publica de una transaccion. */
public record TransaccionResponse(
        Long id,
        String referencia,
        Long cuentaOrigenId,
        String cuentaOrigenNumero,
        Long cuentaDestinoId,
        String cuentaDestinoNumero,
        String tipoTransaccion,
        BigDecimal monto,
        String estado,
        BigDecimal saldoOrigenPost,
        BigDecimal saldoDestinoPost,
        String descripcion,
        Long creadoPor,
        Long actualizadoPor,
        LocalDateTime creadoEn,
        LocalDateTime actualizadoEn) {

    public static TransaccionResponse of(Transaccion t) {
        CuentaBancaria origen = t.getCuentaOrigen();
        CuentaBancaria destino = t.getCuentaDestino();
        return new TransaccionResponse(
                t.getId(),
                t.getReferencia(),
                origen == null ? null : origen.getId(),
                origen == null ? null : origen.getNumeroCuenta(),
                destino == null ? null : destino.getId(),
                destino == null ? null : destino.getNumeroCuenta(),
                t.getTipoTransaccion(),
                t.getMonto(),
                t.getEstado(),
                t.getSaldoOrigenPost(),
                t.getSaldoDestinoPost(),
                t.getDescripcion(),
                t.getCreadoPor(),
                t.getActualizadoPor(),
                t.getCreadoEn(),
                t.getActualizadoEn());
    }
}
