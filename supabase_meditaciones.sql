-- ==========================================================
-- REGISTRO DE SESIONES DE MEDITACIÓN
-- ----------------------------------------------------------
-- Tabla para registrar sesiones de meditación completadas por los usuarios.
-- Correr esto DESPUÉS de supabase_usuarios_regulacion.sql, en el mismo
-- proyecto de Supabase.
-- ==========================================================

create table if not exists sesiones_meditacion (
    id bigint generated always as identity primary key,
    usuario_id bigint not null references usuarios_regulacion(id),
    practica text not null,       -- clave de la práctica (ej. 'loving_kindness')
    sesion int not null,          -- número de sesión (ej. 1)
    completada_en timestamptz not null default now()
);

create index if not exists idx_sesiones_meditacion_usuario
    on sesiones_meditacion(usuario_id);

-- Igual que las otras tablas de esta app: se deshabilita RLS desde el
-- principio (el acceso se controla a nivel de API key en la capa de
-- aplicación, no con RLS, para evitar el bug conocido de RLS-por-defecto
-- que bloqueaba el acceso en proyectos anteriores de esta misma app).
alter table sesiones_meditacion disable row level security;

