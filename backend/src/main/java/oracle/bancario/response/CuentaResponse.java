package oracle.bancario.response;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import oracle.bancario.model.CuentaBancaria;

/** Salida publica de una cuenta bancaria. */
public record CuentaResponse(
        Long id,
        String numeroCuenta,
        Long usuarioId,
        String titular,
        String tipoCuenta,
        BigDecimal saldo,
        Boolean activo,
        LocalDateTime creadoEn,
        LocalDateTime actualizadoEn,
        Long actualizadoPor) {

    public static CuentaResponse of(CuentaBancaria cuenta) {
        String titular = cuenta.getUsuario() == null
                ? null
                : (cuenta.getUsuario().getNombre() + " " + cuenta.getUsuario().getApellido()).trim();
        return new CuentaResponse(
                cuenta.getId(),
                cuenta.getNumeroCuenta(),
                cuenta.getUsuario() == null ? null : cuenta.getUsuario().getId(),
                titular,
                cuenta.getTipoCuenta(),
                cuenta.getSaldo(),
                cuenta.getActivo(),
                cuenta.getCreadoEn(),
                cuenta.getActualizadoEn(),
                cuenta.getActualizadoPor());
    }
}
