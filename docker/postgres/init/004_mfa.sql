-- Idempotent migration for existing Neon and fresh local databases.
-- Apply before deploying the MFA code. Never rerun 001_schema.sql on Neon.
BEGIN;
CREATE TABLE IF NOT EXISTS duality.usuario_mfa (
    id_usuario VARCHAR(20) PRIMARY KEY REFERENCES duality.usuario(id_usuario) ON DELETE CASCADE,
    secret_ciphertext TEXT,
    pending_ciphertext TEXT,
    last_accepted_step BIGINT,
    enabled_at TIMESTAMPTZ,
    CONSTRAINT ck_usuario_mfa_enabled CHECK (
        (secret_ciphertext IS NULL AND enabled_at IS NULL)
        OR (secret_ciphertext IS NOT NULL AND enabled_at IS NOT NULL)
    )
);
CREATE TABLE IF NOT EXISTS duality.usuario_mfa_recuperacion (
    id_usuario VARCHAR(20) NOT NULL REFERENCES duality.usuario(id_usuario) ON DELETE CASCADE,
    codigo_hash CHAR(64) NOT NULL,
    usado_at TIMESTAMPTZ,
    PRIMARY KEY (id_usuario, codigo_hash)
);
COMMIT;
