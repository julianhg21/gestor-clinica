-- C-05: ejecutar como propietario del esquema antes de desplegar la API.
-- Los pacientes existentes quedan sin asignación; solo ROL_ADMIN puede consultarlos.
ALTER TABLE duality.paciente
    ADD COLUMN IF NOT EXISTS id_usuario_asignado VARCHAR(20)
    REFERENCES duality.usuario(id_usuario);

CREATE INDEX IF NOT EXISTS idx_paciente_usuario_asignado
    ON duality.paciente(id_usuario_asignado);
