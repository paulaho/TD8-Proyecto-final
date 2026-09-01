-- Tabla de "temas": pensamientos recurrentes que la persona decide seguir
-- trabajando a lo largo del tiempo (con color y estado que ella misma
-- define). Correr esto DESPUÉS de supabase_usuarios_regulacion.sql y
-- ANTES de supabase_reportes_emocionales.sql (que hace referencia a esta
-- tabla), en el mismo proyecto de Supabase.

create table if not exists temas_seguimiento (
    id bigint generated always as identity primary key,
    usuario_id bigint not null references usuarios_regulacion(id),

    titulo text not null,                  -- el pensamiento recurrente, en pocas palabras
    color text not null default 'Gris',    -- vista de un vistazo de cómo viene avanzando
    color_automatico boolean not null default false,  -- true = lo calcula la app según la creencia final más reciente; false = lo elige la persona
    estado text,                           -- etiqueta libre que la persona va actualizando (ej: "Mejorando")

    resuelto boolean not null default false,  -- true = la persona dio esta situación/emoción por totalmente solucionada
    reflexion_final text,                     -- mensaje que se escribe a sí misma sobre cómo lo resolvió, solo visible si resuelto=true
    flor text,                                -- flor propia elegida para esta planta (emoji); null = usa la general de Personalización

    creado_en timestamptz not null default now(),
    actualizado_en timestamptz not null default now()
);

create index if not exists idx_temas_usuario on temas_seguimiento(usuario_id);

-- Si la tabla ya existía de antes, correr esta línea para agregar la
-- columna nueva sin perder los datos:
-- alter table temas_seguimiento add column if not exists flor text;
