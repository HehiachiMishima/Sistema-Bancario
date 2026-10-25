package oracle.bancario.controller;

import java.util.List;
import oracle.bancario.response.AnalistaDashboardResponse;
import oracle.bancario.response.CasoResponse;
import oracle.bancario.response.TransaccionResponse;
import oracle.bancario.service.AnalistaService;
import oracle.common.response.ApiResponse;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

/** Bandeja del analista: movimientos de usuarios USUARIO, casos y dashboard. */
@RestController
@RequestMapping("/api/analista")
@PreAuthorize("hasAuthority('RESOLVER_CASO')")
public class AnalistaController {

    private final AnalistaService analistaService;

    public AnalistaController(AnalistaService analistaService) {
        this.analistaService = analistaService;
    }

    @GetMapping("/transacciones")
    public Mono<ApiResponse<List<TransaccionResponse>>> transacciones(
            @RequestParam(required = false) String estado,
            @RequestParam(required = false) String tipo) {
        return analistaService.listar(estado, tipo);
    }

    @GetMapping("/casos")
    public Mono<ApiResponse<List<CasoResponse>>> casos(
            @RequestParam(required = false) String estado) {
        return analistaService.casos(estado);
    }

    @GetMapping("/dashboard")
    public Mono<ApiResponse<AnalistaDashboardResponse>> dashboard() {
        return analistaService.dashboard();
    }
}
