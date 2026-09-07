-- Progreso del modo "Practicá con escenarios" (bloque 3 del menú
-- principal, integración con MENTO). Correr esto DESPUÉS de
-- supabase_usuarios_regulacion.sql, en el mismo proyecto de Supabase.

create table if not exists progreso_juegos_reappraisal (
    id bigint generated always as identity primary key,
    usuario_id bigint not null references usuarios_regulacion(id),
    fecha timestamptz not null default now(),

    categoria text not null,   -- "familia" | "salud" | "vinculos" | "trabajo"
    nivel smallint not null,   -- 1 a 5

    unique (usuario_id, categoria, nivel)
);

create index if not exists idx_progreso_juegos_usuario on progreso_juegos_reappraisal(usuario_id);

-- Igual que las otras tablas de esta app: se deshabilita RLS desde el
-- principio (ver detalle del bug de RLS-por-defecto en
-- stack_deployment_regulacion_emocional, memoria del asistente).
alter table progreso_juegos_reappraisal disable row level security;
