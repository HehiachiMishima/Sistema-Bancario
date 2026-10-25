package oracle.bancario.repository;

import jakarta.persistence.LockModeType;
import java.util.List;
import java.util.Optional;
import oracle.bancario.model.CuentaBancaria;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

public interface CuentaBancariaRepository extends JpaRepository<CuentaBancaria, Long> {

    boolean existsByNumeroCuenta(String numeroCuenta);

    boolean existsByNumeroCuentaAndIdNot(String numeroCuenta, Long id);

    @EntityGraph(attributePaths = "usuario")
    List<CuentaBancaria> findAllByOrderByCreadoEnDesc(Pageable pageable);

    @EntityGraph(attributePaths = "usuario")
    List<CuentaBancaria> findByUsuarioIdOrderByCreadoEnDesc(Long usuarioId, Pageable pageable);

    @EntityGraph(attributePaths = "usuario")
    Optional<CuentaBancaria> findById(Long id);

    @EntityGraph(attributePaths = "usuario")
    Optional<CuentaBancaria> findByIdAndUsuarioId(Long id, Long usuarioId);

    /** Bloquea la fila para aplicar o revertir saldos sin carreras. */
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("SELECT c FROM CuentaBancaria c WHERE c.id = :id")
    Optional<CuentaBancaria> bloquearPorId(@Param("id") Long id);
}
