from __future__ import annotations
import json
from typing import List, Dict, Any, Optional, Set, Tuple
from google import genai
from pydantic import BaseModel, Field

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


def generar_batch_texto_libre(estado, nivel_inicial: int = 1):
    """
    Genera 5 situaciones de la categoría Familia para el juego de Contraargumento.
    La dificultad está estrictamente determinada por los 5 niveles consecutivos [nivel_inicial .. nivel_inicial+4].
    El perfil_contexto solo se usa para personalizar el ámbito cotidiano.
    """
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")

    spec_niveles = _armar_especificacion_niveles(nivel_inicial)

    prompt = f"""
    Generá EXACTAMENTE 5 situaciones de regulación emocional mediante
    cognitive reappraisal (modo Contraargumento) en la categoría Familia.

    INFORMACIÓN PERSONALIZADA DEL USUARIO (USALA PARA PERSONALIZAR EL CONTEXTO):
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}

    ESPECIFICACIÓN OBLIGATORIA DE CADA UNO DE LOS 5 NIVELES (GENERAR EN ESTE ORDEN EXACTO):
    {spec_niveles}

    CAMPOS REQUERIDOS PARA CADA SITUACIÓN:
    1. "situacion": descripción breve (2-4 oraciones) de una situación familiar concreta que genera malestar.
       Usá segunda persona ("te dice", "tu hermana", etc.). Específica y realista.
    2. "lectura_negativa_implicita": la peor lectura o pensamiento automático que esa situación tiende a disparar
       (ej.: "Seguro está enojado/a conmigo"). Ajustada al Tipo de Lectura pedido.
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
    - Situaciones cotidianas reales del entorno familiar del usuario.
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


def generar_batch_texto_libre_adaptativo(historial_texto, estado, nivel_inicial: int = 1):
    """
    Genera 5 situaciones adaptadas al desempeño previo en el juego de Contraargumento.
    IMPORTANTE: La dificultad está fijada estrictamente por los niveles [nivel_inicial .. nivel_inicial+4].
    El historial solo orienta temas, focos y qué fallas o ángulos reforzar, NUNCA altera la dificultad.
    """
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")

    spec_niveles = _armar_especificacion_niveles(nivel_inicial)

    historial_texto_json = json.dumps(historial_texto, ensure_ascii=False, indent=2)

    prompt = f"""
    Generá EXACTAMENTE 5 situaciones de regulación emocional mediante
    cognitive reappraisal (modo Contraargumento) en la categoría Familia.

    INFORMACIÓN PERSONALIZADA DEL USUARIO:
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}

    HISTORIAL DE DESEMPEÑO PREVIO DEL USUARIO:
    {historial_texto_json}

    PAUTAS DE ADAPTACIÓN CON EL HISTORIAL:
    - Analizá qué ángulos o fallas le costaron más al usuario o qué situaciones le generaron reintentos.
    - Orientá los temas y el foco para ejercitar esos puntos desde ángulos novedosos, SIN alterar la dificultad fijada por los niveles.
    - No copies situaciones anteriores.

    ESPECIFICACIÓN OBLIGATORIA DE CADA UNO DE LOS 5 NIVELES (GENERAR EN ESTE ORDEN EXACTO):
    {spec_niveles}

    CAMPOS REQUERIDOS PARA CADA SITUACIÓN:
    1. "situacion": descripción breve (2-4 oraciones) de una situación familiar concreta que genera malestar.
    2. "lectura_negativa_implicita": la peor lectura o pensamiento automático que esa situación tiende a disparar.
    3. "reappraisal_inicial": UNA interpretación alternativa inicial razonable que reduzca el malestar, basada en
       Reconstrual y acorde a su Tipo (Tipo I, II o III).
    4. "punto_debil": explicación concisa de dónde está el punto débil o límite del reappraisal inicial.

    REGLAS:
    - 5 situaciones distintas entre sí y distintas al historial.
    - Con lectura Tipo III, nada obliga a negar hechos reales.
    - Español argentino simple.
    - Evitá: suicidio, autolesión, violencia grave, abuso, diagnósticos médicos.
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
    1. "situacion": Hecho familiar que genera malestar.
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
