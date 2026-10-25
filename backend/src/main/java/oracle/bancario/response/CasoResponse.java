package oracle.bancario.response;

import java.time.LocalDateTime;
import oracle.bancario.model.Caso;

/** Caso de la bandeja del analista, con la transaccion que lo origino. */
public record CasoResponse(
        Long id,
        String numeroCaso,
        String estado,
        String cuentaOrigenNumero,
        String cuentaDestinoNumero,
        TransaccionResponse transaccion,
        LocalDateTime creadoEn,
        LocalDateTime actualizadoEn) {

    public static CasoResponse of(Caso caso) {
        return new CasoResponse(
                caso.getId(),
                caso.getNumeroCaso(),
                caso.getEstado(),
                caso.getCuentaOrigenNumero(),
                caso.getCuentaDestinoNumero(),
                TransaccionResponse.of(caso.getTransaccion()),
                caso.getCreadoEn(),
                caso.getActualizadoEn());
    }
}
