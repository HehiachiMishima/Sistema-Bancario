package oracle.bancario.service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.security.SecureRandom;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import oracle.bancario.model.Caso;
import oracle.bancario.model.CuentaBancaria;
import oracle.bancario.model.Transaccion;
import oracle.bancario.repository.CasoRepository;
import oracle.bancario.repository.CuentaBancariaRepository;
import oracle.bancario.repository.TransaccionRepository;
import oracle.bancario.request.TransaccionActualizarRequest;
import oracle.bancario.request.TransaccionCrearRequest;
import oracle.bancario.request.TransaccionFiltroRequest;
import oracle.bancario.response.TransaccionDashboardResponse;
import oracle.bancario.response.TransaccionResponse;
import oracle.common.config.Transacciones;
import oracle.common.exception.ConflictoException;
import oracle.common.exception.RecursoNoEncontradoException;
import oracle.common.response.ApiResponse;
import oracle.common.security.AutorizacionCache;
import oracle.common.support.ActorActual;
import oracle.common.support.Auditoria;
import oracle.common.support.Filtros;
import oracle.common.support.Listas;
import oracle.common.support.Trazas;
import org.springframework.stereotype.Service;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

/**
 * Movimientos financieros.
 *
 * - El usuario registra movimientos. Las transferencias/pagos entre cuentas de
 *   usuarios USUARIO pasan por el motor de reglas: si cumplen, se aprueban y
 *   aplican saldos automaticamente; si no, quedan PENDIENTES y abren un caso.
 * - Solo quien tiene RESOLVER_CASO puede modificarlos, aprobarlos o eliminarlos.
 * - Al aprobar se aplican los saldos; al rechazar o eliminar una transaccion
 *   aprobada se revierte el efecto. Todo ocurre dentro de una transaccion SQL
 *   con bloqueo pesimista de las cuentas implicadas.
 */
@Slf4j
@Service
public class TransaccionService {

    private static final List<String> ESTADOS = List.of("PENDIENTE", "APROBADA", "RECHAZADA");
    private static final List<String> TIPOS = List.of("DEPOSITO", "RETIRO", "TRANSFERENCIA", "PAGO");
    private static final SecureRandom RANDOM = new SecureRandom();
    private static final DateTimeFormatter FECHA_REFERENCIA = DateTimeFormatter.BASIC_ISO_DATE;

    private final TransaccionRepository transaccionRepository;
    private final CuentaBancariaRepository cuentaRepository;
    private final CasoRepository casoRepository;
    private final AutorizacionCache autorizacionCache;
    private final ReglasService reglasService;
    private final Transacciones transacciones;

    public TransaccionService(
            TransaccionRepository transaccionRepository,
            CuentaBancariaRepository cuentaRepository,
            CasoRepository casoRepository,
            AutorizacionCache autorizacionCache,
            ReglasService reglasService,
            Transacciones transacciones) {
        this.transaccionRepository = transaccionRepository;
        this.cuentaRepository = cuentaRepository;
        this.casoRepository = casoRepository;
        this.autorizacionCache = autorizacionCache;
        this.reglasService = reglasService;
        this.transacciones = transacciones;
    }

    public Mono<ApiResponse<List<TransaccionResponse>>> listar(TransaccionFiltroRequest filtro) {
        Long actor = ActorActual.id();
        String estado = normalizarFiltro(filtro.estado());
        String tipo = normalizarFiltro(filtro.tipo());
        return Mono.fromCallable(() -> Trazas.medir(log, "TransaccionService.listar", () ->
                        transacciones.consultar(() -> {
                            List<Transaccion> lista = transaccionRepository.buscar(
                                    actor, verTodas(actor), estado, tipo, filtro.cuentaId());
                            Listas.avisarSiCorto(log, lista.size(), "TransaccionService.listar");
                            return lista.stream().map(TransaccionResponse::of).toList();
                        })))
                .subscribeOn(Schedulers.boundedElastic())
                .map(lista -> ApiResponse.ok("Movimientos listados.", lista));
    }

    public Mono<ApiResponse<TransaccionDashboardResponse>> dashboard() {
        Long actor = ActorActual.id();
        return Mono.fromCallable(() -> Trazas.medir(log, "TransaccionService.dashboard", () ->
                        transacciones.consultar(() -> {
                            List<Transaccion> lista = transaccionRepository.buscar(
                                    actor, verTodas(actor), null, null, null);
                            Listas.avisarSiCorto(log, lista.size(), "TransaccionService.dashboard");

                            long pendientes = contar(lista, "PENDIENTE");
                            long aprobadas = contar(lista, "APROBADA");
                            long rechazadas = contar(lista, "RECHAZADA");
                            TransaccionDashboardResponse.Kpis kpis = new TransaccionDashboardResponse.Kpis(
                                    lista.size(),
                                    pendientes,
                                    aprobadas,
                                    rechazadas,
                                    montoDe(lista, "APROBADA"),
                                    montoDe(lista, "PENDIENTE"));

                            List<TransaccionDashboardResponse.Conteo> porEstado = ESTADOS.stream()
                                    .map(estado -> new TransaccionDashboardResponse.Conteo(
                                            estado, contar(lista, estado), montoDe(lista, estado)))
                                    .toList();
                            List<TransaccionDashboardResponse.Conteo> porTipo = TIPOS.stream()
                                    .map(tipo -> new TransaccionDashboardResponse.Conteo(
                                            tipo,
                                            lista.stream().filter(t -> tipo.equals(t.getTipoTransaccion())).count(),
                                            lista.stream()
                                                    .filter(t -> tipo.equals(t.getTipoTransaccion()))
                                                    .map(Transaccion::getMonto)
                                                    .reduce(BigDecimal.ZERO, BigDecimal::add)))
                                    .toList();

                            List<TransaccionResponse> recientes = lista.stream()
                                    .limit(5)
                                    .map(TransaccionResponse::of)
                                    .toList();

                            return ApiResponse.ok("Dashboard de transacciones.",
                                    new TransaccionDashboardResponse(kpis, porEstado, porTipo, recientes));
                        })))
                .subscribeOn(Schedulers.boundedElastic());
    }

    public Mono<ApiResponse<TransaccionResponse>> crear(TransaccionCrearRequest peticion) {
        Long actor = ActorActual.id();
        return Mono.fromCallable(() -> Trazas.medir(log, "TransaccionService.crear", () ->
                        transacciones.ejecutar(() -> {
                            String tipo = peticion.tipoTransaccion().trim().toUpperCase();
                            boolean privilegiado = verTodas(actor);
                            CuentaBancaria origen = cargarCuentaOperable(
                                    peticion.cuentaOrigenId(), actor, privilegiado);
                            CuentaBancaria destino = cargarDestino(
                                    peticion, actor, privilegiado);
                            validarCombinacion(tipo, origen, destino);
                            validarActiva(origen, "origen");
                            validarActiva(destino, "destino");

                            Transaccion transaccion = new Transaccion();
                            transaccion.setReferencia(generarReferencia());
                            transaccion.setCuentaOrigen(origen);
                            transaccion.setCuentaDestino(destino);
                            transaccion.setTipoTransaccion(tipo);
                            transaccion.setMonto(escalar(peticion.monto()));
                            transaccion.setEstado("PENDIENTE");
                            transaccion.setDescripcion(descripcion(peticion.descripcion()));

                            ReglasService.Resultado evaluacion =
                                    reglasService.evaluar(transaccion, origen, destino);
                            evaluacion.reglas().forEach(regla -> regla.setTransaccion(transaccion));
                            transaccion.setReglas(new ArrayList<>(evaluacion.reglas()));
                            if (evaluacion.aprobada()) {
                                transaccion.setEstado("APROBADA");
                                aplicar(transaccion, origen, destino, actor);
                            }

                            Auditoria.alCrear(transaccion, actor);
                            transaccionRepository.save(transaccion);

                            if (!"APROBADA".equals(transaccion.getEstado())) {
                                abrirCaso(transaccion, actor);
                                return ApiResponse.ok(
                                        "Movimiento registrado. Queda pendiente de resolucion.",
                                        TransaccionResponse.of(transaccion));
                            }

                            return ApiResponse.ok(
                                    "Movimiento aprobado automaticamente: cumplio las reglas de evaluacion.",
                                    TransaccionResponse.of(transaccion));
                        })))
                .subscribeOn(Schedulers.boundedElastic());
    }

    public Mono<ApiResponse<TransaccionResponse>> actualizar(Long id, TransaccionActualizarRequest peticion) {
        Long actor = ActorActual.id();
        return Mono.fromCallable(() -> Trazas.medir(log, "TransaccionService.actualizar id=" + id, () ->
                        transacciones.ejecutar(() -> {
                            Transaccion transaccion = transaccionRepository.cargar(id)
                                    .orElseThrow(() -> new RecursoNoEncontradoException(
                                            "No existe la transaccion con id " + id + "."));
                            CuentaBancaria origen = bloquear(transaccion.getCuentaOrigen());
                            CuentaBancaria destino = bloquear(transaccion.getCuentaDestino());

                            String estadoAnterior = transaccion.getEstado();
                            BigDecimal montoAnterior = transaccion.getMonto();
                            String estadoNuevo = peticion.estado() == null
                                    ? estadoAnterior
                                    : peticion.estado().trim().toUpperCase();
                            BigDecimal montoNuevo = peticion.monto() == null
                                    ? montoAnterior
                                    : escalar(peticion.monto());

                            boolean estabaAprobada = "APROBADA".equals(estadoAnterior);
                            boolean quedaAprobada = "APROBADA".equals(estadoNuevo);
                            boolean cambiaMonto = montoNuevo.compareTo(montoAnterior) != 0;

                            if (estabaAprobada && (!quedaAprobada || cambiaMonto)) {
                                revertir(transaccion, origen, destino, actor);
                            }

                            transaccion.setMonto(montoNuevo);
                            if (peticion.descripcion() != null) {
                                transaccion.setDescripcion(descripcion(peticion.descripcion()));
                            }
                            transaccion.setEstado(estadoNuevo);

                            if (quedaAprobada && (!estabaAprobada || cambiaMonto)) {
                                aplicar(transaccion, origen, destino, actor);
                            }

                            Auditoria.alActualizar(transaccion, actor);
                            transaccionRepository.save(transaccion);
                            sincronizarCaso(transaccion, actor);

                            return ApiResponse.ok("Transaccion actualizada.", TransaccionResponse.of(transaccion));
                        })))
                .subscribeOn(Schedulers.boundedElastic());
    }

    public Mono<ApiResponse<Void>> eliminar(Long id) {
        Long actor = ActorActual.id();
        return Mono.<Void>fromRunnable(() -> Trazas.medir(log, "TransaccionService.eliminar id=" + id, () ->
                        transacciones.ejecutar(() -> {
                            Transaccion transaccion = transaccionRepository.cargar(id)
                                    .orElseThrow(() -> new RecursoNoEncontradoException(
                                            "No existe la transaccion con id " + id + "."));
                            CuentaBancaria origen = bloquear(transaccion.getCuentaOrigen());
                            CuentaBancaria destino = bloquear(transaccion.getCuentaDestino());
                            if ("APROBADA".equals(transaccion.getEstado())) {
                                revertir(transaccion, origen, destino, actor);
                            }
                            casoRepository.eliminarPorTransaccion(transaccion.getId());
                            transaccionRepository.delete(transaccion);
                            return null;
                        })))
                .subscribeOn(Schedulers.boundedElastic())
                .then(Mono.fromSupplier(() -> ApiResponse.<Void>ok("Transaccion eliminada.", null)));
    }

    private void aplicar(Transaccion transaccion, CuentaBancaria origen, CuentaBancaria destino, Long actor) {
        BigDecimal monto = transaccion.getMonto();
        if (origen != null) {
            if (origen.getSaldo().compareTo(monto) < 0) {
                throw new ConflictoException("Saldo insuficiente en la cuenta origen "
                        + origen.getNumeroCuenta() + " para aprobar el movimiento.");
            }
            origen.setSaldo(origen.getSaldo().subtract(monto));
            marcarCuenta(origen, actor);
            transaccion.setSaldoOrigenPost(origen.getSaldo());
        }
        if (destino != null) {
            destino.setSaldo(destino.getSaldo().add(monto));
            marcarCuenta(destino, actor);
            transaccion.setSaldoDestinoPost(destino.getSaldo());
        }
    }

    private void revertir(Transaccion transaccion, CuentaBancaria origen, CuentaBancaria destino, Long actor) {
        BigDecimal monto = transaccion.getMonto();
        if (origen != null) {
            origen.setSaldo(origen.getSaldo().add(monto));
            marcarCuenta(origen, actor);
        }
        if (destino != null) {
            destino.setSaldo(destino.getSaldo().subtract(monto));
            marcarCuenta(destino, actor);
        }
        transaccion.setSaldoOrigenPost(null);
        transaccion.setSaldoDestinoPost(null);
    }

    private void marcarCuenta(CuentaBancaria cuenta, Long actor) {
        cuenta.setActualizadoPor(actor);
        cuenta.setActualizadoEn(LocalDateTime.now());
        cuentaRepository.save(cuenta);
    }

    private CuentaBancaria bloquear(CuentaBancaria cuenta) {
        if (cuenta == null) {
            return null;
        }
        return cuentaRepository.bloquearPorId(cuenta.getId())
                .orElseThrow(() -> new RecursoNoEncontradoException(
                        "No existe la cuenta con id " + cuenta.getId() + "."));
    }

    private CuentaBancaria cargarDestino(
            TransaccionCrearRequest peticion, Long actor, boolean privilegiado) {
        String numero = Filtros.normalizar(peticion.cuentaDestinoNumero());
        if (numero != null) {
            return cuentaRepository.findByNumeroCuenta(numero)
                    .orElseThrow(() -> new RecursoNoEncontradoException(
                            "No existe la cuenta destino " + numero + "."));
        }
        return cargarCuentaOperable(peticion.cuentaDestinoId(), actor, privilegiado);
    }

    private void abrirCaso(Transaccion transaccion, Long actor) {
        if (casoRepository.findByTransaccionId(transaccion.getId()).isPresent()) {
            return;
        }
        LocalDateTime ahora = LocalDateTime.now();
        Caso caso = new Caso();
        caso.setNumeroCaso(generarNumeroCaso());
        caso.setTransaccion(transaccion);
        caso.setCuentaOrigenNumero(transaccion.getCuentaOrigen() == null
                ? null : transaccion.getCuentaOrigen().getNumeroCuenta());
        caso.setCuentaDestinoNumero(transaccion.getCuentaDestino() == null
                ? null : transaccion.getCuentaDestino().getNumeroCuenta());
        caso.setEstado("ABIERTO");
        caso.setActualizadoPor(actor);
        caso.setCreadoEn(ahora);
        caso.setActualizadoEn(ahora);
        casoRepository.save(caso);
    }

    private void sincronizarCaso(Transaccion transaccion, Long actor) {
        String estadoCaso = switch (transaccion.getEstado()) {
            case "APROBADA" -> "RESUELTO";
            case "RECHAZADA" -> "RECHAZADO";
            default -> "ABIERTO";
        };
        casoRepository.findByTransaccionId(transaccion.getId()).ifPresentOrElse(caso -> {
            caso.setEstado(estadoCaso);
            caso.setActualizadoPor(actor);
            caso.setActualizadoEn(LocalDateTime.now());
            casoRepository.save(caso);
        }, () -> {
            if ("PENDIENTE".equals(transaccion.getEstado())) {
                abrirCaso(transaccion, actor);
            }
        });
    }

    private String generarNumeroCaso() {
        for (int intento = 0; intento < 20; intento++) {
            String numero = "CASO-" + LocalDate.now().format(FECHA_REFERENCIA)
                    + "-" + String.format("%06d", RANDOM.nextInt(1_000_000));
            if (!casoRepository.existsByNumeroCaso(numero)) {
                return numero;
            }
        }
        throw new ConflictoException("No se pudo generar un numero de caso unico. Intente de nuevo.");
    }

    private CuentaBancaria cargarCuentaOperable(Long cuentaId, Long actor, boolean privilegiado) {
        if (cuentaId == null) {
            return null;
        }
        if (privilegiado) {
            return cuentaRepository.findById(cuentaId)
                    .orElseThrow(() -> new RecursoNoEncontradoException(
                            "No existe la cuenta con id " + cuentaId + "."));
        }
        return cuentaRepository.findByIdAndUsuarioId(cuentaId, actor)
                .orElseThrow(() -> new RecursoNoEncontradoException(
                        "No existe la cuenta con id " + cuentaId + "."));
    }

    private void validarCombinacion(String tipo, CuentaBancaria origen, CuentaBancaria destino) {
        switch (tipo) {
            case "DEPOSITO" -> {
                if (destino == null || origen != null) {
                    throw new ConflictoException(
                            "Un deposito requiere cuenta destino y no admite cuenta origen.");
                }
            }
            case "RETIRO" -> {
                if (origen == null || destino != null) {
                    throw new ConflictoException(
                            "Un retiro requiere cuenta origen y no admite cuenta destino.");
                }
            }
            case "TRANSFERENCIA", "PAGO" -> {
                if (origen == null || destino == null) {
                    throw new ConflictoException(
                            "Una " + tipo.toLowerCase() + " requiere cuenta origen y cuenta destino.");
                }
                if (origen.getId().equals(destino.getId())) {
                    throw new ConflictoException(
                            "La cuenta origen y la cuenta destino deben ser distintas.");
                }
            }
            default -> throw new ConflictoException("Tipo de transaccion no soportado: " + tipo + ".");
        }
    }

    private void validarActiva(CuentaBancaria cuenta, String lado) {
        if (cuenta != null && !Boolean.TRUE.equals(cuenta.getActivo())) {
            throw new ConflictoException(
                    "La cuenta " + lado + " " + cuenta.getNumeroCuenta() + " esta inactiva.");
        }
    }

    private String generarReferencia() {
        for (int intento = 0; intento < 20; intento++) {
            String referencia = "TX-" + LocalDate.now().format(FECHA_REFERENCIA)
                    + "-" + String.format("%06d", RANDOM.nextInt(1_000_000));
            if (!transaccionRepository.existsByReferencia(referencia)) {
                return referencia;
            }
        }
        throw new ConflictoException("No se pudo generar una referencia unica. Intente de nuevo.");
    }

    private boolean verTodas(Long actor) {
        return tienePermiso(actor, "PANEL_ADMIN") || tienePermiso(actor, "RESOLVER_CASO");
    }

    private boolean tienePermiso(Long actor, String permiso) {
        return autorizacionCache.cargar(actor).autoridades().stream()
                .anyMatch(autoridad -> permiso.equals(autoridad.getAuthority()));
    }

    private long contar(List<Transaccion> lista, String estado) {
        return lista.stream().filter(t -> estado.equals(t.getEstado())).count();
    }

    private BigDecimal montoDe(List<Transaccion> lista, String estado) {
        return lista.stream()
                .filter(t -> estado.equals(t.getEstado()))
                .map(Transaccion::getMonto)
                .reduce(BigDecimal.ZERO, BigDecimal::add);
    }

    private String normalizarFiltro(String valor) {
        String limpio = Filtros.normalizar(valor);
        return limpio == null ? null : limpio.toUpperCase();
    }

    private String descripcion(String valor) {
        String limpio = Filtros.normalizar(valor);
        return limpio;
    }

    private BigDecimal escalar(BigDecimal valor) {
        return valor == null ? BigDecimal.ZERO : valor.setScale(2, RoundingMode.HALF_UP);
    }
}
