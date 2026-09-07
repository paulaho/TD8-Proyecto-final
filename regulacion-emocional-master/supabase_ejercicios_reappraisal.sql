-- Tabla de ejercicios de reappraisal (bloque 3 del menú principal).
-- Correr esto DESPUÉS de supabase_usuarios_regulacion.sql y de
-- supabase_temas_seguimiento.sql (esta tabla hace referencia a esa), en
-- el mismo proyecto de Supabase.

create table if not exists ejercicios_reappraisal (
    id bigint generated always as identity primary key,
    usuario_id bigint not null references usuarios_regulacion(id),
    tema_id bigint references temas_seguimiento(id),  -- solo si es "propia" sacada del historial
    fecha timestamptz not null default now(),

    modo text not null,               -- "inventada" o "propia"
    categoria text,                   -- nombre de la categoría (null si es "propia" con situación nueva)
    situacion_texto text not null,

    paso_pensamiento text not null,    -- qué pensamiento/emoción genera (o generaría) la situación
    paso_hechos text not null,         -- solo los hechos, sin emoción
    paso_tercero text not null,        -- perspectiva de alguien que conoce los hechos pero no las emociones
    paso_temporal text not null        -- perspectiva a un año
);

create index if not exists idx_reappraisal_usuario on ejercicios_reappraisal(usuario_id);

-- Igual que las otras tablas de esta app: se deshabilita RLS desde el
-- principio (ver detalle del bug de RLS-por-defecto en
-- stack_deployment_regulacion_emocional, memoria del asistente).
alter table ejercicios_reappraisal disable row level security;
