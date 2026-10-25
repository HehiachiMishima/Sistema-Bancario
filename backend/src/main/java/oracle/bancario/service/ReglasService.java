package oracle.bancario.service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.ArrayList;
import java.util.List;
import oracle.admin.repository.UsuarioRolRepository;
import oracle.bancario.model.CuentaBancaria;
import oracle.bancario.model.EvaluacionRegla;
import oracle.bancario.model.Transaccion;
import oracle.bancario.repository.TransaccionRepository;
import org.springframework.stereotype.Service;

/**
 * Motor de reglas para movimientos entre cuentas de usuarios con rol USUARIO.
 *
 * Se evalua el historial de la cuenta origen ANTES de guardar la transaccion
 * actual. La transaccion solo se aprueba sola si pasa las cuatro reglas y el
 * saldo alcanza; en cualquier otro caso queda PENDIENTE y se abre un caso.
 */
@Service
public class ReglasService {

    private static final BigDecimal FACTOR_MONTO = new BigDecimal("2.5");
    private static final BigDecimal UNO_PORCIENTO = new BigDecimal("0.01");
    private static final BigDecimal UMBRAL_MINIMO = new BigDecimal("0.01");
    private static final BigDecimal CIEN = BigDecimal.valueOf(100);

    private final TransaccionRepository transaccionRepository;
    private final UsuarioRolRepository usuarioRolRepository;

    public ReglasService(
            TransaccionRepository transaccionRepository,
            UsuarioRolRepository usuarioRolRepository) {
        this.transaccionRepository = transaccionRepository;
        this.usuarioRolRepository = usuarioRolRepository;
    }

    public record Resultado(boolean aplicable, boolean aprobada, List<EvaluacionRegla> reglas) {
    }

    public Resultado evaluar(Transaccion transaccion, CuentaBancaria origen, CuentaBancaria destino) {
        if (!esAplicable(transaccion, origen, destino)) {
            return new Resultado(false, false, List.of());
        }

        Long origenId = origen.getId();
        Long destinoId = destino.getId();
        BigDecimal monto = transaccion.getMonto();
        long total = transaccionRepository.countByCuentaOrigenId(origenId);
        long haciaDestino = transaccionRepository.countByCuentaOrigenIdAndCuentaDestinoId(origenId, destinoId);
        long delTipo = transaccionRepository.countByCuentaOrigenIdAndTipoTransaccion(
                origenId, transaccion.getTipoTransaccion());

        List<EvaluacionRegla> reglas = new ArrayList<>();

        boolean r1 = total > 0 && haciaDestino * 5 >= total;
        reglas.add(regla(1, "R1", "Recurrencia hacia el destino", r1,
                total == 0
                        ? "La cuenta origen aun no tiene historial de movimientos."
                        : "%d de %d movimientos del origen van a esta cuenta (%d%%).".formatted(
                                haciaDestino, total, porcentaje(haciaDestino, total))));

        boolean r2 = total > 0 && delTipo * 5 >= total;
        reglas.add(regla(2, "R2", "Recurrencia del tipo", r2,
                total == 0
                        ? "La cuenta origen aun no tiene historial de movimientos."
                        : "%d de %d movimientos del origen son %s (%d%%).".formatted(
                                delTipo, total, tipoLegible(transaccion.getTipoTransaccion()),
                                porcentaje(delTipo, total))));

        BigDecimal promedio = total == 0
                ? BigDecimal.ZERO
                : transaccionRepository.promedioMontoOrigen(origenId).setScale(2, RoundingMode.HALF_UP);
        BigDecimal limite = promedio.multiply(FACTOR_MONTO).setScale(2, RoundingMode.HALF_UP);
        boolean r3 = total > 0 && monto.compareTo(limite) <= 0;
        reglas.add(regla(3, "R3", "Monto vs promedio", r3,
                total == 0
                        ? "La cuenta origen aun no tiene historial de montos."
                        : "Monto %s frente al limite %s (promedio %s x 2.5).".formatted(
                                monto, limite, promedio)));

        BigDecimal saldo = origen.getSaldo() == null ? BigDecimal.ZERO : origen.getSaldo();
        BigDecimal umbral = saldo.abs().multiply(UNO_PORCIENTO).max(UMBRAL_MINIMO)
                .setScale(2, RoundingMode.HALF_UP);
        BigDecimal diferencia = monto.subtract(saldo).abs();
        boolean r4 = diferencia.compareTo(umbral) > 0;
        reglas.add(regla(4, "R4", "Intento de vaciado", r4,
                r4
                        ? "El monto %s se aleja del saldo %s (diferencia %s > umbral %s).".formatted(
                                monto, saldo, diferencia, umbral)
                        : "El monto %s deja la cuenta practicamente vacia (diferencia %s <= umbral %s).".formatted(
                                monto, diferencia, umbral)));

        boolean saldoSuficiente = saldo.compareTo(monto) >= 0;
        if (!saldoSuficiente) {
            reglas.add(regla(5, "SALDO", "Saldo suficiente", false,
                    "El saldo %s no cubre el monto %s.".formatted(saldo, monto)));
        }

        boolean aprobada = r1 && r2 && r3 && r4 && saldoSuficiente;
        return new Resultado(true, aprobada, reglas);
    }

    private boolean esAplicable(Transaccion transaccion, CuentaBancaria origen, CuentaBancaria destino) {
        if (!"TRANSFERENCIA".equals(transaccion.getTipoTransaccion())
                && !"PAGO".equals(transaccion.getTipoTransaccion())) {
            return false;
        }
        if (origen == null || destino == null
                || origen.getUsuario() == null || destino.getUsuario() == null) {
            return false;
        }
        return usuarioRolRepository.tieneRol(origen.getUsuario().getId(), "USUARIO")
                && usuarioRolRepository.tieneRol(destino.getUsuario().getId(), "USUARIO");
    }

    private EvaluacionRegla regla(int orden, String codigo, String titulo, boolean aprobada, String detalle) {
        EvaluacionRegla regla = new EvaluacionRegla();
        regla.setOrden(orden);
        regla.setRegla(codigo);
        regla.setTitulo(titulo);
        regla.setAprobada(aprobada);
        regla.setDetalle(detalle.length() > 255 ? detalle.substring(0, 255) : detalle);
        return regla;
    }

    private long porcentaje(long parte, long total) {
        return Math.round(parte * CIEN.doubleValue() / total);
    }

    private String tipoLegible(String tipo) {
        return switch (tipo) {
            case "DEPOSITO" -> "depositos";
            case "RETIRO" -> "retiros";
            case "TRANSFERENCIA" -> "transferencias";
            case "PAGO" -> "pagos";
            default -> tipo.toLowerCase();
        };
    }
}
