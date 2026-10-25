package oracle.bancario.request;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Pattern;
import java.math.BigDecimal;

/** Apertura de cuenta. El numero puede omitirse para generarlo automaticamente. */
public record CuentaCrearRequest(
        @Pattern(regexp = "^$|^[0-9-]{6,30}$",
                message = "El numero de cuenta debe tener entre 6 y 30 digitos o guiones.")
        String numeroCuenta,

        @NotBlank(message = "El tipo de cuenta es obligatorio.")
        @Pattern(regexp = "(?i)AHORRO|CORRIENTE|EMPRESARIAL",
                message = "El tipo de cuenta debe ser AHORRO, CORRIENTE o EMPRESARIAL.")
        String tipoCuenta,

        @DecimalMin(value = "0.00", message = "El saldo inicial no puede ser negativo.")
        @Digits(integer = 16, fraction = 2, message = "El saldo admite hasta 2 decimales.")
        BigDecimal saldo) {
}
