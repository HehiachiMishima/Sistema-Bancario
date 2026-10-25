package oracle.bancario.request;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;

/**
 * Registro de un movimiento. El estado inicial siempre es PENDIENTE:
 * el usuario lo registra y el analista (RESOLVER_CASO) lo aprueba o rechaza.
 */
public record TransaccionCrearRequest(
        Long cuentaOrigenId,

        Long cuentaDestinoId,

        @NotBlank(message = "El tipo de transaccion es obligatorio.")
        @Pattern(regexp = "(?i)DEPOSITO|RETIRO|TRANSFERENCIA|PAGO",
                message = "El tipo debe ser DEPOSITO, RETIRO, TRANSFERENCIA o PAGO.")
        String tipoTransaccion,

        @NotNull(message = "El monto es obligatorio.")
        @DecimalMin(value = "0.01", message = "El monto debe ser mayor que cero.")
        @Digits(integer = 16, fraction = 2, message = "El monto admite hasta 2 decimales.")
        BigDecimal monto,

        @Size(max = 255, message = "La descripcion no puede exceder 255 caracteres.")
        String descripcion) {
}
