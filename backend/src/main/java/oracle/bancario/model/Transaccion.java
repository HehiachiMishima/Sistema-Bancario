package oracle.bancario.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.OneToMany;
import jakarta.persistence.OrderBy;
import jakarta.persistence.Table;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import lombok.Getter;
import lombok.Setter;
import oracle.common.model.Auditable;

/** Movimiento financiero. Los saldos post solo se llenan al aprobar. */
@Entity
@Table(name = "transacciones")
@Getter
@Setter
public class Transaccion extends Auditable {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "referencia", nullable = false, unique = true, length = 50)
    private String referencia;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cuenta_origen_id")
    private CuentaBancaria cuentaOrigen;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "cuenta_destino_id")
    private CuentaBancaria cuentaDestino;

    @Column(name = "tipo_transaccion", nullable = false, length = 20)
    private String tipoTransaccion;

    @Column(name = "monto", nullable = false, precision = 18, scale = 2)
    private BigDecimal monto;

    @Column(name = "estado", nullable = false, length = 20)
    private String estado = "PENDIENTE";

    @Column(name = "saldo_origen_post", precision = 18, scale = 2)
    private BigDecimal saldoOrigenPost;

    @Column(name = "saldo_destino_post", precision = 18, scale = 2)
    private BigDecimal saldoDestinoPost;

    @Column(name = "descripcion", length = 255)
    private String descripcion;

    @OneToMany(mappedBy = "transaccion", cascade = jakarta.persistence.CascadeType.ALL,
            orphanRemoval = true)
    @OrderBy("orden ASC")
    private List<EvaluacionRegla> reglas = new ArrayList<>();
}
