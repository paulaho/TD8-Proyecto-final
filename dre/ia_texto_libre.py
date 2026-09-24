import json

from google import genai
from pydantic import BaseModel, Field
from typing import List


# ==========================================================
# SCHEMAS PYDANTIC — Generación de situaciones
# ==========================================================

class SituacionTextoLibre(BaseModel):
    situacion: str
    reappraisal_inicial: str


class BatchSituacionesTextoLibre(BaseModel):
    situaciones: List[SituacionTextoLibre] = Field(min_length=5, max_length=5)


# ==========================================================
# SCHEMAS PYDANTIC — Evaluación de respuestas
# ==========================================================

class CorrectionItem(BaseModel):
    feedback: str  # máximo 15 palabras


class BatchCorreccionesTextoLibre(BaseModel):
    correcciones: List[CorrectionItem] = Field(min_length=5, max_length=5)


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
# GENERACIÓN DE BATCHES
# ==========================================================

def generar_batch_texto_libre(estado):
    """
    Genera 5 situaciones de la categoría Familia con su reappraisal inicial
    para el modo de texto libre. Usa el perfil del usuario del test inicial.
    """
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    prompt = f"""
    Generá EXACTAMENTE 5 situaciones de regulación emocional mediante
    cognitive reappraisal para el modo de escritura libre.

    Categoría: Familia
    Estrategia: Reappraisal cognitivo

    INFORMACIÓN PERSONALIZADA DEL USUARIO:
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})

    PAUTAS SEGÚN EL NIVEL:
    - Nivel 1: situaciones cotidianas simples y claras, lenguaje accesible.
    - Nivel 2: situaciones que involucren sesgos automáticos del día a día.
    - Nivel 3: situaciones más sutiles y desafiantes, con matices emocionales complejos.

    Para cada situación generá:
    1. "situacion": descripción breve (2-4 oraciones) de una situación concreta en
       el ámbito familiar que genera malestar emocional. Usá segunda persona
       ("te dice", "tu hermano/a", etc.). Debe ser específica y realista.
    2. "reappraisal_inicial": UNA interpretación alternativa de esa situación que
       reduzca el malestar emocional. Debe ser:
       - Plausible y realista (no positivismo mágico)
       - Que no niegue lo ocurrido
       - Que no minimice las emociones
       - Que sea una reinterpretación genuina de la intención, contexto o significado

    REGLAS GENERALES:
    - Las 5 situaciones deben ser DISTINTAS entre sí.
    - Situaciones cotidianas reales del entorno familiar del usuario.
    - Usá español argentino simple.
    - Evitá: suicidio, autolesión, violencia grave, abuso, diagnósticos médicos.
    - NO repitas situaciones del tipo "te critican en la mesa" o "discusión por el teléfono".
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

    print("Gemini texto libre respondió — batch inicial")

    batch = BatchSituacionesTextoLibre.model_validate_json(response.text)
    situaciones = [s.model_dump() for s in batch.situaciones]

    if len(situaciones) != 5:
        raise ValueError(
            f"Gemini devolvió {len(situaciones)} situaciones en lugar de 5"
        )

    print(f"Batch texto libre generado: {len(situaciones)} situaciones")
    return situaciones


def generar_batch_texto_libre_adaptativo(historial_texto, estado):
    """
    Genera 5 situaciones adaptadas al desempeño previo del usuario en el
    modo de texto libre. Analiza patrones en sus contraargumentos y
    reappraisals anteriores para ajustar la dificultad y el foco.
    """
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    historial_texto_json = json.dumps(
        historial_texto,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
    Generá EXACTAMENTE 5 situaciones de regulación emocional mediante
    cognitive reappraisal para el modo de escritura libre.

    Categoría: Familia
    Estrategia: Reappraisal cognitivo

    INFORMACIÓN PERSONALIZADA DEL USUARIO:
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})

    HISTORIAL DE DESEMPEÑO PREVIO DEL USUARIO:
    {historial_texto_json}

    Analizá especialmente:
    - Si los contraargumentos del usuario tienden a ser defensivos o agresivos.
    - Si los nuevos reappraisals caen en positivismo mágico o minimización.
    - Qué tipos de situaciones familiares le generan más dificultad.
    - Qué patrones cognitivos le cuesta más reevaluar.

    Adaptá las próximas 5 situaciones:
    - Si tuvo dificultades con algún patrón, generá situaciones que trabajen ese mismo principio desde un ángulo diferente.
    - Si le fue bien, aumentá ligeramente la complejidad emocional.
    - No copies literalmente situaciones anteriores.

    Para cada situación generá:
    1. "situacion": descripción breve (2-4 oraciones) de una situación concreta
       en el ámbito familiar que genera malestar. Usá segunda persona.
    2. "reappraisal_inicial": UNA interpretación alternativa realista que reduzca
       el malestar sin negar los hechos ni caer en positivismo.

    REGLAS:
    - Las 5 situaciones deben ser distintas entre sí y distintas a las del historial.
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

    print("Gemini texto libre respondió — batch adaptativo")

    batch = BatchSituacionesTextoLibre.model_validate_json(response.text)
    situaciones = [s.model_dump() for s in batch.situaciones]

    if len(situaciones) != 5:
        raise ValueError(
            f"Gemini devolvió {len(situaciones)} situaciones en lugar de 5"
        )

    print(f"Batch texto libre adaptativo generado: {len(situaciones)} situaciones")
    return situaciones


# ==========================================================
# EVALUACIÓN DE RESPUESTAS EN BATCH
# ==========================================================

def evaluar_batch_texto_libre(ejercicios):
    """
    Evalúa las 5 parejas (contraargumento + nuevo reappraisal) del usuario
    en una sola llamada a Gemini y devuelve feedback ultracorto (≤15 palabras)
    por cada ejercicio.

    Args:
        ejercicios: lista de 5 dicts con claves:
            - situacion: str
            - reappraisal_inicial: str
            - contraargumento: str (escrito por el usuario en Fase 1)
            - nuevo_reappraisal: str (escrito por el usuario en Fase 2)

    Returns:
        lista de 5 dicts con clave:
            - feedback: str (≤15 palabras)
    """
    if len(ejercicios) != 5:
        raise ValueError(
            f"Se esperaban 5 ejercicios para evaluar, se recibieron {len(ejercicios)}"
        )

    ejercicios_json = json.dumps(ejercicios, ensure_ascii=False, indent=2)

    prompt = f"""
    Evaluá las siguientes 5 respuestas de reappraisal cognitivo de un usuario
    y devolvé un comentario de corrección ultracorto (MÁXIMO 15 palabras) por cada una.

    CONTEXTO DE LA TAREA:
    El usuario recibió una situación familiar estresante junto con un reappraisal
    inicial (interpretación alternativa). Primero debía escribir un contraargumento
    a ese reappraisal (una objeción plausible). Luego debía escribir un nuevo
    reappraisal que integrara tanto el reappraisal inicial como su propia objeción.

    CRITERIOS DE EVALUACIÓN para cada ejercicio:
    1. El contraargumento debe ser una objeción válida y plausible al reappraisal inicial
       (no una negación total, no un insulto, sino una duda o matiz razonable).
    2. El nuevo reappraisal debe:
       - Reestructurar cognitivamente la situación de forma realista.
       - Integrar o desarmar la objeción del propio usuario.
       - No caer en positivismo tóxico ("todo pasa por algo", "en el fondo me quiere").
       - No minimizar las emociones ni los hechos.
       - No ser agresivo hacia los demás ni hacia uno mismo.

    FORMATO DEL FEEDBACK:
    - Máximo 15 palabras por respuesta.
    - Si el ejercicio está bien hecho: empezá con "✅" y destacá lo que funcionó.
    - Si hay algo que mejorar: empezá con "💡" y señalá específicamente qué mejorar.
    - Si hay un error importante: empezá con "⚠️" y explicá brevemente el problema.
    - Usá español argentino simple y tono cálido, no punitivo.

    EJERCICIOS A EVALUAR:
    {ejercicios_json}

    Devolvé exactamente 5 correcciones en el array "correcciones", en el mismo
    orden que los ejercicios. El campo "feedback" de cada una debe tener máximo 15 palabras.
    """

    client = _obtener_gemini_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": BatchCorreccionesTextoLibre,
        },
    )

    print("Gemini evaluó el batch de texto libre")

    batch = BatchCorreccionesTextoLibre.model_validate_json(response.text)
    correcciones = [c.model_dump() for c in batch.correcciones]

    if len(correcciones) != 5:
        raise ValueError(
            f"Gemini devolvió {len(correcciones)} correcciones en lugar de 5"
        )

    return correcciones

