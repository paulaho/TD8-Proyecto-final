-- Tabla de reportes emocionales (registro de pensamiento / thought record).
-- Correr esto DESPUÉS de supabase_usuarios_regulacion.sql y de
-- supabase_temas_seguimiento.sql (esta tabla hace referencia a esa), en
-- el mismo proyecto de Supabase.

create table if not exists reportes_emocionales (
    id bigint generated always as identity primary key,
    usuario_id bigint not null references usuarios_regulacion(id),
    tema_id bigint references temas_seguimiento(id),  -- si es parte de un pensamiento que se viene siguiendo
    fecha timestamptz not null default now(),

    situacion text not null,
    tipo_situacion text,                   -- ej: duelo, conflicto, preocupacion, etc. (cambia qué preguntas se hicieron)
    emocion_inicial text not null,
    intensidad_inicial int not null,       -- 0 a 10

    pensamiento_automatico text not null,
    creencia_inicial_pct int not null,     -- 0 a 100

    evidencia_a_favor text,
    evidencia_en_contra text,
    perspectiva_amigo text,

    distorsiones text,                     -- lista separada por coma

    pensamiento_alternativo text not null,
    creencia_final_pct int not null,       -- 0 a 100

    rondas_reflexion int not null default 0,  -- vueltas extra cuando la creencia no aflojaba
    reflexiones_extra text,                   -- respuestas de esas vueltas extra, separadas por " | "

    recomendaciones_dadas text,            -- lista separada por coma

    feedback_recomendacion_anterior text,  -- si retomó un tema: si probó algo de la vez pasada y si le sirvió
    feedback_recomendacion_porque text     -- por qué cree que le funcionó (o no) lo que probó
);

create index if not exists idx_reportes_usuario on reportes_emocionales(usuario_id);

-- Si la tabla ya existía de antes (proyecto de Supabase ya creado), correr
-- también estas líneas para agregar las columnas nuevas sin perder los datos:
-- alter table reportes_emocionales add column if not exists feedback_recomendacion_anterior text;
-- alter table reportes_emocionales add column if not exists feedback_recomendacion_porque text;
