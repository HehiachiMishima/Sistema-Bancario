package oracle.bancario.request;

import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.Pattern;
import java.math.BigDecimal;

/**
 * Edicion de cuenta. No incluye "activo": activar/desactivar es una accion
 * separada y reservada al permiso CAMBIAR_ESTADO_CUENTAS.
 */
public record CuentaActualizarRequest(
        @Pattern(regexp = "^$|^[0-9-]{6,30}$",
                message = "El numero de cuenta debe tener entre 6 y 30 digitos o guiones.")
        String numeroCuenta,

        @Pattern(regexp = "(?i)AHORRO|CORRIENTE|EMPRESARIAL",
                message = "El tipo de cuenta debe ser AHORRO, CORRIENTE o EMPRESARIAL.")
        String tipoCuenta,

        @Digits(integer = 16, fraction = 2, message = "El saldo admite hasta 2 decimales.")
        BigDecimal saldo) {
}
