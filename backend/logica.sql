-- Active: 1791152181635@@127.0.0.1@3306@sistema_bancario
-- ============================================================
-- 7) cuentas_bancarias
-- ============================================================
CREATE TABLE IF NOT EXISTS cuentas_bancarias (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la cuenta.',
    numero_cuenta VARCHAR(30) NOT NULL COMMENT 'Número de cuenta único. Ej: 001-1234567890.',
    usuario_id BIGINT NOT NULL COMMENT 'FK al usuario titular. Es el usuario ORIGEN: quien abre y a quien pertenece la cuenta.',
    tipo_cuenta VARCHAR(20) NOT NULL COMMENT 'AHORRO | CORRIENTE | EMPRESARIAL.',
    saldo DECIMAL(18, 2) NOT NULL DEFAULT 0.00 COMMENT 'Saldo actual. Puede ser negativo si se permite sobregiro.',
    activo BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'TRUE = operativa; FALSE = cerrada/bloqueada.',
    actualizado_por BIGINT NOT NULL COMMENT 'ID del usuario que actualizó la cuenta por última vez (operador/admin). 0 = sistema/seeding.',
    creado_en TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha y hora de apertura.',
    actualizado_en TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Última modificación.',
    CONSTRAINT uq_cuentas_bancarias_numero UNIQUE (numero_cuenta),
    CONSTRAINT fk_cuentas_bancarias_usuario FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE RESTRICT,
    INDEX idx_cuentas_usuario_activo (usuario_id, activo) COMMENT 'Listado de cuentas por usuario filtrando estado. Cubre también solo usuario_id.',
    INDEX idx_cuentas_activo_tipo (activo, tipo_cuenta) COMMENT 'Reportes por tipo y estado (cuántas AHORRO activas, etc.).',
    INDEX idx_cuentas_creado_en (creado_en) COMMENT 'Ordenamientos y rangos temporales (altas por día/mes).',
    INDEX idx_cuentas_saldo (saldo) COMMENT 'Búsquedas por rango/umbral de saldo (cuentas de alto valor, morosidad, etc.).'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'Cuentas bancarias. usuario_id = usuario ORIGEN (titular). FK RESTRICT para no perder historial contable.';

-- ============================================================
-- 8) transacciones
-- ============================================================
CREATE TABLE IF NOT EXISTS transacciones (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la transacción.',
    referencia VARCHAR(50) NOT NULL COMMENT 'Referencia única legible. Ej: TX-20240101-000123.',
    cuenta_origen_id BIGINT NULL COMMENT 'FK cuenta origen. NULL en DEPOSITO.',
    cuenta_destino_id BIGINT NULL COMMENT 'FK cuenta destino. NULL en RETIRO.',
    tipo_transaccion VARCHAR(20) NOT NULL COMMENT 'DEPOSITO | RETIRO | TRANSFERENCIA | PAGO | AJUSTE.',
    monto DECIMAL(18, 2) NOT NULL COMMENT 'Monto, siempre positivo.',
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE' COMMENT 'PENDIENTE | APROBADA | RECHAZADA.',
    saldo_origen_post DECIMAL(18, 2) NULL COMMENT 'Saldo de la cuenta origen tras aplicar la transacción.',
    saldo_destino_post DECIMAL(18, 2) NULL COMMENT 'Saldo de la cuenta destino tras aplicar la transacción.',
    descripcion VARCHAR(255) NULL COMMENT 'Concepto o nota.',
    creado_por BIGINT NOT NULL COMMENT 'ID del usuario ORIGEN: titular de cuenta_origen en TRANSFERENCIA/RETIRO/PAGO; en DEPOSITO, el usuario que origina el depósito. 0 = sistema/seeding.',
    actualizado_por BIGINT NOT NULL COMMENT 'ID del usuario que actualizó el estado por última vez (quien aprueba o rechaza). 0 = sistema/seeding.',
    creado_en TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha y hora de registro.',
    actualizado_en TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Última modificación.',
    CONSTRAINT uq_transacciones_referencia UNIQUE (referencia),
    CONSTRAINT fk_transacciones_cuenta_origen FOREIGN KEY (cuenta_origen_id) REFERENCES cuentas_bancarias (id) ON DELETE RESTRICT,
    CONSTRAINT fk_transacciones_cuenta_destino FOREIGN KEY (cuenta_destino_id) REFERENCES cuentas_bancarias (id) ON DELETE RESTRICT,
    INDEX idx_transacciones_creado_por_fecha (creado_por, creado_en) COMMENT 'Historial global de un usuario origen (todas sus cuentas) ordenado por fecha.',
    INDEX idx_transacciones_origen_fecha (cuenta_origen_id, creado_en) COMMENT 'Historial saliente por cuenta ordenado por fecha.',
    INDEX idx_transacciones_destino_fecha (cuenta_destino_id, creado_en) COMMENT 'Historial entrante por cuenta ordenado por fecha.',
    INDEX idx_transacciones_origen_estado_fecha (
        cuenta_origen_id,
        estado,
        creado_en
    ) COMMENT 'Query estrella: historial de una cuenta filtrado por estado y ordenado por fecha.',
    INDEX idx_transacciones_destino_estado_fecha (
        cuenta_destino_id,
        estado,
        creado_en
    ) COMMENT 'Espejo del anterior para el lado destino.',
    INDEX idx_transacciones_estado_fecha (estado, creado_en) COMMENT 'Bandeja de PENDIENTES / APROBADAS / RECHAZADAS por rango de fechas (procesos batch).',
    INDEX idx_transacciones_tipo_fecha (tipo_transaccion, creado_en) COMMENT 'Reportes por tipo (volumen de transferencias, depósitos, etc.).',
    INDEX idx_transacciones_fecha (creado_en) COMMENT 'Corte global por fecha (cierres diarios, auditorías).',
    INDEX idx_transacciones_monto (monto) COMMENT 'Filtros por umbral/rango de monto (operaciones sospechosas, top movimientos).'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'Transacciones financieras. creado_por = usuario ORIGEN de la operación. FK RESTRICT para preservar integridad contable.';

-- ============================================================
-- 9) casos
-- ============================================================
CREATE TABLE IF NOT EXISTS casos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único del caso.',
    numero_caso VARCHAR(50) NOT NULL COMMENT 'Referencia única legible. Ej: CASO-20240101-000123.',
    transaccion_id BIGINT NOT NULL COMMENT 'FK a la transacción que origina el caso.',
    cuenta_origen_numero VARCHAR(30) NULL COMMENT 'Snapshot del número de cuenta origen al abrir el caso. NULL en DEPOSITO.',
    cuenta_destino_numero VARCHAR(30) NULL COMMENT 'Snapshot del número de cuenta destino al abrir el caso. NULL en RETIRO.',
    estado VARCHAR(20) NOT NULL DEFAULT 'ABIERTO' COMMENT 'ABIERTO | EN_REVISION | RESUELTO | CERRADO | RECHAZADO.',
    actualizado_por BIGINT NOT NULL COMMENT 'ID del usuario que actualizó el caso por última vez (agente/back-office). 0 = sistema/seeding.',
    creado_en TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Fecha y hora de apertura del caso.',
    actualizado_en TIMESTAMP(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6) COMMENT 'Última modificación.',
    CONSTRAINT uq_casos_numero UNIQUE (numero_caso),
    CONSTRAINT fk_casos_transaccion FOREIGN KEY (transaccion_id) REFERENCES transacciones (id) ON DELETE RESTRICT,
    INDEX idx_casos_transaccion_fecha (transaccion_id, creado_en) COMMENT 'Todos los casos de una transacción ordenados por fecha. Cubre también solo transaccion_id.',
    INDEX idx_casos_cuenta_origen_fecha (
        cuenta_origen_numero,
        creado_en
    ) COMMENT 'Casos reportados sobre una cuenta origen concreta, ordenados por fecha.',
    INDEX idx_casos_cuenta_destino_fecha (
        cuenta_destino_numero,
        creado_en
    ) COMMENT 'Espejo del anterior para el lado destino.',
    INDEX idx_casos_estado_fecha (estado, creado_en) COMMENT 'Bandeja simple por estado (ABIERTOS, EN_REVISION, ...).',
    INDEX idx_casos_fecha (creado_en) COMMENT 'Cortes diarios / reportes de volumen por fecha.'
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'Casos sobre transacciones. Snapshot de cuentas origen/destino, estado y auditoría mínima.';
-- ============================================================
-- 10) transaccion_reglas
-- ============================================================
CREATE TABLE IF NOT EXISTS transaccion_reglas (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Identificador único de la evaluación.',
    transaccion_id BIGINT NOT NULL COMMENT 'FK a la transacción evaluada.',
    orden TINYINT NOT NULL COMMENT 'Orden de presentación: 1..4 reglas, 5 saldo.',
    regla VARCHAR(10) NOT NULL COMMENT 'R1 | R2 | R3 | R4 | SALDO.',
    titulo VARCHAR(120) NOT NULL COMMENT 'Nombre legible de la regla.',
    aprobada BOOLEAN NOT NULL COMMENT 'TRUE = la regla pasó; FALSE = motivo de revisión.',
    detalle VARCHAR(255) NOT NULL COMMENT 'Explicación del cálculo realizado.',
    CONSTRAINT uq_transaccion_reglas_transaccion_regla UNIQUE (transaccion_id, regla),
    CONSTRAINT fk_transaccion_reglas_transaccion FOREIGN KEY (transaccion_id) REFERENCES transacciones (id) ON DELETE CASCADE
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = 'Resultado de las reglas de aprobación automática por transacción.';
