-- Tabla de usuarios de la app de Regulación Emocional.
-- Correr esto en el SQL Editor de tu proyecto de Supabase (se recomienda un
-- proyecto de Supabase APARTE del de la app de Encuesta, porque acá se
-- guardan datos sensibles de salud mental).

create table if not exists usuarios_regulacion (
    id bigint generated always as identity primary key,
    email text unique not null,
    password_hash text,               -- null si la persona entró solo con Google
    password_salt text,               -- sal aleatoria propia (PBKDF2), null si entró solo con Google
    nombre text,
    edad int,
    genero text,
    en_tratamiento text,              -- "Sí" / "No" / "Prefiero no decir", opcional
    pregunta_seguridad text,          -- para "¿Olvidaste tu contraseña?" (no hay envío de mails)
    respuesta_seguridad_hash text,    -- hash PBKDF2 de la respuesta normalizada, nunca en texto plano
    respuesta_seguridad_salt text,    -- sal aleatoria propia de esa respuesta
    vio_instrucciones boolean not null default false,  -- si ya vio la pantalla de instrucciones alguna vez
    vio_instrucciones_temas boolean not null default false,  -- ídem, para "Pensamientos que estoy trabajando"
    vio_instrucciones_bienestar boolean not null default false,  -- ídem, para el chequeo de bienestar (WHO-5)
    vio_instrucciones_trabajo_emocional boolean not null default false,  -- ídem, para el submenú "Trabajo emocional"
    vio_instrucciones_reappraisal boolean not null default false,  -- ídem, para el submenú "Reappraisal"
    cosmetico_planta text,            -- flor elegida en Personalización para las plantas en flor (emoji)
    cosmetico_fondo text,             -- florcita elegida para la decoración del menú principal (emoji)
    color_fondo text,                 -- color de fondo de pantalla elegido en Personalización (hex)
    creado_en timestamptz not null default now()
);

-- Si la tabla ya existía de antes (proyecto de Supabase ya creado), correr
-- también estas líneas para agregar las columnas nuevas sin perder los datos:
-- alter table usuarios_regulacion add column if not exists en_tratamiento text;
-- alter table usuarios_regulacion add column if not exists pregunta_seguridad text;
-- alter table usuarios_regulacion add column if not exists respuesta_seguridad_hash text;
-- alter table usuarios_regulacion add column if not exists respuesta_seguridad_salt text;
-- alter table usuarios_regulacion add column if not exists vio_instrucciones boolean not null default false;
-- alter table usuarios_regulacion add column if not exists vio_instrucciones_temas boolean not null default false;
-- alter table usuarios_regulacion add column if not exists vio_instrucciones_bienestar boolean not null default false;
-- alter table usuarios_regulacion add column if not exists vio_instrucciones_trabajo_emocional boolean not null default false;
-- alter table usuarios_regulacion add column if not exists vio_instrucciones_reappraisal boolean not null default false;
-- alter table usuarios_regulacion add column if not exists cosmetico_planta text;
-- alter table usuarios_regulacion add column if not exists cosmetico_fondo text;
-- alter table usuarios_regulacion add column if not exists color_fondo text;
