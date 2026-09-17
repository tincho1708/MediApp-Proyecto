-- Tablas del historial de MediBot.
--
-- Usalo si preferís no tocar alembic (tu cadena de migraciones tiene una
-- revisión faltante: 380ac103be08 apunta a '1b3c283f8831', que no está en
-- alembic/versions, así que `alembic upgrade head` va a fallar hasta que
-- aparezca esa revisión o la rearmes).
--
-- Correr con:  psql "$DATABASE_URL" -f migracion_medibot.sql

CREATE TABLE IF NOT EXISTS conversacion_medibot (
    id            SERIAL PRIMARY KEY,
    usuario_id    INTEGER      NOT NULL,
    tipo_usuario  VARCHAR(20)  NOT NULL,
    titulo        VARCHAR(120) NOT NULL DEFAULT 'Nueva conversación',
    creado_en     TIMESTAMP    NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX IF NOT EXISTS ix_conversacion_medibot_usuario
    ON conversacion_medibot (usuario_id, tipo_usuario);

CREATE TABLE IF NOT EXISTS mensaje_medibot (
    id              SERIAL PRIMARY KEY,
    id_conversacion INTEGER     NOT NULL
                    REFERENCES conversacion_medibot(id) ON DELETE CASCADE,
    rol             VARCHAR(20) NOT NULL,
    contenido       TEXT        NOT NULL,
    creado_en       TIMESTAMP   NOT NULL DEFAULT (NOW() AT TIME ZONE 'utc')
);

CREATE INDEX IF NOT EXISTS ix_mensaje_medibot_conversacion
    ON mensaje_medibot (id_conversacion, creado_en);
