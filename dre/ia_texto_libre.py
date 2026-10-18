from __future__ import annotations
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from google import genai
from pydantic import BaseModel, Field
import random

from dre.dificultad_contraargumento import (
    configuracion_nivel,
    banda,
    fase,
    tramo,
    angulo_pedido,
    ANGULOS,
    ESTRATEGIA_ACTUAL,
)
from dre.fallas_contraargumento import (
    estado_fallas,
    TODAS_LAS_FALLAS,
    PRIORIDAD_FALLAS,
    seleccionar_falla_principal,
)


# ==========================================================
# SCHEMAS PYDANTIC — Generación de situaciones
# ==========================================================

class SituacionTextoLibre(BaseModel):
    situacion: str = Field(description="Descripción de la situación concreta en 2-4 oraciones.")
    lectura_negativa_implicita: str = Field(description="La peor lectura automática o distorsión que la situación tiende a disparar.")
    reappraisal_inicial: str = Field(description="Interpretación alternativa inicial dada por la app usando Reconstrual.")
    punto_debil: str = Field(description="Dónde está el límite o punto débil de este reappraisal inicial.")


class BatchSituacionesTextoLibre(BaseModel):
    situaciones: List[SituacionTextoLibre] = Field(min_length=5, max_length=5)


# ==========================================================
# SCHEMAS PYDANTIC — Evaluación de respuestas
# ==========================================================

class EvaluacionItem(BaseModel):
    feedback: str = Field(description="Feedback cálido y constructivo de máximo 45 palabras.")
    fallas_detectadas: List[str] = Field(
        default_factory=list,
        description="Lista de códigos de fallas detectadas (solo de las activas en frena o señala).",
    )


class BatchEvaluacionTextoLibre(BaseModel):
    correcciones: List[EvaluacionItem] = Field(min_length=5, max_length=5)


# Alias para compatibilidad
CorrectionItem = EvaluacionItem
BatchCorreccionesTextoLibre = BatchEvaluacionTextoLibre


# ==========================================================
# SCHEMAS PYDANTIC — Ejemplo en tercer intento
# ==========================================================

class EjemploResolucion(BaseModel):
    contraargumento_ejemplo: str = Field(description="Ejemplo modelo de contraargumento para esta situación.")
    nuevo_reappraisal_ejemplo: str = Field(description="Ejemplo modelo de nuevo reappraisal integrador.")
    explicacion: str = Field(description="Breve explicación de por qué este ejemplo desarma la objeción.")


# ==========================================================
# CLIENTE GEMINI
# ==========================================================

try:
    _gemini_client = genai.Client()
except Exception:
    _gemini_client = None


def _obtener_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = genai.Client()
    return _gemini_client

_PERFILES_CATEGORIA = {
    "familia": {
        "nombre": "Familia",
        "ambito": "el ámbito familiar (padres, hermanos, abuelos, tíos/primos, familia política)",
        "vinculos": "madre, padre, hermano/a si corresponde, abuelos, tíos/primos, familia política si está en pareja, hijos/as si corresponde",
    },
    "salud": {
        "nombre": "Salud",
        "ambito": "la salud y el cuidado propio (hábitos, descanso, controles, comentarios de otros sobre cómo te cuidás), SIN diagnósticos ni cuadros clínicos",
        "vinculos": "familiares, amistades, pareja, profesionales de salud, compañeros/as de actividad física",
    },
    "vinculos": {
        "nombre": "Vínculos",
        "ambito": "los vínculos sociales y afectivos (amistades, pareja, conocidos, grupos), sin centrarse en la familia de origen",
        "vinculos": "amigos/as, pareja o ex pareja, conocidos/as, grupos de amigos, vecinos/as",
    },
    "trabajo": {
        "nombre": "Trabajo o estudio",
        "ambito": "el trabajo o el estudio (jefes/as, compañeros/as, docentes, exámenes, entregas, devoluciones, reuniones)",
        "vinculos": "jefe/a, compañeros/as, docentes, clientes, compañeros/as de cursada",
    },
}


def _perfil_categoria(categoria):
    c = str(categoria or "familia").lower()
    if "salud" in c:
        return _PERFILES_CATEGORIA["salud"]
    if any(k in c for k in ("vinc", "pareja", "amig", "social")):
        return _PERFILES_CATEGORIA["vinculos"]
    if any(k in c for k in ("trabaj", "estud")):
        return _PERFILES_CATEGORIA["trabajo"]
    return _PERFILES_CATEGORIA["familia"]

_DISPARADORES = {
    "familia": {
        "propios": [
            "algo que tenés que contarle a tu familia (una decisión, una noticia) y te preocupa cómo lo van a tomar",
            "una reunión o fecha familiar que se acerca y te genera tensión o cansancio anticipado",
            "sentir que no le dedicás suficiente tiempo a tu familia y sentirte culpable",
            "un recuerdo o una situación pasada con tu familia que te vuelve a la cabeza y no podés soltar",
            "una responsabilidad de la casa o del cuidado de alguien que sentís que recae en vos",
            "una expectativa familiar sobre tu futuro (estudio, trabajo, mudanza) que sentís que no vas a cumplir",
        ],
        "otros": [
            "un silencio, una demora o un gesto de un familiar que no sabés cómo interpretar",
            "un comentario o una decisión de un familiar que te dolió o te desconcertó",
            "una diferencia de criterio con un familiar sobre algo cotidiano",
        ],
    },
    "salud": {
        "propios": [
            "una molestia o dolor físico que aparece y te hace preocupar (sin diagnósticos ni cuadros clínicos)",
            "esperar el resultado de un estudio o una consulta y sentir ansiedad por lo que pueda salir",
            "haber dejado una rutina de cuidado (ejercicio, alimentación, descanso) y sentirte culpable o sin fuerza de voluntad",
            "una época de mal descanso o de cansancio que te hace temer que algo anda mal",
            "ir a una consulta o a un control y ponerte nervioso/a antes",
            "un cambio en tu cuerpo o en tu energía que notás y te inquieta",
            "compararte con personas que parecen cuidarse mejor que vos",
        ],
        "otros": [
            "un comentario de alguien sobre tu cuerpo, tu alimentación o tus hábitos",
            "un consejo no pedido sobre tu salud de alguien cercano",
        ],
    },
    "vinculos": {
        "propios": [
            "ver en redes fotos o historias de un plan al que no te invitaron",
            "sentir ansiedad antes de un encuentro social, una juntada o una cita",
            "sentirte solo/a o sin con quién hablar de lo que te pasa",
            "compararte con personas que parecen tener más vida social o más pareja",
            "darle vueltas a algo que dijiste o hiciste en una juntada y temer haber quedado mal",
            "tener que decir que no a un plan o poner un límite y sentirte culpable",
            "conocer gente nueva o entrar a un grupo y sentirte fuera de lugar",
        ],
        "otros": [
            "un mensaje que queda sin responder durante mucho tiempo",
            "un plan que alguien cancela a último momento",
            "un comentario o una actitud de un amigo/a o de una pareja que te dejó pensando",
        ],
    },
    "trabajo": {
        "propios": [
            "un examen que se acerca y el miedo a desaprobar",
            "una presentación o exposición frente a otras personas (jefe/a, docentes, grupo) y la ansiedad que te genera",
            "una entrega o tarea con poco tiempo que sentís que no vas a llegar a terminar",
            "un error que cometiste en una tarea y la sensación de haber quedado mal",
            "sentir que otras personas avanzan más rápido o rinden mejor que vos",
            "esperar una respuesta importante (una nota, una entrevista, una postulación)",
            "sobrecarga de tareas o pendientes que te hace sentir que no das abasto",
        ],
        "otros": [
            "una devolución o corrección de un/a jefe/a o docente",
            "un mail o mensaje laboral o académico que no te responden",
            "un comentario de un/a compañero/a de trabajo o de estudio",
        ],
    },
}


def _clave_perfil(perfil):
    return next((k for k, v in _PERFILES_CATEGORIA.items() if v is perfil), "familia")


def _asignar_disparadores(perfil, nivel_inicial):
    """Asigna a cada uno de los 5 niveles un tipo de disparador distinto:
    3 situaciones sobre algo propio de la persona y 2 sobre algo que
    hace o dice otra persona, mezcladas al azar."""
    pool = _DISPARADORES.get(_clave_perfil(perfil), _DISPARADORES["familia"])
    rnd = random.Random()
    elegidos = rnd.sample(pool["propios"], 3) + rnd.sample(pool["otros"], min(2, len(pool["otros"])))
    if len(elegidos) < 5:
        resto = [d for d in pool["propios"] if d not in elegidos]
        elegidos += rnd.sample(resto, 5 - len(elegidos))
    rnd.shuffle(elegidos)
    lineas = "\n".join(f"    - NIVEL {nivel_inicial + i}: {d}" for i, d in enumerate(elegidos))
    return (
        "DISPARADOR ASIGNADO A CADA SITUACIÓN (obligatorio, en este orden):\n"
        f"{lineas}\n"
        "    - Cada situación gira en torno a su disparador, con detalles concretos y propios de la persona. "
        "El disparador indica el TIPO de escena: redactala con tus palabras, no copies la frase.\n"
        "    - No hace falta que alguien le diga algo a la persona: puede ser algo que siente, que le pasa o que tiene que enfrentar.\n"
        "    - PROHIBIDO que más de 2 de las 5 situaciones consistan en un comentario o una actitud de otra persona.\n"
        "    - Las 5 escenas deben ser de tipos claramente distintos entre sí."
    )


def _bloque_personalizacion(perfil, contexto, genero, edad_str):
    ocupacion = contexto.get("ocupacion", "No especificado")
    base = (
        "INFORMACIÓN PERSONALIZADA DEL USUARIO:\n"
        f"    - Género: {genero}\n"
        f"    - Edad: {edad_str}\n"
        f"    - Ocupación: {ocupacion}\n"
    )
    if perfil is _PERFILES_CATEGORIA["familia"]:
        return (
            base
            + f"    - Convivencia: {contexto.get('convivencia', 'No especificado')}\n"
            + f"    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}\n"
            + f"    - Estado en pareja: {contexto.get('pareja', 'No especificado')}\n\n"
            "    CÓMO USAR LOS DATOS PERSONALES:\n"
            "    - Convivencia: ambientá las situaciones según con quién vive (solo/a: contacto a distancia y reuniones; "
            "con padres: convivencia diaria; con pareja: mezclar familia de origen y política; con amigos/as: mezclar vida compartida "
            "y familia de origen; con hijos/as: crianza y relación con sus propios padres).\n"
            "    - Hermanos: si respondió \"No tengo hermanos\", NO generes situaciones con hermanos. Si tiene, incluilos en algunas, no en todas.\n"
            "    - Pareja: si está en pareja, familia política en 1 situación como máximo; si no, no menciones pareja.\n"
            "    - Ocupación: solo como trasfondo (agenda, cansancio, tiempo), nunca como tema central.\n"
            "    - Edad y género: ajustá escenarios, vocabulario y personajes en segunda persona, sin estereotipos.\n"
            f"    - Repartí los vínculos entre: {perfil['vinculos']}. Ningún vínculo en más de 2 de las 5 situaciones.\n"
            "    - No nombres los datos del perfil de forma forzada o literal; que se noten orgánicamente en el escenario."
        )

    if perfil is _PERFILES_CATEGORIA["trabajo"]:
        if ocupacion == "Estudio":
            hint = "la persona estudia: priorizá situaciones de estudio (exámenes, cursada, trabajos prácticos, grupos de estudio)."
        elif ocupacion == "Trabajo":
            hint = "la persona trabaja: priorizá situaciones laborales (tareas, reuniones, jefes/as, compañeros/as, entregas)."
        elif ocupacion == "Estudio y trabajo":
            hint = "la persona estudia y trabaja: mezclá situaciones de estudio y laborales, y tensiones por combinar ambas."
        else:
            hint = "la persona no estudia ni trabaja por ahora: usá cursos, trámites, búsqueda laboral, entrevistas o proyectos propios."
        extra_ocupacion = f"    - Ocupación: {hint}\n"
    else:
        extra_ocupacion = "    - Ocupación: solo como trasfondo (agenda, cansancio, tiempo), nunca como tema central.\n"

    if perfil is _PERFILES_CATEGORIA["vinculos"]:
        extra_pareja = (
            "    - Pareja: "
            + ("está en pareja: podés usar a su pareja en hasta 2 situaciones.\n"
               if str(contexto.get("pareja", "")).lower().startswith("s")
               else "NO está en pareja: no uses pareja ni ex pareja; usá amistades, conocidos y grupos.\n")
        )
    else:
        extra_pareja = ""

    return (
        base
        + "\n    CÓMO USAR LOS DATOS PERSONALES:\n"
        f"    - La categoría es {perfil['nombre']} y el centro de TODAS las situaciones es: {perfil['ambito']}.\n"
        "    - NO uses convivencia, hermanos ni familia para armar las escenas. Podés mencionar a un familiar en 1 de las 5 situaciones "
        "como máximo, solo como detalle de fondo y nunca como quien causa el malestar.\n"
        + extra_ocupacion
        + extra_pareja
        + "    - Edad y género: ajustá escenarios, vocabulario y personajes en segunda persona, sin estereotipos.\n"
        "    - No nombres los datos del perfil de forma forzada o literal; que se noten orgánicamente en el escenario."
    )

# ==========================================================
# GENERACIÓN DE BATCHES (PROGRESIVA POR NIVELES)
# ==========================================================

def _armar_especificacion_niveles(nivel_inicial: int) -> str:
    """
    Construye la descripción detallada de los 5 niveles consecutivos
    para incluirla en el prompt de Gemini.
    """
    lineas = []
    for i in range(5):
        lvl = nivel_inicial + i
        cfg = configuracion_nivel(lvl)
        ang_str = "A libre elección de la persona"
        if cfg["angulo_pedido"]:
            ang_info = ANGULOS[cfg["angulo_pedido"]]
            ang_str = f"Ángulo {cfg['angulo_pedido']}: {ang_info['nombre']} ('{ang_info['guia']}')"

        lineas.append(
            f"NIVEL {lvl} (Posición {i+1} de 5 en el batch):\n"
            f"- Banda: {cfg['banda']} | Fase: {cfg['fase']}"
            + (f" | Tramo: {cfg['tramo']}" if cfg['tramo'] else "")
            + f"\n- Tipo de situación: {cfg['tipo_situacion']} ({cfg['intensidad']}, {cfg['enfoque']})\n"
            f"  Detalle situación: {cfg['descripcion_situacion']}\n"
            f"- Tipo de lectura negativa implícita: {cfg['tipo_lectura']}\n"
            f"  Detalle lectura: {cfg['descripcion_lectura']}\n"
            f"- Tipo de reappraisal inicial: {cfg['tipo_reappraisal']}\n"
            f"  Detalle reappraisal: {cfg['descripcion_reappraisal']}\n"
            f"- Ángulo requerido para contraargumento: {ang_str}\n"
            f"- Estrategia: Reconstrual ({ESTRATEGIA_ACTUAL['definicion']})"
        )
    return "\n\n".join(lineas)


def generar_batch_texto_libre(estado, nivel_inicial: int = 1, categoria: str = "familia"):
    """
    Genera 5 situaciones para el juego de Contraargumento.
    La dificultad está estrictamente determinada por los 5 niveles consecutivos [nivel_inicial .. nivel_inicial+4].
    El perfil_contexto solo se usa para personalizar el ámbito cotidiano.
    """
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    edad = estado.get("edad")
    edad_str = f"{edad} años" if edad is not None else "No especificada"
    perfil_cat = _perfil_categoria(categoria)
    nombre_cat = perfil_cat["nombre"]    
    bloque_personal = _bloque_personalizacion(perfil_cat, contexto, genero, edad_str)
    bloque_disparadores = _asignar_disparadores(perfil_cat, nivel_inicial)
    spec_niveles = _armar_especificacion_niveles(nivel_inicial)

    prompt = f"""
    Generá EXACTAMENTE 5 situaciones de regulación emocional mediante
    cognitive reappraisal (modo Contraargumento) en la categoría {nombre_cat}.

    {bloque_personal}

    {bloque_disparadores}

    ESPECIFICACIÓN OBLIGATORIA DE CADA UNO DE LOS 5 NIVELES (GENERAR EN ESTE ORDEN EXACTO):
    {spec_niveles}

    CAMPOS REQUERIDOS PARA CADA SITUACIÓN:
    1. "situacion": descripción breve (2-4 oraciones) de una situación concreta que genera malestar y que respete 
        el DISPARADOR asignado a ese nivel. Usá segunda persona. Puede no haber ningún diálogo ni comentario de otra 
        persona: lo central es lo que la persona siente y piensa. Específica y realista.
    2. "lectura_negativa_implicita": la peor lectura o pensamiento automático que esa situación tiende a disparar
       (puede ser sobre sí misma, sobre el futuro o sobre otra persona; ej.: "Seguro es algo grave", "Voy a desaprobar", 
       "Seguro está enojado/a conmigo"). Ajustada al Tipo de Lectura pedido.
    3. "reappraisal_inicial": UNA interpretación alternativa inicial razonable que reduzca el malestar, basada en
       la estrategia Reconstrual. Debe coincidir con el Tipo de Reappraisal pedido para ese nivel.
       - Siempre es razonable (nunca una respuesta absurda o de evasión).
       - Siempre tiene un punto débil o límite acorde a su Tipo (Tipo I: afirma más de lo que sabe con palabras señalables;
         Tipo II: se apoya en un supuesto sin verificar; Tipo III: sólida pero deja algo sin resolver).
       - Sin positivismo mágico, sin negar los hechos ni minimizar emociones.
    4. "punto_debil": explicación concisa de dónde está el punto débil o límite del reappraisal inicial.

    REQUISITOS ADICIONALES PARA FASE 2 SEGÚN EL ÁNGULO:
    - Si pide Ángulo 2 (un dato que no cierra): la situación DEBE traer al menos un dato concreto que el reappraisal inicial NO tenga en cuenta.
    - Si pide Ángulo 3 (otra explicación): el reappraisal inicial debe apoyarse en una explicación probable de lo que pasó.

    REGLAS GENERALES:
    - Las 5 situaciones deben ser DISTINTAS entre sí.
    - Situaciones cotidianas reales de {perfil_cat['ambito']}, no todas basadas en lo que otra persona dice o hace.
    - Con lectura Tipo III, NADA en la situación ni en el reappraisal puede obligar a la persona a demostrar que algo real es falso.
    - Usá español argentino simple.
    - Evitá: suicidio, autolesión, violencia grave, abuso, diagnósticos médicos.
    - NO repitas clichés como "te critican en la mesa" o "discusión por el teléfono".
    """

    client = _obtener_gemini_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": BatchSituacionesTextoLibre,
        },
    )

    print(f"Gemini respondió batch niveles {nivel_inicial} a {nivel_inicial + 4}")

    batch = BatchSituacionesTextoLibre.model_validate_json(response.text)
    situaciones = [s.model_dump() for s in batch.situaciones]

    if len(situaciones) != 5:
        raise ValueError(f"Gemini devolvió {len(situaciones)} situaciones en lugar de 5")

    # Adjuntar metadatos por Python (no Gemini)
    for i, s in enumerate(situaciones):
        lvl = nivel_inicial + i
        cfg = configuracion_nivel(lvl)
        s["nivel"] = lvl
        s["banda"] = cfg["banda"]
        s["fase"] = cfg["fase"]
        s["tramo"] = cfg["tramo"]
        s["tipo_situacion"] = cfg["tipo_situacion"]
        s["tipo_reappraisal"] = cfg["tipo_reappraisal"]
        s["tipo_lectura"] = cfg["tipo_lectura"]
        s["estrategia"] = cfg["estrategia"]
        s["angulo_pedido"] = cfg["angulo_pedido"]

    return situaciones


def generar_batch_texto_libre_adaptativo(historial_texto, estado, nivel_inicial: int = 1, categoria: str = "familia"):
    """
    Genera 5 situaciones adaptadas al desempeño previo en el juego de Contraargumento.
    IMPORTANTE: La dificultad está fijada estrictamente por los niveles [nivel_inicial .. nivel_inicial+4].
    El historial solo orienta temas, focos y qué fallas o ángulos reforzar, NUNCA altera la dificultad ni el perfil.
    """
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    edad = estado.get("edad")
    edad_str = f"{edad} años" if edad is not None else "No especificada"
    perfil_cat = _perfil_categoria(categoria)
    nombre_cat = perfil_cat["nombre"]
    bloque_personal = _bloque_personalizacion(perfil_cat, contexto, genero, edad_str)
    bloque_disparadores = _asignar_disparadores(perfil_cat, nivel_inicial)
    spec_niveles = _armar_especificacion_niveles(nivel_inicial)

    historial_texto_json = json.dumps(historial_texto, ensure_ascii=False, indent=2)

    prompt = f"""
    Generá EXACTAMENTE 5 situaciones de regulación emocional mediante
    cognitive reappraisal (modo Contraargumento) en la categoría {nombre_cat}.

    {bloque_personal}

    {bloque_disparadores}

    HISTORIAL DE DESEMPEÑO PREVIO DEL USUARIO:
    {historial_texto_json}

    PAUTAS DE ADAPTACIÓN CON EL HISTORIAL:
    - El historial SOLO ajusta temas y foco: analizá qué ángulos o fallas le costaron más al usuario o qué situaciones le generaron reintentos para orientar los temas y ejercitar esos puntos desde ángulos novedosos.
    - NUNCA alteres ni subas/bajes la dificultad fijada por los niveles (la dificultad está estrictamente determinada por la especificación de niveles).
    - NUNCA alteres ni relajes la personalización por perfil (respetá rigurosamente las pautas de CÓMO USAR LOS DATOS PERSONALES).
    - No copies situaciones anteriores del historial.

    ESPECIFICACIÓN OBLIGATORIA DE CADA UNO DE LOS 5 NIVELES (GENERAR EN ESTE ORDEN EXACTO):
    {spec_niveles}

    CAMPOS REQUERIDOS PARA CADA SITUACIÓN:
    1. "situacion": descripción breve (2-4 oraciones) de una situación concreta de {perfil_cat['ambito']} que genera malestar
       y que respete el DISPARADOR asignado a ese nivel. Usá segunda persona. Puede no haber ningún diálogo ni comentario de 
       otra persona: lo central es lo que la persona siente y piensa. Específica y realista.
    2. "lectura_negativa_implicita": la peor lectura o pensamiento automático que esa situación tiende a disparar (puede ser 
        sobre sí misma, sobre el futuro o sobre otra persona; ej.: "Seguro es algo grave", "Voy a desaprobar", "Seguro está enojado/a conmigo").
    3. "reappraisal_inicial": UNA interpretación alternativa inicial razonable que reduzca el malestar, basada en
       Reconstrual y acorde a su Tipo (Tipo I, II o III).
       - Siempre es razonable (nunca una respuesta absurda o de evasión).
       - Siempre tiene un punto débil o límite acorde a su Tipo (Tipo I: afirma más de lo que sabe con palabras señalables;
         Tipo II: se apoya en un supuesto sin verificar; Tipo III: sólida pero deja algo sin resolver).
       - Sin positivismo mágico, sin negar los hechos ni minimizar emociones.
    4. "punto_debil": explicación concisa de dónde está el punto débil o límite del reappraisal inicial.

    REQUISITOS ADICIONALES PARA FASE 2 SEGÚN EL ÁNGULO:
    - Si pide Ángulo 2 (un dato que no cierra): la situación DEBE traer al menos un dato concreto que el reappraisal inicial NO tenga en cuenta.
    - Si pide Ángulo 3 (otra explicación): el reappraisal inicial debe apoyarse en una explicación probable de lo que pasó.

    REGLAS GENERALES:
    - 5 situaciones distintas entre sí y distintas al historial.
    - Situaciones cotidianas reales de {perfil_cat['ambito']}, no todas basadas en lo que otra persona dice o hace.
    - Con lectura Tipo III, nada en la situación ni en el reappraisal obliga a negar hechos reales.
    - Usá español argentino simple.
    - Evitá: suicidio, autolesión, violencia grave, abuso, diagnósticos médicos.
    - NO repitas clichés como "te critican en la mesa" o "discusión por el teléfono".
    """

    client = _obtener_gemini_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": BatchSituacionesTextoLibre,
        },
    )

    print(f"Gemini respondió batch adaptativo niveles {nivel_inicial} a {nivel_inicial + 4}")

    batch = BatchSituacionesTextoLibre.model_validate_json(response.text)
    situaciones = [s.model_dump() for s in batch.situaciones]

    if len(situaciones) != 5:
        raise ValueError(f"Gemini devolvió {len(situaciones)} situaciones en lugar de 5")

    # Adjuntar metadatos por Python
    for i, s in enumerate(situaciones):
        lvl = nivel_inicial + i
        cfg = configuracion_nivel(lvl)
        s["nivel"] = lvl
        s["banda"] = cfg["banda"]
        s["fase"] = cfg["fase"]
        s["tramo"] = cfg["tramo"]
        s["tipo_situacion"] = cfg["tipo_situacion"]
        s["tipo_reappraisal"] = cfg["tipo_reappraisal"]
        s["tipo_lectura"] = cfg["tipo_lectura"]
        s["estrategia"] = cfg["estrategia"]
        s["angulo_pedido"] = cfg["angulo_pedido"]

    return situaciones


# ==========================================================
# EVALUACIÓN DE RESPUESTAS (BATCH Y REINTENTOS INDIVIDUALES)
# ==========================================================

def _armar_instrucciones_fallas(frena_set: Set[str], señala_set: Set[str]) -> str:
    """
    Construye la guía de fallas relevantes para el prompt de evaluación.
    """
    activas = frena_set | señala_set
    if not activas:
        return "Para este nivel no hay fallas específicas que frenen o señalen; evaluá la coherencia general."

    lineas = []
    lineas.append("FALLAS ACTIVAS A EVALUAR EN ESTE EJERCICIO:")
    for cod in PRIORIDAD_FALLAS:
        if cod in activas:
            info = TODAS_LAS_FALLAS[cod]
            estado_str = "FRENA EL AVANCE" if cod in frena_set else "SEÑALA SIN FRENAR"
            lineas.append(
                f"- [{cod}] {info['nombre']} ({estado_str}):\n"
                f"  Cómo se reconoce: {info['descripcion']}\n"
                f"  Ejemplo: {info['ejemplo']}"
            )
    return "\n".join(lineas)


def evaluar_batch_texto_libre(ejercicios: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Evalúa en 1 sola llamada batch a Gemini las 5 tuplas completas.
    Calcula en Python 'resultado' ("pasa" o "frena") y ajusta el prefijo.
    """
    if len(ejercicios) != 5:
        raise ValueError(f"Se esperaban 5 ejercicios para evaluar, se recibieron {len(ejercicios)}")

    # Preparar el contenido estructurado de cada ejercicio
    ejercicios_para_prompt = []
    for i, ej in enumerate(ejercicios):
        frena_set = set(ej.get("frena", []))
        señala_set = set(ej.get("señala", []))
        guia_fallas = _armar_instrucciones_fallas(frena_set, señala_set)

        ejercicios_para_prompt.append({
            "posicion": i + 1,
            "nivel": ej.get("nivel", 1),
            "banda": ej.get("banda", 1),
            "tipo_lectura": ej.get("tipo_lectura", "Tipo I"),
            "angulo_pedido": ej.get("angulo_pedido"),
            "situacion": ej["situacion"],
            "lectura_negativa_implicita": ej.get("lectura_negativa_implicita", ""),
            "reappraisal_inicial": ej["reappraisal_inicial"],
            "punto_debil": ej.get("punto_debil", ""),
            "contraargumento": ej["contraargumento"],
            "emocion": ej["emocion"],
            "nuevo_reappraisal": ej["nuevo_reappraisal"],
            "frena": ej.get("frena", []),
            "señala": ej.get("señala", []),
            "guia_fallas": guia_fallas,
        })

    prompt = f"""
    Evaluá las siguientes 5 respuestas completas de regulación emocional mediante
    cognitive reappraisal (modo Contraargumento) de un usuario.
    Devolvé un comentario de corrección conciso (MÁXIMO 45 palabras) y la lista de códigos de fallas detectadas por cada una.

    CONTEXTO DE LA TAREA:
    Cada situación presenta:
    1. "situacion": Hecho que genera malestar.
    2. "lectura_negativa_implicita": Pensamiento automático negativo que suele disparar.
    3. "reappraisal_inicial": Reappraisal 1 dado por la app (con su "punto_debil").
    4. "contraargumento": Objeción redactada por el usuario al Reappraisal 1.
    5. "emocion": Emoción asociada al contraargumento.
    6. "nuevo_reappraisal": Nuevo reappraisal (Reappraisal 2) que debe responder a su propia objeción.

    REGLAS ESTRICTAS DE EVALUACIÓN Y FEEDBACK:
    1. Si hay varias fallas, marcá UNA sola en el feedback (la más importante).
       Prioridad de fallas: FC0, FC1, FCD, FCG, FCA, F1, F2, F3, F4, F5, FG, FP.
       Primero las que frenan ('frena'), luego las que se señalan ('señala').
       Las fallas del contraargumento tienen prioridad porque el nuevo reappraisal se construye sobre él.
    2. En el feedback: primero destacá lo que está bien y luego lo que falta.
    3. Usá lenguaje común. NUNCA menciones nombres técnicos de fallas ni digas "positividad forzada" (decí "salteás que esto puede doler").
    4. NUNCA uses palabras como "incorrecto" o "mal". Siempre terminá con una pregunta o pista para seguir, no con un veredicto.
    5. Evaluá qué hace la respuesta, no cómo está escrita: no penalices ortografía, coloquialismos ni respuestas cortas.
    6. Con lectura Tipo III, JAMÁS pidas que la persona demuestre que algo real es falso.
    7. NO des un ejemplo completo de respuesta aquí (eso solo se hace si el usuario agota sus intentos).
    8. En el campo "fallas_detectadas", incluí los códigos de las fallas encontradas que pertenezcan a 'frena' o 'señala' del ejercicio.
    9. Máximo 45 palabras por feedback.

    EJERCICIOS A EVALUAR:
    {json.dumps(ejercicios_para_prompt, ensure_ascii=False, indent=2)}

    Devolvé exactamente 5 correcciones en el array "correcciones", en el mismo orden.
    """

    client = _obtener_gemini_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": BatchEvaluacionTextoLibre,
        },
    )

    print("Gemini evaluó el batch de texto libre")

    batch = BatchEvaluacionTextoLibre.model_validate_json(response.text)
    correcciones = [c.model_dump() for c in batch.correcciones]

    if len(correcciones) != 5:
        raise ValueError(f"Gemini devolvió {len(correcciones)} correcciones en lugar de 5")

    # Procesar resultado en Python (NO Gemini) y formatear prefijo
    for ej, corr in zip(ejercicios, correcciones):
        frena_set = set(ej.get("frena", []))
        señala_set = set(ej.get("señala", []))

        # Filtrar solo a las activas
        raw_fallas = corr.get("fallas_detectadas", [])
        fallas_activas = [f for f in raw_fallas if f in frena_set or f in señala_set]
        corr["fallas_detectadas"] = fallas_activas

        # Python calcula si frena o pasa
        frena_match = any(f in frena_set for f in fallas_activas)
        corr["resultado"] = "frena" if frena_match else "pasa"

        # Limpiar y asegurar prefijos consistentes: ⚠️ si frena, 💡 si señala, ✅ si pasa limpio
        fb = corr["feedback"].strip()
        for p in ["✅", "⚠️", "💡", "✓", "✗"]:
            if fb.startswith(p):
                fb = fb[len(p):].strip()

        if corr["resultado"] == "frena":
            corr["feedback"] = f"⚠️ {fb}"
        elif any(f in señala_set for f in fallas_activas):
            corr["feedback"] = f"💡 {fb}"
        else:
            corr["feedback"] = f"✅ {fb}"

    return correcciones


def evaluar_intento_texto_libre(ejercicio: Dict[str, Any], numero_intento: int = 1) -> Dict[str, Any]:
    """
    Evalúa una única situación durante un reintento (intento 1, 2 o 3).
    Aplica ayuda creciente según el número de intento.
    """
    frena_set = set(ejercicio.get("frena", []))
    señala_set = set(ejercicio.get("señala", []))
    guia_fallas = _armar_instrucciones_fallas(frena_set, señala_set)

    instruccion_ayuda = ""
    if numero_intento == 1:
        instruccion_ayuda = "Intento 1: Señalá con claridad la falla principal con tono constructivo."
    elif numero_intento == 2:
        pregunta_guia = ""
        ang = ejercicio.get("angulo_pedido")
        if ang and ang in ANGULOS:
            pregunta_guia = ANGULOS[ang]["guia"]
        else:
            pregunta_guia = "¿Qué parte puntual de lo que dice no sabés con certeza y qué otra explicación plausible habría?"
        instruccion_ayuda = (
            f"Intento 2: Además de señalar qué ajustar, incluí obligatoriamente esta pregunta guía concreta "
            f"para orientar a la persona: '{pregunta_guia}'."
        )
    elif numero_intento >= 3:
        instruccion_ayuda = "Intento 3: Evaluá si la respuesta es aceptable o si aún mantiene la objeción."

    prompt = f"""
    Evaluá el siguiente reintento (Intento {numero_intento} de 3) de regulación emocional
    en el juego de Contraargumento (Familia).

    DATOS DEL EJERCICIO:
    - Nivel: {ejercicio.get('nivel', 1)} | Banda: {ejercicio.get('banda', 1)}
    - Situación: {ejercicio['situacion']}
    - Lectura negativa implícita: {ejercicio.get('lectura_negativa_implicita', '')}
    - Reappraisal 1: {ejercicio['reappraisal_inicial']}
    - Punto débil: {ejercicio.get('punto_debil', '')}
    - Contraargumento redactado: {ejercicio['contraargumento']}
    - Emoción: {ejercicio['emocion']}
    - Nuevo Reappraisal redactado: {ejercicio['nuevo_reappraisal']}
    - Fallas que frenan: {ejercicio.get('frena', [])}
    - Fallas que señalan: {ejercicio.get('señala', [])}

    {guia_fallas}

    PAUTAS DE AYUDA CRECIENTE:
    {instruccion_ayuda}

    REGLAS DE TONO:
    - Tono cálido, argentino simple con voseo.
    - Primero lo que está bien, luego lo que falta.
    - No uses nombres técnicos. No digas 'incorrecto' o 'mal'. Terminá con una pregunta o pista.
    - Máximo 45 palabras.
    """

    client = _obtener_gemini_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": EvaluacionItem,
        },
    )

    item = EvaluacionItem.model_validate_json(response.text).model_dump()

    # Procesar resultado en Python
    raw_fallas = item.get("fallas_detectadas", [])
    fallas_activas = [f for f in raw_fallas if f in frena_set or f in señala_set]
    item["fallas_detectadas"] = fallas_activas

    frena_match = any(f in frena_set for f in fallas_activas)
    item["resultado"] = "frena" if frena_match else "pasa"

    fb = item["feedback"].strip()
    for p in ["✅", "⚠️", "💡", "✓", "✗"]:
        if fb.startswith(p):
            fb = fb[len(p):].strip()

    if item["resultado"] == "frena":
        item["feedback"] = f"⚠️ {fb}"
    elif any(f in señala_set for f in fallas_activas):
        item["feedback"] = f"💡 {fb}"
    else:
        item["feedback"] = f"✅ {fb}"

    return item


def generar_ejemplo_texto_libre(ejercicio: Dict[str, Any]) -> Dict[str, Any]:
    """
    Genera un ejemplo de contraargumento y nuevo reappraisal para una situación
    cuando el usuario no logra pasar en el 3er intento.
    Permite al usuario avanzar con 'avanzó con ejemplo'.
    """
    ang_desc = ""
    ang = ejercicio.get("angulo_pedido")
    if ang and ang in ANGULOS:
        ang_desc = f"Ángulo {ang}: {ANGULOS[ang]['nombre']} ({ANGULOS[ang]['descripcion']})"

    prompt = f"""
    Generá un EJEMPLO MODELO de resolución para una persona que intentó 3 veces y necesita
    ver cómo se resuelve esta situación de Contraargumento.

    DATOS DE LA SITUACIÓN:
    - Nivel: {ejercicio.get('nivel', 1)}
    - Situación: {ejercicio['situacion']}
    - Reappraisal 1 inicial dado por la app: {ejercicio['reappraisal_inicial']}
    - Punto débil del reappraisal inicial: {ejercicio.get('punto_debil', '')}
    {f"- Ángulo requerido: {ang_desc}" if ang_desc else ""}
    - Estrategia: Reconstrual ({ESTRATEGIA_ACTUAL['definicion']})

    REQUISITOS DEL EJEMPLO:
    1. "contraargumento_ejemplo": Un contraargumento claro y honesto que señale el punto débil.
    2. "nuevo_reappraisal_ejemplo": Un nuevo reappraisal que integre esa duda y reestructure la situación
       con realismo y compasión (sin positivismo mágico ni negar lo ocurrido).
    3. "explicacion": 1 o 2 oraciones cálidas explicando por qué este ejemplo desarma la objeción.
    Usá español argentino simple.
    """

    client = _obtener_gemini_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": EjemploResolucion,
        },
    )

    return EjemploResolucion.model_validate_json(response.text).model_dump()
