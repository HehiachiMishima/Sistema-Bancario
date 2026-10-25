package oracle.auth;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;

/** Autorregistro publico. Siempre crea la cuenta con el rol USUARIO. */
public record RegistroRequest(
        @NotBlank(message = "El usuario es obligatorio.")
        @Size(max = 50, message = "El usuario no puede exceder 50 caracteres.")
        String usuario,

        @NotBlank(message = "La contrasena es obligatoria.")
        @Size(min = 6, max = 100, message = "La contrasena debe tener entre 6 y 100 caracteres.")
        String contrasena,

        @NotBlank(message = "El nombre es obligatorio.")
        @Size(max = 100)
        String nombre,

        @NotBlank(message = "El apellido es obligatorio.")
        @Size(max = 100)
        String apellido,

        @NotBlank(message = "El email es obligatorio.")
        @Email(message = "El email no es valido.")
        @Size(max = 100)
        String email,

        @Size(max = 20, message = "El telefono no puede exceder 20 caracteres.")
        String telefono) {
}
