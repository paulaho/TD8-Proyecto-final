import json
import random
<<<<<<< HEAD
from typing import List

=======
>>>>>>> c6bfd46ec0702d1296ffa7b8a099dd31579ac276
from google import genai
from pydantic import BaseModel, Field

<<<<<<< HEAD

class EjercicioIA(BaseModel):
=======
TECHO_UX = 7

class EjercicioFamiliaIA(BaseModel):
>>>>>>> c6bfd46ec0702d1296ffa7b8a099dd31579ac276
    estrategia: str
    nombre: str
    tipo: str
    escenario: List[str]
    opciones: List[str] = Field(min_length=4, max_length=TECHO_UX)
    correctas: List[int] = Field(min_length=1, max_length=1)
    mensaje_exito: str
    mensaje_error: str

<<<<<<< HEAD

class BatchEjerciciosIA(BaseModel):
    niveles: List[EjercicioIA]


# Aliases para mantener compatibilidad previa
EjercicioFamiliaIA = EjercicioIA
BatchEjerciciosFamiliaIA = BatchEjerciciosIA

=======
class BatchEjerciciosFamiliaIA(BaseModel):
    niveles: List[EjercicioFamiliaIA]
>>>>>>> c6bfd46ec0702d1296ffa7b8a099dd31579ac276

try:
    gemini_client = genai.Client()
except Exception:
    gemini_client = None


def _obtener_gemini_client():
    global gemini_client
    if gemini_client is None:
        gemini_client = genai.Client()
    return gemini_client

<<<<<<< HEAD

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
=======

def _receta_dificultad(numero):
    """Cantidad de distractores G1..G5 para un nivel absoluto (1 en adelante)."""
    if numero <= 3:
        grupos = [3, 0, 0, 0, 0]
        situacion = 'Banda 1: intensidad leve; señal única y clara; evento puntual.'
    elif numero <= 6:
        grupos = [2, 1, 0, 0, 0]
        situacion = 'Banda 2: intensidad leve-moderada; señal única algo cargada; evento puntual.'
    elif numero <= 9:
        grupos = [1, 2, 0, 0, 0]
        situacion = 'Banda 3: intensidad moderada; dos señales mixtas; posible patrón.'
    elif numero <= 12:
        grupos = [0, 1, 1, 1, 0]
        situacion = 'Banda 4: intensidad moderada-alta; señales mixtas difíciles de leer; relación con historia.'
    else:
        grupos = [0, 0, 1, 1, 1]
        situacion = ('Banda 5: intensidad alta pero no extrema (TECHO FIJO); '
                     'incertidumbre genuina con varias lecturas razonables; relación con historia.')
        if numero >= 14:
            opciones = min(TECHO_UX, 5 + (numero - 14) // 5)
            adicionales = opciones - 4
            # Priorizar hasta cuatro G5 en total; después añadir G4.
            nuevos_g5 = min(adicionales, 3)
            grupos[4] += nuevos_g5
            grupos[3] += adicionales - nuevos_g5
    return grupos, situacion
>>>>>>> c6bfd46ec0702d1296ffa7b8a099dd31579ac276


<<<<<<< HEAD
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
=======
def _instrucciones_niveles(inicio):
    instrucciones = []
    for numero in range(inicio, inicio + 10):
        grupos, situacion = _receta_dificultad(numero)
        instrucciones.append(
            f'Ejercicio {numero - inicio + 1} (nivel global {numero}): '
            f'{sum(grupos) + 1} opciones EXACTAS (1 correcta + '
            f'G1={grupos[0]}, G2={grupos[1]}, G3={grupos[2]}, '
            f'G4={grupos[3]}, G5={grupos[4]}). {situacion}'
        )
    return '\n'.join(instrucciones)


def _generar_batch(estado, inicio, historial=None):
    contexto = estado.get('perfil_contexto', {})
    genero = estado.get('genero', 'no especificado')
    nivel_reg = contexto.get('nivel_regulacion', 1)
    familiaridad = contexto.get('familiaridad_regulacion', 'No especificado')
    historial_texto = json.dumps(historial or [], ensure_ascii=False, indent=2)

    prompt = f"""
Generá EXACTAMENTE 10 ejercicios consecutivos de cognitive reappraisal.
Categoría: Familia. Estrategia que se evalúa: Reconstrual. Tipo: opcion_multiple.
Cada ejercicio debe tener UNA SOLA respuesta correcta y respetar EXACTAMENTE su receta individual.
Generá las opciones EN ORDEN FIJO: primero la correcta y luego los distractores por grupo, G1, G2, G3, G4 y G5 según la receta. No mezcles las opciones: Python las mezclará después.

PERFIL PARA ELEGIR CONTEXTOS REALISTAS (no cambia las cantidades ni las bandas):
- Género: {genero}
- Convivencia: {contexto.get('convivencia', 'No especificado')}
- Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
- Ocupación: {contexto.get('ocupacion', 'No especificado')}
- Estado en pareja: {contexto.get('pareja', 'No especificado')}
- Familiaridad con regulación emocional: Nivel {nivel_reg} ({familiaridad}).
Usá lenguaje empático y simple independientemente de la familiaridad.

RECETA OBLIGATORIA PARA LOS 10 EJERCICIOS, EN ESTE ORDEN:
{_instrucciones_niveles(inicio)}

DEFINICIÓN DE LOS DISTRACTORES (cada opción incorrecta debe pertenecer a UN grupo):
G1 - Distorsión pura: exagerar el pensamiento automático usando UNA distorsión plausible:
catastrofización, lectura de mente, adivinación del futuro, razonamiento emocional,
'debería', etiquetado, filtro mental, descalificar lo positivo, personalización,
sobregeneralización o todo-o-nada. No ofrece interpretación nueva.
G2 - Evitación con careta de calma: suena serena, pero esquiva el tema, sin reinterpretarlo.
G3 - Positividad forzada: suena bienintencionada, pero salta a lo positivo negando u omitiendo
la dificultad real. No la hagas absurda ni caricaturesca.
G4 - Reappraisal incompleto: interpretación razonable y coherente, pero deja afuera una
pieza esencial de la reinterpretación completa. Escribí primero la correcta y luego construí G4.
G5 - Estrategia correcta, encaje equivocado: respuesta válida aplicada a LA MISMA situación,
pero corresponde a OTRA estrategia de MENTO, NO a Reconstrual. Elegí entre Repurposing,
Reappraisal interpersonal, Reappraisal inventivo y Reinterpretación positiva. Si hay varios
G5 en un mismo ejercicio, usá estrategias diferentes, máximo cuatro.

CONTROL DE AMBIGÜEDAD OBLIGATORIO: cada distractor G4 debe ser realmente incompleto,
no otra explicación alternativa completa. G5 NO puede explicar de otra forma las causas
del mismo hecho: eso sería también Reconstrual. G5 debe cambiar el objetivo cognitivo
(por ejemplo, encontrar propósito, reinterpretar consecuencias o considerar una respuesta
interpersonal), sin cambiar la lectura de los hechos como lo hace Reconstrual.
Si dos opciones podrían ser Reconstrual, reescribí la incorrecta hasta diferenciarlas.

RESPUESTA CORRECTA: Reconstrual: reconoce lo difícil y amplía la interpretación de los
mismos hechos sin inventar certezas ni minimizar la emoción. Debe ser claramente la opción
más adecuada para la estrategia pedida. Las opciones G5 pueden ser saludables, pero NO
pueden constituir Reconstrual; evitá ambigüedades entre la correcta y las demás.

SITUACIONES: En bandas 1-2, un hecho simple sin pistas extra; en bandas 3-4, dos datos
que se matizan sin resolver la duda; en banda 5, incertidumbre real y contexto con historia.
La intensidad emocional NUNCA aumenta más allá de la banda 5. No agregues gravedad
artificial para subir dificultad: desde nivel 14 solo cambian cantidad/calidad de opciones.
Diez escenarios distintos, familiares y cotidianos, sin repetir literalmente los anteriores.

DESEMPEÑO ANTERIOR (si existe):
{historial_texto}
Si hubo errores, retomá el principio en escenarios NUEVOS, pero NO cambies la receta
numérica del nivel. Si no hubo errores, tampoco adelantes bandas ni opciones.

CONTRATO DE SALIDA: 10 elementos en 'niveles' en el orden indicado; cada uno con
'estrategia' EXACTAMENTE 'Reconstrual', 'tipo' EXACTAMENTE 'opcion_multiple',
'nombre', 'escenario' (lista de textos), 'opciones' (lista de textos, cantidad según receta),
'correctas' (lista con UN índice válido desde cero), 'mensaje_exito' y 'mensaje_error'.
'correctas' DEBE SER SIEMPRE [0] antes de mezclar. ORDEN OBLIGATORIO de 'opciones':
posición 0 = CORRECTA; después exactamente los G1 solicitados; después los G2;
después G3; después G4; después G5. Por ejemplo, para un nivel con G1=3 y
los demás 0: opciones=[CORRECTA, G1, G1, G1] y correctas=[0].
Para G1=2, G2=1: opciones=[CORRECTA, G1, G1, G2].
No incluyas etiquetas en el texto visible ni un campo grupos_opciones. Español argentino simple.
Evitá suicidio, autolesión, abuso, violencia grave, muerte de familiares y diagnósticos
o enfermedades graves. No incluyas afirmaciones de certezas sobre intenciones ajenas.
REGLAS DE FEEDBACK:
- mensaje_error debe orientar sin revelar cuál es la respuesta correcta.
- Nunca mencionar posiciones: primera, segunda, última, opción 1, etc.
- Las opciones se mezclan aleatoriamente después de generarse.
- mensaje_exito debe explicar brevemente por qué la respuesta es válida.
"""
    client = _obtener_gemini_client()
    ultimo_error = None
    for intento in range(3):
        prompt_intento = prompt
        if ultimo_error:
            prompt_intento += (
                "\nEL BATCH ANTERIOR FUE RECHAZADO: " + ultimo_error +
                "\nRegenerá los diez ejercicios completos y corregí estrictamente "
                "las cantidades y el ORDEN fijo de opciones: correcta en 0, luego G1, G2, G3, G4, G5."
            )
        try:
            response = client.models.generate_content(
                model='gemini-3.5-flash-lite',
                contents=prompt_intento,
                config={
                    'response_mime_type': 'application/json',
                    'response_schema': BatchEjerciciosFamiliaIA,
                },
            )
            batch = BatchEjerciciosFamiliaIA.model_validate_json(response.text)
            niveles = [nivel.model_dump() for nivel in batch.niveles]
            if len(niveles) != 10:
                raise ValueError(f'Se esperaban 10 niveles, llegaron {len(niveles)}')
            for numero, nivel in enumerate(niveles, start=inicio):
                validar_nivel_ia(nivel, numero, mezclar=False)
                validar_nivel_ia(nivel, mezclar=True)
            print(f'Batch IA validado: niveles globales {inicio}-{inicio + 9}')
            print('\n===== BATCH IA GENERADO =====')
            print(json.dumps(niveles, ensure_ascii=False, indent=2))
            print('=============================\n')
            return niveles
        except Exception as e:
            ultimo_error = str(e)
            print(f'Batch IA rechazado (intento {intento + 1}/3): {ultimo_error}')
    raise ValueError(f'No se pudo generar un batch válido: {ultimo_error}')


def generar_batch_familia_ia(estado):
    return _generar_batch(estado, inicio=1)
>>>>>>> c6bfd46ec0702d1296ffa7b8a099dd31579ac276


def generar_batch_familia_ia_adaptativo(historial, estado):
    # La precarga se dispara tras el 7.º ejercicio de cada batch; también
    # puede llamarse al terminar el 10.º si falló la precarga.
    completados = len(estado.get('_historial_ia', []))
    inicio = ((completados + 3) // 10) * 10 + 1
    return _generar_batch(estado, inicio=inicio, historial=historial)


def validar_nivel_ia(ejercicio, numero_nivel=None, mezclar=True):
    if ejercicio['tipo'] != 'opcion_multiple':
        raise ValueError('El tipo debe ser opcion_multiple')
    if ejercicio['estrategia'] != 'Reconstrual':
        raise ValueError('La estrategia debe ser Reconstrual')
    opciones = ejercicio['opciones']
    cantidad = len(opciones)
    if not 4 <= cantidad <= TECHO_UX:
        raise ValueError(f'Cantidad de opciones fuera de rango: {cantidad}')
    if len(ejercicio['correctas']) != 1:
        raise ValueError('Debe haber exactamente una respuesta correcta')
    indice = ejercicio['correctas'][0]
    if not isinstance(indice, int) or not 0 <= indice < cantidad:
        raise ValueError('Índice correcto inválido')
    if len(set(opciones)) != cantidad or any(not t.strip() for t in opciones):
        raise ValueError('Opciones duplicadas o vacías')

    if numero_nivel is not None:
        grupos, _ = _receta_dificultad(numero_nivel)
        esperado = 1 + sum(grupos)
        if cantidad != esperado:
            raise ValueError(
                f'Nivel global {numero_nivel}: esperaba {esperado} opciones, recibió {cantidad}'
            )
        if indice != 0:
            raise ValueError(f'Nivel global {numero_nivel}: la correcta debe estar en posición 0 antes de mezclar')

<<<<<<< HEAD
    INFORMACIÓN PERSONALIZADA DEL USUARIO (USALOS PARA CREAR ESCENARIOS RELEVANTES):
    - Género: {genero}
    - Convivencia: {contexto.get('convivencia', 'No especificado')}
    - Tiene hermanos: {contexto.get('hermanos', 'No especificado')}
    - Ocupación: {contexto.get('ocupacion', 'No especificado')}
    - Estado en pareja: {contexto.get('pareja', 'No especificado')}
    - Nivel de familiaridad con Regulación Emocional: Nivel {nivel_reg} ({familiaridad})
=======
    if mezclar:
        texto_correcto = opciones[indice]
        random.shuffle(opciones)
        ejercicio['correctas'] = [opciones.index(texto_correcto)]
>>>>>>> c6bfd46ec0702d1296ffa7b8a099dd31579ac276

    # Evitar feedback que revele posiciones incorrectas.
    import re

    mensaje = ejercicio.get("mensaje_error", "")

<<<<<<< HEAD
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
=======
    if re.search(
        r"(?i)\b(primera|segunda|tercera|cuarta|quinta|"
        r"sexta|séptima|última|opción\s*[1-7]|alternativa\s*[1-7])\b",
        mensaje,
    ):
        ejercicio["mensaje_error"] = (
            "Revisá las opciones y buscá una reinterpretación "
            "equilibrada que considere todo el contexto."
        )

    return ejercicio
>>>>>>> c6bfd46ec0702d1296ffa7b8a099dd31579ac276
