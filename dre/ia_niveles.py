import json
import random

from google import genai
from pydantic import BaseModel, Field
from typing import List

class EjercicioFamiliaIA(BaseModel):
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


class BatchEjerciciosFamiliaIA(BaseModel):
    niveles: List[EjercicioFamiliaIA]

try:
    gemini_client = genai.Client()
except Exception:
    gemini_client = None

def _obtener_gemini_client():
    global gemini_client
    if gemini_client is None:
        gemini_client = genai.Client()
    return gemini_client

def generar_batch_familia_ia(estado):
    # Extraemos la información del test inicial guardada en el estado
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")
    nivel_reg = contexto.get("nivel_regulacion", 1)
    familiaridad = contexto.get("familiaridad_regulacion", "No especificado")

    # Inyectamos las variables con f""" dentro del prompt
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

    client = _obtener_gemini_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": BatchEjerciciosFamiliaIA,
        },
    )

    print("Gemini respondió")
    print("RAW RESPONSE:")
    print(response.text)

    batch = BatchEjerciciosFamiliaIA.model_validate_json(
        response.text
    )

    niveles = [nivel.model_dump() for nivel in batch.niveles]

    if len(niveles) != 10:
        raise ValueError(
            f"Gemini devolvió {len(niveles)} niveles en lugar de 10"
        )

    for nivel in niveles:
        validar_nivel_ia(nivel)

    print("Batch de 10 niveles validado")

    return niveles


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

    INFORMACIÓN PERSONALIZADA DEL USUARIO:
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

    client = _obtener_gemini_client()
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": BatchEjerciciosFamiliaIA,
        },
    )

    print("Gemini respondió batch adaptativo")

    batch = BatchEjerciciosFamiliaIA.model_validate_json(
        response.text
    )

    niveles = [
        nivel.model_dump()
        for nivel in batch.niveles
    ]

    if len(niveles) != 10:
        raise ValueError(
            f"Gemini devolvió {len(niveles)} niveles en lugar de 10"
        )

    for nivel in niveles:
        validar_nivel_ia(nivel)

    print("Batch adaptativo de 10 niveles validado")

    return niveles
    
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
