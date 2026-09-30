import json
import random
from typing import List

from google import genai
from pydantic import BaseModel, Field


class EjercicioIA(BaseModel):
    estrategia: str
    nombre: str
    tipo: str
    escenario: List[str]

    opciones: List[str] = Field(
        min_length=4,
        max_length=4,
    )

    correctas: List[int] = Field(
        min_length=1,
        max_length=1,
    )

    mensaje_exito: str
    mensaje_error: str


class BatchEjerciciosIA(BaseModel):
    niveles: List[EjercicioIA]


# Aliases para mantener compatibilidad previa
EjercicioFamiliaIA = EjercicioIA
BatchEjerciciosFamiliaIA = BatchEjerciciosIA


try:
    gemini_client = genai.Client()
except Exception:
    gemini_client = None


def _obtener_gemini_client():
    global gemini_client
    if gemini_client is None:
        gemini_client = genai.Client()
    return gemini_client


def validar_nivel_ia(ejercicio):

    if ejercicio["tipo"] != "opcion_multiple":
        raise ValueError("El tipo debe ser opcion_multiple")

    if ejercicio["estrategia"] != "Reconstrual":
        raise ValueError("La estrategia debe ser Reconstrual")

    if len(ejercicio["opciones"]) != 4:
        raise ValueError("El ejercicio debe tener exactamente 4 opciones")

    if len(ejercicio["correctas"]) != 1:
        raise ValueError("Debe haber exactamente una respuesta correcta")

    indice_correcto = ejercicio["correctas"][0]

    if indice_correcto < 0 or indice_correcto >= len(ejercicio["opciones"]):
        raise ValueError("El índice de la respuesta correcta no es válido")

    # Mezclar las opciones aleatoriamente para evitar sesgos de la IA
    texto_correcto = ejercicio["opciones"][indice_correcto]
    random.shuffle(ejercicio["opciones"])
    nuevo_indice_correcto = ejercicio["opciones"].index(texto_correcto)
    ejercicio["correctas"] = [nuevo_indice_correcto]

    return ejercicio


def _generar_batch_generico_ia(estado, prompt_categoria, nombre_categoria):
    client = _obtener_gemini_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt_categoria,
        config={
            "response_mime_type": "application/json",
            "response_schema": BatchEjerciciosIA,
        },
    )

    print(f"Gemini respondió batch para {nombre_categoria}")
    print("RAW RESPONSE:")
    print(response.text)

    batch = BatchEjerciciosIA.model_validate_json(response.text)
    niveles = [nivel.model_dump() for nivel in batch.niveles]

    if len(niveles) != 10:
        raise ValueError(
            f"Gemini devolvió {len(niveles)} niveles en lugar de 10 para {nombre_categoria}"
        )

    for nivel in niveles:
        validar_nivel_ia(nivel)

    print(f"Batch de 10 niveles validado para {nombre_categoria}")
    return niveles


# ==============================================================================
# 1. FAMILIA
# ==============================================================================

def generar_batch_familia_ia(estado):
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    prompt = f"""
    Generá EXACTAMENTE 10 ejercicios consecutivos de regulación emocional
    mediante cognitive reappraisal.

    Categoría: Familia
    Estrategia principal: Reconstrual
    Tipo: opcion_multiple

    INFORMACIÓN PERSONALIZADA DEL USUARIO (USALOS PARA CREAR ESCENARIOS RELEVANTES):
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})

    PAUTAS DE ADAPTACIÓN SEGÚN EL NIVEL:
    - Si es Nivel 1: situaciones cotidianas muy claras, lenguaje empático y accesible, sin tecnicismos.
    - Si es Nivel 2: foco en notar sesgos automáticos del día a día y construir interpretaciones más funcionales.
    - Si es Nivel 3: ejercicios de reevaluación cognitiva con matices más sutiles y desafiantes frente a sesgos automáticos.

    Los 10 ejercicios deben tener dificultad progresiva:
    - Los primeros ejercicios deben ser más simples.
    - La dificultad debe aumentar gradualmente.
    - Los últimos ejercicios deben ser los más desafiantes.

    Reglas generales:
    - Los 10 escenarios deben ser diferentes entre sí.
    - Deben representar situaciones cotidianas y realistas adaptadas al entorno familiar y personal del usuario.
    - Exactamente 4 opciones por ejercicio.
    - Solo UNA respuesta correcta por ejercicio.
    - La respuesta correcta debe ofrecer una reinterpretación alternativa plausible.
    - No debe negar lo ocurrido.
    - No debe minimizar las emociones.
    - Evitá positivismo exagerado.
    - Las opciones incorrectas deben ser pensamientos automáticos plausibles.
    - A medida que aumenta el nivel, las opciones incorrectas deben ser
      progresivamente más difíciles de distinguir de la correcta.
    - Evitá suicidio, autolesión, violencia grave, abuso y diagnósticos médicos.
    - Usá español argentino simple.
    - "correctas" debe contener el índice de la opción correcta empezando desde 0.
    """

    return _generar_batch_generico_ia(estado, prompt, "Familia")


def generar_batch_familia_ia_adaptativo(historial, estado):
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    historial_texto = json.dumps(
        historial,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
    Generá EXACTAMENTE 10 ejercicios consecutivos de regulación emocional
    mediante cognitive reappraisal.

    Categoría: Familia
    Estrategia principal: Reconstrual
    Tipo: opcion_multiple

    INFORMACIÓN PERSONALIZADA DEL USUARIO (USALOS PARA CREAR ESCENARIOS RELEVANTES):
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})

    PAUTAS DE ADAPTACIÓN SEGÚN EL NIVEL:
    - Si es Nivel 1: situaciones cotidianas muy claras, lenguaje empático y accesible, sin tecnicismos.
    - Si es Nivel 2: foco en notar sesgos automáticos del día a día y construir interpretaciones más funcionales.
    - Si es Nivel 3: ejercicios de reevaluación cognitiva con matices más sutiles y desafiantes frente a sesgos automáticos.

    El usuario ya realizó ejercicios anteriormente.

    Este fue su desempeño:

    {historial_texto}

    Analizá especialmente:
    - qué respuestas incorrectas eligió
    - en qué tipos de situaciones se confundió
    - qué formas de pensamiento parecen costarle más

    Generá los próximos 10 ejercicios adaptándolos a ese desempeño y a la realidad de su perfil personal.

    Si el usuario se confundió en algún aspecto:
    - volvé a trabajar ese mismo principio
    - usá un escenario diferente
    - no copies literalmente el ejercicio anterior

    Si no tuvo dificultades:
    - aumentá ligeramente la dificultad

    Los 10 escenarios deben ser diferentes.

    Cada ejercicio debe:
    - tener exactamente 4 opciones
    - tener solamente una respuesta correcta
    - tener una reinterpretación alternativa plausible
    - no negar lo ocurrido
    - no minimizar las emociones
    - evitar positivismo exagerado

    Las opciones incorrectas deben ser pensamientos plausibles.

    Evitá:
    - suicidio
    - autolesión
    - abuso
    - violencia grave
    - muerte de familiares
    - diagnósticos o enfermedades graves

    Usá español argentino simple.

    "correctas" debe contener solamente el índice de la opción correcta,
    empezando desde 0.
    """

    return _generar_batch_generico_ia(estado, prompt, "Familia Adaptativo")


# ==============================================================================
# 2. VÍNCULOS
# ==============================================================================

def generar_batch_vinculos_ia(estado):
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    prompt = f"""
    Generá EXACTAMENTE 10 ejercicios consecutivos de regulación emocional
    mediante cognitive reappraisal.

    Categoría: Vínculos (pareja, amigos y relaciones cercanas)
    Estrategia principal: Reconstrual
    Tipo: opcion_multiple

    INFORMACIÓN PERSONALIZADA DEL USUARIO (USALOS PARA CREAR ESCENARIOS RELEVANTES):
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})

    PAUTAS DE ADAPTACIÓN SEGÚN EL NIVEL:
    - Si es Nivel 1: situaciones cotidianas muy claras, lenguaje empático y accesible, sin tecnicismos.
    - Si es Nivel 2: foco en notar sesgos automáticos del día a día y construir interpretaciones más funcionales.
    - Si es Nivel 3: ejercicios de reevaluación cognitiva con matices más sutiles y desafiantes frente a sesgos automáticos.

    Los 10 ejercicios deben tener dificultad progresiva:
    - Los primeros ejercicios deben ser más simples.
    - La dificultad debe aumentar gradualmente.
    - Los últimos ejercicios deben ser los más desafiantes.

    Reglas generales:
    - Los 10 escenarios deben ser diferentes entre sí.
    - Deben representar situaciones cotidianas y realistas enfocadas en relaciones de pareja, amistades, comunicación interpersonal, malentendidos y dinámicas vinculares cercanas adaptadas al perfil del usuario.
    - Exactamente 4 opciones por ejercicio.
    - Solo UNA respuesta correcta por ejercicio.
    - La respuesta correcta debe ofrecer una reinterpretación alternativa plausible.
    - No debe negar lo ocurrido.
    - No debe minimizar las emociones.
    - Evitá positivismo exagerado.
    - Las opciones incorrectas deben ser pensamientos automáticos plausibles.
    - A medida que aumenta el nivel, las opciones incorrectas deben ser
      progresivamente más difíciles de distinguir de la correcta.
    - Evitá suicidio, autolesión, violencia grave, abuso y diagnósticos médicos.
    - Usá español argentino simple.
    - "correctas" debe contener el índice de la opción correcta empezando desde 0.
    """

    return _generar_batch_generico_ia(estado, prompt, "Vínculos")


def generar_batch_vinculos_ia_adaptativo(historial, estado):
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    historial_texto = json.dumps(
        historial,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
    Generá EXACTAMENTE 10 ejercicios consecutivos de regulación emocional
    mediante cognitive reappraisal.

    Categoría: Vínculos (pareja, amigos y relaciones cercanas)
    Estrategia principal: Reconstrual
    Tipo: opcion_multiple

    INFORMACIÓN PERSONALIZADA DEL USUARIO (USALOS PARA CREAR ESCENARIOS RELEVANTES):
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})

    PAUTAS DE ADAPTACIÓN SEGÚN EL NIVEL:
    - Si es Nivel 1: situaciones cotidianas muy claras, lenguaje empático y accesible, sin tecnicismos.
    - Si es Nivel 2: foco en notar sesgos automáticos del día a día y construir interpretaciones más funcionales.
    - Si es Nivel 3: ejercicios de reevaluación cognitiva con matices más sutiles y desafiantes frente a sesgos automáticos.

    El usuario ya realizó ejercicios anteriormente.

    Este fue su desempeño:

    {historial_texto}

    Analizá especialmente:
    - qué respuestas incorrectas eligió
    - en qué tipos de situaciones se confundió
    - qué formas de pensamiento parecen costarle más

    Generá los próximos 10 ejercicios adaptándolos a ese desempeño y a la realidad de sus vínculos personales (pareja, amigos, relaciones cercanas).

    Si el usuario se confundió en algún aspecto:
    - volvé a trabajar ese mismo principio
    - usá un escenario diferente
    - no copies literalmente el ejercicio anterior

    Si no tuvo dificultades:
    - aumentá ligeramente la dificultad

    Los 10 escenarios deben ser diferentes.

    Cada ejercicio debe:
    - tener exactamente 4 opciones
    - tener solamente una respuesta correcta
    - tener una reinterpretación alternativa plausible
    - no negar lo ocurrido
    - no minimizar las emociones
    - evitar positivismo exagerado

    Las opciones incorrectas deben ser pensamientos plausibles.

    Evitá:
    - suicidio
    - autolesión
    - abuso
    - violencia grave
    - rupturas traumáticas o violencia de género
    - diagnósticos o enfermedades graves

    Usá español argentino simple.

    "correctas" debe contener solamente el índice de la opción correcta,
    empezando desde 0.
    """

    return _generar_batch_generico_ia(estado, prompt, "Vínculos Adaptativo")


# ==============================================================================
# 3. SALUD
# ==============================================================================

def generar_batch_salud_ia(estado):
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    prompt = f"""
    Generá EXACTAMENTE 10 ejercicios consecutivos de regulación emocional
    mediante cognitive reappraisal.

    Categoría: Salud (hábitos, cansancio y bienestar físico)
    Estrategia principal: Reconstrual
    Tipo: opcion_multiple

    INFORMACIÓN PERSONALIZADA DEL USUARIO (USALOS PARA CREAR ESCENARIOS RELEVANTES):
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})

    PAUTAS DE ADAPTACIÓN SEGÚN EL NIVEL:
    - Si es Nivel 1: situaciones cotidianas muy claras, lenguaje empático y accesible, sin tecnicismos.
    - Si es Nivel 2: foco en notar sesgos automáticos del día a día y construir interpretaciones más funcionales.
    - Si es Nivel 3: ejercicios de reevaluación cognitiva con matices más sutiles y desafiantes frente a sesgos automáticos.

    Los 10 ejercicios deben tener dificultad progresiva:
    - Los primeros ejercicios deben ser más simples.
    - La dificultad debe aumentar gradualmente.
    - Los últimos ejercicios deben ser los más desafiantes.

    Reglas generales:
    - Los 10 escenarios deben ser diferentes entre sí.
    - Deben representar situaciones cotidianas y realistas enfocadas en hábitos diarios, cansancio físico/mental, descanso, ejercicio, alimentación y preocupación por el bienestar físico general adaptadas al perfil del usuario.
    - Exactamente 4 opciones por ejercicio.
    - Solo UNA respuesta correcta por ejercicio.
    - La respuesta correcta debe ofrecer una reinterpretación alternativa plausible.
    - No debe negar lo ocurrido.
    - No debe minimizar las emociones.
    - Evitá positivismo exagerado.
    - Las opciones incorrectas deben ser pensamientos automáticos plausibles.
    - A medida que aumenta el nivel, las opciones incorrectas deben ser
      progresivamente más difíciles de distinguir de la correcta.
    - Evitá suicidio, autolesión, enfermedades terminales, dolor crónico severo o diagnósticos médicos reales.
    - Usá español argentino simple.
    - "correctas" debe contener el índice de la opción correcta empezando desde 0.
    """

    return _generar_batch_generico_ia(estado, prompt, "Salud")


def generar_batch_salud_ia_adaptativo(historial, estado):
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    historial_texto = json.dumps(
        historial,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
    Generá EXACTAMENTE 10 ejercicios consecutivos de regulación emocional
    mediante cognitive reappraisal.

    Categoría: Salud (hábitos, cansancio y bienestar físico)
    Estrategia principal: Reconstrual
    Tipo: opcion_multiple

    INFORMACIÓN PERSONALIZADA DEL USUARIO (USALOS PARA CREAR ESCENARIOS RELEVANTES):
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})

    PAUTAS DE ADAPTACIÓN SEGÚN EL NIVEL:
    - Si es Nivel 1: situaciones cotidianas muy claras, lenguaje empático y accesible, sin tecnicismos.
    - Si es Nivel 2: foco en notar sesgos automáticos del día a día y construir interpretaciones más funcionales.
    - Si es Nivel 3: ejercicios de reevaluación cognitiva con matices más sutiles y desafiantes frente a sesgos automáticos.

    El usuario ya realizó ejercicios anteriormente.

    Este fue su desempeño:

    {historial_texto}

    Analizá especialmente:
    - qué respuestas incorrectas eligió
    - en qué tipos de situaciones se confundió
    - qué formas de pensamiento parecen costarle más

    Generá los próximos 10 ejercicios adaptándolos a ese desempeño y a la realidad de sus hábitos y bienestar físico (cansancio, descanso, cuerpo, hábitos saludables).

    Si el usuario se confundió en algún aspecto:
    - volvé a trabajar ese mismo principio
    - usá un escenario diferente
    - no copies literalmente el ejercicio anterior

    Si no tuvo dificultades:
    - aumentá ligeramente la dificultad

    Los 10 escenarios deben ser diferentes.

    Cada ejercicio debe:
    - tener exactamente 4 opciones
    - tener solamente una respuesta correcta
    - tener una reinterpretación alternativa plausible
    - no negar lo ocurrido
    - no minimizar las emociones
    - evitar positivismo exagerado

    Las opciones incorrectas deben ser pensamientos plausibles.

    Evitá:
    - suicidio
    - autolesión
    - abuso
    - violencia grave
    - enfermedades graves o terminales
    - diagnósticos médicos

    Usá español argentino simple.

    "correctas" debe contener solamente el índice de la opción correcta,
    empezando desde 0.
    """

    return _generar_batch_generico_ia(estado, prompt, "Salud Adaptativo")


# ==============================================================================
# 4. TRABAJO O ESTUDIO
# ==============================================================================

def generar_batch_trabajo_estudio_ia(estado):
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    prompt = f"""
    Generá EXACTAMENTE 10 ejercicios consecutivos de regulación emocional
    mediante cognitive reappraisal.

    Categoría: Trabajo o Estudio (presión laboral/académica, exámenes, entregas y equipo)
    Estrategia principal: Reconstrual
    Tipo: opcion_multiple

    INFORMACIÓN PERSONALIZADA DEL USUARIO (USALOS PARA CREAR ESCENARIOS RELEVANTES):
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})

    PAUTAS DE ADAPTACIÓN SEGÚN EL NIVEL:
    - Si es Nivel 1: situaciones cotidianas muy claras, lenguaje empático y accesible, sin tecnicismos.
    - Si es Nivel 2: foco en notar sesgos automáticos del día a día y construir interpretaciones más funcionales.
    - Si es Nivel 3: ejercicios de reevaluación cognitiva con matices más sutiles y desafiantes frente a sesgos automáticos.

    Los 10 ejercicios deben tener dificultad progresiva:
    - Los primeros ejercicios deben ser más simples.
    - La dificultad debe aumentar gradualmente.
    - Los últimos ejercicios deben ser los más desafiantes.

    Reglas generales:
    - Los 10 escenarios deben ser diferentes entre sí.
    - Deben representar situaciones cotidianas y realistas enfocadas en presión laboral o académica, entregas, exámenes, proyectos, trabajo en equipo, feedback de superiores o profesores y responsabilidades adaptadas a la ocupación del usuario.
    - Exactamente 4 opciones por ejercicio.
    - Solo UNA respuesta correcta por ejercicio.
    - La respuesta correcta debe ofrecer una reinterpretación alternativa plausible.
    - No debe negar lo ocurrido.
    - No debe minimizar las emociones.
    - Evitá positivismo exagerado.
    - Las opciones incorrectas deben ser pensamientos automáticos plausibles.
    - A medida que aumenta el nivel, las opciones incorrectas deben ser
      progresivamente más difíciles de distinguir de la correcta.
    - Evitá suicidio, autolesión, violencia grave, abuso y diagnósticos médicos.
    - Usá español argentino simple.
    - "correctas" debe contener el índice de la opción correcta empezando desde 0.
    """

    return _generar_batch_generico_ia(estado, prompt, "Trabajo o Estudio")


def generar_batch_trabajo_estudio_ia_adaptativo(historial, estado):
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    historial_texto = json.dumps(
        historial,
        ensure_ascii=False,
        indent=2,
    )

    prompt = f"""
    Generá EXACTAMENTE 10 ejercicios consecutivos de regulación emocional
    mediante cognitive reappraisal.

    Categoría: Trabajo o Estudio (presión laboral/académica, exámenes, entregas y equipo)
    Estrategia principal: Reconstrual
    Tipo: opcion_multiple

    INFORMACIÓN PERSONALIZADA DEL USUARIO (USALOS PARA CREAR ESCENARIOS RELEVANTES):
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})

    PAUTAS DE ADAPTACIÓN SEGÚN EL NIVEL:
    - Si es Nivel 1: situaciones cotidianas muy claras, lenguaje empático y accesible, sin tecnicismos.
    - Si es Nivel 2: foco en notar sesgos automáticos del día a día y construir interpretaciones más funcionales.
    - Si es Nivel 3: ejercicios de reevaluación cognitiva con matices más sutiles y desafiantes frente a sesgos automáticos.

    El usuario ya realizó ejercicios anteriormente.

    Este fue su desempeño:

    {historial_texto}

    Analizá especialmente:
    - qué respuestas incorrectas eligió
    - en qué tipos de situaciones se confundió
    - qué formas de pensamiento parecen costarle más

    Generá los próximos 10 ejercicios adaptándolos a ese desempeño y a la realidad de su entorno laboral o académico (exámenes, entregas, jefes, profesores, compañeros, presión).

    Si el usuario se confundió en algún aspecto:
    - volvé a trabajar ese mismo principio
    - usá un escenario diferente
    - no copies literalmente el ejercicio anterior

    Si no tuvo dificultades:
    - aumentá ligeramente la dificultad

    Los 10 escenarios deben ser diferentes.

    Cada ejercicio debe:
    - tener exactamente 4 opciones
    - tener solamente una respuesta correcta
    - tener una reinterpretación alternativa plausible
    - no negar lo ocurrido
    - no minimizar las emociones
    - evitar positivismo exagerado

    Las opciones incorrectas deben ser pensamientos plausibles.

    Evitá:
    - suicidio
    - autolesión
    - abuso
    - violencia grave
    - despidos traumáticos masivos
    - diagnósticos o enfermedades graves

    Usá español argentino simple.

    "correctas" debe contener solamente el índice de la opción correcta,
    empezando desde 0.
    """

    return _generar_batch_generico_ia(estado, prompt, "Trabajo o Estudio Adaptativo")


# ==============================================================================
# ROUTER / DISPATCHER GENÉRICO DE BATCHES IA
# ==============================================================================

GENERADORES_BATCH_IA = {
    "familia": generar_batch_familia_ia,
    "vinculos": generar_batch_vinculos_ia,
    "salud": generar_batch_salud_ia,
    "trabajo": generar_batch_trabajo_estudio_ia,
    "trabajo_estudio": generar_batch_trabajo_estudio_ia,
    "trabajo o estudio": generar_batch_trabajo_estudio_ia,
}

GENERADORES_BATCH_IA_ADAPTATIVO = {
    "familia": generar_batch_familia_ia_adaptativo,
    "vinculos": generar_batch_vinculos_ia_adaptativo,
    "salud": generar_batch_salud_ia_adaptativo,
    "trabajo": generar_batch_trabajo_estudio_ia_adaptativo,
    "trabajo_estudio": generar_batch_trabajo_estudio_ia_adaptativo,
    "trabajo o estudio": generar_batch_trabajo_estudio_ia_adaptativo,
}


def generar_batch_ia(categoria, estado):
    clave = categoria.lower() if isinstance(categoria, str) else "familia"
    generador = GENERADORES_BATCH_IA.get(clave, generar_batch_familia_ia)
    return generador(estado)


def generar_batch_ia_adaptativo(categoria, historial, estado):
    clave = categoria.lower() if isinstance(categoria, str) else "familia"
    generador = GENERADORES_BATCH_IA_ADAPTATIVO.get(clave, generar_batch_familia_ia_adaptativo)
    return generador(historial, estado)
