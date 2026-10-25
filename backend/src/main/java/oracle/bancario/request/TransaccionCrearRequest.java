package oracle.bancario.request;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;

/**
 * Registro de un movimiento. Cuando la operacion tiene cuenta destino, esta
 * puede ser de otro usuario y se identifica por numero. El estado inicial
 * depende del motor de reglas: APROBADA automaticamente o PENDIENTE para el
 * analista.
 */
public record TransaccionCrearRequest(
        Long cuentaOrigenId,

        Long cuentaDestinoId,

        @Size(max = 30, message = "El numero de cuenta destino no puede exceder 30 caracteres.")
        String cuentaDestinoNumero,

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
