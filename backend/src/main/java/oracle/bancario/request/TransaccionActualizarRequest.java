package oracle.bancario.request;

import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Digits;
import jakarta.validation.constraints.Pattern;
import jakarta.validation.constraints.Size;
import java.math.BigDecimal;

/**
 * Resolucion de un caso: cambiar monto, estado o concepto.
 * Solo accesible con el permiso RESOLVER_CASO.
 */
public record TransaccionActualizarRequest(
        @DecimalMin(value = "0.01", message = "El monto debe ser mayor que cero.")
        @Digits(integer = 16, fraction = 2, message = "El monto admite hasta 2 decimales.")
        BigDecimal monto,

        @Pattern(regexp = "(?i)PENDIENTE|APROBADA|RECHAZADA",
                message = "El estado debe ser PENDIENTE, APROBADA o RECHAZADA.")
        String estado,

        @Size(max = 255, message = "La descripcion no puede exceder 255 caracteres.")
        String descripcion) {
}
