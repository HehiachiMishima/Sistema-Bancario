package oracle.bancario.controller;

import jakarta.validation.Valid;
import java.util.List;
import oracle.admin.request.CambiarEstadoRequest;
import oracle.bancario.request.CuentaActualizarRequest;
import oracle.bancario.request.CuentaCrearRequest;
import oracle.bancario.response.CuentaDashboardResponse;
import oracle.bancario.response.CuentaResponse;
import oracle.bancario.service.CuentaService;
import oracle.common.response.ApiResponse;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PatchMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Mono;

/** CRUD de cuentas bancarias. Activar/desactivar exige un permiso aparte. */
@RestController
@RequestMapping("/api/cuentas")
public class CuentaController {

    private final CuentaService cuentaService;

    public CuentaController(CuentaService cuentaService) {
        this.cuentaService = cuentaService;
    }

    @GetMapping
    @PreAuthorize("hasAuthority('VER_CUENTAS')")
    public Mono<ApiResponse<List<CuentaResponse>>> listar() {
        return cuentaService.listar();
    }

    @GetMapping("/dashboard")
    @PreAuthorize("hasAuthority('DASHBOARD_CUENTAS')")
    public Mono<ApiResponse<CuentaDashboardResponse>> dashboard() {
        return cuentaService.dashboard();
    }

    @GetMapping("/{id}")
    @PreAuthorize("hasAuthority('VER_CUENTAS')")
    public Mono<ApiResponse<CuentaResponse>> obtener(@PathVariable Long id) {
        return cuentaService.obtener(id);
    }

    @PostMapping
    @PreAuthorize("hasAuthority('CREAR_CUENTAS')")
    public Mono<ApiResponse<CuentaResponse>> crear(@Valid @RequestBody CuentaCrearRequest peticion) {
        return cuentaService.crear(peticion);
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAuthority('MODIFICAR_CUENTAS')")
    public Mono<ApiResponse<CuentaResponse>> actualizar(@PathVariable Long id,
            @Valid @RequestBody CuentaActualizarRequest peticion) {
        return cuentaService.actualizar(id, peticion);
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasAuthority('ELIMINAR_CUENTAS')")
    public Mono<ApiResponse<Void>> eliminar(@PathVariable Long id) {
        return cuentaService.eliminar(id);
    }

    @PatchMapping("/{id}/activo")
    @PreAuthorize("hasAuthority('CAMBIAR_ESTADO_CUENTAS')")
    public Mono<ApiResponse<CuentaResponse>> cambiarActivo(@PathVariable Long id,
            @Valid @RequestBody CambiarEstadoRequest peticion) {
        return cuentaService.cambiarActivo(id, peticion.activo());
    }
}
