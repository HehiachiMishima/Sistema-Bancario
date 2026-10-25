package oracle.bancario.repository;

import java.util.List;
import java.util.Optional;
import oracle.bancario.model.Caso;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.transaction.annotation.Transactional;

public interface CasoRepository extends JpaRepository<Caso, Long> {

    boolean existsByNumeroCaso(String numeroCaso);

    Optional<Caso> findByTransaccionId(Long transaccionId);

    long countByEstado(String estado);

    /** Bandeja del analista con la transaccion y sus cuentas ya resueltas. */
    @Query("""
            SELECT c FROM Caso c
            JOIN FETCH c.transaccion t
            LEFT JOIN FETCH t.cuentaOrigen co
            LEFT JOIN FETCH co.usuario cou
            LEFT JOIN FETCH t.cuentaDestino cd
            LEFT JOIN FETCH cd.usuario cdu
            WHERE (:estado IS NULL OR c.estado = :estado)
            ORDER BY c.creadoEn DESC, c.id DESC
            """)
    List<Caso> buscar(@Param("estado") String estado);

    @Transactional
    @Modifying
    @Query("DELETE FROM Caso c WHERE c.transaccion.id = :transaccionId")
    void eliminarPorTransaccion(@Param("transaccionId") Long transaccionId);
}
