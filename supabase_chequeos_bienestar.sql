-- Tabla de chequeos periódicos de bienestar (WHO-5). Correr esto DESPUÉS
-- de supabase_usuarios_regulacion.sql, en el mismo proyecto de Supabase.

create table if not exists chequeos_bienestar (
    id bigint generated always as identity primary key,
    usuario_id bigint not null references usuarios_regulacion(id),
    fecha timestamptz not null default now(),

    p1 int not null,  -- "Me he sentido alegre y de buen humor" (0-5)
    p2 int not null,  -- "Me he sentido tranquilo/a y relajado/a" (0-5)
    p3 int not null,  -- "Me he sentido activo/a y con energía" (0-5)
    p4 int not null,  -- "Me desperté sintiéndome fresco/a y descansado/a" (0-5)
    p5 int not null,  -- "Mi vida diaria ha estado llena de cosas que me interesan" (0-5)

    puntaje_total int not null,  -- suma de p1..p5 (0-25)
    porcentaje int not null      -- puntaje_total * 4 (0-100, a mayor %, mejor bienestar)
);

create index if not exists idx_bienestar_usuario on chequeos_bienestar(usuario_id);

-- Igual que las otras 3 tablas de esta app: Supabase habilita Row Level
-- Security por defecto en proyectos nuevos, lo que bloquea cualquier
-- insert/update hecho con la clave anon (ver stack_deployment_regulacion_emocional
-- en la memoria del asistente para el detalle del bug que esto causó la
-- primera vez). Esta app maneja su propia autenticación a mano (no usa el
-- sistema nativo de Supabase Auth + RLS), así que se deshabilita acá desde
-- el principio para no repetir ese mismo problema.
alter table chequeos_bienestar disable row level security;
