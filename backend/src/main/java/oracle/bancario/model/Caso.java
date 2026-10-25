package oracle.bancario.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.LocalDateTime;
import lombok.Getter;
import lombok.Setter;

/**
 * Caso abierto para una transaccion que no supero el motor de reglas.
 * La tabla no tiene creado_por: solo registra quien hizo la ultima gestion.
 */
@Entity
@Table(name = "casos")
@Getter
@Setter
public class Caso {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "numero_caso", nullable = false, unique = true, length = 50)
    private String numeroCaso;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "transaccion_id", nullable = false)
    private Transaccion transaccion;

    @Column(name = "cuenta_origen_numero", length = 30)
    private String cuentaOrigenNumero;

    @Column(name = "cuenta_destino_numero", length = 30)
    private String cuentaDestinoNumero;

    @Column(name = "estado", nullable = false, length = 20)
    private String estado = "ABIERTO";

    @Column(name = "actualizado_por", nullable = false)
    private Long actualizadoPor;

    @Column(name = "creado_en", nullable = false)
    private LocalDateTime creadoEn;

    @Column(name = "actualizado_en", nullable = false)
    private LocalDateTime actualizadoEn;
}
