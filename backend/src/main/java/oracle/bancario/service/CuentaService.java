package oracle.bancario.service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.security.SecureRandom;
import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import oracle.admin.model.Usuario;
import oracle.admin.repository.UsuarioRepository;
import oracle.bancario.model.CuentaBancaria;
import oracle.bancario.repository.CuentaBancariaRepository;
import oracle.bancario.request.CuentaActualizarRequest;
import oracle.bancario.request.CuentaCrearRequest;
import oracle.bancario.response.CuentaDashboardResponse;
import oracle.bancario.response.CuentaResponse;
import oracle.common.config.Transacciones;
import oracle.common.exception.ConflictoException;
import oracle.common.exception.NoAutorizadoException;
import oracle.common.exception.RecursoNoEncontradoException;
import oracle.common.response.ApiResponse;
import oracle.common.security.AutorizacionCache;
import oracle.common.support.ActorActual;
import oracle.common.support.Listas;
import oracle.common.support.Trazas;
import org.springframework.stereotype.Service;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

/**
 * CRUD de cuentas bancarias con alcance por titular:
 * un usuario normal solo ve y opera sus propias cuentas; el administrador
 * (permiso PANEL_ADMIN) ve todas. Activar/desactivar queda fuera del CRUD y
 * se expone en un endpoint aparte con su propio permiso.
 */
@Slf4j
@Service
public class CuentaService {

    private static final List<String> TIPOS = List.of("AHORRO", "CORRIENTE", "EMPRESARIAL");
    private static final SecureRandom RANDOM = new SecureRandom();

    private final CuentaBancariaRepository cuentaRepository;
    private final UsuarioRepository usuarioRepository;
    private final AutorizacionCache autorizacionCache;
    private final Transacciones transacciones;

    public CuentaService(
            CuentaBancariaRepository cuentaRepository,
            UsuarioRepository usuarioRepository,
            AutorizacionCache autorizacionCache,
            Transacciones transacciones) {
        this.cuentaRepository = cuentaRepository;
        this.usuarioRepository = usuarioRepository;
        this.autorizacionCache = autorizacionCache;
        this.transacciones = transacciones;
    }

    public Mono<ApiResponse<List<CuentaResponse>>> listar() {
        Long actor = ActorActual.id();
        return Mono.fromCallable(() -> Trazas.medir(log, "CuentaService.listar", () ->
                        transacciones.consultar(() -> listarCuentas(actor).stream()
                                .map(CuentaResponse::of)
                                .toList())))
                .subscribeOn(Schedulers.boundedElastic())
                .map(lista -> ApiResponse.ok("Cuentas listadas.", lista));
    }

    public Mono<ApiResponse<CuentaResponse>> obtener(Long id) {
        Long actor = ActorActual.id();
        return Mono.fromCallable(() -> Trazas.medir(log, "CuentaService.obtener id=" + id, () ->
                        transacciones.consultar(() ->
                                ApiResponse.ok("Cuenta encontrada.", CuentaResponse.of(obtenerCuenta(id, actor))))))
                .subscribeOn(Schedulers.boundedElastic());
    }

    public Mono<ApiResponse<CuentaResponse>> crear(CuentaCrearRequest peticion) {
        Long actor = ActorActual.id();
        return Mono.fromCallable(() -> Trazas.medir(log, "CuentaService.crear", () ->
                        transacciones.ejecutar(() -> {
                            Usuario titular = usuarioRepository.findById(actor)
                                    .orElseThrow(() -> new NoAutorizadoException("La sesion ya no es valida."));

                            String numero = normalizarNumero(peticion.numeroCuenta());
                            if (numero == null) {
                                numero = generarNumeroCuenta();
                            } else if (cuentaRepository.existsByNumeroCuenta(numero)) {
                                throw new ConflictoException(
                                        "Ya existe una cuenta con el numero '" + numero + "'.");
                            }

                            LocalDateTime ahora = LocalDateTime.now();
                            CuentaBancaria cuenta = new CuentaBancaria();
                            cuenta.setNumeroCuenta(numero);
                            cuenta.setUsuario(titular);
                            cuenta.setTipoCuenta(peticion.tipoCuenta().trim().toUpperCase());
                            cuenta.setSaldo(escalar(peticion.saldo()));
                            cuenta.setActivo(Boolean.TRUE);
                            cuenta.setActualizadoPor(actor);
                            cuenta.setCreadoEn(ahora);
                            cuenta.setActualizadoEn(ahora);
                            cuentaRepository.save(cuenta);

                            return ApiResponse.ok("Cuenta creada.", CuentaResponse.of(cuenta));
                        })))
                .subscribeOn(Schedulers.boundedElastic());
    }

    public Mono<ApiResponse<CuentaResponse>> actualizar(Long id, CuentaActualizarRequest peticion) {
        Long actor = ActorActual.id();
        return Mono.fromCallable(() -> Trazas.medir(log, "CuentaService.actualizar id=" + id, () ->
                        transacciones.ejecutar(() -> {
                            CuentaBancaria cuenta = obtenerCuenta(id, actor);

                            String numero = normalizarNumero(peticion.numeroCuenta());
                            if (numero != null && !numero.equals(cuenta.getNumeroCuenta())) {
                                if (cuentaRepository.existsByNumeroCuentaAndIdNot(numero, id)) {
                                    throw new ConflictoException(
                                            "Ya existe otra cuenta con el numero '" + numero + "'.");
                                }
                                cuenta.setNumeroCuenta(numero);
                            }
                            if (peticion.tipoCuenta() != null) {
                                cuenta.setTipoCuenta(peticion.tipoCuenta().trim().toUpperCase());
                            }
                            if (peticion.saldo() != null) {
                                cuenta.setSaldo(escalar(peticion.saldo()));
                            }
                            cuenta.setActualizadoPor(actor);
                            cuenta.setActualizadoEn(LocalDateTime.now());
                            cuentaRepository.save(cuenta);

                            return ApiResponse.ok("Cuenta actualizada.", CuentaResponse.of(cuenta));
                        })))
                .subscribeOn(Schedulers.boundedElastic());
    }

    public Mono<ApiResponse<Void>> eliminar(Long id) {
        Long actor = ActorActual.id();
        return Mono.<Void>fromRunnable(() -> Trazas.medir(log, "CuentaService.eliminar id=" + id, () ->
                        transacciones.ejecutar(() -> {
                            CuentaBancaria cuenta = obtenerCuenta(id, actor);
                            cuentaRepository.delete(cuenta);
                            return null;
                        })))
                .subscribeOn(Schedulers.boundedElastic())
                .then(Mono.fromSupplier(() -> ApiResponse.<Void>ok("Cuenta eliminada.", null)));
    }

    public Mono<ApiResponse<CuentaResponse>> cambiarActivo(Long id, boolean activo) {
        Long actor = ActorActual.id();
        return Mono.fromCallable(() -> Trazas.medir(log, "CuentaService.cambiarActivo id=" + id, () ->
                        transacciones.ejecutar(() -> {
                            CuentaBancaria cuenta = obtenerCuenta(id, actor);
                            cuenta.setActivo(activo);
                            cuenta.setActualizadoPor(actor);
                            cuenta.setActualizadoEn(LocalDateTime.now());
                            cuentaRepository.save(cuenta);
                            return ApiResponse.ok(activo ? "Cuenta activada." : "Cuenta desactivada.",
                                    CuentaResponse.of(cuenta));
                        })))
                .subscribeOn(Schedulers.boundedElastic());
    }

    public Mono<ApiResponse<CuentaDashboardResponse>> dashboard() {
        Long actor = ActorActual.id();
        return Mono.fromCallable(() -> Trazas.medir(log, "CuentaService.dashboard", () ->
                        transacciones.consultar(() -> {
                            List<CuentaBancaria> cuentas = listarCuentas(actor);

                            long activas = cuentas.stream().filter(c -> Boolean.TRUE.equals(c.getActivo())).count();
                            BigDecimal saldoTotal = cuentas.stream()
                                    .map(CuentaBancaria::getSaldo)
                                    .reduce(BigDecimal.ZERO, BigDecimal::add);
                            CuentaDashboardResponse.Kpis kpis = new CuentaDashboardResponse.Kpis(
                                    cuentas.size(), activas, cuentas.size() - activas, saldoTotal);

                            Map<String, List<CuentaBancaria>> agrupadas = new LinkedHashMap<>();
                            for (String tipo : TIPOS) {
                                agrupadas.put(tipo, new ArrayList<>());
                            }
                            for (CuentaBancaria cuenta : cuentas) {
                                agrupadas.computeIfAbsent(cuenta.getTipoCuenta(), k -> new ArrayList<>()).add(cuenta);
                            }
                            List<CuentaDashboardResponse.Conteo> porTipo = agrupadas.entrySet().stream()
                                    .filter(entrada -> !entrada.getValue().isEmpty())
                                    .map(entrada -> new CuentaDashboardResponse.Conteo(
                                            entrada.getKey(),
                                            entrada.getValue().size(),
                                            entrada.getValue().stream()
                                                    .map(CuentaBancaria::getSaldo)
                                                    .reduce(BigDecimal.ZERO, BigDecimal::add)))
                                    .toList();

                            List<CuentaResponse> recientes = cuentas.stream()
                                    .sorted(Comparator.comparing(CuentaBancaria::getCreadoEn).reversed())
                                    .limit(5)
                                    .map(CuentaResponse::of)
                                    .toList();

                            return ApiResponse.ok("Dashboard de cuentas.",
                                    new CuentaDashboardResponse(kpis, porTipo, recientes));
                        })))
                .subscribeOn(Schedulers.boundedElastic());
    }

    private List<CuentaBancaria> listarCuentas(Long actor) {
        List<CuentaBancaria> cuentas = esAdministrador(actor)
                ? cuentaRepository.findAllByOrderByCreadoEnDesc(Listas.limitado())
                : cuentaRepository.findByUsuarioIdOrderByCreadoEnDesc(actor, Listas.limitado());
        Listas.avisarSiCorto(log, cuentas.size(), "CuentaService.listarCuentas");
        return cuentas;
    }

    private CuentaBancaria obtenerCuenta(Long id, Long actor) {
        if (esAdministrador(actor)) {
            return cuentaRepository.findById(id)
                    .orElseThrow(() -> new RecursoNoEncontradoException("No existe la cuenta con id " + id + "."));
        }
        return cuentaRepository.findByIdAndUsuarioId(id, actor)
                .orElseThrow(() -> new RecursoNoEncontradoException("No existe la cuenta con id " + id + "."));
    }

    private boolean esAdministrador(Long actor) {
        return autorizacionCache.cargar(actor).autoridades().stream()
                .anyMatch(autoridad -> "PANEL_ADMIN".equals(autoridad.getAuthority()));
    }

    private String normalizarNumero(String numero) {
        if (numero == null) {
            return null;
        }
        String limpio = numero.trim();
        return limpio.isEmpty() ? null : limpio;
    }

    private String generarNumeroCuenta() {
        for (int intento = 0; intento < 20; intento++) {
            String numero = "001-" + String.format("%010d", RANDOM.nextLong(10_000_000_000L));
            if (!cuentaRepository.existsByNumeroCuenta(numero)) {
                return numero;
            }
        }
        throw new ConflictoException("No se pudo generar un numero de cuenta unico. Intente de nuevo.");
    }

    private BigDecimal escalar(BigDecimal valor) {
        return valor == null ? BigDecimal.ZERO : valor.setScale(2, RoundingMode.HALF_UP);
    }
}
