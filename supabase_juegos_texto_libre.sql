-- Tabla para guardar sesiones completas del modo "Reappraisal en texto libre".
-- Correr esto DESPUÉS de supabase_usuarios_regulacion.sql, en el mismo
-- proyecto de Supabase.

create table if not exists sesiones_texto_libre (
    id bigint generated always as identity primary key,
    usuario_id bigint not null references usuarios_regulacion(id),
    fecha timestamptz not null default now(),

    categoria text not null default 'familia',  -- por ahora solo 'familia'

    -- Las 5 situaciones generadas por la IA para esta sesión
    -- Cada item: { "situacion": str, "reappraisal_inicial": str }
    situaciones jsonb not null,

    -- Los 5 contraargumentos escritos por el usuario en Fase 1
    -- Array de strings
    fase1_respuestas jsonb not null,

    -- Los 5 nuevos reappraisals escritos por el usuario en Fase 2
    -- Array de strings
    fase2_respuestas jsonb not null,

    -- Las 5 correcciones de la IA
    -- Cada item: { "feedback": str }
    correcciones jsonb not null
);

create index if not exists idx_sesiones_texto_libre_usuario
    on sesiones_texto_libre(usuario_id);

-- Igual que las otras tablas de esta app: se deshabilita RLS desde el
-- principio (el acceso se controla a nivel de API key en la capa de
-- aplicación, no con RLS, para evitar el bug conocido de RLS-por-defecto
-- que bloqueaba el acceso en proyectos anteriores de esta misma app).
alter table sesiones_texto_libre disable row level security;

-- Si la tabla ya existía y hay que agregar columnas nuevas sin perder datos:
-- alter table sesiones_texto_libre add column if not exists categoria text not null default 'familia';
