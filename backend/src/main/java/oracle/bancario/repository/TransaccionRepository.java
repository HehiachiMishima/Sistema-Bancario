package oracle.bancario.repository;

import java.math.BigDecimal;
import java.util.List;
import java.util.Optional;
import oracle.bancario.model.Transaccion;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface TransaccionRepository extends JpaRepository<Transaccion, Long> {

    boolean existsByReferencia(String referencia);

    /**
     * Listado con alcance: el analista/administrador (todas = true) ve todo;
     * el usuario ve lo que creo y los movimientos donde participa alguna de
     * sus cuentas (origen o destino).
     */
    @Query("""
            SELECT t FROM Transaccion t
            LEFT JOIN FETCH t.cuentaOrigen co
            LEFT JOIN FETCH co.usuario
            LEFT JOIN FETCH t.cuentaDestino cd
            LEFT JOIN FETCH cd.usuario
            WHERE (:todas = TRUE OR t.creadoPor = :actor
                   OR co.usuario.id = :actor OR cd.usuario.id = :actor)
              AND (:estado IS NULL OR t.estado = :estado)
              AND (:tipo IS NULL OR t.tipoTransaccion = :tipo)
              AND (:cuentaId IS NULL OR co.id = :cuentaId OR cd.id = :cuentaId)
            ORDER BY t.creadoEn DESC, t.id DESC
            """)
    List<Transaccion> buscar(
            @Param("actor") Long actor,
            @Param("todas") boolean todas,
            @Param("estado") String estado,
            @Param("tipo") String tipo,
            @Param("cuentaId") Long cuentaId);

    /** Carga una transaccion con cuentas y titulares resueltos. */
    @Query("""
            SELECT t FROM Transaccion t
            LEFT JOIN FETCH t.cuentaOrigen co
            LEFT JOIN FETCH co.usuario
            LEFT JOIN FETCH t.cuentaDestino cd
            LEFT JOIN FETCH cd.usuario
            WHERE t.id = :id
            """)
    Optional<Transaccion> cargar(@Param("id") Long id);

    /**
     * Bandeja del analista: solo movimientos creados por usuarios con rol
     * USUARIO, de cualquier titular, con cuentas y titulares resueltos.
     */
    @Query("""
            SELECT t FROM Transaccion t
            LEFT JOIN FETCH t.cuentaOrigen co
            LEFT JOIN FETCH co.usuario cou
            LEFT JOIN FETCH t.cuentaDestino cd
            LEFT JOIN FETCH cd.usuario cdu
            WHERE EXISTS (
                SELECT 1 FROM UsuarioRol ur
                WHERE ur.usuario.id = t.creadoPor AND ur.rol.nombre = 'USUARIO'
            )
              AND (:estado IS NULL OR t.estado = :estado)
              AND (:tipo IS NULL OR t.tipoTransaccion = :tipo)
            ORDER BY t.creadoEn DESC, t.id DESC
            """)
    List<Transaccion> buscarDeUsuarios(
            @Param("estado") String estado,
            @Param("tipo") String tipo);

    long countByCuentaOrigenId(Long cuentaOrigenId);

    long countByCuentaOrigenIdAndCuentaDestinoId(Long cuentaOrigenId, Long cuentaDestinoId);

    long countByCuentaOrigenIdAndTipoTransaccion(Long cuentaOrigenId, String tipoTransaccion);

    @Query("SELECT COALESCE(AVG(t.monto), 0) FROM Transaccion t WHERE t.cuentaOrigen.id = :cuentaOrigenId")
    BigDecimal promedioMontoOrigen(@Param("cuentaOrigenId") Long cuentaOrigenId);
}
