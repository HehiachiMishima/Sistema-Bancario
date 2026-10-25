package oracle.bancario.response;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import oracle.bancario.model.CuentaBancaria;
import oracle.bancario.model.EvaluacionRegla;
import oracle.bancario.model.Transaccion;

/** Salida publica de una transaccion. */
public record TransaccionResponse(
        Long id,
        String referencia,
        Long cuentaOrigenId,
        String cuentaOrigenNumero,
        String cuentaOrigenTitular,
        Long cuentaDestinoId,
        String cuentaDestinoNumero,
        String cuentaDestinoTitular,
        String tipoTransaccion,
        BigDecimal monto,
        String estado,
        BigDecimal saldoOrigenPost,
        BigDecimal saldoDestinoPost,
        String descripcion,
        List<ReglaResponse> reglas,
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
                titular(origen),
                destino == null ? null : destino.getId(),
                destino == null ? null : destino.getNumeroCuenta(),
                titular(destino),
                t.getTipoTransaccion(),
                t.getMonto(),
                t.getEstado(),
                t.getSaldoOrigenPost(),
                t.getSaldoDestinoPost(),
                t.getDescripcion(),
                t.getReglas().stream().map(ReglaResponse::of).toList(),
                t.getCreadoPor(),
                t.getActualizadoPor(),
                t.getCreadoEn(),
                t.getActualizadoEn());
    }

    private static String titular(CuentaBancaria cuenta) {
        if (cuenta == null || cuenta.getUsuario() == null) {
            return null;
        }
        String nombre = cuenta.getUsuario().getNombre();
        String apellido = cuenta.getUsuario().getApellido();
        return (nombre + " " + apellido).trim();
    }

    public record ReglaResponse(
            String regla,
            String titulo,
            boolean aprobada,
            String detalle) {

        public static ReglaResponse of(EvaluacionRegla evaluacion) {
            return new ReglaResponse(
                    evaluacion.getRegla(),
                    evaluacion.getTitulo(),
                    Boolean.TRUE.equals(evaluacion.getAprobada()),
                    evaluacion.getDetalle());
        }
    }
}
