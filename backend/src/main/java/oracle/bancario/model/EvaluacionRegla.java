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
import lombok.Getter;
import lombok.Setter;

/** Resultado de una regla del motor de evaluacion para una transaccion. */
@Entity
@Table(name = "transaccion_reglas")
@Getter
@Setter
public class EvaluacionRegla {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "transaccion_id", nullable = false)
    private Transaccion transaccion;

    @Column(name = "orden", nullable = false)
    private Integer orden;

    @Column(name = "regla", nullable = false, length = 10)
    private String regla;

    @Column(name = "titulo", nullable = false, length = 120)
    private String titulo;

    @Column(name = "aprobada", nullable = false)
    private Boolean aprobada;

    @Column(name = "detalle", nullable = false, length = 255)
    private String detalle;
}
