package oracle.bancario.service;

import java.math.BigDecimal;
import java.util.List;
import oracle.bancario.model.Caso;
import oracle.bancario.model.EvaluacionRegla;
import oracle.bancario.model.Transaccion;
import oracle.bancario.repository.CasoRepository;
import oracle.bancario.repository.TransaccionRepository;
import oracle.bancario.response.AnalistaDashboardResponse;
import oracle.bancario.response.CasoResponse;
import oracle.bancario.response.TransaccionResponse;
import oracle.common.config.Transacciones;
import oracle.common.response.ApiResponse;
import oracle.common.support.Filtros;
import oracle.common.support.Listas;
import oracle.common.support.Trazas;
import org.springframework.stereotype.Service;
import lombok.extern.slf4j.Slf4j;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

/** Consultas del panel de analista, sin escrituras propias. */
@Slf4j
@Service
public class AnalistaService {

    private static final List<String> ESTADOS = List.of("PENDIENTE", "APROBADA", "RECHAZADA");
    private static final List<String> TIPOS = List.of("DEPOSITO", "RETIRO", "TRANSFERENCIA", "PAGO");

    private final TransaccionRepository transaccionRepository;
    private final CasoRepository casoRepository;
    private final Transacciones transacciones;

    public AnalistaService(
            TransaccionRepository transaccionRepository,
            CasoRepository casoRepository,
            Transacciones transacciones) {
        this.transaccionRepository = transaccionRepository;
        this.casoRepository = casoRepository;
        this.transacciones = transacciones;
    }

    public Mono<ApiResponse<List<TransaccionResponse>>> listar(String estado, String tipo) {
        String estadoLimpio = normalizarFiltro(estado);
        String tipoLimpio = normalizarFiltro(tipo);
        return Mono.fromCallable(() -> Trazas.medir(log, "AnalistaService.listar", () ->
                        transacciones.consultar(() -> {
                            List<Transaccion> lista = transaccionRepository
                                    .buscarDeUsuarios(estadoLimpio, tipoLimpio);
                            Listas.avisarSiCorto(log, lista.size(), "AnalistaService.listar");
                            return lista.stream().map(TransaccionResponse::of).toList();
                        })))
                .subscribeOn(Schedulers.boundedElastic())
                .map(lista -> ApiResponse.ok("Movimientos de usuarios listados.", lista));
    }

    public Mono<ApiResponse<List<CasoResponse>>> casos(String estado) {
        String estadoLimpio = "TODOS".equalsIgnoreCase(estado) ? null : normalizarFiltro(estado);
        return Mono.fromCallable(() -> Trazas.medir(log, "AnalistaService.casos", () ->
                        transacciones.consultar(() -> {
                            List<Caso> lista = casoRepository.buscar(estadoLimpio);
                            Listas.avisarSiCorto(log, lista.size(), "AnalistaService.casos");
                            return lista.stream().map(CasoResponse::of).toList();
                        })))
                .subscribeOn(Schedulers.boundedElastic())
                .map(lista -> ApiResponse.ok("Casos listados.", lista));
    }

    public Mono<ApiResponse<AnalistaDashboardResponse>> dashboard() {
        return Mono.fromCallable(() -> Trazas.medir(log, "AnalistaService.dashboard", () ->
                        transacciones.consultar(() -> {
                            List<Transaccion> lista = transaccionRepository
                                    .buscarDeUsuarios(null, null);
                            Listas.avisarSiCorto(log, lista.size(), "AnalistaService.dashboard");

                            long pendientes = contar(lista, "PENDIENTE");
                            long aprobadas = contar(lista, "APROBADA");
                            long rechazadas = contar(lista, "RECHAZADA");
                            long autoAprobadas = lista.stream().filter(this::esAutoAprobada).count();
                            long casosAbiertos = casoRepository.countByEstado("ABIERTO");

                            AnalistaDashboardResponse.Kpis kpis = new AnalistaDashboardResponse.Kpis(
                                    lista.size(),
                                    pendientes,
                                    aprobadas,
                                    rechazadas,
                                    casosAbiertos,
                                    autoAprobadas,
                                    montoDe(lista, "APROBADA"),
                                    montoDe(lista, "PENDIENTE"));

                            List<AnalistaDashboardResponse.Conteo> porEstado = ESTADOS.stream()
                                    .map(estado -> new AnalistaDashboardResponse.Conteo(
                                            estado, contar(lista, estado), montoDe(lista, estado)))
                                    .toList();
                            List<AnalistaDashboardResponse.Conteo> porTipo = TIPOS.stream()
                                    .map(tipo -> new AnalistaDashboardResponse.Conteo(
                                            tipo,
                                            lista.stream()
                                                    .filter(t -> tipo.equals(t.getTipoTransaccion()))
                                                    .count(),
                                            lista.stream()
                                                    .filter(t -> tipo.equals(t.getTipoTransaccion()))
                                                    .map(Transaccion::getMonto)
                                                    .reduce(BigDecimal.ZERO, BigDecimal::add)))
                                    .toList();

                            List<TransaccionResponse> recientes = lista.stream()
                                    .limit(5)
                                    .map(TransaccionResponse::of)
                                    .toList();
                            List<CasoResponse> casosRecientes = casoRepository.buscar(null).stream()
                                    .limit(5)
                                    .map(CasoResponse::of)
                                    .toList();

                            return ApiResponse.ok("Dashboard del analista.",
                                    new AnalistaDashboardResponse(
                                            kpis, porEstado, porTipo, recientes, casosRecientes));
                        })))
                .subscribeOn(Schedulers.boundedElastic());
    }

    private boolean esAutoAprobada(Transaccion transaccion) {
        if (!"APROBADA".equals(transaccion.getEstado())) {
            return false;
        }
        List<EvaluacionRegla> reglas = transaccion.getReglas();
        long evaluadas = reglas.stream()
                .filter(regla -> regla.getRegla() != null && regla.getRegla().startsWith("R"))
                .count();
        return evaluadas == 4
                && reglas.stream()
                        .filter(regla -> regla.getRegla() != null && regla.getRegla().startsWith("R"))
                        .allMatch(regla -> Boolean.TRUE.equals(regla.getAprobada()));
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
}
