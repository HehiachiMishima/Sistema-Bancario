package oracle.bancario.controller;

import jakarta.validation.Valid;
import java.util.List;
import oracle.bancario.request.TransaccionActualizarRequest;
import oracle.bancario.request.TransaccionCrearRequest;
import oracle.bancario.request.TransaccionFiltroRequest;
import oracle.bancario.response.TransaccionDashboardResponse;
import oracle.bancario.response.TransaccionResponse;
import oracle.bancario.service.TransaccionService;
import oracle.common.response.ApiResponse;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

/**
 * Movimientos. Crear y consultar esta disponible para USUARIO; editar,
 * aprobar, rechazar o eliminar exige RESOLVER_CASO.
 */
@RestController
@RequestMapping("/api/transacciones")
public class TransaccionController {

    private final TransaccionService transaccionService;

    public TransaccionController(TransaccionService transaccionService) {
        this.transaccionService = transaccionService;
    }

    @GetMapping
    @PreAuthorize("hasAuthority('VER_TRANSACCIONES')")
    public Mono<ApiResponse<List<TransaccionResponse>>> listar(
            @Valid @ModelAttribute TransaccionFiltroRequest filtro) {
        return transaccionService.listar(filtro);
    }

    @GetMapping("/dashboard")
    @PreAuthorize("hasAuthority('DASHBOARD_TRANSACCIONES')")
    public Mono<ApiResponse<TransaccionDashboardResponse>> dashboard() {
        return transaccionService.dashboard();
    }

    @PostMapping
    @PreAuthorize("hasAuthority('CREAR_TRANSACCIONES')")
    public Mono<ApiResponse<TransaccionResponse>> crear(
            @Valid @RequestBody TransaccionCrearRequest peticion) {
        return transaccionService.crear(peticion);
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAuthority('RESOLVER_CASO')")
    public Mono<ApiResponse<TransaccionResponse>> actualizar(@PathVariable Long id,
            @Valid @RequestBody TransaccionActualizarRequest peticion) {
        return transaccionService.actualizar(id, peticion);
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasAuthority('RESOLVER_CASO')")
    public Mono<ApiResponse<Void>> eliminar(@PathVariable Long id) {
        return transaccionService.eliminar(id);
    }
}
