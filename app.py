import flet as ft
import requests
import os
import hashlib
import time
import threading
import unicodedata
import random
import json
import csv
import io
import urllib.parse
import asyncio
from datetime import datetime
from flet.auth.providers import GoogleOAuthProvider
from google import genai
from pydantic import BaseModel, Field
from typing import List
from test_inicial import mostrar_test_inicial

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

gemini_client = genai.Client()

def generar_batch_familia_ia(estado):
    # Extraemos la información del test inicial guardada en el estado
    contexto = estado.get("perfil_contexto", {})
    genero = estado.get("genero", "no especificado")

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

    response = gemini_client.models.generate_content(
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

    response = gemini_client.models.generate_content(
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

    return ejercicio

# ==========================================================
# --- CONFIGURACIÓN DE SUPABASE ---
# ----------------------------------------------------------
# OJO: completar estos 2 valores con los de TU PROYECTO de Supabase antes de
# desplegar. Se recomienda usar un proyecto de Supabase separado del de la
# app de Encuesta, porque acá se guardan datos sensibles de salud mental.
# Corré primero los archivos supabase_usuarios_regulacion.sql,
# supabase_temas_seguimiento.sql y supabase_reportes_emocionales.sql (en
# ese orden) en el SQL Editor de ese proyecto.
# ==========================================================
SUPABASE_BASE_URL = "https://wtevnqwkvkposusqraph.supabase.co/rest/v1"
SUPABASE_KEY = "sb_publishable_olUJCGB-IsB7lYI0k3sSuA_Qfej5kmi"

SUPABASE_USUARIOS_URL = f"{SUPABASE_BASE_URL}/usuarios_regulacion"
SUPABASE_REPORTES_URL = f"{SUPABASE_BASE_URL}/reportes_emocionales"
SUPABASE_TEMAS_URL = f"{SUPABASE_BASE_URL}/temas_seguimiento"
SUPABASE_BIENESTAR_URL = f"{SUPABASE_BASE_URL}/chequeos_bienestar"
SUPABASE_REAPPRAISAL_URL = f"{SUPABASE_BASE_URL}/ejercicios_reappraisal"
SUPABASE_JUEGOS_REAPPRAISAL_URL = f"{SUPABASE_BASE_URL}/progreso_juegos_reappraisal"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# Login con Google (opcional, igual patrón que la app de Encuesta): si estas
# 3 variables de entorno no están seteadas, el botón de Google directamente
# no aparece y la app sigue funcionando con el login por mail.
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URL = os.environ.get("GOOGLE_REDIRECT_URL", "")

# ==========================================================
# --- PALETA DE COLORES ---
# ----------------------------------------------------------
# Apps de bienestar "serias" (Calm, Headspace, etc.) evitan el blanco/gris
# puro y el alto contraste: usan fondos cálidos de baja saturación (crema,
# no blanco), un color principal frío-suave (azul o verde azulado, asociado
# a calma/confianza) y como mucho un acento cálido puntual (durazno/dorado
# apagado), con textos en gris cálido en vez de negro puro. Los rojos se
# reservan para errores y la pantalla de crisis (ahí el rojo cumple una
# función real de alerta, no es parte de la paleta "de todos los días").
# ==========================================================
COLOR_FONDO = "#E8DBC0"           # crema cálido: fondo de toda la página (más marcado, se nota bien en pantallas OLED)
COLOR_TARJETA = "#FFFAF0"         # blanco cálido: la tarjeta central de cada pantalla
COLOR_PRIMARIO = "#3D7A7B"        # verde azulado: color "semilla" del tema (botones, ícono principal)
COLOR_PRIMARIO_OSCURO = "#2C5F60"
COLOR_CAJA_SUAVE = "#E4D2AE"      # cajas de contenido (distorsiones, tarjetas de temas)
COLOR_CAJA_INFO = "#CCE3DD"       # cajas de "recordatorio" (contexto de la vez anterior)
COLOR_EXITO = "#4F8F6D"           # verde salvia (en vez de verde saturado)
COLOR_EXITO_CAJA = "#D2E9DA"
COLOR_DORADO = "#C79433"          # acento cálido puntual (ideas/recomendaciones)
COLOR_TEXTO_FUERTE = "#352F27"    # reemplaza negro puro
COLOR_TEXTO_MEDIO = "#665C4C"     # reemplaza GREY_700
COLOR_TEXTO_SUAVE = "#8A7C68"     # reemplaza GREY_500/600

# ==========================================================
# --- DETECCIÓN DE RIESGO SUICIDA ---
# ----------------------------------------------------------
# Se revisa CADA texto libre que la persona escribe a lo largo de todo el
# cuestionario (situación, pensamiento, evidencia, pensamiento
# alternativo, reflexiones), en cualquier paso — la declaración de
# intención suicida puede aparecer desde el arranque o más adelante. Si
# aparece, el flujo normal se corta ahí mismo y pasa al flujo de crisis
# (ver más abajo), sin importar en qué paso estaba.
# Es un detector simple por frases (no un diagnóstico), pensado para
# priorizar sensibilidad: preferimos activarlo de más antes que dejar
# pasar una señal real.
# ==========================================================
def _sin_acentos(texto):
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c))


def _normalizar_riesgo(texto):
    return _sin_acentos((texto or "").strip().lower())


FRASES_RIESGO_SUICIDA = [
    "quiero morir", "quiero morirme", "prefiero estar muerto", "prefiero estar muerta",
    "no quiero vivir", "no quiero seguir viviendo", "no quiero seguir viva", "no quiero seguir vivo",
    "no quiero existir", "no quiero estar viva", "no quiero estar vivo",
    "me quiero matar", "quiero matarme", "matarme de una vez",
    "quiero suicidarme", "me quiero suicidar", "pensando en suicidarme", "pienso en suicidarme", "pense en suicidarme",
    "quitarme la vida", "quitarme mi vida", "quitarme la vida de una vez",
    "terminar con mi vida", "terminar con esta vida", "acabar con mi vida", "acabar con esta vida",
    "poner fin a mi vida",
    "no vale la pena seguir viviendo", "no tiene sentido seguir viviendo",
    "ya no aguanto mas vivir", "ya no aguanto mas seguir viviendo",
    "mejor estaria muerto", "mejor estaria muerta",
    "estarian mejor sin mi", "estarian todos mejor sin mi", "todos estarian mejor sin mi",
    "el mundo estaria mejor sin mi", "si yo no estuviera todo seria mejor",
    "quiero desaparecer para siempre", "yo desapareciera para siempre", "si yo desapareciera",
    "no quiero despertar", "no quiero despertarme mas",
    "tengo un plan para matarme", "como matarme", "como suicidarme",
    "hacerme dano de verdad", "lastimarme para terminar con esto",
]


def detectar_riesgo_suicida(*textos):
    for texto in textos:
        t = _normalizar_riesgo(texto)
        if not t:
            continue
        if any(frase in t for frase in FRASES_RIESGO_SUICIDA):
            return True
    return False


# ==========================================================
# --- DETECCIÓN DE RIESGO HACIA TERCEROS ---
# ----------------------------------------------------------
# Distinto del riesgo suicida: acá se busca una intención real de
# lastimar a otra persona, no el miedo obsesivo a hacerlo sin querer
# (que es justamente el contenido típico de un pensamiento intrusivo de
# tipo "Harm OCD", y NO debe disparar esto). Por eso las frases usan
# verbos de intención/plan ("voy a", "quiero", "tengo un plan para"), no
# de miedo ("puedo", "podría", "sin querer"), que es como está redactado
# el propio hint de la app para esa situación. Igual que con el riesgo
# suicida: es un detector simple por frases, no un diagnóstico, pensado
# para priorizar sensibilidad ante una señal real.
# ==========================================================
FRASES_RIESGO_TERCEROS = [
    "voy a matar a", "quiero matar a", "voy a lastimar a", "quiero lastimar a",
    "le voy a hacer dano a", "le voy a hacer daño a", "tengo un plan para lastimar",
    "tengo ganas de matar a", "quiero hacerle dano de verdad a", "quiero hacerle daño de verdad a",
    "voy a atacar a", "quiero herir a", "voy a herir a", "me quiero vengar de",
    # Variantes de "tengo un plan para..." con los mismos verbos de arriba
    # (encontrado con una simulación grande: "tengo un plan para lastimar"
    # estaba cubierto, pero "tengo un plan para hacerle daño a" —una
    # frase igual de plausible— no).
    "tengo un plan para matar a", "tengo un plan para hacerle dano a", "tengo un plan para hacerle daño a",
    "tengo un plan para atacar a", "tengo un plan para herir a",
]


def detectar_riesgo_terceros(*textos):
    for texto in textos:
        t = _normalizar_riesgo(texto)
        if not t:
            continue
        if any(frase in t for frase in FRASES_RIESGO_TERCEROS):
            return True
    return False


# ==========================================================
# --- CONTENIDO CLÍNICO (basado en Terapia Cognitiva Conductual) ---
# ----------------------------------------------------------
# Distorsiones cognitivas más usadas clínicamente (Beck / Burns), con una
# explicación en criollo para que cualquier persona las entienda sin
# necesitar formación en psicología.
# ==========================================================
DISTORSIONES = [
    ("Todo o nada", "Ver la situación en blanco o negro, sin grises: \"si no sale perfecto, es un fracaso total\"."),
    ("Sobregeneralización", "Sacar una conclusión general y permanente a partir de un solo hecho puntual: \"esto siempre me pasa\", \"nunca me sale nada bien\"."),
    ("Catastrofización", "Pensar que va a pasar lo peor posible, como si fuera casi seguro."),
    ("Lectura de mente", "Suponer que sabés lo que el otro está pensando de vos, sin haber preguntado."),
    ("Adivinación del futuro", "Dar por hecho cómo va a salir algo, como si pudieras predecirlo con certeza."),
    ("Razonamiento emocional", "Creer que algo es cierto solo porque lo sentís así: \"me siento un fracaso, entonces lo soy\"."),
    ("Debería", "Exigirte (o exigirle a otros) reglas rígidas de cómo \"tendría que\" ser todo."),
    ("Etiquetado", "Ponerte (o ponerle a alguien) una etiqueta negativa global por un solo error: \"soy un inútil\"."),
    ("Filtro mental", "Quedarte solo con el detalle negativo de la situación e ignorar todo lo demás."),
    ("Descalificar lo positivo", "Restarle valor a las cosas buenas que pasan, como si no contaran."),
    ("Personalización", "Sentirte responsable de algo que no dependía (solo, o para nada) de vos."),
]

# Un "antídoto" concreto por cada distorsión (técnica estándar de CBT,
# ej. Burns, "Feeling Good"), para que lo que la persona marca en el
# checklist (hoy dentro del Paso 3) deje de ser solo reconocerlo y
# también alimente las recomendaciones finales (Paso 6) y una pista
# breve antes de escribir el pensamiento alternativo (Paso 5).
RECOMENDACIONES_POR_DISTORSION = {
    "Todo o nada": "Ya que notaste que lo estás viendo en blanco o negro: buscá algún punto intermedio, un porcentaje entre 0 y 100 en vez de solo \"perfecto\" o \"fracaso\".",
    "Sobregeneralización": "Ya que notaste que lo estás generalizando: pensá en alguna vez, aunque sea una sola, en la que no pasó lo que decís que \"siempre\" o \"nunca\" pasa.",
    "Catastrofización": "Ya que notaste que estás yendo al peor escenario: preguntate cuál es el resultado más probable, no el peor posible.",
    "Lectura de mente": "Ya que notaste que estás suponiendo lo que otro piensa: considerá si podés simplemente preguntarle, en vez de darlo por hecho.",
    "Adivinación del futuro": "Ya que notaste que estás dando por segura una predicción: recordá que es una predicción, no un hecho, y las predicciones a veces fallan.",
    "Razonamiento emocional": "Ya que notaste que estás usando cómo te sentís como prueba: preguntate qué diría la evidencia real, más allá de lo que sentís ahora.",
    "Debería": "Ya que notaste una regla rígida de \"debería\": probá reemplazarla por \"me gustaría\" o \"preferiría\", y notá si se siente distinto.",
    "Etiquetado": "Ya que notaste que te (o le) pusiste una etiqueta: describí el hecho puntual en vez de la etiqueta global (\"me equivoqué en esto\" en vez de \"soy un desastre\").",
    "Filtro mental": "Ya que notaste que te quedaste con el detalle negativo: buscá activamente algo que también haya salido bien en esa misma situación.",
    "Descalificar lo positivo": "Ya que notaste que le restás valor a lo bueno: anotá algo positivo de esto, por chico que sea, y dejalo contar tanto como lo negativo.",
    "Personalización": "Ya que notaste que te hacés responsable de algo: separá qué parte dependía realmente de vos y qué parte no.",
}


# ==========================================================
# --- BANCO DE SITUACIONES PARA "EJERCICIOS DE REAPPRAISAL" ---
# ----------------------------------------------------------
# Ver banco_situaciones_reappraisal.md para el detalle completo y las
# fuentes (BIBLIOGRAFIA.md sección 7). 10 categorías, 4 situaciones de
# ejemplo cada una (situación, pensamiento automático típico), con su
# controlabilidad (Troy, Shallcross & Mauss, 2013: el reappraisal ayuda
# más ante lo incontrolable) y la técnica de reappraisal más indicada
# según la evidencia para ese tipo de situación.
# ==========================================================
CATEGORIAS_REAPPRAISAL = [
    {
        "nombre": "Conflictos interpersonales",
        "controlabilidad": "Mixta",
        "tecnica": "Perspectiva de un tercero + reinterpretación",
        "situaciones": [
            ("Julieta discutió con su pareja por algo chico (quién lavaba los platos) y quedó un clima incómodo el resto del día.", "Julieta piensa: \"si discutimos por esto, es porque en el fondo no nos entendemos\"."),
            ("Martín le canceló el plan a su amigo Diego a último momento, por segunda vez seguida.", "Diego piensa: \"le importo menos de lo que yo creía\"."),
            ("En una reunión familiar, el hermano de Carla hizo un comentario que ella sintió como una crítica encubierta.", "Carla piensa: \"siempre me está juzgando\"."),
            ("Pablo le pidió a su compañero de casa que ordenara, y al volver encontró todo desordenado otra vez.", "Pablo piensa: \"no le importa nada de lo que le pido\"."),
        ],
    },
    {
        "nombre": "Trabajo o estudio",
        "controlabilidad": "Mixta",
        "tecnica": "Reinterpretación + distanciamiento temporal",
        "situaciones": [
            ("La jefa de Sofía le corrigió un informe delante de todos sus compañeros.", "Sofía piensa: \"quedé como una incompetente delante de todos\"."),
            ("A Andrés se le juntó más trabajo del que puede manejar esta semana.", "Andrés piensa: \"no voy a llegar a nada, esto me supera\"."),
            ("A Valeria no le fue como esperaba en un examen que venía preparando hace meses.", "Valeria piensa: \"esto confirma que no soy buena para esto\"."),
            ("Un compañero de Gustavo recibió el reconocimiento que él venía esperando para sí.", "Gustavo piensa: \"nunca van a valorar lo mío\"."),
        ],
    },
    {
        "nombre": "Autocrítica y errores propios",
        "controlabilidad": "Alta",
        "tecnica": "Autodistanciamiento en 3ª persona",
        "situaciones": [
            ("Celeste se dio cuenta de que mandó un mail con un error evidente a un cliente importante.", "Celeste piensa: \"soy un desastre, esto no tiene arreglo\"."),
            ("Ramiro se olvidó de algo que le había prometido a su hija.", "Ramiro piensa: \"no se puede confiar en mí para nada\"."),
            ("Paula dijo algo en una charla con amigos y se arrepintió apenas salió de su boca.", "Paula piensa: \"quedé como una tonta, seguro todos lo están pensando\"."),
            ("Hernán siente que quedó atrás comparado con cómo se imaginaba a esta altura de su vida.", "Hernán piensa: \"ya perdí el tiempo, es tarde para cambiar algo\"."),
        ],
    },
    {
        "nombre": "Rechazo social y comparación",
        "controlabilidad": "Baja",
        "tecnica": "Distanciamiento temporal",
        "situaciones": [
            ("Noelia publicó algo en redes que le importaba mucho y tuvo muchísima menos repercusión de la que esperaba.", "Noelia piensa: \"a nadie le importa lo que hago\"."),
            ("Federico vio fotos de una juntada de su grupo de conocidos a la que no lo invitaron.", "Federico piensa: \"me dejaron afuera a propósito\"."),
            ("Rocío le mandó un mensaje a una amiga hace tres días y todavía no tuvo respuesta.", "Rocío piensa: \"hice algo mal, por eso no me contesta\"."),
            ("Mirando lo que muestran otros en redes, Sebastián siente que su vida se queda corta.", "Sebastián piensa: \"todos la están pasando mejor que yo\"."),
        ],
    },
    {
        "nombre": "Dinero y finanzas",
        "controlabilidad": "Mixta",
        "tecnica": "Reinterpretación orientada a resolución + distanciamiento temporal",
        "situaciones": [
            ("A Mariela se le rompió el auto y tuvo que hacer un gasto grande que no tenía contemplado.", "Mariela piensa: \"nunca voy a poder organizarme con la plata\"."),
            ("Tomás revisó los gastos del mes y vio que gastó bastante más de lo que planeaba.", "Tomás piensa: \"soy un desastre para manejar el dinero\"."),
            ("Silvia se enteró de que una excompañera de su edad está mucho mejor económicamente que ella.", "Silvia piensa: \"me quedé atrás, hice todo mal\"."),
            ("Leo tiene que pedirle ayuda económica a su familia este mes y le da vergüenza.", "Leo piensa: \"esto demuestra que no puedo solo\"."),
        ],
    },
    {
        "nombre": "Preocupación por la salud",
        "controlabilidad": "Baja",
        "tecnica": "Distanciamiento (observador objetivo)",
        "situaciones": [
            ("Camila tiene un síntoma nuevo desde hace unos días y todavía no sabe qué es.", "Camila piensa: \"seguro es algo grave\"."),
            ("El papá de Bruno se hizo un chequeo de rutina y la familia está esperando los resultados.", "Bruno piensa: \"algo malo va a salir, lo presiento\"."),
            ("Verónica nota que últimamente se cansa más de lo habitual.", "Verónica piensa: \"mi cuerpo ya no da más\"."),
            ("Un amigo le contó a Facundo una experiencia de salud difícil, y ahora Facundo no deja de pensar en eso.", "Facundo piensa: \"es cuestión de tiempo hasta que me toque a mí\"."),
        ],
    },
    {
        "nombre": "Pérdidas y finales cotidianos",
        "controlabilidad": "Baja",
        "tecnica": "Distanciamiento temporal + autodistanciamiento",
        "situaciones": [
            ("Elena terminó una relación de varios años y siente que quedó un vacío.", "Elena piensa: \"nunca voy a encontrar algo así de nuevo\"."),
            ("Matías se mudó de ciudad por trabajo y extraña cómo era su vida antes.", "Matías piensa: \"dejé atrás lo único bueno que tenía\"."),
            ("Un proyecto en el que Lucía invirtió mucho tiempo se terminó sin salir como esperaba.", "Lucía piensa: \"perdí años en algo que no sirvió para nada\"."),
            ("El grupo con el que Marcos se juntaba hace años a jugar al fútbol se disolvió.", "Marcos piensa: \"ya nada va a volver a ser lo mismo\"."),
        ],
    },
    {
        "nombre": "Presión de tiempo y sobrecarga",
        "controlabilidad": "Alta",
        "tecnica": "Reinterpretación + resolución de problemas",
        "situaciones": [
            ("Ana tiene el día lleno de cosas por hacer y siente que no va a llegar con nada.", "Ana piensa: \"esto es imposible, me voy a quedar corta en todo\"."),
            ("Iván intentaba concentrarse en algo importante y lo interrumpieron cuatro veces en una hora.", "Iván piensa: \"así no puedo avanzar en nada\"."),
            ("Florencia postergó un trámite importante durante semanas y ahora lo tiene encima.", "Florencia piensa: \"soy un desastre organizándome, siempre me pasa lo mismo\"."),
            ("Ezequiel siente que le dedica todo su tiempo a obligaciones y nada a él.", "Ezequiel piensa: \"mi vida es solo cumplir con cosas\"."),
        ],
    },
    {
        "nombre": "Imprevistos y decepciones menores",
        "controlabilidad": "Baja",
        "tecnica": "Reinterpretación con perspectiva/humor",
        "situaciones": [
            ("Juan perdió el tren por un minuto justo el día que tenía una reunión importante.", "Juan piensa: \"siempre me pasa esto a mí\"."),
            ("El viaje que Daniela venía organizando hace meses se canceló por algo fuera de su control.", "Daniela piensa: \"nada me sale como lo planeo\"."),
            ("A Cristian se le rompió el lavarropas justo la semana que estaba más ajustado de plata.", "Cristian piensa: \"no puede ser que siempre se rompa algo justo ahora\"."),
            ("Belén hizo dos horas de fila para un trámite y al llegar le dijeron que le faltaba un papel.", "Belén piensa: \"estoy perdiendo el día por esto\"."),
        ],
    },
    {
        "nombre": "Incertidumbre y falta de control",
        "controlabilidad": "Baja",
        "tecnica": "Distanciamiento temporal",
        "situaciones": [
            ("Marina está esperando la respuesta de una entrevista de trabajo, y la decisión no depende de ella.", "Marina piensa: \"no aguanto no saber qué va a pasar\"."),
            ("Agustín mira las noticias sobre la situación del país y le crece la angustia por el futuro.", "Agustín piensa: \"cada vez va a estar peor, no hay nada que hacer\"."),
            ("La pareja de Lorena tiene que decidir si acepta un traslado, y esa decisión la afecta de lleno a ella.", "Lorena piensa: \"mi vida depende de algo que no controlo para nada\"."),
            ("A Nico se le viene un cambio grande y todavía no sabe cómo va a ser.", "Nico piensa: \"no voy a poder manejar lo que sea que pase\"."),
        ],
    },
]

# Ejercicios "inventados" a completar antes de desbloquear "propias".
# Era 10, después 3, y quedó en 1 (pedido de Gabriel, 2026-07-14): con
# probar la técnica una sola vez en frío alcanza para habilitar el
# trabajo sobre situaciones de verdad.
UMBRAL_REAPPRAISAL_PROPIAS = 1

# ==========================================================
# "PRACTICÁ CON ESCENARIOS" — juegos de reappraisal (integración MENTO)
# ----------------------------------------------------------
# Gabriel se puso a colaborar con el equipo de MENTO (Bernardita Arditti
# y compañía, repo github.com/bernarditaarditti/MENTO.app), que armó una
# versión gamificada por "islas" (Familia/Salud/Vínculos/Trabajo) con 5
# niveles cada una, en Next.js/React. Acá se REESCRIBIERON en Flet los 20
# escenarios y las 2 mecánicas de juego de ese repo (opción múltiple con
# feedback, y emparejar pensamiento negativo↔reinterpretación positiva),
# tal cual el contenido y la paleta de colores de MENTO — no se copió
# código React (arquitecturas distintas), se migró el contenido. Esto se
# suma como un modo NUEVO dentro de "Otra perspectiva", sin sacar el
# ejercicio de escribir la propia reinterpretación (decisión de Gabriel,
# 2026-07-17). Paleta y tipografía (Poppins) usadas SOLO en estas
# pantallas, como identidad propia de este modo de juego.
# ==========================================================
MENTO_ROSA = "#FFC7D1"
MENTO_ROSA_TEXTO = "#F36E86"
MENTO_VERDE = "#52B788"
MENTO_VERDE_OSCURO = "#00C49A"
MENTO_AMARILLO = "#FFC832"
MENTO_AMARILLO_CLARO = "#FED45F"
MENTO_CELESTE = "#0096C7"
MENTO_CELESTE_CAJA = "#C7EAF5"
MENTO_NARANJA = "#FE814A"
MENTO_EXITO_JUEGO = "#5CD98C"
MENTO_ERROR_JUEGO = "#FF6464"
MENTO_SELECCION_JUEGO = "#F9B702"
MENTO_FUENTE = "Poppins"

MENTO_CATEGORIAS = [
    {"clave": "familia", "nombre": "Familia", "color": MENTO_AMARILLO, "icono": ft.Icons.FAMILY_RESTROOM},
    {"clave": "salud", "nombre": "Salud", "color": MENTO_VERDE, "icono": ft.Icons.FAVORITE},
    {"clave": "vinculos", "nombre": "Vínculos", "color": MENTO_NARANJA, "icono": ft.Icons.GROUPS},
    {"clave": "trabajo", "nombre": "Trabajo o estudio", "color": MENTO_CELESTE, "icono": ft.Icons.WORK},
]

# Explicación de cada estrategia ("¿Sabías que...?" en MENTO), accesible
# desde el ícono de información de cada nivel.
MENTO_EXPLICACIONES = {
    "Reconstrual": (
        "Reconstrual es una estrategia para regular tus emociones cambiando el enfoque de una situación: "
        "en vez de quedarte atrapado/a en un detalle que te estresa, ampliás la mirada y la reinterpretás "
        "desde un contexto más general o más neutral."
    ),
    "Repurposing": (
        "Repurposing es una forma de regular tus emociones cambiando el propósito que le das a una "
        "situación. En lugar de verla solo como algo molesto o difícil, la reinterpretás como una "
        "oportunidad: para aprender, practicar paciencia, fortalecer un valor, o crecer de alguna manera."
    ),
    "Reappraisal interpersonal": (
        "El reappraisal interpersonal consiste en reinterpretar lo que otra persona dijo o hizo. No se "
        "trata de justificar comportamientos dañinos, sino de abrir espacio a interpretaciones más "
        "realistas y reducir conclusiones automáticas."
    ),
    "Reappraisal inventivo": (
        "El reappraisal inventivo consiste en generar una interpretación nueva, creativa o inesperada "
        "sobre una situación negativa, para cambiar la emoción que te provoca. No se trata de negar la "
        "realidad, sino de buscar activamente alternativas, aunque no sean las más obvias."
    ),
    "Reinterpretación positiva": (
        "La reinterpretación positiva busca encontrar un aspecto constructivo o beneficioso dentro de una "
        "situación difícil. No es negar lo negativo, sino reconocer que puede haber algo bueno mezclado: "
        "un aprendizaje, una oportunidad, un fortalecimiento personal."
    ),
}

# Los 20 escenarios: 4 categorías × 10 niveles. Contenido migrado de MENTO
# (mismos escenarios, opciones y mensajes de feedback; se corrigió un
# typo de esa fuente, "Reppraisal" → "Reappraisal"). Cada nivel es
# "opcion_multiple" (elegís UNA opción entre varias; puede haber más de
# un índice válido en "correctas", pero con marcar una sola alcanza) o
# "emparejar" (unís cada pensamiento negativo con su reinterpretación
# positiva correspondiente, un par a la vez).
MENTO_NIVELES = {
    "familia": [
        {
            "estrategia": "Reconstrual",
            "nombre": "Discusión familiar",
            "tipo": "opcion_multiple",
            "escenario": [
                "En la mesa, un familiar te dice: \"Siempre estás en el teléfono, nunca prestás atención\".",
                "Esto te molesta, porque pensás que te está atacando y no valora que también necesitás tu espacio.",
            ],
            "opciones": [
                "No me soporta y siempre busca criticarme",
                "Exagera y no tiene razón",
                "Solo dice eso para dejarme mal frente a los demás",
                "Quizás está preocupado por nuestra conexión y esto es su manera de expresarlo",
            ],
            "correctas": [3],
            "mensaje_exito": "Reinterpretar la crítica como una oportunidad reduce el malestar y te ayuda a crecer.",
            "mensaje_error": "Esa interpretación aumenta la frustración.",
        },
        {
            "estrategia": "Repurposing",
            "nombre": "Cambio de planes",
            "tipo": "opcion_multiple",
            "escenario": [
                "Se cancela un viaje en familia por mal clima.",
                "Eso te hace sentir muy mal porque era algo que anhelabas bastante.",
            ],
            "opciones": [
                "Mejor cada uno hace lo suyo, ya está todo perdido",
                "Todo arruinado, el día ya no sirve",
                "Pasar tiempo en casa jugando juegos de mesa",
                "Aprovechar para cocinar juntos una comida especial",
                "No hay nada que pueda reemplazar este plan",
                "Hacer una tarde de películas en familia",
            ],
            "correctas": [2, 3, 5],
            "mensaje_exito": "Reinterpretar la situación de manera constructiva te ayuda a encontrar alternativas positivas.",
            "mensaje_error": "Esa interpretación aumenta la frustración.",
        },
        {
            "estrategia": "Reappraisal interpersonal",
            "nombre": "Gastos en la casa",
            "tipo": "opcion_multiple",
            "escenario": ["Mamá/papá está preocupado por un gasto imprevisto en la casa."],
            "opciones": [
                "Esto nos enseña a organizarnos mejor",
                "Bueno, ya está, no hay nada que hacer",
                "Es un desastre, siempre pasa lo mismo",
                "No pensemos en eso, ignoremos el problema",
                "Seguro vamos a tener más gastos así",
            ],
            "correctas": [0],
            "mensaje_exito": "Reinterpretar la crítica como una oportunidad reduce el malestar y te ayuda a crecer.",
            "mensaje_error": "Esa interpretación aumenta la frustración.",
        },
        {
            "estrategia": "Reinterpretación positiva",
            "nombre": "Recorte de ingresos",
            "tipo": "emparejar",
            "escenario": [
                "La familia recibe la noticia de un recorte de ingresos.",
                "Aparecen tres pensamientos automáticos negativos: uní cada uno con su reinterpretación positiva.",
            ],
            "negativos": ["Esto destruye nuestra vida", "Nunca vamos a poder salir adelante", "Todo empeora"],
            "positivos": [
                "Vamos a aprender a organizar mejor los gastos",
                "Podemos apoyarnos más como familia",
                "Quizás encontremos formas nuevas de resolver juntos",
            ],
            "pares_correctos": [(0, 1), (1, 0), (2, 2)],
            "mensaje_exito": "Pudiste transformar un pensamiento negativo en uno más realista y positivo. Ese es un gran paso para cuidar tu bienestar emocional.",
            "mensaje_error": "Esa combinación no es la correcta — fijate qué reinterpretación responde mejor a ese pensamiento.",
        },
        {
            "estrategia": "Reconstrual",
            "nombre": "Consejo a tu hermano",
            "tipo": "opcion_multiple",
            "escenario": ["Tu hermano/a no consiguió una beca a la que había aplicado y te pide consejo."],
            "opciones": [
                "Es cierto, el mercado laboral es imposible",
                "Una negativa no define tu camino; esto te ayuda a ver qué mejorar",
                "Quizás esta experiencia te preparó para la próxima entrevista",
                "No le des importancia, ya fue",
                "Podemos revisar juntos tu CV o practicar para la próxima, no estás solo/a",
                "Si no te tomaron, seguramente algo hiciste mal",
            ],
            "correctas": [1, 2, 4],
            "mensaje_exito": "Reinterpretar la crítica como una oportunidad reduce el malestar y te ayuda a crecer.",
            "mensaje_error": "Esa interpretación aumenta la frustración.",
        },
    ],
    "salud": [
        {
            "estrategia": "Reconstrual",
            "nombre": "Sala de espera",
            "tipo": "opcion_multiple",
            "escenario": ["Estás en una sala de espera hospitalaria con otros pacientes. Parece que hay mucha demora."],
            "opciones": [
                "Estoy cuidando mi salud",
                "Aprovecho para descansar y revisar mensajes",
                "Voy a perder mucho tiempo inútilmente",
            ],
            "correctas": [0, 1],
            "mensaje_exito": "El reappraisal por reconstrual consiste en reinterpretar la situación de una manera alternativa y más realista, reduciendo la reacción emocional automática.",
            "mensaje_error": "Esta interpretación aumenta la emoción negativa y no es constructiva. La idea es encontrar una perspectiva más positiva y útil de la situación.",
        },
        {
            "estrategia": "Repurposing",
            "nombre": "Noticia médica",
            "tipo": "opcion_multiple",
            "escenario": ["Aparece una notificación médica: \"Colesterol alto detectado\"."],
            "opciones": [
                "Todo va a empeorar a partir de ahora",
                "Esto arruina mi salud para siempre",
                "Ya no tiene sentido intentar mejorar",
                "Puedo hacer cambios a tiempo",
                "Esto me motiva a moverme más y cuidarme",
                "No hay nada que pueda hacer",
            ],
            "correctas": [3, 4],
            "mensaje_exito": "Cambiar la meta original por una alternativa valiosa ayuda a mantener el bienestar y reduce el impacto emocional.",
            "mensaje_error": "Parece difícil ver alternativas cuando estamos decepcionados. Buscar un nuevo propósito para ese tiempo puede aliviar la reacción negativa.",
        },
        {
            "estrategia": "Reconstrual",
            "nombre": "Noticia mundial",
            "tipo": "opcion_multiple",
            "escenario": [
                "Titular negativo: \"Se intensifica la pandemia\". Esto te hace sentir frustrado/a y pesimista, "
                "porque pensás que el mundo nunca va a mejorar."
            ],
            "opciones": [
                "Nada de lo que haga sirve para protegerme",
                "Esto demuestra que todo va a seguir empeorando sin remedio",
                "Esto une a la comunidad científica",
                "Me recuerda la importancia de cuidar a mis seres queridos",
                "No hay manera de que el mundo se recupere de algo así",
            ],
            "correctas": [2, 3],
            "mensaje_exito": "El reappraisal por reconstrual consiste en reinterpretar la situación de una manera alternativa y más realista, reduciendo la reacción emocional automática.",
            "mensaje_error": "Esta interpretación aumenta la emoción negativa y no es constructiva. La idea es encontrar una perspectiva más positiva y útil de la situación.",
        },
        {
            "estrategia": "Repurposing",
            "nombre": "Hábitos",
            "tipo": "emparejar",
            "escenario": ["Aparecen tres pensamientos automáticos sobre cambiar de hábitos: uní cada uno con su reinterpretación positiva."],
            "negativos": ["No tengo tiempo.", "Me falta motivación.", "No sé por dónde empezar."],
            "positivos": [
                "Elegir un hábito pequeño hoy es mejor que no empezar.",
                "Puedo empezar con solo 10 minutos de caminata diaria.",
                "Un recordatorio de respiración cada tanto ya reduce el estrés.",
            ],
            "pares_correctos": [(0, 1), (1, 2), (2, 0)],
            "mensaje_exito": "Pudiste transformar preocupaciones sobre hábitos en reinterpretaciones positivas. Ese es un gran paso para cuidar tu salud.",
            "mensaje_error": "Esa combinación no es la correcta — fijate qué reinterpretación responde mejor a ese pensamiento.",
        },
        {
            "estrategia": "Reappraisal inventivo",
            "nombre": "Dolor de cabeza",
            "tipo": "opcion_multiple",
            "escenario": ["Te duele la cabeza y estás cansado/a."],
            "opciones": [
                "Este dolor arruina por completo mi jornada",
                "Mi cuerpo me pide descansar",
                "Quizás solo necesito hidratarme mejor",
                "Seguro que me voy a sentir peor todo el día",
                "Es una señal para bajar el ritmo",
                "No hay nada que pueda hacer para mejorar",
            ],
            "correctas": [1, 2, 4],
            "mensaje_exito": "Cambiar la meta original por una alternativa valiosa ayuda a mantener el bienestar y reduce el impacto emocional.",
            "mensaje_error": "Parece difícil ver alternativas cuando estamos decepcionados. Buscar un nuevo propósito para ese tiempo puede aliviar la reacción negativa.",
        },
    ],
    "vinculos": [
        {
            "estrategia": "Reconstrual",
            "nombre": "Mensaje sin respuesta",
            "tipo": "opcion_multiple",
            "escenario": [
                "Ves la pantalla de chat: \"Visto a las 17:05\" y no llega ninguna respuesta.",
                "Sentís ansiedad o molestia porque pensás que la otra persona te está ignorando.",
            ],
            "opciones": [
                "Está ocupado/a y no pudo responder todavía",
                "Seguro que todo va a terminar saliendo perfecto gracias a esto",
                "Es obvio que me está evitando y debería preocuparme más",
                "Voy a distraerme y no pensar en esto para no sentir nada",
            ],
            "correctas": [0],
            "mensaje_exito": "El reappraisal por reconstrual consiste en reinterpretar la situación de una manera alternativa y más realista, reduciendo la reacción emocional automática.",
            "mensaje_error": "Esa interpretación aumenta la frustración.",
            "mensajes_error_opcion": {
                1: "Esta opción busca encontrar beneficios. Es útil en otros contextos, pero acá el objetivo es reinterpretar la situación, no buscar un lado positivo.",
                2: "Esta interpretación aumenta la emoción negativa y no es un reappraisal. La idea del ejercicio es abrir posibilidades flexibles, no asumir lo peor.",
                3: "Esto no es reappraisal. La supresión intenta no sentir, pero no cambia el significado de la situación. Reappraisal busca reinterpretarla para reducir la carga emocional.",
            },
        },
        {
            "estrategia": "Repurposing",
            "nombre": "Cita cancelada",
            "tipo": "opcion_multiple",
            "escenario": [
                "Recibís la notificación: \"Lo siento, no voy a poder ir hoy\".",
                "Sentís decepción y pensás que el día está arruinado.",
            ],
            "opciones": [
                "Aprovecho la tarde para descansar y recargar energía",
                "Todo arruinado, ya no sirve el día",
                "Puedo usar este tiempo para avanzar en algo que me importa",
                "No voy a pensar en esto, me distraigo y ya",
                "Tal vez puedo hacer algo que venía postergando y me haría bien",
                "Seguro lo canceló porque ya no le interesa verme",
            ],
            "correctas": [0, 2, 4],
            "mensaje_exito": "Cambiar la meta original por una alternativa valiosa ayuda a mantener el bienestar y reduce el impacto emocional.",
            "mensaje_error": "Parece difícil ver alternativas cuando estamos decepcionados. Buscar un nuevo propósito para ese tiempo puede aliviar la reacción negativa.",
        },
        {
            "estrategia": "Reconstrual",
            "nombre": "Amigo distante",
            "tipo": "opcion_multiple",
            "escenario": ["Un amigo/a tuyo está más distante que de costumbre y no sabés bien por qué."],
            "opciones": [
                "No le importo, me está ignorando",
                "Capaz está abrumado/a o pendiente de algo importante",
                "Lo hace para molestarme",
            ],
            "correctas": [1],
            "mensaje_exito": "Esta respuesta ayuda a reinterpretar la situación como una mala coincidencia específica en lugar de una falla personal.",
            "mensaje_error": "Esa interpretación aumenta la frustración.",
            "mensajes_error_opcion": {
                0: "Evadir no es una buena forma de manejar lo que a uno le pasa, es preferible trabajarlo para estar mejor preparado/a.",
            },
        },
        {
            "estrategia": "Reinterpretación positiva",
            "nombre": "Discusión de pareja",
            "tipo": "emparejar",
            "escenario": ["Aparecen tres pensamientos automáticos tras una discusión de pareja: uní cada uno con su reinterpretación positiva."],
            "negativos": [
                "Esto demuestra que no le importo.",
                "Siempre pasa lo mismo, seguro lo hizo a propósito.",
                "Nunca me presta atención.",
            ],
            "positivos": [
                "Un malentendido no define toda la relación.",
                "Tal vez solo se olvidó, no es falta de amor.",
                "Discutir también significa que la relación nos importa.",
            ],
            "pares_correctos": [(0, 2), (1, 0), (2, 1)],
            "mensaje_exito": "Pudiste transformar un pensamiento negativo en uno más realista y positivo. Ese es un gran paso para cuidar tu bienestar emocional.",
            "mensaje_error": "Esa combinación no es la correcta — fijate qué reinterpretación responde mejor a ese pensamiento.",
        },
        {
            "estrategia": "Repurposing",
            "nombre": "Apoyo a un amigo",
            "tipo": "opcion_multiple",
            "escenario": ["Un amigo/a te escribe: \"Me siento re mal, nadie me entiende\"."],
            "opciones": [
                "Entiendo que duela, es horrible sentirse solo/a. Buscar apoyo ya muestra tu fortaleza",
                "Y... si nadie te entiende, es porque explicás mal las cosas",
                "Bueno, no debe ser tan grave, distraete y ya",
                "A todos les pasa, no tenés por qué sentirte así",
                "Acá estoy. A veces sentirse incomprendido/a no significa que estés solo/a; podemos pensar juntos qué necesitás",
                "Lo que sentís es válido. A veces hablarlo con alguien más ayuda a ver opciones que no se notan ahora",
            ],
            "correctas": [0, 4, 5],
            "mensaje_exito": "Cambiar la meta original por una alternativa valiosa ayuda a mantener el bienestar y reduce el impacto emocional.",
            "mensaje_error": "Parece difícil ver alternativas cuando estamos decepcionados. Buscar un nuevo propósito para ese tiempo puede aliviar la reacción negativa.",
        },
    ],
    "trabajo": [
        {
            "estrategia": "Reconstrual",
            "nombre": "Feedback de tu jefe/profesor",
            "tipo": "opcion_multiple",
            "escenario": [
                "Tu jefe/profesor dice: \"Este trabajo está lleno de errores, no parece que le hayas dedicado esfuerzo\".",
                "Esto te hace sentir mal.",
            ],
            "opciones": [
                "Si el jefe/profesor no reconoce tu trabajo, tu trabajo debe haber sido poco valioso",
                "Como el jefe/profesor piensa que te esforzaste poco, tu esfuerzo real es irrelevante",
                "Aunque no te hayan valorado como esperabas, los errores cometidos te van a servir para mejorar",
                "Vos sabés el esfuerzo que pusiste en esto, y que no te lo reconozcan no le resta valor",
            ],
            "correctas": [2, 3],
            "mensaje_exito": "Reinterpretar la crítica como una oportunidad reduce el malestar y te ayuda a crecer.",
            "mensaje_error": "Esa interpretación aumenta la frustración.",
        },
        {
            "estrategia": "Repurposing",
            "nombre": "Plan B",
            "tipo": "opcion_multiple",
            "escenario": ["Sacaste una nota baja en un examen que venías preparando."],
            "opciones": [
                "Soy un fracaso",
                "Esto demuestra que el esfuerzo no sirve",
                "Me cuesta pero puedo aprender",
                "Aprendí qué temas reforzar para la próxima",
                "Al menos tengo una base para avanzar",
                "Siempre me va mal en todo",
            ],
            "correctas": [2, 3, 4],
            "mensaje_exito": "Detectar cómo te hablás es el primer paso para cambiarlo.",
            "mensaje_error": "Esa interpretación aumenta la frustración.",
        },
        {
            "estrategia": "Reappraisal interpersonal",
            "nombre": "Amigo desanimado",
            "tipo": "opcion_multiple",
            "escenario": ["Un amigo/a tuyo no consiguió una beca a la que había aplicado y está desanimado/a."],
            "opciones": [
                "Sí, es injusto, quizás no vale la pena seguir intentando",
                "Quizás esta no era la beca adecuada, podés aplicar a otra con más chances",
                "Tranquilo/a, olvidate del tema y no pienses más",
            ],
            "correctas": [1],
            "mensaje_exito": "Esta respuesta ayuda a reinterpretar la situación como una mala coincidencia específica en lugar de una falla personal.",
            "mensaje_error": "Esa interpretación aumenta la frustración.",
            "mensajes_error_opcion": {
                0: "Evadir no es una buena forma de manejar lo que a uno le pasa, es preferible trabajarlo para estar mejor preparado/a.",
            },
        },
        {
            "estrategia": "Reinterpretación positiva",
            "nombre": "Recorte de personal",
            "tipo": "emparejar",
            "escenario": ["Aparecen cuatro pensamientos automáticos tras un recorte de personal: uní cada uno con su reinterpretación positiva."],
            "negativos": ["Voy a perder mi trabajo", "Es el final de mi carrera", "Todo está perdido", "Me voy a quedar sin plata"],
            "positivos": [
                "Tengo ahorros. Voy a aguantar hasta conseguir otro",
                "Es momento de actualizar mis habilidades",
                "Voy a aprovechar para buscar nuevas oportunidades laborales",
                "Es un cambio que abre nuevas oportunidades",
            ],
            "pares_correctos": [(0, 2), (1, 1), (2, 3), (3, 0)],
            "mensaje_exito": "Pudiste transformar un pensamiento negativo en uno más realista y positivo. Ese es un gran paso para cuidar tu bienestar emocional.",
            "mensaje_error": "Esa combinación no es la correcta — fijate qué reinterpretación responde mejor a ese pensamiento.",
        },
        {
            "estrategia": "Repurposing",
            "nombre": "Proyecto grupal",
            "tipo": "opcion_multiple",
            "escenario": ["Un proyecto grupal no salió como esperaban."],
            "opciones": [
                "Mejoramos aunque no llegamos al objetivo",
                "Fue un desastre total, no sirve para nada",
                "Seguro el profesor nos tiene bronca",
                "No aprendimos nada, solo perdimos tiempo",
                "No voy a trabajar en grupos nunca más",
                "Aprendí a coordinar mejor en equipo",
            ],
            "correctas": [0, 5],
            "mensaje_exito": "Detectar cómo te hablás es el primer paso para cambiarlo.",
            "mensaje_error": "Esa interpretación aumenta la frustración.",
        },
    ],
}


def calcular_distorsiones_frecuentes(reportes, top_n=3):
    # Cuenta cuántas veces aparece cada distorsión marcada a lo largo de
    # TODOS los reportes de la persona (no por tema puntual), para mostrar
    # un patrón general en el resumen del historial.
    conteo = {}
    for rep in reportes:
        texto = rep.get("distorsiones") or ""
        for nombre in [n.strip() for n in texto.split(",") if n.strip()]:
            conteo[nombre] = conteo.get(nombre, 0) + 1
    return sorted(conteo.items(), key=lambda kv: kv[1], reverse=True)[:top_n]


# ==========================================================
# --- COMPARTIR EL HISTORIAL ---
# ----------------------------------------------------------
# Primera versión, sin backend propio para compartir: arma una planilla
# (CSV) descargable con todo el historial, y un resumen de texto corto
# para compartir directo por WhatsApp/mail (con el propio botón de
# WhatsApp/mail del celular, no se manda nada automáticamente — la
# persona elige el destinatario y confirma el envío ella misma). Cuando
# haya un backend propio (Supabase configurado del todo), esto se puede
# reemplazar por un link compartible de verdad.
# ==========================================================
def generar_csv_historial(reportes):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Fecha", "Situación", "Tipo de situación", "Emoción", "Intensidad (0-10)", "% inicial", "% final", "Pensamiento alternativo / compromiso"])
    for rep in sorted(reportes, key=lambda x: x.get("fecha") or ""):
        writer.writerow([
            (rep.get("fecha") or "")[:10],
            rep.get("situacion") or "",
            rep.get("tipo_situacion") or "",
            rep.get("emocion_inicial") or "",
            rep.get("intensidad_inicial", ""),
            rep.get("creencia_inicial_pct", ""),
            rep.get("creencia_final_pct", ""),
            rep.get("pensamiento_alternativo") or "",
        ])
    return buffer.getvalue()


def generar_texto_resumen_historial(reportes, maximo=15):
    # Se limita a los últimos registros para que el link de WhatsApp/mail
    # no quede demasiado largo (los enlaces muy extensos pueden fallar).
    ordenados = sorted(reportes, key=lambda x: x.get("fecha") or "", reverse=True)[:maximo]
    ordenados.reverse()
    lineas = ["Mi evolución en DRE:", ""]
    for rep in ordenados:
        fecha = (rep.get("fecha") or "")[:10]
        situ = (rep.get("situacion") or "")[:60]
        etiqueta = "impulso" if rep.get("tipo_situacion") == TIPO_OBSESION else "creencia"
        lineas.append(f"{fecha} — {situ}: {etiqueta} {rep.get('creencia_inicial_pct')}% → {rep.get('creencia_final_pct')}%")
    return "\n".join(lineas)


# Banco de recomendaciones conductuales (activación conductual): actividades
# concretas y de bajo costo, elegidas según la emoción predominante. Se
# mantienen fijas (no generadas libremente) para asegurar que siempre estén
# basadas en evidencia y sean seguras.
RECOMENDACIONES_POR_EMOCION = {
    "Tristeza": [
        "Elegí una actividad chica que antes disfrutabas y hacela hoy, aunque no tengas muchas ganas (el ánimo suele mejorar después de la acción, no antes).",
        "Contactá a una persona con la que tengas buena relación, aunque sea un mensaje corto.",
        "Salí a caminar 15-20 minutos al aire libre.",
        "Anotá una tarea chica y concreta que puedas terminar hoy, para tener una sensación de logro.",
        "Exponete un rato a la luz del sol o abrí las cortinas/ventanas de tu casa.",
    ],
    "Ansiedad": [
        "Hacé un ejercicio de respiración lenta: inhalar 4 segundos, sostener 4, exhalar 6, repetir 5 veces.",
        "Escribí qué es lo peor que podría pasar realmente, y qué harías vos si pasara (para bajar la incertidumbre).",
        "Postergá la preocupación a un horario fijo del día (20 minutos), en vez de darle vueltas todo el día — no a todos les funciona igual, pero vale la pena probarlo.",
        "Hacé algo con las manos que requiera atención (cocinar, ordenar, dibujar) para salir del ciclo de pensamientos que se repiten.",
        "Movete: una caminata rápida o algo de actividad física ayuda a bajar la activación física de la ansiedad.",
    ],
    "Enojo": [
        "Antes de responder o actuar, esperá al menos 10 minutos y alejate físicamente de la situación si podés.",
        "Escribí lo que te pasó y por qué te enojó, sin mostrárselo a nadie, para bajar la intensidad antes de decidir qué hacer.",
        "Hacé alguna actividad física breve (caminar rápido, estirar, ejercicio) para descargar la tensión del cuerpo.",
        "Pensá qué le dirías a un amigo que te cuenta la misma situación, y probá aplicarte ese mismo consejo.",
    ],
    "Culpa": [
        "Escribí qué parte de lo que pasó dependía realmente de vos, y qué parte no.",
        "Si corresponde, pensá en una acción concreta de reparación que puedas hacer (pedir disculpas, aclarar algo, ayudar).",
        "Preguntate qué le dirías a un amigo que se siente igual de culpable por algo parecido.",
    ],
    "Vergüenza": [
        "Contale lo que te pasó a alguien de confianza: la vergüenza suele bajar mucho cuando se comparte en vez de guardarla.",
        "Recordá una situación parecida que le haya pasado a otra persona, y cómo la viste vos desde afuera (probablemente con más comprensión que con vos mismo/a).",
        "Hacé algo que te conecte con tus valores o con algo que te haga sentir bien con vos mismo/a hoy.",
    ],
    "General": [
        "Salí a caminar al aire libre al menos 15 minutos.",
        "Contactá a alguien de confianza, aunque sea con un mensaje corto.",
        "Elegí una actividad chica y concreta que puedas terminar hoy.",
        "Hacé un ejercicio de respiración lenta durante 2-3 minutos.",
    ],
}

# Recomendaciones específicas para duelo/pérdida (distintas de las de
# "Tristeza" en general): en vez de activación conductual estándar,
# apuntan a permitir el proceso de duelo, mantener el vínculo de otra
# forma (memoria) y sostener rutinas básicas, con apoyo social y
# profesional si el dolor se vuelve muy difícil de sobrellevar.
RECOMENDACIONES_DUELO = [
    "Permitite sentir lo que sientas, sin apurarte a \"estar bien\": el duelo no tiene un tiempo correcto ni una forma única de vivirse.",
    "Buscá un momento para recordar a esa persona de una forma que te haga bien: mirar fotos, escuchar algo que le gustaba, escribirle una carta. Seguir sintiéndola cerca, o hablarle, no es quedarse pegado/a — es parte de cómo muchas personas atraviesan el duelo.",
    "Está bien reírte, distraerte o disfrutar de algo aunque estés en duelo: no significa que quieras menos a esa persona ni que la estés dejando atrás.",
    "Apoyate en tu entorno, aunque sea con algo chico: contarle a alguien de confianza cómo te sentís hoy.",
    "Si podés, sostené alguna rutina básica (comer, dormir, algo de movimiento), aunque todo lo demás esté difícil.",
    "Si esto viene pasando hace más de un año y el dolor sigue tan intenso como al principio, o evitás por completo pensar en esto o hablar de eso, buscar acompañamiento profesional en duelo puede ayudar mucho — no hace falta atravesarlo en soledad.",
]

# Recomendaciones para un diagnóstico/noticia de salud ya confirmada:
# apuntan a procesar la noticia, apoyarse en el equipo médico y en el
# entorno, y sostener rutinas, en vez de "activación conductual" genérica.
RECOMENDACIONES_DIAGNOSTICO = [
    "Date tiempo para procesar la noticia: no hace falta tener todo resuelto o entendido de entrada.",
    "Buscar información confiable sobre tu diagnóstico (con tu equipo médico, o fuentes serias) puede bajar la incertidumbre y ayudarte a sentir más manejo de la situación.",
    "Anotá las dudas que te vayan surgiendo para tu próxima consulta médica, así no se te escapan en el momento.",
    "Apoyate en las personas de tu entorno, o en grupos de personas que ya atravesaron algo parecido: suelen aportar algo que nadie más puede darte, la experiencia de haber pasado por esto.",
    "Un ejercicio breve de respiración lenta o de atención al momento presente, unos minutos cuando lo necesites, tiene buen respaldo para bajar la ansiedad que trae un diagnóstico así.",
    "Si podés, sostené alguna rutina básica (comer, dormir, algo de movimiento) mientras te reacomodás a esta noticia.",
    "Si esta noticia se te hace difícil de sobrellevar solo/a, o sentís que te está costando sostener tu día a día desde hace semanas, buscar acompañamiento psicológico específico puede ayudar mucho — no hace falta atravesarlo en soledad.",
]

# Recomendaciones para pensamientos obsesivos / compulsiones (tipo TOC):
# basadas en Exposición con Prevención de Respuesta (ERP), el tratamiento
# de primera línea. Apuntan a tolerar el malestar sin hacer la
# compulsión, no a convencerse de que el pensamiento es falso.
RECOMENDACIONES_OBSESION = [
    "El contenido de estos pensamientos, por más feo, violento o raro que sea, no dice nada de vos ni predice lo que vas a hacer — es parte del patrón, no una señal de alarma sobre tu carácter.",
    "Cada vez que lográs demorar o no hacer la compulsión, aunque sea un poco, le enseñás a tu cabeza que puede tolerar esa incomodidad sin necesitar el ritual.",
    "Si podés, evitá pedirle a alguien que te tranquilice sobre esto (y evitá autoconvencerte buscando \"pruebas\"): calma por un rato, pero suele hacer que el impulso vuelva más fuerte después.",
    "Cuando aparezca el impulso, probá \"surfear la ola\": notá cómo sube, se mantiene un rato y baja solo si no lo alimentás con la acción — aunque ahora cueste creerlo.",
    "Anotá cada vez que lograste resistir la compulsión, por poco que sea — es una victoria real, aunque el pensamiento haya seguido apareciendo.",
    "Si esto pasa seguido y te complica el día a día, un tratamiento específico (Exposición con Prevención de Respuesta, con un profesional especializado en este tipo de pensamientos y compulsiones) funciona mucho mejor que intentar resolverlo en soledad.",
]

# ==========================================================
# --- ÚLTIMO CONSEJO ADAPTADO A SI YA ESTÁ EN TRATAMIENTO ---
# ----------------------------------------------------------
# El último consejo de duelo, diagnóstico y pensamientos repetitivos
# invita a buscar ayuda profesional. Si la persona ya cargó en su
# perfil que está en tratamiento, no tiene sentido sugerirle "buscar"
# algo que ya tiene — tiene más sentido invitarla a llevar esto a su
# psicólogo/a o psiquiatra. Estas listas quedan igual (se siguen
# usando tal cual en la biblioteca de Consejos, que no sabe si hay una
# persona logueada en tratamiento); solo se reemplaza el último ítem al
# armar las recomendaciones de un reporte puntual, en
# mostrar_paso_recomendaciones.
# ==========================================================
FRASE_PROFESIONAL_DUELO_EN_TRATAMIENTO = "Ya que estás en tratamiento, esto puede ser algo importante para llevarle a tu psicólogo/a o psiquiatra — no hace falta atravesarlo en soledad."
FRASE_PROFESIONAL_DIAGNOSTICO_EN_TRATAMIENTO = "Ya que estás en tratamiento, esto también puede ser algo para llevarle a tu psicólogo/a o psiquiatra, además de tu equipo médico — no hace falta atravesarlo en soledad."
FRASE_PROFESIONAL_OBSESION_EN_TRATAMIENTO = "Ya que estás en tratamiento, vale la pena sumar esto a la conversación con tu psicólogo/a o psiquiatra — un tratamiento específico como Exposición con Prevención de Respuesta funciona mucho mejor armado junto a un profesional."


def recomendaciones_con_tratamiento(lista_base, frase_en_tratamiento, en_tratamiento):
    if en_tratamiento == "Sí":
        return lista_base[:-1] + [frase_en_tratamiento]
    return lista_base


def mezclar_recomendaciones(lista, mantener_ultima=False):
    # Sin esto, alguien que retoma el mismo tema varias veces ve siempre
    # las mismas sugerencias en el mismo orden. Mezclar el orden en cada
    # sesión (sin agregar ni sacar contenido) alcanza para que no se
    # sienta repetitivo. En duelo/diagnóstico/TOC la última línea es el
    # cierre hacia ayuda profesional (o su versión adaptada si ya está en
    # tratamiento) y queda mejor siempre al final, no mezclada en el medio.
    if not lista:
        return lista
    if mantener_ultima and len(lista) > 1:
        cuerpo = list(lista[:-1])
        random.shuffle(cuerpo)
        return cuerpo + [lista[-1]]
    resultado = list(lista)
    random.shuffle(resultado)
    return resultado


# ==========================================================
# --- TIPOS DE CONSEJO FINAL: CBT o BUDISTA TIBETANO ---
# ----------------------------------------------------------
# Al final, la persona puede elegir entre un consejo de Terapia Cognitivo
# Conductual (los bancos de arriba) o uno inspirado en la tradición
# budista tibetana. El contenido está basado en prácticas y enseñanzas
# reales de esa tradición, pero el texto que ve la persona NO nombra
# técnicas, autores ni términos en tibetano/sánscrito (la mayoría de la
# gente no los conoce, y usarlos sin explicación no suma nada) — se
# describe directamente la práctica en criollo, de forma pragmática.
# Fuentes de referencia (para mantenimiento futuro, no se muestran en la
# app):
# - Respiración de "dar y recibir" (inhalar el malestar, exhalar alivio):
#   práctica de "tonglen", tradición de entrenamiento mental (lojong)
#   tibetano, popularizada en occidente por Pema Chödrön.
# - Hablarse con calidez ("maitri" / amistad incondicional hacia uno
#   mismo): mismo origen; converge además con la evidencia (no budista)
#   de la autocompasión de Kristin Neff, con ensayos randomizados que
#   muestran menos ansiedad/depresión/estrés tras practicarla.
# - Los estados emocionales cambian con el tiempo (impermanencia):
#   enseñanza central budista, usada acá como reencuadre cognitivo, no
#   como doctrina.
# - Quedarse con la incomodidad en vez de huir de ella / tolerar la
#   inestabilidad: enseñanza de Pema Chödrön (maestra budista tibetana).
# - La paciencia como respuesta al enojo, y notar el costo del enojo
#   antes de actuar: capítulo sobre la paciencia de Shantideva, texto
#   clásico (s. VIII) con enorme influencia en las 4 escuelas del budismo
#   tibetano.
# - Diferenciar el arrepentimiento (reconocer el error y reparar) de la
#   culpa/vergüenza que se vuelve maltrato hacia uno mismo, y los 4 pasos
#   para trabajar un error (reconocer, proponerse no repetirlo, reparar,
#   apoyarse en algo que dé fuerza): los "cuatro poderes" del budismo
#   tibetano para trabajar acciones de las que uno se arrepiente.
# - "Si hay solución no hace falta angustiarse, si no la hay, angustiarse
#   no ayuda": enseñanza clásica citada tanto por Shantideva como por el
#   Dalai Lama sobre cómo relacionarse con una dificultad de salud.
# ==========================================================
TIPO_RECOMENDACION_CBT = "cbt"
TIPO_RECOMENDACION_BUDISTA = "budista"

RECOMENDACIONES_BUDISTA_POR_EMOCION = {
    "Tristeza": [
        "Probá esto: al inhalar, aceptá esta tristeza tal como es, sin empujarla lejos; al exhalar, date a vos mismo/a un poco de alivio y calma.",
        "Hablate con la misma calidez con la que le hablarías a alguien que querés mucho, en vez de exigirte o retarte.",
        "Los estados de ánimo cambian con el tiempo, como el clima: este tampoco se va a quedar igual para siempre.",
        "En vez de pelear contra la tristeza o distraerte todo el tiempo de ella, probá quedarte un momento con lo que sentís, sin juzgarlo.",
        "Dedicá unos minutos a sentarte en silencio y seguir tu respiración, dejando que la tristeza esté ahí sin tener que resolverla ya mismo.",
    ],
    "Ansiedad": [
        "La ansiedad muchas veces es la sensación de no tener nada firme bajo los pies. En vez de buscar certezas que no existen, a veces ayuda más quedarte un momento con esa inestabilidad, sin pelear contra ella.",
        "Probá esto: al inhalar, aceptá el miedo tal como es; al exhalar, date a vos mismo/a un poco de espacio y calma.",
        "El miedo suele aparecer cuando algo nos importa de verdad — no siempre es señal de que algo esté mal.",
        "Volvé la atención a tu respiración: contá 4 al inhalar y 6 al exhalar, dejando que la mente se aquiete de a poco.",
        "Es normal que la mente salte de un pensamiento a otro sin parar — no hace falta que se quede del todo quieta para que estés bien.",
    ],
    "Enojo": [
        "Un solo momento de enojo puede opacar mucho de lo bueno que veníamos construyendo — no se trata de reprimirlo, sino de no dejar que decida por vos.",
        "Ser paciente no es lo mismo que no hacer nada: si hay algo para resolver, podés hacerlo, pero desde la calma en vez de la reactividad.",
        "Antes de actuar, notá qué se siente en el cuerpo cuando aparece el enojo — esa pausa de un instante ya ayuda a no reaccionar de manera impulsiva.",
        "Probá esto: al inhalar, aceptá ese calor tal como es; al exhalar, soltá un poco esa tensión.",
        "Preguntate qué límite o qué valor tuyo te está señalando este enojo, más allá de la reacción del momento.",
    ],
    "Culpa": [
        "Hay una diferencia entre el arrepentimiento (que reconoce el error y motiva a reparar) y la culpa que se convierte en maltrato hacia uno mismo: lo primero ayuda, lo segundo no.",
        "Cuatro pasos que pueden ayudar con un error: reconocé lo que pasó, proponete no repetirlo, hacé algo concreto para reparar si podés, y apoyate en algo que te dé fuerza para seguir adelante.",
        "Hablate con la misma calidez con la que tratarías a alguien que querés y que cometió el mismo error.",
        "Probá esto: al inhalar, aceptá ese peso tal como es; al exhalar, ofrecete a vos mismo/a un poco de perdón.",
    ],
    "Vergüenza": [
        "Un error no te convierte en una persona mala o indigna — lo que hiciste no es lo que sos.",
        "Practicá tratarte con la misma amistad incondicional que le tendrías a otra persona en tu misma situación.",
        "Compartir lo que te pasa con alguien de confianza también es un acto de compasión hacia vos mismo/a, no una debilidad.",
        "Probá esto: al inhalar, aceptá esa sensación tal como es; al exhalar, date a vos mismo/a un poco de aceptación.",
    ],
    "General": [
        "Probá esto: al inhalar, aceptá este malestar tal como es, sin empujarlo lejos; al exhalar, date a vos mismo/a un poco de alivio y calma.",
        "Hablate con la misma calidez con la que le hablarías a alguien que querés mucho, en vez de exigirte o retarte.",
        "Este estado también es pasajero: no se va a quedar exactamente así para siempre.",
        "En vez de pelear contra lo que sentís o distraerte todo el tiempo de eso, probá quedarte un momento con la sensación tal cual es, sin juzgarla.",
        "Dedicá unos minutos a sentarte en silencio y seguir tu respiración; cuando la mente se te vaya, notalo con suavidad y volvé a traerla, sin exigirte que se quede quieta.",
    ],
}

RECOMENDACIONES_BUDISTA_DUELO = [
    "Probá esto: al inhalar, aceptá este dolor tal como es; al exhalar, date a vos mismo/a un poco de alivio.",
    "Tratate con la misma ternura que le darías a un amigo que está atravesando una pérdida.",
    "Nada permanece igual para siempre, ni siquiera el dolor de este momento, aunque ahora se sienta así.",
    "En vez de huir del dolor o distraerte todo el tiempo, permitite quedarte un momento con lo que sentís, sin la urgencia de que se resuelva ya.",
    "Si sentís culpa o \"debería haber hecho algo distinto\", tratá de diferenciar el arrepentimiento (que reconoce lo que pasó y ayuda a seguir adelante) de la culpa que se convierte en maltrato hacia uno mismo.",
    "Permitirte un momento de alivio, risa o disfrute en medio del duelo no traiciona a quien perdiste — el corazón puede sostener el dolor y la alegría a la vez, no son opuestos.",
]

RECOMENDACIONES_BUDISTA_DIAGNOSTICO = [
    "Frente a una dificultad de salud: si hay un tratamiento posible, lo mejor es aplicarlo con la mayor calma posible; si no lo hay, angustiarse no cambia el resultado y sí te quita paz mientras tanto.",
    "Aceptar esta dificultad como parte de lo que te toca atravesar ahora, en vez de pelear contra la realidad de lo que está pasando, puede aliviar bastante la carga.",
    "Probá esto: al inhalar, aceptá este malestar tal como es; al exhalar, date a vos mismo/a un poco de alivio y fuerza.",
    "Tratá a tu cuerpo y a vos mismo/a con paciencia en este momento, en vez de exigirte que ya tengas todo resuelto.",
    "Apoyarte en otras personas también es parte del camino — no hace falta atravesarlo en soledad.",
]

# La idea de "no alimentar" un impulso y dejar que pase solo, y la de que
# necesitar certeza total es en sí mismo un apego, coinciden bastante
# entre esta tradición y lo que busca el tratamiento de primera línea
# para el TOC (no pelear con el pensamiento, tolerar no saber).
RECOMENDACIONES_BUDISTA_OBSESION = [
    "Notá el impulso como una ola: sube, se queda un rato y baja sola si no la alimentás con la acción — no hace falta empujarla ni seguirla.",
    "Necesitar estar 100% seguro/a de algo es, en el fondo, una forma de apego. Probá notar esa necesidad sin intentar satisfacerla esta vez.",
    "Cuando el pensamiento vuelva, probá simplemente notarlo y dejarlo pasar, en vez de discutir con él o intentar resolverlo del todo.",
    "Tratate con paciencia: no hacer la compulsión es incómodo a propósito, no es una señal de que algo esté saliendo mal.",
    "Volvé a tu respiración cada vez que el impulso te empuje a actuar — no para escapar del malestar, sino para acompañarte mientras pasa.",
]


def recomendaciones_budistas_para(emocion):
    return RECOMENDACIONES_BUDISTA_POR_EMOCION.get(emocion, RECOMENDACIONES_BUDISTA_POR_EMOCION["General"])


EMOCIONES = ["Tristeza", "Ansiedad", "Enojo", "Culpa", "Vergüenza", "Otra"]

# ==========================================================
# --- TIPO DE SITUACIÓN ---
# ----------------------------------------------------------
# Las preguntas de "evidencia a favor / en contra" (reestructuración
# cognitiva clásica) solo tienen sentido cuando el pensamiento es una
# interpretación que puede ser más o menos exacta (ej: "no le caigo bien
# a nadie", "voy a rendir mal"). No tienen sentido, y pueden resultar
# invalidantes, cuando el pensamiento parte de un HECHO consumado, no de
# una distorsión: un duelo/pérdida, o un diagnóstico de salud ya
# confirmado. La literatura de CBT para duelo complicado apunta la
# reestructuración solo a pensamientos secundarios como la culpa o el
# autorreproche, no al hecho en sí — y lo mismo aplica a una noticia de
# salud ya confirmada (distinto de un miedo o sospecha todavía incierta,
# donde sí tiene sentido desafiar el pensamiento). Por eso se separan en
# dos categorías distintas, en vez de una sola "problema de salud", y se
# pregunta primero qué tipo de situación es para cambiar las preguntas
# siguientes.
# ==========================================================
TIPO_DUELO = "Perdí a alguien o algo importante (duelo)"
TIPO_DIAGNOSTICO = "Recibí un diagnóstico o una noticia de salud difícil"
TIPO_OBSESION = "Tengo un pensamiento que se repite y una necesidad de hacer algo al respecto"
TIPOS_SITUACION = [
    TIPO_DUELO,
    "Tuve un conflicto con alguien",
    "Me preocupa algo que puede pasar",
    "Sentí que fallé o no estuve a la altura",
    "Me preocupa un posible problema de salud (todavía no lo sé con certeza)",
    TIPO_DIAGNOSTICO,
    TIPO_OBSESION,
    "Otra situación",
]
# Situaciones donde el pensamiento parte de un hecho, no de una posible
# distorsión: no pasan por "evidencia a favor/en contra" ni se fuerza una
# creencia final más baja.
TIPOS_HECHO_CONSUMADO = {TIPO_DUELO, TIPO_DIAGNOSTICO}

# ==========================================================
# --- PENSAMIENTOS OBSESIVOS / COMPULSIONES (tipo TOC) ---
# ----------------------------------------------------------
# Acá el enfoque clásico de "evidencia a favor/en contra" no solo no
# ayuda: puede empeorar las cosas. La literatura sobre TOC muestra que
# buscar tranquilidad o "pruebas" (reassurance-seeking) alivia un
# momento, pero refuerza el círculo — el cerebro aprende que hacía falta
# esa tranquilidad, y la próxima vez el impulso vuelve más fuerte y pide
# más. El tratamiento de primera línea, Exposición con Prevención de
# Respuesta (ERP), no busca resolver ni desmentir el pensamiento: busca
# aumentar la tolerancia a la incertidumbre mientras se resiste la
# compulsión (el ritual, físico o mental, incluido pedir que lo/la
# tranquilicen). Por eso esta rama:
# - NO pregunta evidencia a favor/en contra ni pasa por el checklist de
#   distorsiones (analizar de más el contenido del pensamiento es, en sí
#   mismo, parte de la compulsión).
# - Identifica la compulsión/impulso en vez de debatir el pensamiento.
# - Suma una pregunta breve de "confusión inferencial" (I-CBT): notar si
#   esto es algo que está pasando de verdad ahora o una posibilidad que
#   la mente imaginó, sin intentar resolver cuál de las dos es.
# - En vez de "creencia en el pensamiento", mide la intensidad del
#   impulso/malestar (estilo SUDS, la escala 0-100 que se usa en ERP).
# - Pide un compromiso concreto de "no hacer la compulsión" por un rato,
#   en vez de buscar cambiar el pensamiento.
# - No entra al loop de reflexión (esas técnicas tampoco corresponden
#   acá): la meta no es bajar la creencia, es tolerar el malestar.
# ==========================================================

# ==========================================================
# --- SUGERIR UN TIPO MÁS ESPECÍFICO CUANDO ELIGE "OTRA SITUACIÓN" ---
# ----------------------------------------------------------
# Algunas personas no van a reconocerse en las opciones específicas (por
# ejemplo, alguien con pensamientos repetitivos/compulsiones puede no
# saber que eso tiene un nombre, y por eso el dropdown ya no lo nombra).
# Para no perder esos casos, cuando elige "Otra situación" se revisa el
# texto libre que escribió por si describe, en sus propias palabras, un
# duelo, un diagnóstico ya confirmado, o un pensamiento repetitivo con
# necesidad de hacer algo al respecto — y si hay coincidencia, se la
# REDIRIGE directo a esas preguntas específicas (con un aviso breve, sin
# ofrecer la alternativa de seguir con las genéricas). Las preguntas
# genéricas quedan solo para cuando no se pudo categorizar la situación.
# Se describe el patrón en criollo, nunca con el nombre clínico.
# ==========================================================
FRASES_DUELO = [
    "se murio", "murio mi", "murio un", "murio una", "fallecio", "perdi a mi",
    "la muerte de", "su muerte", "lo perdi", "la perdi", "ya no esta conmigo",
    "se nos fue", "el velorio", "el funeral", "la despedida de",
]
FRASES_DIAGNOSTICO = [
    "me diagnosticaron", "me detectaron", "el medico me dijo que tengo",
    "me dieron el diagnostico", "me confirmaron que tengo", "resultado positivo",
    "tengo cancer", "tengo diabetes", "padezco de", "me acaban de diagnosticar",
]
FRASES_OBSESION = [
    "no puedo dejar de revisar", "reviso una y otra vez", "necesito revisar varias veces",
    "tengo que revisar", "me tengo que lavar las manos", "lavarme las manos muchas veces",
    "lavo las manos varias veces", "me lavo las manos varias veces",
    "tengo que repetir", "tengo que hacerlo varias veces hasta que se sienta bien",
    "si no lo hago va a pasar algo malo", "va a pasar algo malo",
    "no me puedo sacar ese pensamiento de la cabeza",
    "pensamiento que no se va", "necesito que quede perfecto", "necesito simetria",
    "compulsion", "obsesivo", "obsesiva", "obsesionado", "obsesionada",
]


def _detectar_frase(texto, lista_frases):
    t = _normalizar_riesgo(texto)
    return any(frase in t for frase in lista_frases)


def detectar_tipo_sugerido(texto):
    if _detectar_frase(texto, FRASES_DUELO):
        return TIPO_DUELO
    if _detectar_frase(texto, FRASES_DIAGNOSTICO):
        return TIPO_DIAGNOSTICO
    if _detectar_frase(texto, FRASES_OBSESION):
        return TIPO_OBSESION
    return None


# Descripción en criollo de cada tipo sugerido, sin nombre clínico, para
# mostrar en el aviso de que las preguntas van a cambiar (mostrar_paso_sugerencia_tipo).
DESCRIPCION_TIPO_SUGERIDO = {
    TIPO_DUELO: "esto suena a que perdiste a alguien o algo importante para vos",
    TIPO_DIAGNOSTICO: "esto suena a que recibiste una noticia de salud ya confirmada",
    TIPO_OBSESION: "esto suena a un pensamiento que se te repite mucho y te genera la necesidad de hacer algo al respecto (revisar, repetir, pedir que te tranquilicen, etc.)",
}

# ==========================================================
# --- PENSAMIENTOS A SEGUIR TRABAJANDO ("temas") ---
# ----------------------------------------------------------
# Un pensamiento automático que vuelve a aparecer en distintas situaciones
# suele señalar una creencia de fondo (registros de pensamiento repetidos
# a lo largo del tiempo son justamente cómo se detectan esos patrones en
# CBT). Acá se guarda como un "tema": la persona le pone un nombre y un
# color, y cada vez que lo retoma queda un reporte más vinculado a ese
# mismo tema, para poder ver cómo fue cambiando la creencia en él.
# El color siempre lo calcula la app sola según el avance
# (creencia_final_pct del último reporte vinculado): verde/celeste para
# valencias más positivas (la creencia en el pensamiento negativo bajó),
# rojo/naranja para valencias todavía negativas, más intenso cuanto más
# alta siga esa creencia.
# ==========================================================
COLORES_TEMA = [
    ("Rojo", "#EF5350"),
    ("Naranja", "#FFA726"),
    ("Amarillo", "#FDD835"),
    ("Verde", "#66BB6A"),
    ("Celeste", "#42A5F5"),
    ("Violeta", "#AB47BC"),
    ("Gris", "#BDBDBD"),
]


def color_hex(nombre_color):
    for nombre, hexcode in COLORES_TEMA:
        if nombre == nombre_color:
            return hexcode
    return "#BDBDBD"


def color_por_avance(creencia_final_pct):
    # Escala roja→naranja→amarilla→verde→celeste a medida que baja la
    # creencia en el pensamiento negativo (0% = totalmente superado).
    if creencia_final_pct is None:
        return "Gris"
    if creencia_final_pct >= 70:
        return "Rojo"
    if creencia_final_pct >= 50:
        return "Naranja"
    if creencia_final_pct >= 30:
        return "Amarillo"
    if creencia_final_pct >= 15:
        return "Verde"
    return "Celeste"


# ==========================================================
# --- CHEQUEO PERIÓDICO DE BIENESTAR (WHO-5) ---
# ----------------------------------------------------------
# Índice de Bienestar de la OMS (WHO-5): 5 preguntas sobre las últimas 2
# semanas, pensado específicamente para uso repetido (semanal/mensual) y
# seguimiento de la propia evolución en el tiempo — a diferencia de un
# cuestionario de screening clínico (PHQ-9/GAD-7), no da una "categoría
# diagnóstica", por eso encaja mejor con la idea de "llevar un registro
# de cómo vengo estando" que pidió Gabriel. Versión en español validada
# (ver https://www.psykiatri-regionh.dk, sitio oficial del WHO-5).
# Puntaje: se suman las 5 respuestas (0 a 5 cada una, total 0-25) y se
# multiplica por 4 para obtener un % de 0 a 100 (a mayor %, mejor
# bienestar). El color reusa la misma escala que ya usa la app para los
# "temas" (color_por_avance), invertido: acá 100% de bienestar = mejor
# estado = Celeste, no Rojo.
# ==========================================================
PREGUNTAS_BIENESTAR = [
    "Me he sentido alegre y de buen humor",
    "Me he sentido tranquilo/a y relajado/a",
    "Me he sentido activo/a y con energía",
    "Me desperté sintiéndome fresco/a y descansado/a",
    "Mi vida diaria ha estado llena de cosas que me interesan",
]

OPCIONES_BIENESTAR = [
    ("En ningún momento", 0),
    ("Alguna vez", 1),
    ("Menos de la mitad del tiempo", 2),
    ("Más de la mitad del tiempo", 3),
    ("La mayor parte del tiempo", 4),
    ("Todo el tiempo", 5),
]

# Descripción cortita para el historial (pensado para verse "de un
# vistazo", igual criterio que el punto de color): usa el mismo nombre de
# color que ya calcula color_por_avance, para que texto y color nunca
# queden desalineados entre sí.
DESCRIPCION_BIENESTAR_POR_COLOR = {
    # Regla (Gabriel, 2026-07-14): las etiquetas de los resultados más
    # bajos nunca califican a la persona ("Flojo", "Bajo") — describen la
    # semana con calidez y dejan una nota de aliento.
    "Rojo": "Semana difícil — un paso a la vez",
    "Naranja": "Remontando, de a poco",
    "Amarillo": "A mitad de camino",
    "Verde": "Bien",
    "Celeste": "Muy bien",
    "Gris": "Sin datos",
}

# Consejos concretos de activación conductual, uno por cada pregunta del
# WHO-5 (mismo índice que PREGUNTAS_BIENESTAR) — se muestran en el
# resultado del chequeo eligiendo la(s) pregunta(s) donde salió más bajo,
# para que el consejo apunte a lo que realmente le está costando a la
# persona en vez de ser un mensaje genérico igual para todos.
RECOMENDACIONES_BIENESTAR_POR_PREGUNTA = [
    [  # 0: "Me he sentido alegre y de buen humor"
        "Elegí una actividad chica que antes disfrutabas y hacela hoy, aunque no tengas muchas ganas.",
        "Exponete un rato a la luz del sol o abrí las cortinas/ventanas de tu casa.",
        "Contactá a una persona con la que tengas buena relación, aunque sea un mensaje corto.",
    ],
    [  # 1: "Me he sentido tranquilo/a y relajado/a"
        "Hacé un ejercicio de respiración lenta: inhalar 4 segundos, sostener 4, exhalar 6, repetir 5 veces.",
        "Postergá las preocupaciones a un horario fijo del día (20 minutos), en vez de darles vueltas todo el día.",
        "Hacé algo con las manos que requiera atención (cocinar, ordenar, dibujar) para bajar un rato la cabeza.",
    ],
    [  # 2: "Me he sentido activo/a y con energía"
        "Salí a caminar 15-20 minutos al aire libre, aunque sea a paso lento.",
        "Empezá con algo físico bien chico (subir una escalera, estirar 5 minutos) en vez de plantearte \"hacer ejercicio\" entero.",
        "Fijate si estás pasando muchas horas seguidas sentado/a, y probá cortar con una pausa cada tanto.",
    ],
    [  # 3: "Me desperté sintiéndome fresco/a y descansado/a"
        "Probá mantener un horario fijo para acostarte y levantarte, incluso los fines de semana.",
        "Evitá pantallas (celular, tele) la última media hora antes de dormir.",
        "Si tomás café o mate por la tarde/noche, probá cortarlo antes y ver si duerme distinto.",
    ],
    [  # 4: "Mi vida diaria ha estado llena de cosas que me interesan"
        "Anotá una tarea chica y concreta que puedas terminar hoy, para tener una sensación de logro.",
        "Retomá aunque sea 15 minutos algo que solías disfrutar y dejaste de lado.",
        "Pensá en algo que te gustaría aprender o probar, y dale el primer paso más chico posible hoy.",
    ],
]


# ==========================================================
# --- COLECCIÓN DE ENSEÑANZAS (gamificación, opción B) ---
# ----------------------------------------------------------
# Cada "trabajo real" completado (un registro de Trabajo emocional, un
# ejercicio de Otra perspectiva o un chequeo de bienestar) desbloquea la
# siguiente enseñanza de esta lista, en orden. No hay puntos ni castigos:
# la recompensa ES contenido con sentido (ver BIBLIOGRAFIA.md sección 9 —
# las recompensas tangibles socavan la motivación intrínseca, el
# reconocimiento con contenido la fortalece). El desbloqueo se calcula
# contando los trabajos ya guardados (sin tabla nueva en Supabase).
# Mismo criterio que el resto de la app: sin jerga clínica ni nombres de
# autores/términos en tibetano en el texto que ve la persona.
PERLAS_SABIDURIA = [
    ("Un pensamiento no es un hecho", "Que algo se te cruce por la cabeza no lo vuelve cierto. Cuando un pensamiento te pegue fuerte, probá decirte: \"estoy teniendo el pensamiento de que...\" — nombrarlo así ya le baja el peso."),
    ("Las emociones pasan solas", "Ninguna emoción dura para siempre, ni siquiera las más intensas: suben, llegan a un pico y bajan. Si lográs esperar unos minutos sin actuar en caliente, baja sola."),
    ("Hablate como a alguien que querés", "Solemos decirnos cosas que jamás le diríamos a un amigo en la misma situación. La próxima vez que te escuches tratándote duro, preguntate: ¿qué le diría a alguien que quiero si le pasara esto mismo?"),
    ("La acción viene antes que las ganas", "Cuando el ánimo está bajo, esperar a tener ganas suele ser esperar para siempre. Funciona al revés: primero se arranca con algo chico, y las ganas aparecen después."),
    ("Nada difícil se queda igual", "Lo que hoy se siente insoportable no se va a sentir igual dentro de un tiempo: las situaciones cambian, y vos también. Vale recordarlo antes de tomar decisiones definitivas en un mal momento."),
    ("La mente exagera para protegerte", "El cerebro está hecho para detectar peligros, no para ser justo: por eso te muestra el peor escenario como si fuera el más probable. Cuando aparezca, preguntate: ¿qué es lo más probable, no lo peor posible?"),
    ("Este momento difícil no te define", "Una mala semana no es una mala vida. Estás atravesando algo difícil; no sos algo difícil — y esa diferencia cambia cómo se sigue."),
    ("Contarlo alivia", "La vergüenza y la preocupación crecen en el silencio. Contarle a una persona de confianza lo que te pasa suele aliviar más que semanas de darle vueltas a solas."),
    ("El cuerpo también escucha", "Cuando exhalás más lento de lo que inhalás, el cuerpo entiende que el peligro pasó y se afloja. Probá: inhalar contando 4, exhalar contando 6, unas cinco veces."),
    ("Dar vueltas no es resolver", "Darle vueltas a un problema parece \"estar trabajándolo\", pero muchas veces es un círculo. Un buen filtro: ¿esto que estoy pensando termina en algo concreto que puedo hacer? Si no, mejor cortar y volver más tarde."),
    ("Mirate desde afuera", "Cuando estés muy metido/a en un problema, probá describirlo como si le pasara a otra persona. Desde afuera casi siempre se ven salidas que desde adentro no aparecen."),
    ("¿Cuánto va a pesar esto en un año?", "Muchas cosas que hoy ocupan toda tu atención, dentro de un año van a ser una anécdota. Preguntarte \"¿cuánto me va a importar esto en un año?\" no resuelve el problema, pero lo pone en su tamaño real."),
    ("Ojo con los \"debería\"", "Buena parte del malestar no viene de lo que pasó, sino del \"esto no debería ser así\". Probá cambiar \"debería\" por \"me gustaría\": la situación es la misma, pero el nudo afloja."),
    ("Compararse es una trampa", "Cuando te comparás con otros, comparás lo que vos vivís por dentro con lo que ellos muestran por fuera. Nadie anda mostrando sus peores días — vos tampoco."),
    ("Sos más que tu peor error", "Un error es algo que hiciste, no algo que sos. Decir \"me equivoqué en esto\" en vez de \"soy un desastre\" deja lugar para arreglarlo y seguir."),
    ("Lo que sentís, lo sienten muchos", "Sea lo que sea que te esté pasando, le está pasando también a muchísima gente en este mismo momento. Eso no achica tu problema, pero sí tu soledad."),
    ("Descansar también es avanzar", "El descanso no es tiempo perdido: es lo que hace posible todo lo demás. Exigirse sin pausa rinde menos que trabajar con recreos."),
    ("Elegí una cosa, no todas", "Cuando todo parece urgente, lo que mejor funciona es elegir UNA sola cosa chica y terminarla. Un logro real, por chico que sea, empuja más que diez planes perfectos."),
    ("Esperar antes de reaccionar es fuerza", "Aguantarse el impulso de contestar en caliente no es debilidad: es la habilidad que más problemas evita. Diez minutos de espera suelen ganarle a semanas de arrepentimiento."),
    ("Mirá lo conocido con ojos nuevos", "Cuando una situación se repite hace tiempo, la costumbre tapa las salidas. Preguntate: si esto me pasara hoy por primera vez, ¿qué haría? A veces la respuesta sorprende."),
    ("La alegría ajena también suma", "Alegrarte de verdad por algo bueno que le pasó a otro no te quita nada: es una fuente más de momentos buenos en tu día. Y como casi todo, se entrena."),
    ("Agradecer una sola cosa concreta", "No hace falta estar bien para encontrar UNA cosa que hoy salió bien, aunque sea mínima. Nombrarla no niega lo difícil: le hace contrapeso."),
    ("Lo que evitás se agranda", "Evitar algo que da miedo alivia hoy, pero agranda el miedo para mañana. Acercarse de a poco, en dosis chicas y manejables, es la forma más comprobada de achicarlo."),
    ("Ya atravesaste cosas difíciles antes", "Pensá en algo que hace unos años te parecía imposible de superar y hoy casi ni recordás. Esa es la prueba más concreta de que también vas a poder con esto."),
]


# ==========================================================
# --- CATÁLOGO DE COSMÉTICOS (gamificación, "pase" del bloque 3) ---
# ----------------------------------------------------------
# Estilo pase de recompensas: cada ejercicio de "Otra perspectiva"
# completado suma 1 nivel, y cada nivel va desbloqueando flores/plantas
# nuevas para personalizar (a) la flor con la que florecen tus
# pensamientos trabajados y (b) las florcitas decorativas del menú
# principal. Son emojis a propósito: mismo lenguaje visual que las
# plantas del jardín, cero problemas de copyright y cero peso extra.
# La elección se guarda en el perfil (cosmetico_planta/cosmetico_fondo
# en usuarios_regulacion).
FLOR_POR_DEFECTO = "🌸"
FONDO_POR_DEFECTO = "🌼"

CATALOGO_COSMETICOS = [
    {"emoji": "🌸", "nombre": "Flor de cerezo", "nivel": 0},
    {"emoji": "🌼", "nombre": "Margarita", "nivel": 0},
    {"emoji": "🌷", "nombre": "Tulipán", "nivel": 2},
    {"emoji": "🌻", "nombre": "Girasol", "nivel": 4},
    {"emoji": "🌺", "nombre": "Hibisco", "nivel": 6},
    {"emoji": "🌹", "nombre": "Rosa", "nivel": 9},
    {"emoji": "🪷", "nombre": "Flor de loto", "nivel": 12},
    {"emoji": "💐", "nombre": "Ramo de flores", "nivel": 16},
    {"emoji": "🍀", "nombre": "Trébol de la suerte", "nivel": 20},
    {"emoji": "🌵", "nombre": "Cactus florecido", "nivel": 25},
    {"emoji": "🌾", "nombre": "Espigas doradas", "nivel": 30},
    {"emoji": "🎋", "nombre": "Bambú de los deseos", "nivel": 40},
]

# Colores de fondo desbloqueables (misma lógica de niveles). Todos en la
# misma familia del crema original: pasteles suaves, cálidos y de
# luminosidad parecida, para que la tarjeta y los textos se lean igual
# de bien sobre cualquiera.
CATALOGO_COLORES_FONDO = [
    {"hex": "#E8DBC0", "nombre": "Crema clásico", "nivel": 0},
    {"hex": "#EFD9D3", "nombre": "Rosa suave", "nivel": 3},
    {"hex": "#DCE5D3", "nombre": "Verde menta", "nivel": 5},
    {"hex": "#D7E2E8", "nombre": "Celeste bruma", "nivel": 8},
    {"hex": "#E3DAE9", "nombre": "Lavanda", "nivel": 11},
    {"hex": "#F0DCC6", "nombre": "Durazno", "nivel": 14},
    {"hex": "#E0E0D6", "nombre": "Salvia", "nivel": 18},
]


def recomendaciones_para(emocion):
    return RECOMENDACIONES_POR_EMOCION.get(emocion, RECOMENDACIONES_POR_EMOCION["General"])


# ==========================================================
# --- CUANDO EL PENSAMIENTO NO AFLOJA ---
# ----------------------------------------------------------
# Si la persona todavía cree con fuerza el pensamiento automático (o no se
# le ocurre nada para desafiarlo), no tiene sentido pasar a las
# recomendaciones como si ya estuviera "resuelto". En vez de eso, se la
# guía por 1 a 3 técnicas adicionales (distintas entre sí, no más
# preguntas de evidencia) antes de volver a preguntar cuánto lo cree.
# Basado en evidencia de:
# - Autodistanciamiento / habla en tercera persona (Kross & Ayduk): tomar
#   distancia de la propia experiencia reduce malestar y reactividad.
# - Distanciamiento temporal: proyectar la situación a futuro (ej. "en un
#   año") reduce la intensidad emocional actual.
# - Defusión cognitiva (ACT): notar "estoy teniendo el pensamiento de
#   que..." reduce cuánto se cree y cuánto pesa un pensamiento, sin
#   necesitar cambiar su contenido.
# ==========================================================
UMBRAL_CREENCIA_ALTA = 60   # % a partir del cual seguimos insistiendo
# Tope de vueltas extra antes de seguir igual. Era 3, pero cansaba: una
# sola vuelta extra alcanza para ofrecer otra mirada sin insistir — y
# siempre está el botón "Prefiero terminar por ahora" como salida.
MAX_RONDAS_REFLEXION = 1
# Si la persona reportó una intensidad emocional baja (Paso 1), no tiene
# sentido insistir con más rondas de reflexión solo porque un porcentaje
# quedó en el medio: sería ineficiente e invalidaría su propio reporte de
# "esto no me afecta tanto". La intensidad que la persona reportó pesa
# más que el número de creencia derivado.
UMBRAL_INTENSIDAD_PARA_INSISTIR = 5   # sobre 10

_FRASES_NO_SABE = [
    "no se", "no sé", "nose", "ns", "no lo se", "no lo sé",
    "no tengo idea", "ni idea", "no sabria decir", "no sabría decir",
]


def contiene_no_sabe(texto):
    t = (texto or "").strip().lower()
    if not t:
        return False
    # Antes bastaba con que "no se" apareciera en cualquier parte del
    # texto, lo que daba falsos positivos en respuestas largas que
    # solo de casualidad contienen esas dos palabras (ej. "el tren no
    # se detuvo", "no se lavó bien la ropa", "todavía no se sabe qué
    # pasó") — encontrado con fuzzing (5/5 casos de este tipo probados
    # daban falso positivo). Una respuesta de "no sé" genuina es
    # corta, no una oración larga que la menciona de paso.
    if len(t) > 25:
        return False
    return any(t == frase or frase in t for frase in _FRASES_NO_SABE)


def necesita_reflexion_extra(r):
    if r.get("intensidad_inicial", 0) < UMBRAL_INTENSIDAD_PARA_INSISTIR:
        return False
    no_sabe = contiene_no_sabe(r.get("evidencia_en_contra")) or contiene_no_sabe(r.get("pensamiento_alternativo"))
    creencia_alta = r.get("creencia_final_pct", 0) >= UMBRAL_CREENCIA_ALTA
    return no_sabe or creencia_alta


TECNICAS_REFLEXION = [
    {
        "titulo": "Mirémoslo desde afuera",
        "intro": "Tomar distancia de un pensamiento, hablándonos como si fuéramos otra persona, suele bajarle intensidad.",
        "consigna": lambda r: "Contate lo que te pasó en tercera persona, usando tu nombre en vez de \"yo\" (ej: \"[Tu nombre] siente que...\"). ¿Qué le dirías a esa persona?",
        "hint": "Ej: \"Ale siente que todo va a salir mal, pero otras veces logró salir adelante...\"",
    },
    {
        "titulo": "Pensemos en el tiempo",
        "intro": "Imaginar cómo vas a ver esto más adelante ayuda a ganar perspectiva sobre lo que sentís ahora.",
        "consigna": lambda r: "Imaginate mirando esta misma situación dentro de 1 año. ¿Qué importancia te parece que va a tener entonces?",
        "hint": "Escribí lo que se te ocurra, no hay una respuesta correcta.",
    },
    {
        "titulo": "Es un pensamiento, no un hecho",
        "intro": "Notar que un pensamiento es solo un pensamiento (y no necesariamente la realidad) puede aflojar su peso.",
        "consigna": lambda r: f"Repetite (o escribilo): \"Estoy teniendo el pensamiento de que {r.get('pensamiento_automatico', '')}\". Después de notarlo así, ¿qué te parece?",
        "hint": "No hace falta estar de acuerdo ni en desacuerdo, solo notarlo.",
    },
    {
        "titulo": "Un momento de compasión con vos mismo/a",
        "intro": "Tratarte con la misma calidez que le darías a alguien que querés, en un momento difícil, también ayuda a bajarle intensidad al pensamiento.",
        "consigna": lambda r: "Si querés, poné una mano en el pecho y decite: \"esto es un momento difícil\", \"no soy el único/a al que le pasa esto\", \"¿puedo tratarme con la misma amabilidad que le daría a alguien que quiero?\". ¿Qué te pasa al hacerlo?",
        "hint": "No hace falta que te salga natural la primera vez, alcanza con probarlo.",
    },
]


# PBKDF2-HMAC-SHA256 con sal aleatoria por usuario y 600.000 iteraciones:
# recomendación vigente de OWASP (Password Storage Cheat Sheet) para que
# probar contraseñas por fuerza bruta sea lento incluso si la base de
# datos se filtrara. Un hash simple (ej. SHA256 solo) se prueba a
# millones por segundo en hardware moderno, así que no alcanza para
# datos sensibles como los de esta app.
PBKDF2_ITERACIONES = 600_000


def generar_salt():
    return os.urandom(16).hex()


def hash_contrasena(contrasena, salt_hex):
    salt = bytes.fromhex(salt_hex)
    derivado = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), salt, PBKDF2_ITERACIONES)
    return derivado.hex()


def main(page: ft.Page):
    page.title = "DRE"
    if page.platform in (ft.PagePlatform.WINDOWS, ft.PagePlatform.MACOS, ft.PagePlatform.LINUX):
        page.window.width = 420
        page.window.height = 800
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    # Semilla de color única: Flet deriva de acá los tonos de botones,
    # sliders, checkboxes y radios en toda la app, así queda coherente
    # sin tener que restylear control por control.
    page.theme = ft.Theme(color_scheme_seed=COLOR_PRIMARIO)
    page.bgcolor = COLOR_FONDO
    page.padding = 0
    # Tipografía Poppins: solo la usan las pantallas de "Practicá con
    # escenarios" (integración MENTO), como identidad propia de ese modo.
    page.fonts = {MENTO_FUENTE: "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;900&display=swap"}

    def ancho_campo(base=320):
        disponible = (page.width or (base + 70)) - 70
        return max(220, min(base, disponible))

    # --- ESTADO DE LA APLICACIÓN ---
    estado = {
        "email": "",
        "usuario_id": None,
        "nombre": "",
        "edad": None,
        "genero": "",
        "en_tratamiento": "",      # "Sí" / "No" / "Prefiero no decir", modula algunos consejos finales
        "tiene_password": True,    # False si entró solo con Google (no tiene contraseña propia)
        "pregunta_seguridad": "",  # solo el texto de la pregunta (no la respuesta), para mostrarla precargada en "Mi perfil"
        "vio_instrucciones": False,  # si ya vio la pantalla de instrucciones alguna vez (no se muestra sola de nuevo)
        "vio_instrucciones_temas": False,  # ídem, para las instrucciones de "Pensamientos que estoy trabajando"
        "vio_instrucciones_bienestar": False,  # ídem, para las instrucciones del chequeo de bienestar
        "vio_instrucciones_trabajo_emocional": False,  # ídem, para el submenú "Trabajo emocional"
        "vio_instrucciones_reappraisal": False,  # ídem, para el submenú "Reappraisal"
        "cosmetico_planta": "",    # flor elegida para las plantas en flor ("" = la de defecto)
        "cosmetico_fondo": "",     # florcita elegida para la decoración del menú ("" = la de defecto)
        "color_fondo": "",         # color de fondo de pantalla elegido ("" = COLOR_FONDO clásico)
        "reporte_actual": {},
        "modo_local": False,       # True cuando se entra con el acceso de prueba (no toca Supabase)
        "_reportes_locales": [],   # historial en memoria, solo para el acceso de prueba
        "_temas_locales": [],      # temas en memoria, solo para el acceso de prueba
        "_bienestar_locales": [],  # chequeos de bienestar en memoria, solo para el acceso de prueba
        "_reappraisal_locales": [],  # ejercicios de reappraisal en memoria, solo para el acceso de prueba
        "_latido_token": None,     # controla el hilo del latido (mantener viva la conexión)
        "apoyo_menu_pendiente": False,  # True tras un autorreporte <60%: el menú muestra (una vez) un mensaje cálido de acompañamiento
        "_niveles_ia_batch": [],
        "_nivel_ia_actual": 0,
        "_batch_ia_generando": False,
        "_siguiente_batch_ia": [],
        "_siguiente_batch_ia_generando": False,
        "_historial_ia": [],
        "_intentos_nivel_ia": 0,
        "_errores_nivel_ia": [],       # <-- 
        "realizo_test_inicial": False,  # <-- TEMP TEST
        "perfil_contexto": {},          # <-- TEMP TEST
    }

    # ==========================================================
    # NAVEGACIÓN (mismo patrón que la app de Encuesta)
    # ==========================================================
    historial = []

    def _clave_borrador():
        return f"borrador_reporte_{estado.get('usuario_id')}"

    async def _guardar_borrador():
        # Guarda el reporte en curso en el almacenamiento del navegador
        # (page.shared_preferences), no en Supabase: es solo para poder
        # recuperar lo escrito si la conexión se corta a mitad de un
        # reporte largo, nunca se manda al servidor hasta que la persona
        # llega de verdad al paso de recomendaciones. Se llama después de
        # cada cambio de pantalla; como es "fire and forget" (no bloquea
        # la navegación), un fallo acá no debería impedir seguir usando
        # la app, solo se pierde la posibilidad de retomar el borrador.
        try:
            r = estado.get("reporte_actual") or {}
            clave = _clave_borrador()
            if r and not r.get("_guardado"):
                await page.shared_preferences.set(clave, json.dumps(r))
            else:
                await page.shared_preferences.remove(clave)
        except Exception as e:
            print("Error de borrador (shared_preferences):", e)

    def ir_a(pantalla_funcion):
        historial.append(pantalla_funcion)
        pantalla_funcion()
        page.run_task(_guardar_borrador)

    def volver(e=None):
        if len(historial) > 1:
            historial.pop()
            historial[-1]()

    # ------------------------------------------------------------------
    # Ajuste de género en los textos que hablan del usuario (pedido de
    # Gabriel, 2026-07-14): si ya sabemos el género de la persona, no
    # tiene sentido mostrarle "solo/a" — se muestra "solo", "sola" o
    # "sole" (no binario). La tabla es EXPLÍCITA a propósito: solo
    # entran palabras que refieren al usuario mismo; "psicólogo/a",
    # "amigo/a", etc. refieren a terceros y deben quedar como están.
    # Con "Prefiero no decir" (o sin dato) se mantiene la forma "o/a".
    # Si se agrega un texto nuevo con una palabra "o/a" que refiera al
    # usuario, sumarla acá.
    # ------------------------------------------------------------------
    PALABRAS_GENERO = {
        # las entradas más largas van primero (ganan el reemplazo antes
        # de que una más corta rompa la frase)
        "el único/a al que": ("el único al que", "la única a la que", "le únique a quien"),
        "solo/a": ("solo", "sola", "sole"),
        "mismo/a": ("mismo", "misma", "misme"),
        "pegado/a": ("pegado", "pegada", "pegade"),
        "sentado/a": ("sentado", "sentada", "sentade"),
        "descansado/a": ("descansado", "descansada", "descansade"),
        "tranquilo/a": ("tranquilo", "tranquila", "tranquile"),
        "relajado/a": ("relajado", "relajada", "relajade"),
        "activo/a": ("activo", "activa", "active"),
        "fresco/a": ("fresco", "fresca", "fresque"),
        "metido/a": ("metido", "metida", "metide"),
        "seguro/a": ("seguro", "segura", "segure"),
        "Bienvenido/a": ("Bienvenido", "Bienvenida", "Bienvenide"),
    }

    def ajustar_genero_texto(texto):
        if not texto or "/a" not in texto:
            return texto
        indice = {"Masculino": 0, "Femenino": 1, "No binario": 2}.get(estado.get("genero") or "")
        if indice is None:
            return texto
        for palabra, formas in PALABRAS_GENERO.items():
            if palabra in texto:
                texto = texto.replace(palabra, formas[indice])
        return texto

    _ATRIBUTOS_TEXTO = ("value", "label", "hint_text", "text", "helper_text", "tooltip")
    _ATRIBUTOS_HIJOS = ("controls", "content", "options", "leading", "trailing", "actions", "title")

    def ajustar_genero_controles(control):
        # Recorre el árbol de controles de la pantalla y ajusta cada
        # texto visible. Se hace acá (una sola vez, al dibujar) para no
        # tener que acordarse en cada pantalla nueva.
        for attr in _ATRIBUTOS_TEXTO:
            valor = getattr(control, attr, None)
            if isinstance(valor, str) and "/a" in valor:
                setattr(control, attr, ajustar_genero_texto(valor))
        for attr in _ATRIBUTOS_HIJOS:
            hijos = getattr(control, attr, None)
            if hijos is None:
                continue
            if isinstance(hijos, str):
                # En Flet 0.84 los botones guardan su texto en .content
                # como string — también es texto visible.
                if "/a" in hijos:
                    setattr(control, attr, ajustar_genero_texto(hijos))
                continue
            if isinstance(hijos, (list, tuple)):
                for hijo in hijos:
                    if hijo is not None and not isinstance(hijo, str):
                        ajustar_genero_controles(hijo)
            else:
                ajustar_genero_controles(hijos)

    def pantalla(*controles, mostrar_volver=True, decoraciones=None):
        # decoraciones: lista opcional de controles ya posicionados
        # (left/top/right/bottom) que se dibujan DETRÁS del contenido,
        # como empapelado de la tarjeta — hoy lo usa solo el menú
        # principal para las florcitas del chequeo de bienestar.
        page.controls.clear()
        page.overlay.clear()

        for control in controles:
            ajustar_genero_controles(control)

        filas = []
        if mostrar_volver and len(historial) > 1:
            filas.append(
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            tooltip="Volver",
                            on_click=volver,
                            icon_color=ft.Colors.WHITE,
                            bgcolor=COLOR_PRIMARIO,
                        )
                    ],
                    alignment=ft.MainAxisAlignment.START,
                )
            )
        filas.extend(controles)

        columna = ft.Column(
            filas,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )

        if decoraciones:
            # El contenido va anclado a los 4 bordes para ocupar toda la
            # tarjeta (misma geometría que sin decoraciones); las flores
            # quedan debajo, como fondo.
            contenido_tarjeta = ft.Stack(
                [
                    *decoraciones,
                    ft.Container(content=columna, left=0, top=0, right=0, bottom=0),
                ],
                expand=True,
            )
        else:
            contenido_tarjeta = columna

        tarjeta = ft.Container(
            content=contenido_tarjeta,
            padding=20,
            margin=15,
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.97, COLOR_TARJETA),
            expand=True,
        )

        page.add(ft.Container(content=tarjeta, alignment=ft.Alignment.CENTER, expand=True))
        page.update()
        _iniciar_latido()

    # Latido (heartbeat): en el celular, cuando la app queda en segundo
    # plano un rato (cambiás a otra app y volvés), la conexión en vivo con
    # el servidor se corta y al volver los botones quedan sin responder.
    # Para evitarlo, mientras se muestra cualquier pantalla se manda una
    # actualización liviana cada 20 segundos, así la conexión nunca queda
    # del todo quieta. Cada pantalla nueva cancela el latido de la
    # anterior (por eso el token), para no ir acumulando hilos.
    def _iniciar_latido():
        token = object()
        estado["_latido_token"] = token

        def loop():
            while estado.get("_latido_token") is token:
                time.sleep(20)
                if estado.get("_latido_token") is not token:
                    return
                try:
                    page.update()
                except Exception:
                    return

        threading.Thread(target=loop, daemon=True).start()

    def mostrar_error(texto_control, mensaje):
        texto_control.value = mensaje
        page.update()

    # ==========================================================
    # LOGIN / REGISTRO
    # ==========================================================
    def buscar_usuario_por_email(email):
        try:
            resp = requests.get(
                SUPABASE_USUARIOS_URL,
                headers=HEADERS,
                params={"email": f"eq.{email}", "select": "*"},
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase GET usuarios_regulacion [{resp.status_code}]: {resp.text}")
                return None, False
            resultados = resp.json()
            return (resultados[0], True) if resultados else (None, True)
        except Exception as e:
            print("Error de red (usuarios_regulacion):", repr(e))
            return None, False

    def crear_usuario(email, password_hash, password_salt=None):
        try:
            resp = requests.post(
                SUPABASE_USUARIOS_URL,
                headers={**HEADERS, "Prefer": "return=representation"},
                json={"email": email, "password_hash": password_hash, "password_salt": password_salt},
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase POST usuarios_regulacion [{resp.status_code}]: {resp.text}")
                return None
            creados = resp.json()
            return creados[0] if creados else None
        except Exception as e:
            print("Error de red (crear usuario):", repr(e))
            return None

    def buscar_o_crear_usuario_google(email):
        # Usado solo por el login con Google: no pide/valida contraseña.
        usuario, ok = buscar_usuario_por_email(email)
        if not ok:
            return None
        if usuario:
            return usuario
        return crear_usuario(email, None)

    def actualizar_password_supabase(usuario_id, password_hash, password_salt):
        try:
            resp = requests.patch(
                f"{SUPABASE_USUARIOS_URL}?id=eq.{usuario_id}",
                headers=HEADERS,
                json={"password_hash": password_hash, "password_salt": password_salt},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (actualizar password):", e)
            return False

    def ir_a_menu_principal():
        if not estado.get("vio_instrucciones"):
            ir_a(lambda: mostrar_instrucciones(0, PAGINAS_INSTRUCCIONES_INICIALES))

        elif not estado.get("realizo_test_inicial"):
            mostrar_test_inicial(
                page=page,
                estado=estado,
                SUPABASE_USUARIOS_URL=SUPABASE_USUARIOS_URL,
                HEADERS=HEADERS,
                al_completar_callback=finalizar_test_inicial
            )

        else:
            page.run_task(precargar_batch_ia)
            ir_a(mostrar_menu_principal)

    def finalizar_test_inicial():
        page.run_task(precargar_batch_ia)
        ir_a_menu_principal()

    def entrar_con_usuario(usuario, local=False):
        estado["email"] = usuario["email"]
        estado["usuario_id"] = usuario["id"]
        estado["nombre"] = usuario.get("nombre") or ""
        estado["edad"] = usuario.get("edad")
        estado["genero"] = usuario.get("genero") or ""
        estado["en_tratamiento"] = usuario.get("en_tratamiento") or ""
        estado["tiene_password"] = usuario.get("password_hash") is not None
        estado["pregunta_seguridad"] = usuario.get("pregunta_seguridad") or ""
        estado["vio_instrucciones"] = bool(usuario.get("vio_instrucciones"))
        estado["vio_instrucciones_temas"] = bool(usuario.get("vio_instrucciones_temas"))
        estado["vio_instrucciones_bienestar"] = bool(usuario.get("vio_instrucciones_bienestar"))
        estado["vio_instrucciones_trabajo_emocional"] = bool(usuario.get("vio_instrucciones_trabajo_emocional"))
        estado["vio_instrucciones_reappraisal"] = bool(usuario.get("vio_instrucciones_reappraisal"))
        estado["cosmetico_planta"] = usuario.get("cosmetico_planta") or ""
        estado["cosmetico_fondo"] = usuario.get("cosmetico_fondo") or ""
        estado["color_fondo"] = usuario.get("color_fondo") or ""
        page.bgcolor = estado["color_fondo"] or COLOR_FONDO
        estado["modo_local"] = local
        estado["realizo_test_inicial"] = bool(usuario.get("realizo_test_inicial")) # TEMP TEST
        estado["perfil_contexto"] = usuario.get("perfil_contexto") or {} # TEMP TEST

        historial.clear()

        if estado["nombre"]:
            ir_a_menu_principal()
        else:
            ir_a(mostrar_perfil)

    # Usuarios de acceso rápido para testear la app sin Supabase (ver uso
    # más abajo, en iniciar_sesion). Clave = lo que se escribe en el campo
    # "Usuario (email)", en minúsculas.
    USUARIOS_PRUEBA = {
        "gaby": "taekwondo",
        "marlen": "Contreras",
        "jp":"jp"
    }

    google_provider = None
    if GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET and GOOGLE_REDIRECT_URL:
        google_provider = GoogleOAuthProvider(
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            redirect_url=GOOGLE_REDIRECT_URL,
        )

    def _al_iniciar_sesion_google(e):
        if e.error:
            print("Error de login con Google:", e.error, e.error_description)
            return
        email_google = (page.auth.user.get("email") or "").strip().lower()
        if not email_google:
            return
        usuario = buscar_o_crear_usuario_google(email_google)
        if usuario:
            entrar_con_usuario(usuario)

    page.on_login = _al_iniciar_sesion_google

    def mostrar_login():
        async def iniciar_con_google(e):
            await page.login(google_provider)

        def iniciar_sesion(e):
            email = (input_email.value or "").strip().lower()
            contrasena = input_contrasena.value or ""

            # Accesos de prueba: entran directo con datos en memoria, sin
            # tocar Supabase para nada. Sirve para testear la app mientras
            # no está configurada la base de datos real. Sacar esto (o
            # cambiar las contraseñas) antes de compartir la app
            # públicamente con otras personas.
            if email in USUARIOS_PRUEBA and contrasena == USUARIOS_PRUEBA[email]:
                # Nombre ya precargado (nunca vacío) para que el acceso de
                # prueba salte directo al menú principal en vez de pasar
                # por "Contanos un poco sobre vos" cada vez.
                usuario_prueba = {
                    "id": f"local-prueba-{email}",
                    "email": f"{email}.prueba@test.local",
                    "nombre": estado.get("nombre") or email.capitalize(),
                    "edad": estado.get("edad"),
                    "genero": estado.get("genero") or "",
                }
                entrar_con_usuario(usuario_prueba, local=True)
                return

            if "@" not in email or "." not in email.split("@")[-1]:
                input_email.error_text = "Ingresá un email válido"
                page.update()
                return
            input_email.error_text = None

            if len(contrasena) < 6:
                input_contrasena.error_text = "La contraseña tiene que tener al menos 6 caracteres"
                page.update()
                return
            input_contrasena.error_text = None

            texto_error.value = ""
            boton_ingresar.disabled = True
            boton_ingresar.text = "Ingresando..."
            page.update()

            usuario, ok = buscar_usuario_por_email(email)

            if not ok:
                boton_ingresar.disabled = False
                boton_ingresar.text = "Ingresar"
                mostrar_error(texto_error, "No pudimos conectar. Revisá tu conexión e intentá de nuevo.")
                return

            if usuario is None:
                # Cuenta nueva: se registra con esta contraseña, con una
                # sal aleatoria propia (no derivada del email).
                salt_nueva = generar_salt()
                hash_nuevo = hash_contrasena(contrasena, salt_nueva)
                usuario = crear_usuario(email, hash_nuevo, salt_nueva)
                boton_ingresar.disabled = False
                boton_ingresar.text = "Ingresar"
                if usuario is None:
                    mostrar_error(texto_error, "No pudimos crear tu cuenta. Revisá tu conexión e intentá de nuevo.")
                    return
                entrar_con_usuario(usuario)
                return

            boton_ingresar.disabled = False
            boton_ingresar.text = "Ingresar"

            if usuario.get("password_hash") is None:
                mostrar_error(texto_error, "Esta cuenta fue creada con Google. Iniciá sesión con el botón de Google.")
                return

            salt_guardada = usuario.get("password_salt")
            if not salt_guardada:
                mostrar_error(texto_error, "Hubo un problema con tu cuenta. Contactanos para ayudarte a recuperarla.")
                return

            hash_ingresado = hash_contrasena(contrasena, salt_guardada)
            if usuario.get("password_hash") != hash_ingresado:
                mostrar_error(texto_error, "Contraseña incorrecta.")
                return

            entrar_con_usuario(usuario)

        input_email = ft.TextField(label="Usuario (email)", width=ancho_campo(), keyboard_type=ft.KeyboardType.EMAIL)
        input_contrasena = ft.TextField(label="Contraseña", width=ancho_campo(), password=True, can_reveal_password=True)
        texto_error = ft.Text("", color=ft.Colors.RED)
        boton_ingresar = ft.ElevatedButton("Ingresar", on_click=iniciar_sesion, width=ancho_campo(), height=50)

        controles = [
            ft.Icon(ft.Icons.SELF_IMPROVEMENT, size=50, color=COLOR_PRIMARIO),
            ft.Text("DRE", size=26, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("Diario de Reflexión Emocional", size=12, color=COLOR_TEXTO_SUAVE, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Un espacio tranquilo para poner en palabras lo que sentís y acompañarte a pensarlo de otra forma.",
                text_align=ft.TextAlign.CENTER,
                color=COLOR_TEXTO_MEDIO,
            ),
            ft.Text(
                "Esto no reemplaza la atención de un profesional de salud mental.",
                size=11,
                color=COLOR_TEXTO_SUAVE,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.TextButton(
                "¿Necesitás hablar con alguien ahora?",
                icon=ft.Icons.PHONE_IN_TALK,
                on_click=lambda _: ir_a(mostrar_paso_crisis_recursos),
            ),
        ]

        if google_provider:
            controles.append(
                ft.ElevatedButton(
                    "Continuar con Google",
                    icon=ft.Icons.LOGIN,
                    on_click=iniciar_con_google,
                    width=ancho_campo(),
                    height=50,
                )
            )
            controles.append(ft.Text("— o —", color=COLOR_TEXTO_SUAVE))

        controles.extend([
            input_email,
            input_contrasena,
            texto_error,
            boton_ingresar,
            ft.TextButton("¿Olvidaste tu contraseña?", on_click=lambda _: ir_a(mostrar_recuperar_paso1)),
            ft.Text(
                "Si es tu primera vez, se crea la cuenta automáticamente con ese usuario y contraseña.",
                size=11,
                color=COLOR_TEXTO_SUAVE,
                text_align=ft.TextAlign.CENTER,
            ),
        ])

        pantalla(*controles, mostrar_volver=False)

    # ==========================================================
    # RECUPERAR CONTRASEÑA
    # ----------------------------------------------------------
    # Sin envío de mails (la app no tiene ese servicio configurado): se
    # verifica identidad con una pregunta de seguridad que la persona
    # eligió y respondió en "Mi perfil" (guardada con el mismo esquema de
    # hash+sal que la contraseña, nunca en texto plano). Si la cuenta es
    # de Google, o todavía no configuró una pregunta, se le avisa en vez
    # de dejarla en un callejón sin salida.
    # ==========================================================
    def mostrar_recuperar_paso1():
        input_email = ft.TextField(label="Tu email", width=ancho_campo(), keyboard_type=ft.KeyboardType.EMAIL)
        texto_error = ft.Text("", color=ft.Colors.RED)
        boton_continuar = ft.ElevatedButton("Continuar", width=ancho_campo(), height=50)

        def continuar(e):
            email = (input_email.value or "").strip().lower()
            if "@" not in email or "." not in email.split("@")[-1]:
                mostrar_error(texto_error, "Ingresá un email válido.")
                return

            boton_continuar.disabled = True
            boton_continuar.text = "Buscando..."
            page.update()

            usuario, ok = buscar_usuario_por_email(email)

            boton_continuar.disabled = False
            boton_continuar.text = "Continuar"

            if not ok:
                mostrar_error(texto_error, "No pudimos conectar. Revisá tu conexión e intentá de nuevo.")
                return
            if usuario is None:
                mostrar_error(texto_error, "No encontramos una cuenta con ese email.")
                return
            if usuario.get("password_hash") is None:
                mostrar_error(texto_error, "Esta cuenta fue creada con Google. Iniciá sesión con el botón de Google.")
                return
            if not usuario.get("pregunta_seguridad") or not usuario.get("respuesta_seguridad_hash"):
                mostrar_error(texto_error, "Esta cuenta todavía no tiene una pregunta de seguridad configurada. Contactanos para ayudarte a recuperarla.")
                return

            ir_a(lambda: mostrar_recuperar_paso2(usuario))

        boton_continuar.on_click = continuar

        pantalla(
            ft.Icon(ft.Icons.LOCK_RESET, size=44, color=COLOR_PRIMARIO),
            ft.Text("Recuperar tu cuenta", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Ingresá el email con el que te registraste.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            input_email,
            texto_error,
            boton_continuar,
            ft.TextButton("Volver a iniciar sesión", on_click=lambda _: ir_a(mostrar_login)),
            mostrar_volver=False,
        )

    def mostrar_recuperar_paso2(usuario):
        input_respuesta = ft.TextField(label="Tu respuesta", width=ancho_campo())
        texto_error = ft.Text("", color=ft.Colors.RED)

        def continuar(e):
            respuesta = (input_respuesta.value or "").strip()
            if not respuesta:
                mostrar_error(texto_error, "Escribí tu respuesta para poder seguir.")
                return
            respuesta_normalizada = _sin_acentos(respuesta.lower())
            hash_ingresado = hash_contrasena(respuesta_normalizada, usuario["respuesta_seguridad_salt"])
            if hash_ingresado != usuario["respuesta_seguridad_hash"]:
                mostrar_error(texto_error, "Esa no es la respuesta que tenemos guardada. Probá de nuevo.")
                return
            ir_a(lambda: mostrar_recuperar_paso3(usuario))

        pantalla(
            ft.Icon(ft.Icons.LOCK_RESET, size=44, color=COLOR_PRIMARIO),
            ft.Text("Tu pregunta de seguridad", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(usuario["pregunta_seguridad"], color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            input_respuesta,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
            ft.TextButton("Volver a iniciar sesión", on_click=lambda _: ir_a(mostrar_login)),
            mostrar_volver=False,
        )

    def mostrar_recuperar_paso3(usuario):
        input_nueva = ft.TextField(label="Nueva contraseña", width=ancho_campo(), password=True, can_reveal_password=True)
        texto_error = ft.Text("", color=ft.Colors.RED)
        boton_guardar = ft.ElevatedButton("Guardar nueva contraseña", width=ancho_campo(), height=50)

        def guardar(e):
            nueva = input_nueva.value or ""
            if len(nueva) < 6:
                mostrar_error(texto_error, "La contraseña tiene que tener al menos 6 caracteres.")
                return

            boton_guardar.disabled = True
            boton_guardar.text = "Guardando..."
            page.update()

            salt_nueva = generar_salt()
            hash_nuevo = hash_contrasena(nueva, salt_nueva)
            ok = actualizar_password_supabase(usuario["id"], hash_nuevo, salt_nueva)

            boton_guardar.disabled = False
            boton_guardar.text = "Guardar nueva contraseña"

            if not ok:
                mostrar_error(texto_error, "No pudimos guardar la contraseña nueva. Revisá tu conexión e intentá de nuevo.")
                return

            ir_a(mostrar_recuperar_listo)

        boton_guardar.on_click = guardar

        pantalla(
            ft.Icon(ft.Icons.LOCK_RESET, size=44, color=COLOR_PRIMARIO),
            ft.Text("Elegí tu nueva contraseña", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            input_nueva,
            texto_error,
            boton_guardar,
            mostrar_volver=False,
        )

    def mostrar_recuperar_listo():
        pantalla(
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=44, color=COLOR_EXITO),
            ft.Text("Listo, ya podés ingresar", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Tu contraseña se actualizó. Iniciá sesión con la nueva.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.ElevatedButton("Ir a iniciar sesión", on_click=lambda _: ir_a(mostrar_login), width=ancho_campo(), height=50),
            mostrar_volver=False,
        )

    def cerrar_sesion(e):
        estado["email"] = ""
        estado["usuario_id"] = None
        estado["nombre"] = ""
        estado["edad"] = None
        estado["genero"] = ""
        estado["en_tratamiento"] = ""
        estado["pregunta_seguridad"] = ""
        estado["vio_instrucciones"] = False
        estado["vio_instrucciones_temas"] = False
        estado["vio_instrucciones_bienestar"] = False
        estado["vio_instrucciones_trabajo_emocional"] = False
        estado["vio_instrucciones_reappraisal"] = False
        estado["cosmetico_planta"] = ""
        estado["cosmetico_fondo"] = ""
        estado["color_fondo"] = ""
        page.bgcolor = COLOR_FONDO
        estado["modo_local"] = False
        estado["_reportes_locales"] = []
        estado["_temas_locales"] = []
        estado["_bienestar_locales"] = []
        estado["_reappraisal_locales"] = []
        estado["apoyo_menu_pendiente"] = False
        page.logout()
        historial.clear()
        ir_a(mostrar_login)

    # ==========================================================
    # MI PERFIL
    # ==========================================================
    OPCIONES_GENERO = ["Femenino", "Masculino", "No binario", "Prefiero no decir"]
    # Se usa para adaptar algunos consejos finales (ver mostrar_paso_recomendaciones):
    # si ya está en tratamiento, tiene más sentido invitar a llevar el tema a su
    # psicólogo/a o psiquiatra que sugerirle buscar uno desde cero.
    OPCIONES_TRATAMIENTO = ["Sí", "No", "Prefiero no decir"]

    # Preguntas de seguridad para "¿Olvidaste tu contraseña?": la app no
    # tiene un servicio de mails configurado, así que la recuperación se
    # hace verificando esto en vez de mandar un link. La respuesta se
    # guarda con el mismo esquema de hash+sal que la contraseña (nunca en
    # texto plano), normalizada (sin acentos, en minúscula) para que no
    # se trabe por mayúsculas o tildes al volver a escribirla.
    PREGUNTAS_SEGURIDAD = [
        "¿Cuál fue el nombre de tu primera mascota?",
        "¿En qué ciudad naciste?",
        "¿Cuál es tu comida favorita?",
        "¿Cómo se llamaba tu mejor amigo/a de la infancia?",
        "¿Cuál es tu película favorita?",
    ]

    def guardar_perfil_supabase(nombre, edad, genero, en_tratamiento, pregunta_seguridad=None, respuesta_hash=None, respuesta_salt=None):
        if estado["modo_local"]:
            return True
        datos = {"nombre": nombre, "edad": edad, "genero": genero, "en_tratamiento": en_tratamiento}
        # Solo se tocan estos campos si la persona escribió una respuesta
        # nueva: si los dejó vacíos porque ya tenía una configurada de
        # antes, no hay que pisarla con nada.
        if pregunta_seguridad is not None:
            datos["pregunta_seguridad"] = pregunta_seguridad
            datos["respuesta_seguridad_hash"] = respuesta_hash
            datos["respuesta_seguridad_salt"] = respuesta_salt
        try:
            resp = requests.patch(
                f"{SUPABASE_USUARIOS_URL}?id=eq.{estado['usuario_id']}",
                headers=HEADERS,
                json=datos,
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (guardar perfil):", e)
            return False

    def mostrar_perfil():
        es_primera_vez = not estado["nombre"]

        input_nombre = ft.TextField(label="Nombre", value=estado["nombre"], width=ancho_campo())
        input_edad = ft.TextField(
            label="Edad",
            value=str(estado["edad"]) if estado["edad"] is not None else "",
            width=ancho_campo(),
            keyboard_type=ft.KeyboardType.NUMBER,
        )
        dropdown_genero = ft.Dropdown(
            label="Género (opcional)",
            options=[ft.dropdown.Option(op) for op in OPCIONES_GENERO],
            value=estado["genero"] or None,
            width=ancho_campo(),
        )
        dropdown_tratamiento = ft.Dropdown(
            label="¿Estás en tratamiento con un psicólogo/a o psiquiatra? (opcional)",
            options=[ft.dropdown.Option(op) for op in OPCIONES_TRATAMIENTO],
            value=estado["en_tratamiento"] or None,
            width=ancho_campo(),
        )
        dropdown_pregunta_seguridad = ft.Dropdown(
            label="Pregunta de seguridad (para recuperar tu cuenta)",
            options=[ft.dropdown.Option(op) for op in PREGUNTAS_SEGURIDAD],
            value=estado.get("pregunta_seguridad") or None,
            width=ancho_campo(),
        )
        input_respuesta_seguridad = ft.TextField(
            label="Tu respuesta",
            hint_text=(
                "Dejalo vacío si no querés cambiarla"
                if estado.get("pregunta_seguridad")
                else "La vamos a usar solo si algún día te olvidás la contraseña"
            ),
            width=ancho_campo(),
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def guardar(e):
            nombre_valor = (input_nombre.value or "").strip()
            if not nombre_valor:
                input_nombre.error_text = "Ingresá tu nombre"
                page.update()
                return
            input_nombre.error_text = None

            edad_texto = (input_edad.value or "").strip()
            edad_valor = None
            if edad_texto:
                if not edad_texto.isdigit():
                    input_edad.error_text = "Ingresá un número"
                    page.update()
                    return
                edad_valor = int(edad_texto)
            input_edad.error_text = None

            genero_valor = dropdown_genero.value or ""
            tratamiento_valor = dropdown_tratamiento.value or ""

            respuesta_valor = (input_respuesta_seguridad.value or "").strip()
            pregunta_valor = None
            hash_respuesta = None
            salt_respuesta = None
            if respuesta_valor:
                if not dropdown_pregunta_seguridad.value:
                    mostrar_error(texto_error, "Elegí una pregunta de seguridad antes de escribir la respuesta.")
                    return
                pregunta_valor = dropdown_pregunta_seguridad.value
                salt_respuesta = generar_salt()
                hash_respuesta = hash_contrasena(_sin_acentos(respuesta_valor.lower()), salt_respuesta)

            if not guardar_perfil_supabase(nombre_valor, edad_valor, genero_valor, tratamiento_valor, pregunta_valor, hash_respuesta, salt_respuesta):
                mostrar_error(texto_error, "No pudimos guardar los cambios. Revisá tu conexión e intentá de nuevo.")
                return

            estado["nombre"] = nombre_valor
            estado["edad"] = edad_valor
            estado["genero"] = genero_valor
            estado["en_tratamiento"] = tratamiento_valor
            if pregunta_valor is not None:
                estado["pregunta_seguridad"] = pregunta_valor

            historial.clear()
            ir_a_menu_principal()

        boton_guardar = ft.ElevatedButton("Guardar", on_click=guardar, width=ancho_campo(), height=50)

        controles = [ft.Text("Contanos un poco sobre vos" if es_primera_vez else "Mi perfil", size=24, weight=ft.FontWeight.BOLD)]
        if es_primera_vez:
            controles.append(
                ft.Text(
                    "Así podemos acompañarte mejor. Es rápido, prometido.",
                    text_align=ft.TextAlign.CENTER,
                    color=COLOR_TEXTO_MEDIO,
                )
            )
        controles.extend([input_nombre, input_edad, dropdown_genero, dropdown_tratamiento])
        if estado.get("tiene_password", True):
            # No tiene sentido pedir esto a alguien que entró con Google:
            # nunca va a necesitar "¿Olvidaste tu contraseña?" porque no
            # tiene una contraseña propia que recuperar.
            controles.extend([dropdown_pregunta_seguridad, input_respuesta_seguridad])
        controles.extend([texto_error, boton_guardar])

        pantalla(*controles, mostrar_volver=not es_primera_vez)

    # ==========================================================
    # MENÚ PRINCIPAL
    # ==========================================================
    # ==========================================================
    # INSTRUCCIONES (onboarding)
    # ----------------------------------------------------------
    # Se muestra automáticamente la primera vez que la persona llega al
    # menú principal (ver ir_a_menu_principal), y nunca más de forma
    # automática después de eso — pero queda siempre disponible a mano
    # desde el ícono de instrucciones en el menú. "Vista" se guarda en el
    # perfil (persiste entre dispositivos), no solo en este navegador.
    # ==========================================================
    # La versión que aparece sola la primera vez es corta a propósito (2
    # páginas, solo lo esencial: para qué sirve y que es privado/seguro).
    # La versión completa (con el "extra" de herramientas) solo se
    # muestra cuando la persona la pide a mano, con el ícono de
    # instrucciones del menú — ahí sí tiene sentido que sea más larga,
    # porque ya está buscando esa información.
    PAGINAS_INSTRUCCIONES_INICIALES = [
        {
            "icono": ft.Icons.WAVING_HAND_OUTLINED,
            "color": COLOR_PRIMARIO,
            "titulo": "¡Bienvenido/a!",
            "texto": "Este es un espacio para reflexionar sobre pensamientos, emociones o situaciones que te generen malestar. Podés empezar un registro y retomarlo cuando quieras, incluso días después.",
        },
        {
            "icono": ft.Icons.FAVORITE_BORDER,
            "color": COLOR_EXITO,
            "titulo": "Privado y seguro",
            "texto": "Todo lo que registrás acá es privado: solo vos podés verlo con tu cuenta. La única forma de compartirlo con otra persona es que vos mismo/a decidas descargar o enviar tu planilla desde \"Compartir mi evolución\". DRE no reemplaza la atención de un profesional de salud mental — el botón \"Necesito ayuda ahora\" está siempre disponible si lo necesitás.",
        },
    ]

    PAGINAS_INSTRUCCIONES_EXTRA = [
        {
            "icono": ft.Icons.EXPLORE_OUTLINED,
            "color": COLOR_DORADO,
            "titulo": "Herramientas para acompañarte",
            "texto": "Podés guardar los pensamientos que se repiten en \"Pensamientos que estoy trabajando\" para seguir su evolución, revisar \"Consejos\" en cualquier momento sin cargar nada nuevo, compartir cómo fuiste evolucionando desde \"Compartir mi evolución\" (en Trabajo emocional) cuando quieras, y completar tu perfil para que la app se adapte mejor a vos.",
        },
    ]

    PAGINAS_INSTRUCCIONES_COMPLETAS = PAGINAS_INSTRUCCIONES_INICIALES + PAGINAS_INSTRUCCIONES_EXTRA

    def guardar_instrucciones_vistas_supabase():
        if estado["modo_local"]:
            return True
        try:
            resp = requests.patch(
                f"{SUPABASE_USUARIOS_URL}?id=eq.{estado['usuario_id']}",
                headers=HEADERS,
                json={"vio_instrucciones": True},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (guardar vio_instrucciones):", e)
            return False

    def mostrar_instrucciones(pagina=0, paginas=None, permitir_volver=False):
        # permitir_volver solo se activa cuando se abre a mano desde el
        # ícono de instrucciones del menú: ahí tiene sentido poder salir
        # de entrada sin tener que recorrer todas las páginas. El flujo
        # automático (primera vez) no lo usa, se deja como está.
        paginas = paginas if paginas is not None else PAGINAS_INSTRUCCIONES_INICIALES
        pagina = max(0, min(pagina, len(paginas) - 1))
        contenido = paginas[pagina]
        es_ultima = pagina == len(paginas) - 1

        def ir_a_pagina(numero):
            def handler(e):
                ir_a(lambda: mostrar_instrucciones(numero, paginas, permitir_volver))
            return handler

        def terminar(e):
            estado["vio_instrucciones"] = True
            guardar_instrucciones_vistas_supabase()
            historial.clear()
            ir_a_menu_principal()

        puntos = ft.Row(
            [
                ft.Container(
                    width=9,
                    height=9,
                    border_radius=5,
                    bgcolor=COLOR_PRIMARIO if i == pagina else COLOR_CAJA_SUAVE,
                )
                for i in range(len(paginas))
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8,
        )

        # ancho_campo() tiene un piso de 220px (pensado para campos de
        # texto de ancho completo) — para 2 botones lado a lado eso se
        # pasaba de la pantalla en celulares angostos. Con expand=True se
        # reparten el ancho disponible entre ellos, sin desbordar nunca.
        botones = []
        if pagina > 0:
            botones.append(ft.OutlinedButton("Atrás", on_click=ir_a_pagina(pagina - 1), height=50, expand=True))
        botones.append(
            ft.ElevatedButton("Empezar" if es_ultima else "Siguiente", on_click=terminar if es_ultima else ir_a_pagina(pagina + 1), height=50, expand=True)
        )

        pantalla(
            ft.Icon(contenido["icono"], size=70, color=contenido["color"]),
            ft.Text(contenido["titulo"], size=26, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(contenido["texto"], size=18, color=COLOR_TEXTO_FUERTE, text_align=ft.TextAlign.CENTER),
            puntos,
            ft.Row(botones, alignment=ft.MainAxisAlignment.CENTER, spacing=12, width=ancho_campo()),
            # La flechita de volver (arriba a la izquierda) solo se
            # muestra en la página 1 cuando se abrió a mano: ahí es la
            # única forma de salir sin avanzar. En las páginas
            # siguientes ya está el botón "Atrás" de abajo para lo mismo.
            mostrar_volver=permitir_volver and pagina == 0,
        )


    def mostrar_menu_principal():
        historial.clear()
        historial.append(mostrar_menu_principal)

        # Aviso para invitar a hacer el chequeo de bienestar cada 1-2
        # semanas (ver sección CHEQUEO DE BIENESTAR más abajo). Se calcula
        # acá, cada vez que se entra al menú principal, en vez de guardar
        # un recordatorio aparte: así siempre refleja el estado real sin
        # arriesgarse a quedar desactualizado.
        aviso_bienestar = ft.Container()
        chequeos_menu = obtener_chequeos_bienestar()
        dias_bienestar = _dias_desde_ultimo_chequeo_bienestar(chequeos_menu)

        # Recompensa visual del bloque 1: mientras el último chequeo de
        # bienestar está "vigente" (menos de 14 días), toda la tarjeta
        # del menú se empapela con florcitas distribuidas por los bordes
        # y esquinas, DETRÁS del contenido y semitransparentes para no
        # molestar la lectura — más flores, más grandes y más presentes
        # cuanto mejor salió el chequeo. Al vencerse la ventana de 2
        # semanas desaparecen solas (no se guarda nada: se recalcula acá).
        decoraciones_menu = None
        if dias_bienestar is not None and dias_bienestar < 14 and chequeos_menu:
            porcentaje_ultimo = chequeos_menu[0].get("porcentaje") or 0
            color_ultimo = color_por_avance(100 - porcentaje_ultimo)
            cantidad, opacidad, tamanos = {
                "Celeste": (18, 0.42, (24, 34, 44)),
                "Verde": (15, 0.36, (22, 30, 40)),
                "Amarillo": (12, 0.30, (20, 28, 34)),
                "Naranja": (9, 0.26, (18, 24, 30)),
            }.get(color_ultimo, (6, 0.22, (16, 22, 26)))

            # Patrón fijo (no aleatorio, para que se vea igual en cada
            # visita): posiciones ancladas a esquinas/bordes, alternando
            # lados y alturas para que se reparta armónico en cualquier
            # tamaño de pantalla. (anclaje, inset_x, inset_y)
            posiciones = [
                ("tl", 2, 58), ("tr", 6, 92), ("tl", 54, 128), ("tr", 60, 170),
                ("tl", 8, 216), ("tr", 4, 262), ("tl", 64, 308), ("tr", 70, 352),
                ("bl", 4, 210), ("br", 8, 252), ("bl", 58, 156), ("br", 64, 118),
                ("bl", 10, 64), ("br", 6, 88), ("bl", 110, 26), ("br", 118, 40),
                ("tl", 120, 30), ("tr", 128, 20),
            ]
            flor = fondo_actual()
            decoraciones_menu = []
            for i, (anclaje, ix, iy) in enumerate(posiciones[:cantidad]):
                props = {}
                if anclaje == "tl":
                    props = {"left": ix, "top": iy}
                elif anclaje == "tr":
                    props = {"right": ix, "top": iy}
                elif anclaje == "bl":
                    props = {"left": ix, "bottom": iy}
                else:
                    props = {"right": ix, "bottom": iy}
                decoraciones_menu.append(
                    ft.Container(
                        content=ft.Text(flor, size=tamanos[i % len(tamanos)]),
                        opacity=opacidad,
                        **props,
                    )
                )

        if dias_bienestar is None or dias_bienestar >= 14:
            aviso_bienestar = ft.Container(
                content=ft.Column(
                    [
                        ft.Text(
                            "¿Hacemos tu primer chequeo de bienestar?"
                            if dias_bienestar is None
                            else f"Pasaron {dias_bienestar} días desde tu último chequeo de bienestar.",
                            weight=ft.FontWeight.BOLD,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        ft.OutlinedButton(
                            "Completar autorreporte",
                            icon=ft.Icons.INSIGHTS,
                            on_click=lambda _: ir_a(mostrar_paso_bienestar),
                            width=ancho_campo(),
                            height=45,
                        ),
                    ],
                    spacing=8,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=15,
                border_radius=12,
                bgcolor=COLOR_CAJA_INFO,
                width=ancho_campo(),
            )

        # Mensaje de acompañamiento (una sola vez) para quien acaba de
        # tener un autorreporte por debajo de 60%: sin números ni colores,
        # solo recordarle que puede mejorar y que la app está para eso.
        tarjeta_apoyo = ft.Container()
        if estado.pop("apoyo_menu_pendiente", False):
            tarjeta_apoyo = ft.Container(
                content=ft.Text(
                    "💛 Gracias por contarnos cómo venís. Los momentos como este pueden mejorar — y no hace "
                    "falta que lo atravieses solo/a: DRE está para acompañarte. El Trabajo emocional y "
                    "Otra perspectiva son dos buenas herramientas para estos días; probalas a tu ritmo.",
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=15,
                border_radius=12,
                bgcolor=COLOR_CAJA_INFO,
                width=ancho_campo(),
            )

        # "Consejos" va solo, con texto, en la esquina superior izquierda
        # (pedido de Gabriel, 2026-07-14); los otros 3 accesos quedan
        # como íconos en la derecha.
        encabezado = ft.Row(
            [
                ft.TextButton(
                    "Consejos",
                    icon=ft.Icons.MENU_BOOK,
                    on_click=lambda _: ir_a(mostrar_consejos_biblioteca),
                    style=ft.ButtonStyle(color=ft.Colors.WHITE, bgcolor=COLOR_PRIMARIO),
                ),
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.HELP_OUTLINE,
                            tooltip="Instrucciones",
                            on_click=lambda _: ir_a(lambda: mostrar_instrucciones(0, PAGINAS_INSTRUCCIONES_COMPLETAS, permitir_volver=True)),
                            icon_color=ft.Colors.WHITE,
                            bgcolor=COLOR_PRIMARIO,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.LOCAL_FLORIST,
                            tooltip="Tu jardín",
                            on_click=lambda _: ir_a(mostrar_jardin),
                            icon_color=ft.Colors.WHITE,
                            bgcolor=COLOR_PRIMARIO,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.PERSON,
                            tooltip="Mi perfil",
                            on_click=lambda _: ir_a(mostrar_perfil),
                            icon_color=ft.Colors.WHITE,
                            bgcolor=COLOR_PRIMARIO,
                        ),
                    ],
                    spacing=8,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=ancho_campo(),
        )

        pantalla(
            encabezado,
            ft.Text("DRE", size=20, weight=ft.FontWeight.BOLD, color=COLOR_PRIMARIO, text_align=ft.TextAlign.CENTER),
            ft.Text("Diario de Reflexión Emocional", size=11, color=COLOR_TEXTO_SUAVE, text_align=ft.TextAlign.CENTER),
            ft.Text(f"Hola, {estado['nombre']}!", size=24, weight=ft.FontWeight.BOLD),
            ft.Text("¿Cómo querés usar este espacio hoy?", color=COLOR_TEXTO_MEDIO),
            tarjeta_apoyo,
            aviso_bienestar,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.ElevatedButton(
                "Autorreporte",
                icon=ft.Icons.INSIGHTS,
                on_click=lambda _: ir_a(mostrar_bienestar),
                width=ancho_campo(),
                height=50,
            ),
            ft.ElevatedButton(
                "Trabajo emocional",
                icon=ft.Icons.SELF_IMPROVEMENT,
                on_click=lambda _: ir_a(mostrar_trabajo_emocional),
                width=ancho_campo(),
                height=50,
            ),
            ft.ElevatedButton(
                "Otra perspectiva",
                icon=ft.Icons.AUTORENEW,
                on_click=lambda _: ir_a(mostrar_reappraisal),
                width=ancho_campo(),
                height=50,
            ),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.OutlinedButton(
                "Personalización",
                icon=ft.Icons.PALETTE_OUTLINED,
                on_click=lambda _: ir_a(mostrar_personalizacion),
                width=ancho_campo(),
                height=45,
            ),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            # Los dos accesos "de servicio" van chicos, uno en cada
            # esquina de abajo (pedido de Gabriel). El de ayuda mantiene
            # el texto completo y el rojo para seguir siendo visible:
            # los recursos de crisis nunca deben quedar enterrados.
            ft.Row(
                [
                    ft.TextButton(
                        "Necesito ayuda ahora",
                        icon=ft.Icons.PHONE_IN_TALK,
                        on_click=lambda _: ir_a(mostrar_paso_crisis_recursos),
                        style=ft.ButtonStyle(color=ft.Colors.RED_700),
                    ),
                    ft.TextButton("Cerrar sesión", on_click=cerrar_sesion),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                width=ancho_campo(),
            ),
            mostrar_volver=False,
            decoraciones=decoraciones_menu,
        )

    # ==========================================================
    # TRABAJO EMOCIONAL (submenú, bloque 2 del menú principal)
    # ----------------------------------------------------------
    # Agrupa las 2 opciones de este bloque: registrar una situación nueva
    # y ver/retomar lo ya registrado. "Ver cómo veniste resolviendo esto"
    # (el historial general de TODOS los reportes, no por tema) queda
    # como link secundario acá abajo en vez de desaparecer — Gabriel ya
    # lo había marcado como candidato a sacar, pero no pidió borrarlo
    # todavía.
    # ==========================================================
    def guardar_instrucciones_trabajo_emocional_vistas_supabase():
        if estado["modo_local"]:
            return True
        try:
            resp = requests.patch(
                f"{SUPABASE_USUARIOS_URL}?id=eq.{estado['usuario_id']}",
                headers=HEADERS,
                json={"vio_instrucciones_trabajo_emocional": True},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (guardar vio_instrucciones_trabajo_emocional):", e)
            return False

    def mostrar_instrucciones_trabajo_emocional(permitir_volver=False, detallada=False):
        # La versión corta se muestra sola la primera vez; la detallada
        # (con la diferencia respecto de Reappraisal) solo cuando la
        # persona la pide a mano con el ícono de ayuda del submenú.
        def continuar(e):
            estado["vio_instrucciones_trabajo_emocional"] = True
            guardar_instrucciones_trabajo_emocional_vistas_supabase()
            ir_a(_mostrar_menu_trabajo_emocional)

        controles = [
            ft.Icon(ft.Icons.SELF_IMPROVEMENT, size=60, color=COLOR_PRIMARIO),
            ft.Text("Trabajo emocional", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Este es el espacio para cuando algo real te está pesando ahora. \"Contame qué te está pasando\" "
                "arranca un registro nuevo, paso a paso, sobre una situación puntual. \"Pensamientos que estoy "
                "trabajando\" te lleva a los registros que ya empezaste, para retomarlos y seguir trabajándolos "
                "cuando quieras.",
                size=18,
                color=COLOR_TEXTO_FUERTE,
                text_align=ft.TextAlign.CENTER,
            ),
        ]
        if detallada:
            controles.append(
                ft.Text(
                    "¿En qué se diferencia de \"Otra perspectiva\"? Acá venís cuando algo te pasó de verdad y lo "
                    "desarmamos juntos, mirando qué tan cierto es ese pensamiento (la evidencia a favor y en "
                    "contra). \"Otra perspectiva\", en cambio, es como un gimnasio: ahí entrenás la habilidad de "
                    "cambiar de perspectiva practicando en frío, sin necesidad de estar mal en ese momento. "
                    "Las dos cosas se complementan: los pensamientos que registrás acá después también los "
                    "podés usar para practicar allá.",
                    size=16,
                    color=COLOR_TEXTO_MEDIO,
                    text_align=ft.TextAlign.CENTER,
                )
            )
        controles.append(ft.ElevatedButton("Entendido", on_click=continuar, width=ancho_campo(), height=50))
        pantalla(*controles, mostrar_volver=permitir_volver)

    def mostrar_trabajo_emocional():
        if not estado.get("vio_instrucciones_trabajo_emocional"):
            mostrar_instrucciones_trabajo_emocional(permitir_volver=True)
            return
        _mostrar_menu_trabajo_emocional()

    def _mostrar_menu_trabajo_emocional():
        pantalla(
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        tooltip="Instrucciones",
                        on_click=lambda _: ir_a(lambda: mostrar_instrucciones_trabajo_emocional(permitir_volver=True, detallada=True)),
                        icon_color=ft.Colors.WHITE,
                        bgcolor=COLOR_PRIMARIO,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            ft.Text("Trabajo emocional", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Registrá una situación nueva, o retomá algo que ya venís trabajando.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.ElevatedButton(
                "Contame qué te está pasando",
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                on_click=lambda _: page.run_task(iniciar_nuevo_reporte),
                width=ancho_campo(),
                height=50,
            ),
            ft.OutlinedButton(
                "Pensamientos que estoy trabajando",
                icon=ft.Icons.TRACK_CHANGES,
                on_click=lambda _: ir_a(mostrar_temas),
                width=ancho_campo(),
                height=50,
            ),
            ft.TextButton(
                "Compartir mi evolución",
                on_click=lambda _: ir_a(mostrar_compartir_evolucion),
            ),
        )

    # ==========================================================
    # REAPPRAISAL (submenú, bloque 3 del menú principal)
    # ----------------------------------------------------------
    # Mecánica confirmada por Gabriel (2026-07-13): arranca siempre por
    # "situaciones inventadas" (banco de CATEGORIAS_REAPPRAISAL); recién
    # al completar UMBRAL_REAPPRAISAL_PROPIAS ejercicios de ese modo se
    # desbloquea "situaciones propias" (desde un tema ya registrado, o
    # una situación nueva). Para elegir QUÉ situación inventada trabajar,
    # 2 caminos: que la app sugiera una al azar, o elegir la categoría a
    # mano de un menú — la técnica de reappraisal sale sola de la
    # categoría (no se elige aparte).
    # ==========================================================
    def guardar_instrucciones_reappraisal_vistas_supabase():
        if estado["modo_local"]:
            return True
        try:
            resp = requests.patch(
                f"{SUPABASE_USUARIOS_URL}?id=eq.{estado['usuario_id']}",
                headers=HEADERS,
                json={"vio_instrucciones_reappraisal": True},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (guardar vio_instrucciones_reappraisal):", e)
            return False

    def mostrar_instrucciones_reappraisal(permitir_volver=False, detallada=False):
        # Igual que en "Trabajo emocional": versión corta la primera vez,
        # versión detallada (por qué inventadas primero, y la diferencia
        # con el otro bloque) solo desde el ícono de ayuda del submenú.
        def continuar(e):
            estado["vio_instrucciones_reappraisal"] = True
            guardar_instrucciones_reappraisal_vistas_supabase()
            ir_a(_mostrar_menu_reappraisal)

        controles = [
            ft.Icon(ft.Icons.AUTORENEW, size=60, color=COLOR_PRIMARIO),
            ft.Text("Otra perspectiva", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Acá entrenás la habilidad de mirar una situación desde otro ángulo, para que pese menos "
                "emocionalmente. Se practica como en un gimnasio: en frío, sin necesidad de estar "
                "mal en ese momento. Empezás probando la técnica con una situación inventada, y enseguida "
                "se desbloquean ejercicios sobre situaciones tuyas de verdad.",
                size=18,
                color=COLOR_TEXTO_FUERTE,
                text_align=ft.TextAlign.CENTER,
            ),
        ]
        if detallada:
            controles.append(
                ft.Text(
                    "¿Por qué primero situaciones inventadas? Porque practicar con material que no te toca de "
                    "cerca hace más fácil aprender la técnica — igual que en un gimnasio no arrancás con el peso "
                    "máximo. Cada ejercicio son 4 pasos cortos: qué pensás/sentís, solo los hechos, la mirada de "
                    "un tercero, y cómo lo vas a ver dentro de un año. ¿En qué se diferencia de \"Trabajo "
                    "emocional\"? Allá vas cuando algo real te está pesando ahora, y lo trabajás mirando qué tan "
                    "cierto es el pensamiento; acá venís a entrenar el cambio de perspectiva, para que te salga "
                    "más fácil cuando lo necesites de verdad. Una vez desbloqueadas las situaciones propias, "
                    "también vas a poder practicar directo desde un pensamiento guardado en \"Trabajo emocional\".",
                    size=16,
                    color=COLOR_TEXTO_MEDIO,
                    text_align=ft.TextAlign.CENTER,
                )
            )
        controles.append(ft.ElevatedButton("Entendido", on_click=continuar, width=ancho_campo(), height=50))
        pantalla(*controles, mostrar_volver=permitir_volver)

    def mostrar_reappraisal():
        if not estado.get("vio_instrucciones_reappraisal"):
            mostrar_instrucciones_reappraisal(permitir_volver=True)
            return
        _mostrar_menu_reappraisal()

    def _mostrar_menu_reappraisal():
        completadas = contar_inventadas_completadas()
        desbloqueada = completadas >= UMBRAL_REAPPRAISAL_PROPIAS

        controles = [
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        tooltip="Instrucciones",
                        on_click=lambda _: ir_a(lambda: mostrar_instrucciones_reappraisal(permitir_volver=True, detallada=True)),
                        icon_color=ft.Colors.WHITE,
                        bgcolor=COLOR_PRIMARIO,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            ft.Text("Otra perspectiva", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Ejercicios para practicar la habilidad de ver una situación desde otro ángulo.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.ElevatedButton(
                "Ejercicios sobre situaciones inventadas",
                icon=ft.Icons.AUTO_STORIES,
                on_click=lambda _: ir_a(mostrar_reappraisal_elegir_inventada),
                width=ancho_campo(),
                height=50,
            ),
            ft.ElevatedButton(
                "Practicá con escenarios",
                icon=ft.Icons.SPORTS_ESPORTS,
                on_click=lambda _: ir_a(mostrar_reappraisal_juegos_categorias),
                width=ancho_campo(),
                height=50,
                bgcolor=MENTO_ROSA_TEXTO,
                color=ft.Colors.WHITE,
            ),
        ]

        if desbloqueada:
            controles.append(
                ft.OutlinedButton(
                    "Ejercicios sobre situaciones propias",
                    icon=ft.Icons.PSYCHOLOGY,
                    on_click=lambda _: ir_a(mostrar_reappraisal_propias_origen),
                    width=ancho_campo(),
                    height=50,
                )
            )
        else:
            controles.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                f"Completá {UMBRAL_REAPPRAISAL_PROPIAS} ejercicio{'s' if UMBRAL_REAPPRAISAL_PROPIAS != 1 else ''} de situaciones inventadas para desbloquear situaciones propias."
                                if UMBRAL_REAPPRAISAL_PROPIAS != 1 else
                                "Probá la técnica con una situación inventada para desbloquear las situaciones propias.",
                                weight=ft.FontWeight.BOLD,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.Text(
                                f"Llevás {completadas} de {UMBRAL_REAPPRAISAL_PROPIAS}." if UMBRAL_REAPPRAISAL_PROPIAS != 1 else "",
                                size=12,
                                color=COLOR_TEXTO_SUAVE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                        ],
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=COLOR_CAJA_SUAVE,
                    width=ancho_campo(),
                )
            )

        pantalla(*controles)

    def mostrar_reappraisal_elegir_inventada():
        def sugerir(e):
            categoria = random.choice(CATEGORIAS_REAPPRAISAL)
            situacion_texto, pensamiento_texto = random.choice(categoria["situaciones"])
            ir_a(lambda: mostrar_reappraisal_ejercicio("inventada", categoria["nombre"], situacion_texto, pensamiento_texto))

        pantalla(
            ft.Text("Situaciones inventadas", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("¿Cómo elegís la situación para practicar?", color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            ft.ElevatedButton("Sugerime una situación", icon=ft.Icons.SHUFFLE, on_click=sugerir, width=ancho_campo(), height=50),
            ft.OutlinedButton(
                "Elegir de un menú",
                icon=ft.Icons.LIST,
                on_click=lambda _: ir_a(mostrar_reappraisal_elegir_categoria_menu),
                width=ancho_campo(),
                height=50,
            ),
        )

    def mostrar_reappraisal_elegir_categoria_menu():
        tarjetas = []
        for categoria in CATEGORIAS_REAPPRAISAL:
            def elegir(e, categoria=categoria):
                situacion_texto, pensamiento_texto = random.choice(categoria["situaciones"])
                ir_a(lambda: mostrar_reappraisal_ejercicio("inventada", categoria["nombre"], situacion_texto, pensamiento_texto))

            tarjetas.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(categoria["nombre"], weight=ft.FontWeight.BOLD),
                            ft.Text(categoria["tecnica"], size=11, color=COLOR_TEXTO_SUAVE),
                        ],
                        spacing=2,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=COLOR_CAJA_SUAVE,
                    width=ancho_campo(),
                    on_click=elegir,
                )
            )
        pantalla(
            ft.Text("Elegí una categoría", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            *tarjetas,
        )

    def mostrar_reappraisal_propias_origen():
        pantalla(
            ft.Text("Situaciones propias", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("¿De dónde sale la situación para este ejercicio?", color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            ft.ElevatedButton(
                "Elegir de tus pensamientos ya trabajados",
                icon=ft.Icons.TRACK_CHANGES,
                on_click=lambda _: ir_a(mostrar_reappraisal_elegir_tema),
                width=ancho_campo(),
                height=50,
            ),
            ft.OutlinedButton(
                "Describir una situación nueva",
                icon=ft.Icons.EDIT_NOTE,
                on_click=lambda _: ir_a(mostrar_reappraisal_nueva_situacion),
                width=ancho_campo(),
                height=50,
            ),
        )

    def mostrar_reappraisal_elegir_tema():
        pantalla(ft.ProgressRing(), ft.Text("Cargando...", color=COLOR_PRIMARIO), mostrar_volver=True)

        temas = obtener_temas_usuario()

        if temas is None:
            pantalla(
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED),
                ft.Text("No pudimos cargar tus pensamientos. Revisá tu conexión e intentá de nuevo.", text_align=ft.TextAlign.CENTER),
            )
            return

        if not temas:
            pantalla(
                ft.Icon(ft.Icons.TRACK_CHANGES, size=50, color=COLOR_TEXTO_SUAVE),
                ft.Text("Todavía no tenés pensamientos registrados. Probá describir una situación nueva.", text_align=ft.TextAlign.CENTER),
            )
            return

        tarjetas = []
        for tema in temas:
            def elegir(e, tema=tema):
                ir_a(lambda: mostrar_reappraisal_ejercicio("propia", None, tema.get("titulo", ""), tema_id=tema["id"]))

            tarjetas.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(width=16, height=16, bgcolor=color_hex(tema.get("color")), border_radius=8),
                            ft.Text(tema.get("titulo") or "", expand=True),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=COLOR_CAJA_SUAVE,
                    width=ancho_campo(),
                    on_click=elegir,
                )
            )

        pantalla(
            ft.Text("Elegí un pensamiento", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            *tarjetas,
        )

    def mostrar_reappraisal_nueva_situacion():
        input_situacion = ft.TextField(
            label="Contame la situación",
            multiline=True,
            min_lines=3,
            max_lines=6,
            width=ancho_campo(),
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def continuar(e):
            situacion = (input_situacion.value or "").strip()
            if not situacion:
                mostrar_error(texto_error, "Contame aunque sea brevemente la situación.")
                return
            if detectar_riesgo_suicida(situacion):
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(situacion):
                ir_a(mostrar_paso_riesgo_terceros)
                return
            ir_a(lambda: mostrar_reappraisal_ejercicio("propia", None, situacion))

        pantalla(
            ft.Text("Describí tu situación", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            input_situacion,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
        )

    def mostrar_reappraisal_ejercicio(modo, categoria, situacion_texto, pensamiento_sugerido=None, tema_id=None):
        # En modo "inventada" la situación es una mini-historia con
        # personajes con nombre, así que las consignas hablan de ponerse
        # en el lugar del protagonista; en "propia" hablan directo de vos.
        es_inventada = modo == "inventada"
        input_pensamiento = ft.TextField(
            label="Poniéndote en su lugar: ¿qué pensarías en ese momento, y qué emoción te traería?"
            if es_inventada else
            "¿Qué pensarías sobre esta situación, y qué emoción te trae?",
            hint_text=(
                "Ya te dejamos escrito lo que piensa el/la protagonista — editalo o sumale lo tuyo, como frase completa (pensamiento + emoción)."
                if (es_inventada and pensamiento_sugerido) else
                "Escribilo como una frase completa, por ejemplo: \"siento que le importo poco, y eso me da tristeza y enojo\". Una sola palabra no alcanza para trabajarlo."
            ),
            value=pensamiento_sugerido or "",
            multiline=True,
            min_lines=2,
            max_lines=4,
            width=ancho_campo(),
        )
        # El objetivo de este paso es separar los HECHOS observables de
        # la INTERPRETACIÓN (el pensamiento del paso anterior es una
        # interpretación, no un hecho). La explicación con el ejemplo va
        # como texto visible ARRIBA del campo (no como hint): los hints
        # largos se cortan en el celular y la consigna quedaba confusa.
        explicacion_hechos = ft.Text(
            "Ahora separemos los hechos de la interpretación. Los hechos son solo lo que se hizo o se dijo "
            "(lo que cualquiera hubiera visto). Por ejemplo: \"canceló el plan dos veces\" es un hecho; "
            "\"le importo poco\" es una interpretación — como lo que escribiste arriba.",
            size=13,
            color=COLOR_TEXTO_MEDIO,
            width=ancho_campo(),
        )
        input_hechos = ft.TextField(
            label="¿Qué pasó, contado solo con hechos?",
            hint_text="Con una frase alcanza.",
            multiline=True,
            min_lines=1,
            max_lines=4,
            width=ancho_campo(),
        )
        # De los 2 pasos de distanciamiento (mirada de un tercero y
        # mirada a un año) alcanza con completar UNO: los dos entrenan lo
        # mismo (tomar distancia del pensamiento) por caminos distintos,
        # y exigir los 4 textos hacía que mucha gente abandonara el
        # ejercicio a mitad de camino. Quien quiera puede completar ambos.
        input_tercero = ft.TextField(
            label="¿Cómo describiría esto alguien de afuera, que conoce los hechos pero no las emociones?",
            hint_text="Completá esta, la de abajo, o las dos",
            multiline=True,
            min_lines=1,
            max_lines=4,
            width=ancho_campo(),
        )
        input_temporal = ft.TextField(
            label="Dentro de un año, ¿cuánto va a pesar esto y cómo se va a ver?",
            hint_text="Completá esta, la de arriba, o las dos",
            multiline=True,
            min_lines=1,
            max_lines=4,
            width=ancho_campo(),
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def guardar(e):
            pensamiento = (input_pensamiento.value or "").strip()
            hechos = (input_hechos.value or "").strip()
            tercero = (input_tercero.value or "").strip()
            temporal = (input_temporal.value or "").strip()

            if not (pensamiento and hechos):
                mostrar_error(texto_error, "Completá los 2 primeros pasos para poder guardar el ejercicio.")
                return
            if len(pensamiento.split()) < 3:
                mostrar_error(texto_error, "En el primer paso, tratá de escribir una frase completa (qué pensarías y qué emoción te trae) — con una sola palabra no hay mucho para trabajar.")
                return
            if not (tercero or temporal):
                mostrar_error(texto_error, "Completá al menos una de las 2 miradas (la de un tercero, o la de dentro de un año).")
                return

            for texto in (pensamiento, hechos, tercero, temporal):
                if texto and detectar_riesgo_suicida(texto):
                    ir_a(mostrar_paso_crisis_1)
                    return
                if texto and detectar_riesgo_terceros(texto):
                    ir_a(mostrar_paso_riesgo_terceros)
                    return

            ejercicio = guardar_ejercicio_reappraisal(
                modo, categoria, situacion_texto, pensamiento, hechos, tercero, temporal, tema_id=tema_id
            )
            if ejercicio is None:
                mostrar_error(texto_error, "No pudimos guardar el ejercicio. Revisá tu conexión e intentá de nuevo.")
                return
            ir_a(mostrar_reappraisal_resultado)

        controles = [
            ft.Text("Practiquemos otra perspectiva", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Text(situacion_texto, color=COLOR_TEXTO_FUERTE, text_align=ft.TextAlign.CENTER),
                padding=15,
                border_radius=12,
                bgcolor=COLOR_CAJA_INFO,
                width=ancho_campo(),
            ),
        ]
        if categoria:
            tecnica = next((c["tecnica"] for c in CATEGORIAS_REAPPRAISAL if c["nombre"] == categoria), None)
            if tecnica:
                controles.append(
                    ft.Text(f"Técnica sugerida: {tecnica}", size=12, color=COLOR_TEXTO_SUAVE, text_align=ft.TextAlign.CENTER)
                )
        controles.extend(
            [
                ft.Text(
                    "No hace falta escribir mucho: con una frase por caja alcanza.",
                    size=12,
                    color=COLOR_TEXTO_SUAVE,
                    text_align=ft.TextAlign.CENTER,
                    width=ancho_campo(),
                ),
                input_pensamiento,
                explicacion_hechos,
                input_hechos,
                input_tercero,
                input_temporal,
                texto_error,
                ft.ElevatedButton("Guardar ejercicio", on_click=guardar, width=ancho_campo(), height=50),
            ]
        )
        pantalla(*controles)

    def mostrar_reappraisal_resultado():
        def volver_al_menu_reappraisal(e):
            historial.clear()
            historial.append(mostrar_menu_principal)
            ir_a(mostrar_reappraisal)

        pantalla(
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=50, color=COLOR_EXITO),
            ft.Text("¡Ejercicio completado!", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Practicar esto seguido ayuda a que te salga más fácil en el momento real.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            *controles_recompensa("✨ Tu colección de enseñanzas creció con este ejercicio."),
            ft.ElevatedButton("Volver", on_click=volver_al_menu_reappraisal, width=ancho_campo(), height=50),
            mostrar_volver=False,
        )

    # ==========================================================
    # "PRACTICÁ CON ESCENARIOS" — pantallas del modo de juego (MENTO)
    # ==========================================================
    def obtener_progreso_juegos_reappraisal():
        if estado["modo_local"]:
            return estado.get("_juegos_reappraisal_locales", [])
        try:
            resp = requests.get(
                SUPABASE_JUEGOS_REAPPRAISAL_URL,
                headers=HEADERS,
                params={"usuario_id": f"eq.{estado['usuario_id']}", "select": "*"},
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase GET progreso_juegos_reappraisal [{resp.status_code}]: {resp.text}")
                return None
            return resp.json()
        except Exception as e:
            print("Error de red (progreso_juegos_reappraisal):", repr(e))
            return None

    def marcar_nivel_juego_completado(categoria, nivel):
        if estado["modo_local"]:
            locales = estado.setdefault("_juegos_reappraisal_locales", [])
            if not any(p["categoria"] == categoria and p["nivel"] == nivel for p in locales):
                locales.append({"categoria": categoria, "nivel": nivel})
            return True
        try:
            resp = requests.post(
                SUPABASE_JUEGOS_REAPPRAISAL_URL,
                headers={**HEADERS, "Prefer": "resolution=ignore-duplicates"},
                params={"on_conflict": "usuario_id,categoria,nivel"},
                json={"usuario_id": estado["usuario_id"], "categoria": categoria, "nivel": nivel},
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase POST progreso_juegos_reappraisal [{resp.status_code}]: {resp.text}")
                return False
            return True
        except Exception as e:
            print("Error de red (guardar progreso juego reappraisal):", repr(e))
            return False

    def mostrar_reappraisal_juegos_categorias():

        tarjetas = []
        for cat in MENTO_CATEGORIAS:
            def elegir(e, clave=cat["clave"]):
                ir_a(lambda: mostrar_reappraisal_juegos_niveles(clave))

            tarjetas.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(cat["icono"], color=ft.Colors.WHITE, size=28),
                            ft.Text(cat["nombre"], color=ft.Colors.WHITE, size=18, weight=ft.FontWeight.BOLD, font_family=MENTO_FUENTE),
                        ],
                        spacing=12,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=18,
                    border_radius=16,
                    bgcolor=cat["color"],
                    width=ancho_campo(),
                    on_click=elegir,
                )
            )
        pantalla(
            ft.Icon(ft.Icons.SPORTS_ESPORTS, size=44, color=MENTO_ROSA_TEXTO),
            ft.Text("Practicá con escenarios", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, font_family=MENTO_FUENTE),
            ft.Text(
                "Elegí un área de tu vida. En cada una hay 5 niveles cortos para entrenar distintas formas de reinterpretar una situación.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            *tarjetas,
        )


    async def precargar_batch_ia():

        if estado.get("_niveles_ia_batch"):
            return

        if estado.get("_batch_ia_generando"):
            return

        estado["_batch_ia_generando"] = True

        try:
            print("Precargando batch IA...")

            niveles = await asyncio.to_thread(
                generar_batch_familia_ia, estado
            )

            estado["_niveles_ia_batch"] = niveles
            estado["_nivel_ia_actual"] = 0

            print(
                f"Batch IA precargado: {len(niveles)} niveles"
            )

        except Exception as e:
            print(
                "Error precargando batch IA:",
                repr(e)
            )

        finally:
            estado["_batch_ia_generando"] = False


    async def precargar_siguiente_batch_ia(historial_5):

        if estado.get("_siguiente_batch_ia"):
            return

        if estado.get("_siguiente_batch_ia_generando"):
            return

        estado["_siguiente_batch_ia_generando"] = True

        try:
            print("Generando próximos 10 niveles en segundo plano...")

            niveles = await asyncio.to_thread(
                generar_batch_familia_ia_adaptativo,
                estado,
                historial_5,
            )

            estado["_siguiente_batch_ia"] = niveles

            print(
                f"Próximo batch IA listo: {len(niveles)} niveles"
            )

        except Exception as e:
            print(
                "Error precargando siguiente batch IA:",
                repr(e)
            )

        finally:
            estado["_siguiente_batch_ia_generando"] = False

    async def mostrar_reappraisal_generando_ia():

        pantalla(
            ft.ProgressRing(),
            ft.Text(
                "Generando 10 nuevos niveles...",
                text_align=ft.TextAlign.CENTER,
            ),
        )

        try:

            if estado.get("_historial_ia"):

                print("Generando batch adaptativo")

                niveles = await asyncio.to_thread(
                    generar_batch_familia_ia_adaptativo,
                    estado["_historial_ia"],
                )

            else:

                print("Generando primer batch")

                niveles = await asyncio.to_thread(
                    generar_batch_familia_ia
                )

            estado["_niveles_ia_batch"] = niveles
            estado["_nivel_ia_actual"] = 0

            print(
                f"Batch generado: {len(niveles)} niveles"
            )

            mostrar_reappraisal_juego_ia(
                "familia",
                0,
            )

        except Exception as e:

            print(
                "Error generando batch IA:",
                repr(e)
            )

            pantalla(
                ft.Icon(
                    ft.Icons.ERROR_OUTLINE,
                    size=50,
                    color=ft.Colors.RED,
                ),
                ft.Text(
                    "No pudimos generar los niveles.",
                    text_align=ft.TextAlign.CENTER,
                ),
            )

    def guardar_resultado_ia(dato):

        correcta = dato["correctas"][0]

        estado["_historial_ia"].append({
            "nombre": dato["nombre"],
            "estrategia": dato["estrategia"],
            "escenario": dato["escenario"],
            "opcion_correcta": dato["opciones"][correcta],
            "errores_elegidos": estado["_errores_nivel_ia"].copy(),
            "tuvo_error": len(estado["_errores_nivel_ia"]) > 0,
        })

    def mostrar_reappraisal_juego_ia(
        categoria_clave,
        indice_nivel,
    ):

        niveles = estado["_niveles_ia_batch"]

        if not niveles:
            return

        dato = niveles[indice_nivel]

        estado["_nivel_ia_actual"] = indice_nivel

        estado["_errores_nivel_ia"] = []

        estado["_intentos_nivel_ia"] = 1

        seleccion = {"valor": None}
        evaluado = {"valor": False}

        def elegir_opcion(i):
            def handler(e):
                if evaluado["valor"]:
                    return

                seleccion["valor"] = i
                renderizar()

            return handler


        def confirmar(e):
            if seleccion["valor"] is None:
                return

            if seleccion["valor"] not in dato["correctas"]:
                estado["_errores_nivel_ia"].append(
                    dato["opciones"][seleccion["valor"]]
                )

            evaluado["valor"] = True
            renderizar()

        def reintentar(e):
            estado["_intentos_nivel_ia"] += 1

            seleccion["valor"] = None
            evaluado["valor"] = False
            renderizar()

        def renderizar():

            opciones_controles = []

            for i, texto in enumerate(dato["opciones"]):

                if evaluado["valor"] and i == seleccion["valor"]:
                    if i in dato["correctas"]:
                        color = MENTO_EXITO_JUEGO
                    else:
                        color = MENTO_ERROR_JUEGO

                elif seleccion["valor"] == i:
                    color = MENTO_SELECCION_JUEGO

                else:
                    color = MENTO_AMARILLO_CLARO

                opciones_controles.append(
                    ft.Container(
                        content=ft.Text(
                            texto,
                            color=ft.Colors.WHITE,
                            text_align=ft.TextAlign.CENTER,
                            font_family=MENTO_FUENTE,
                            size=14,
                        ),
                        padding=14,
                        border_radius=14,
                        bgcolor=color,
                        width=ancho_campo(),
                        on_click=elegir_opcion(i),
                    )
                )

            controles = [
                ft.Text(
                    f"✨ NIVEL IA {indice_nivel + 1} / {len(niveles)}",
                    weight=ft.FontWeight.BOLD,
                    color=MENTO_ROSA_TEXTO,
                    font_family=MENTO_FUENTE,
                ),

                ft.Text(
                    dato["nombre"],
                    size=20,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                    font_family=MENTO_FUENTE,
                ),

                ft.Text(
                    dato["estrategia"],
                    size=13,
                    color=COLOR_TEXTO_SUAVE,
                    text_align=ft.TextAlign.CENTER,
                ),

                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                texto,
                                text_align=ft.TextAlign.CENTER,
                                color=COLOR_TEXTO_FUERTE,
                            )
                            for texto in dato["escenario"]
                        ],
                        spacing=6,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=MENTO_AMARILLO,
                    width=ancho_campo(),
                ),

                ft.Text(
                    "¿Cuál es la reinterpretación más adecuada?",
                    text_align=ft.TextAlign.CENTER,
                    color=COLOR_TEXTO_MEDIO,
                ),

                *opciones_controles,
            ]

            if evaluado["valor"]:

                if seleccion["valor"] in dato["correctas"]:

                    controles.append(
                        ft.Container(
                            content=ft.Text(
                                dato["mensaje_exito"],
                                color=ft.Colors.WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            padding=14,
                            border_radius=14,
                            bgcolor=MENTO_EXITO_JUEGO,
                            width=ancho_campo(),
                        )
                    )
                        
                    hay_siguiente = indice_nivel + 1 < len(niveles)

                    if hay_siguiente:

                        def siguiente_nivel(e):

                            guardar_resultado_ia(dato)

                            # Cuando termina el ejercicio 5,
                            # generar los próximos 10 usando SOLO esos 5 resultados
                            if indice_nivel == 4:

                                historial_5 = estado["_historial_ia"][-5:].copy()

                                page.run_task(
                                    precargar_siguiente_batch_ia,
                                    historial_5,
                                )

                            mostrar_reappraisal_juego_ia(
                                categoria_clave,
                                indice_nivel + 1,
                            )

                        controles.append(
                            ft.ElevatedButton(
                                f"Siguiente nivel IA ({indice_nivel + 2}/{len(niveles)})",
                                icon=ft.Icons.ARROW_FORWARD,
                                on_click=siguiente_nivel,
                                width=ancho_campo(),
                                bgcolor=MENTO_VERDE_OSCURO,
                                color=ft.Colors.WHITE,
                            )
                        )

                    else:

                        controles.append(
                            ft.Container(
                                content=ft.Text(
                                    f"🎉 Completaste los {len(niveles)} niveles IA",
                                    color=ft.Colors.WHITE,
                                    text_align=ft.TextAlign.CENTER,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                padding=14,
                                border_radius=14,
                                bgcolor=MENTO_EXITO_JUEGO,
                                width=ancho_campo(),
                            )
                        )

                        async def continuar_siguiente_batch(e):

                            guardar_resultado_ia(dato)

                            # Si los próximos 10 ya están listos
                            if estado.get("_siguiente_batch_ia"):

                                estado["_niveles_ia_batch"] = estado["_siguiente_batch_ia"]
                                estado["_siguiente_batch_ia"] = []
                                estado["_nivel_ia_actual"] = 0

                                mostrar_reappraisal_juego_ia(
                                    categoria_clave,
                                    0,
                                )
                                return

                            # Si todavía se están generando, esperamos
                            pantalla(
                                ft.ProgressRing(),
                                ft.Text(
                                    "Preparando los próximos niveles...",
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            )

                            while estado.get("_siguiente_batch_ia_generando"):
                                await asyncio.sleep(0.2)

                            if estado.get("_siguiente_batch_ia"):

                                estado["_niveles_ia_batch"] = estado["_siguiente_batch_ia"]
                                estado["_siguiente_batch_ia"] = []
                                estado["_nivel_ia_actual"] = 0

                                mostrar_reappraisal_juego_ia(
                                    categoria_clave,
                                    0,
                                )

                            else:
                                pantalla(
                                    ft.Icon(
                                        ft.Icons.ERROR_OUTLINE,
                                        size=50,
                                        color=ft.Colors.RED,
                                    ),
                                    ft.Text(
                                        "No pudimos preparar los próximos niveles.",
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                )

                        controles.append(
                            ft.ElevatedButton(
                                content="Continuar con otros 10 niveles",
                                icon=ft.Icons.ARROW_FORWARD,
                                on_click=continuar_siguiente_batch,
                                width=ancho_campo(),
                                bgcolor=MENTO_VERDE_OSCURO,
                                color=ft.Colors.WHITE,
                            )
                        )

                                
                    def volver_a_niveles(e):
                        ir_a(
                            lambda: mostrar_reappraisal_juegos_niveles(
                                categoria_clave
                            )
                        )

                    controles.append(
                        ft.OutlinedButton(
                            "Volver a los niveles",
                            on_click=volver_a_niveles,
                            width=ancho_campo(),
                        )
                    )

                else:

                    controles.append(
                        ft.Container(
                            content=ft.Text(
                                dato["mensaje_error"],
                                color=ft.Colors.WHITE,
                                text_align=ft.TextAlign.CENTER,
                            ),
                            padding=14,
                            border_radius=14,
                            bgcolor=MENTO_ERROR_JUEGO,
                            width=ancho_campo(),
                        )
                    )

                    controles.append(
                        ft.ElevatedButton(
                            "Volver a intentar",
                            on_click=reintentar,
                            width=ancho_campo(),
                        )
                    )

            else:

                controles.append(
                    ft.ElevatedButton(
                        "Confirmar",
                        on_click=confirmar,
                        width=ancho_campo(),
                        disabled=seleccion["valor"] is None,
                    )
                )

            pantalla(*controles)

        renderizar()
        
    def mostrar_reappraisal_juegos_niveles(categoria_clave):
        cat = next(c for c in MENTO_CATEGORIAS if c["clave"] == categoria_clave)
        niveles = MENTO_NIVELES[categoria_clave]

        progreso = obtener_progreso_juegos_reappraisal()
        if progreso is None:
            pantalla(
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED),
                ft.Text("No pudimos cargar tu progreso. Revisá tu conexión e intentá de nuevo.", text_align=ft.TextAlign.CENTER),
            )
            return
        completados = {p["nivel"] for p in progreso if p.get("categoria") == categoria_clave}

        filas = []
        for i, nivel_data in enumerate(niveles):
            nivel = i + 1
            desbloqueado = nivel == 1 or (nivel - 1) in completados
            completado = nivel in completados
            icono = ft.Icons.STAR if completado else (ft.Icons.STAR_BORDER if desbloqueado else ft.Icons.LOCK)

            def abrir(e, nivel=nivel, desbloqueado=desbloqueado):
                if not desbloqueado:
                    return
                ir_a(lambda: mostrar_reappraisal_juego_nivel(categoria_clave, nivel))

            filas.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Text(str(nivel), color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=18, font_family=MENTO_FUENTE),
                                width=44,
                                height=44,
                                border_radius=22,
                                bgcolor=cat["color"] if desbloqueado else COLOR_TEXTO_SUAVE,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        nivel_data["nombre"],
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_TEXTO_FUERTE if desbloqueado else COLOR_TEXTO_SUAVE,
                                        font_family=MENTO_FUENTE,
                                    ),
                                    ft.Text(nivel_data["estrategia"], size=12, color=COLOR_TEXTO_SUAVE),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Icon(icono, color=MENTO_AMARILLO if completado else COLOR_TEXTO_SUAVE, size=26),
                        ],
                        alignment=ft.MainAxisAlignment.START,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    padding=12,
                    border_radius=14,
                    bgcolor=COLOR_CAJA_SUAVE if desbloqueado else ft.Colors.with_opacity(0.5, COLOR_CAJA_SUAVE),
                    width=ancho_campo(),
                    on_click=abrir,
                )
            )

        if categoria_clave == "familia":


            async def abrir_nivel_ia(e):

                # Si ya están listos, abrir
                if estado.get("_niveles_ia_batch"):
                    mostrar_reappraisal_juego_ia(
                        "familia",
                        0,
                    )
                    return

                # Si todavía se están generando desde el login, esperar
                pantalla(
                    ft.ProgressRing(),
                    ft.Text(
                        "Preparando tus niveles...",
                        text_align=ft.TextAlign.CENTER,
                    ),
                )

                while estado.get("_batch_ia_generando"):
                    await asyncio.sleep(0.2)

                # Cuando terminó la precarga
                if estado.get("_niveles_ia_batch"):
                    mostrar_reappraisal_juego_ia(
                        "familia",
                        0,
                    )
                else:
                    await mostrar_reappraisal_generando_ia()

            filas.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.AUTO_AWESOME,
                                color=ft.Colors.WHITE,
                                size=26,
                            ),
                            ft.Text(
                                "Nivel IA",
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                                font_family=MENTO_FUENTE,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    padding=16,
                    border_radius=14,
                    bgcolor=MENTO_ROSA_TEXTO,
                    width=ancho_campo(),
                    on_click=abrir_nivel_ia,
                )
            )

            pantalla(
                ft.Icon(cat["icono"], size=44, color=cat["color"]),
                ft.Text(cat["nombre"], size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, font_family=MENTO_FUENTE),
                ft.Text(f"{len(completados)} de {len(niveles)} niveles completados.", color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
                *filas,
            )

    def mostrar_reappraisal_juego_nivel(categoria_clave, nivel):
        cat = next(c for c in MENTO_CATEGORIAS if c["clave"] == categoria_clave)
        dato = MENTO_NIVELES[categoria_clave][nivel - 1]

        estado_juego = {
            "seleccion": None,
            "evaluado": False,
            "mostrar_info": False,
            "hechos": set(),
            "sel_neg": None,
            "sel_pos": None,
            "mensaje_error_par": None,
        }

        def alternar_info(e):
            estado_juego["mostrar_info"] = not estado_juego["mostrar_info"]
            renderizar()

        def encabezado():
            controles = [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Text(f"NIVEL {nivel}", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=13, font_family=MENTO_FUENTE),
                            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
                            border_radius=20,
                            bgcolor=cat["color"],
                        ),
                        ft.IconButton(
                            icon=ft.Icons.HELP_OUTLINE,
                            tooltip="¿Qué estrategia usa este nivel?",
                            icon_color=MENTO_ROSA_TEXTO,
                            on_click=alternar_info,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    width=ancho_campo(),
                ),
                ft.Text(dato["nombre"], size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, font_family=MENTO_FUENTE, color=MENTO_ROSA_TEXTO),
                ft.Text(dato["estrategia"], size=13, color=COLOR_TEXTO_SUAVE, text_align=ft.TextAlign.CENTER),
            ]
            if estado_juego["mostrar_info"]:
                controles.append(
                    ft.Container(
                        content=ft.Text(MENTO_EXPLICACIONES.get(dato["estrategia"], ""), size=13, color=MENTO_ROSA_TEXTO, text_align=ft.TextAlign.CENTER),
                        padding=14,
                        border_radius=12,
                        bgcolor=MENTO_ROSA,
                        width=ancho_campo(),
                    )
                )
            controles.append(
                ft.Container(
                    content=ft.Column(
                        [ft.Text(p, color=COLOR_TEXTO_FUERTE, text_align=ft.TextAlign.CENTER) for p in dato["escenario"]],
                        spacing=6,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=cat["color"],
                    width=ancho_campo(),
                )
            )
            return controles

        def renderizar():
            if dato["tipo"] == "opcion_multiple":
                renderizar_opcion_multiple()
            else:
                renderizar_emparejar()

        def renderizar_opcion_multiple():
            seleccion = estado_juego["seleccion"]
            evaluado = estado_juego["evaluado"]
            correcta = evaluado and seleccion in dato["correctas"]
            incorrecta = evaluado and seleccion is not None and not correcta

            opciones_controles = []
            for i, texto in enumerate(dato["opciones"]):
                if evaluado and i == seleccion:
                    bg = MENTO_EXITO_JUEGO if correcta else MENTO_ERROR_JUEGO
                elif seleccion == i:
                    bg = MENTO_SELECCION_JUEGO
                else:
                    bg = MENTO_AMARILLO_CLARO

                def elegir(e, i=i):
                    if estado_juego["evaluado"]:
                        return
                    estado_juego["seleccion"] = i
                    renderizar()

                opciones_controles.append(
                    ft.Container(
                        content=ft.Text(texto, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER, font_family=MENTO_FUENTE, size=14),
                        padding=14,
                        border_radius=14,
                        bgcolor=bg,
                        width=ancho_campo(),
                        on_click=elegir,
                        opacity=1 if (not evaluado or i == seleccion) else 0.5,
                    )
                )

            controles = encabezado()
            controles.append(
                ft.Text(
                    "¿Cuál es la opción que representa la forma más constructiva de pensar sobre esto?",
                    size=14,
                    color=COLOR_TEXTO_MEDIO,
                    text_align=ft.TextAlign.CENTER,
                )
            )
            controles.extend(opciones_controles)

            if incorrecta:
                mensaje = dato.get("mensajes_error_opcion", {}).get(seleccion, dato["mensaje_error"])
                controles.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("¡Casi!", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER, font_family=MENTO_FUENTE),
                                ft.Text(mensaje, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER, size=13),
                            ],
                            spacing=6,
                        ),
                        padding=14,
                        border_radius=14,
                        bgcolor=MENTO_ERROR_JUEGO,
                        width=ancho_campo(),
                    )
                )

                def reintentar(e):
                    estado_juego["seleccion"] = None
                    estado_juego["evaluado"] = False
                    renderizar()

                controles.append(
                    ft.ElevatedButton("Volver a intentar", on_click=reintentar, width=ancho_campo(), height=46, bgcolor=MENTO_VERDE_OSCURO, color=ft.Colors.WHITE)
                )
            elif correcta:
                controles.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("¡Muy bien!", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER, font_family=MENTO_FUENTE),
                                ft.Text(dato["mensaje_exito"], color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER, size=13),
                            ],
                            spacing=6,
                        ),
                        padding=14,
                        border_radius=14,
                        bgcolor=MENTO_EXITO_JUEGO,
                        width=ancho_campo(),
                    )
                )

                def continuar(e):
                    marcar_nivel_juego_completado(categoria_clave, nivel)
                    ir_a(lambda: mostrar_reappraisal_juego_completado(categoria_clave, nivel))

                controles.append(
                    ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=46, bgcolor=MENTO_VERDE_OSCURO, color=ft.Colors.WHITE)
                )
            else:
                def confirmar(e):
                    if estado_juego["seleccion"] is None:
                        return
                    estado_juego["evaluado"] = True
                    renderizar()

                controles.append(
                    ft.ElevatedButton(
                        "Confirmar",
                        on_click=confirmar,
                        width=ancho_campo(),
                        height=46,
                        bgcolor=MENTO_VERDE_OSCURO,
                        color=ft.Colors.WHITE,
                        disabled=seleccion is None,
                    )
                )

            pantalla(*controles)

        def renderizar_emparejar():
            pendientes_neg = [i for i in range(len(dato["negativos"])) if not any(p[0] == i for p in estado_juego["hechos"])]
            pendientes_pos = [i for i in range(len(dato["positivos"])) if not any(p[1] == i for p in estado_juego["hechos"])]

            def estilo(lado, i):
                sel = estado_juego["sel_neg"] if lado == "neg" else estado_juego["sel_pos"]
                if sel == i:
                    return MENTO_SELECCION_JUEGO
                return MENTO_ERROR_JUEGO if lado == "neg" else MENTO_VERDE_OSCURO

            def elegir_neg(e, i):
                estado_juego["sel_neg"] = None if estado_juego["sel_neg"] == i else i
                estado_juego["mensaje_error_par"] = None
                renderizar()

            def elegir_pos(e, i):
                if estado_juego["sel_neg"] is None:
                    return
                estado_juego["sel_pos"] = None if estado_juego["sel_pos"] == i else i
                estado_juego["mensaje_error_par"] = None
                renderizar()

            columna_neg = ft.Column(
                [ft.Text("Pensamiento negativo", size=13, weight=ft.FontWeight.BOLD, color=MENTO_ERROR_JUEGO, font_family=MENTO_FUENTE)]
                + [
                    ft.Container(
                        content=ft.Text(dato["negativos"][i], color=ft.Colors.WHITE, size=12, text_align=ft.TextAlign.CENTER, font_family=MENTO_FUENTE),
                        padding=10,
                        border_radius=12,
                        bgcolor=estilo("neg", i),
                        on_click=lambda e, i=i: elegir_neg(e, i),
                        width=140,
                    )
                    for i in pendientes_neg
                ],
                spacing=8,
            )
            columna_pos = ft.Column(
                [ft.Text("Reinterpretación positiva", size=13, weight=ft.FontWeight.BOLD, color=MENTO_VERDE_OSCURO, font_family=MENTO_FUENTE)]
                + [
                    ft.Container(
                        content=ft.Text(dato["positivos"][i], color=ft.Colors.WHITE, size=12, text_align=ft.TextAlign.CENTER, font_family=MENTO_FUENTE),
                        padding=10,
                        border_radius=12,
                        bgcolor=estilo("pos", i),
                        on_click=lambda e, i=i: elegir_pos(e, i),
                        width=140,
                    )
                    for i in pendientes_pos
                ],
                spacing=8,
            )

            controles = encabezado()
            controles.append(
                ft.Text(
                    "Uní cada pensamiento negativo con la reinterpretación que le corresponde.",
                    size=14,
                    color=COLOR_TEXTO_MEDIO,
                    text_align=ft.TextAlign.CENTER,
                )
            )
            controles.append(
                ft.Row([columna_neg, columna_pos], alignment=ft.MainAxisAlignment.CENTER, spacing=16, vertical_alignment=ft.CrossAxisAlignment.START)
            )

            if estado_juego["mensaje_error_par"]:
                controles.append(
                    ft.Container(
                        content=ft.Text(estado_juego["mensaje_error_par"], color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER, size=13),
                        padding=12,
                        border_radius=12,
                        bgcolor=MENTO_ERROR_JUEGO,
                        width=ancho_campo(),
                    )
                )

            if not pendientes_neg:
                controles.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("¡Muy bien!", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER, font_family=MENTO_FUENTE),
                                ft.Text(dato["mensaje_exito"], color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER, size=13),
                            ],
                            spacing=6,
                        ),
                        padding=14,
                        border_radius=14,
                        bgcolor=MENTO_EXITO_JUEGO,
                        width=ancho_campo(),
                    )
                )

                def continuar(e):
                    marcar_nivel_juego_completado(categoria_clave, nivel)
                    ir_a(lambda: mostrar_reappraisal_juego_completado(categoria_clave, nivel))

                controles.append(
                    ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=46, bgcolor=MENTO_VERDE_OSCURO, color=ft.Colors.WHITE)
                )
            else:
                def confirmar_par(e):
                    sn, sp = estado_juego["sel_neg"], estado_juego["sel_pos"]
                    if sn is None or sp is None:
                        return
                    if (sn, sp) in dato["pares_correctos"]:
                        estado_juego["hechos"].add((sn, sp))
                        estado_juego["sel_neg"] = None
                        estado_juego["sel_pos"] = None
                        estado_juego["mensaje_error_par"] = None
                    else:
                        estado_juego["mensaje_error_par"] = dato["mensaje_error"]
                        estado_juego["sel_neg"] = None
                        estado_juego["sel_pos"] = None
                    renderizar()

                controles.append(
                    ft.ElevatedButton(
                        "Emparejar",
                        on_click=confirmar_par,
                        width=ancho_campo(),
                        height=46,
                        bgcolor=MENTO_VERDE_OSCURO,
                        color=ft.Colors.WHITE,
                        disabled=estado_juego["sel_neg"] is None or estado_juego["sel_pos"] is None,
                    )
                )

            pantalla(*controles)

        renderizar()

    def mostrar_reappraisal_juego_completado(categoria_clave, nivel):
        cat = next(c for c in MENTO_CATEGORIAS if c["clave"] == categoria_clave)
        niveles = MENTO_NIVELES[categoria_clave]
        hay_siguiente = nivel < len(niveles)

        def volver_a_niveles(e):
            historial.clear()
            historial.append(mostrar_menu_principal)
            ir_a(lambda: mostrar_reappraisal_juegos_niveles(categoria_clave))

        def siguiente_nivel(e):
            ir_a(
                lambda: mostrar_reappraisal_juego_nivel(
                    categoria_clave,
                    nivel + 1
                )
            )

        controles = [
            ft.Icon(ft.Icons.STAR, size=60, color=MENTO_AMARILLO),
            ft.Text("¡Nivel completado!", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER, font_family=MENTO_FUENTE),
            ft.Text(
                "Practicar esto seguido ayuda a que te salga más fácil reinterpretar situaciones reales.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            *controles_recompensa("✨ Tu colección de enseñanzas creció con este ejercicio."),
        ]
        if hay_siguiente:
            controles.append(
                ft.ElevatedButton(
                    f"Siguiente nivel ({nivel + 1})", on_click=siguiente_nivel, width=ancho_campo(), height=50, bgcolor=cat["color"], color=ft.Colors.WHITE
                )
            )
        controles.append(ft.OutlinedButton("Volver a los niveles", on_click=volver_a_niveles, width=ancho_campo(), height=50))
        pantalla(*controles, mostrar_volver=False)

    # ==========================================================
    # NUEVO REPORTE — flujo guiado de reestructuración cognitiva (CBT)
    # ----------------------------------------------------------
    # Si viene de "retomar" un tema (pensamiento recurrente guardado), se
    # precarga el pensamiento automático con el título de ese tema, y el
    # reporte que resulte queda vinculado a él (tema_id) para poder
    # seguir su evolución con el tiempo. También se trae la sesión
    # anterior de ese mismo tema (siempre existe al menos una, porque un
    # tema se crea recién después de completar un primer reporte): no
    # tiene sentido volver a preguntar todo desde cero como si fuera la
    # primera vez, así que el resto del flujo usa "_anterior" para
    # orientar las preguntas hacia qué cambió desde la última vez.
    # ==========================================================
    def _iniciar_reporte_desde_cero(tema=None):
        estado["reporte_actual"] = {}
        if tema is not None:
            estado["reporte_actual"]["tema_id"] = tema["id"]
            estado["reporte_actual"]["tema_obj"] = tema
            estado["reporte_actual"]["pensamiento_automatico"] = tema.get("titulo", "")
            reportes_previos = obtener_reportes_de_tema(tema["id"]) or []
            if reportes_previos:
                anterior = max(reportes_previos, key=lambda x: x.get("fecha") or "")
                estado["reporte_actual"]["_anterior"] = anterior
                # El tipo de situación y la emoción ya se sabían de la
                # vez pasada — no tiene sentido volver a preguntarlos
                # desde cero cada vez que se retoma el mismo tema (Paso
                # 1 usa esto para bloquear el tipo y precargar la
                # emoción en vez de mostrar los desplegables vacíos).
                if anterior.get("tipo_situacion"):
                    estado["reporte_actual"]["tipo_situacion"] = anterior["tipo_situacion"]
                if anterior.get("emocion_inicial"):
                    estado["reporte_actual"]["emocion_inicial"] = anterior["emocion_inicial"]
                    estado["reporte_actual"]["_emocion_es_otra"] = anterior["emocion_inicial"] not in EMOCIONES
        ir_a(mostrar_paso_situacion)

    async def iniciar_nuevo_reporte(tema=None):
        # Si la conexión se cortó a mitad de un reporte anterior, queda
        # un borrador guardado en el navegador (ver _guardar_borrador).
        # Antes de arrancar de cero, se ofrece retomarlo — así no se
        # pierde lo que la persona ya había escrito.
        borrador = None
        try:
            borrador_texto = await page.shared_preferences.get(_clave_borrador())
            if borrador_texto:
                borrador = json.loads(borrador_texto)

        except Exception as e:
            print("ERROR COMPLETO:", repr(e))

            pantalla(
                ft.Icon(
                    ft.Icons.ERROR_OUTLINE,
                    size=50,
                    color=ft.Colors.RED,
                ),
                ft.Text(
                    f"ERROR: {repr(e)}",
                    text_align=ft.TextAlign.CENTER,
                ),
            )

        if borrador:
            ir_a(lambda: mostrar_paso_confirmar_borrador(borrador, tema))
            return

        _iniciar_reporte_desde_cero(tema)

    def mostrar_paso_confirmar_borrador(borrador, tema=None):
        def continuar_borrador(e):
            estado["reporte_actual"] = borrador
            ir_a(mostrar_paso_situacion)

        def empezar_de_nuevo(e):
            _iniciar_reporte_desde_cero(tema)

        pantalla(
            ft.Icon(ft.Icons.HISTORY_EDU, size=40, color=COLOR_PRIMARIO),
            ft.Text("Tenés un reporte sin terminar", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Parece que la conexión se cortó a mitad de un reporte. ¿Querés seguir donde lo dejaste, o empezar de nuevo?",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.ElevatedButton("Seguir donde lo dejé", on_click=continuar_borrador, width=ancho_campo(), height=50),
            ft.OutlinedButton("Empezar de nuevo", on_click=empezar_de_nuevo, width=ancho_campo(), height=50),
            mostrar_volver=False,
        )

    def mostrar_paso_situacion():
        r = estado["reporte_actual"]
        anterior = r.get("_anterior")
        # Si se está retomando un tema ya categorizado, el tipo de
        # situación no tiene sentido volver a preguntarlo — es del
        # mismo pensamiento/tema de siempre (a diferencia de la
        # emoción, que sí puede variar de una vez a otra). Se bloquea
        # en vez de mostrarlo como un desplegable vacío que obligue a
        # elegir de nuevo.
        tipo_bloqueado = r.get("tipo_situacion") if (r.get("tema_obj") and anterior) else None
        input_situacion = ft.TextField(
            label="Contame qué te está pasando",
            hint_text="Escribilo con tus palabras, como te salga, no hace falta que sea prolijo",
            value=r.get("situacion", ""),
            width=ancho_campo(),
            multiline=True,
            min_lines=3,
            max_lines=6,
        )
        if tipo_bloqueado:
            dropdown_tipo = None
            control_tipo = ft.Container(
                content=ft.Text(
                    f"Tipo de situación: {tipo_bloqueado}",
                    size=14,
                    color=COLOR_TEXTO_MEDIO,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=8,
            )
        else:
            dropdown_tipo = ft.Dropdown(
                label="¿Qué tipo de situación es esta?",
                options=[ft.dropdown.Option(op) for op in TIPOS_SITUACION],
                value=r.get("tipo_situacion"),
                width=ancho_campo(),
            )
            control_tipo = dropdown_tipo
        # Si elige "Otra" en emoción, se abre una caja para que la
        # nombre — de lo contrario la opción no serviría de nada (ver
        # feedback de Gabriel: toda opción "Otra/Otra situación" tiene
        # que dar lugar a detallarla). "Otra situación" en el dropdown de
        # arriba no necesita una caja aparte porque el campo "Contame qué
        # te está pasando" ya cumple ese rol (se pregunta siempre, antes
        # de elegir el tipo).
        input_emocion_otra = ft.TextField(
            label="¿Qué emoción sentís?",
            hint_text="Contala con tus palabras",
            value=r.get("emocion_inicial") if r.get("_emocion_es_otra") else "",
            visible=bool(r.get("_emocion_es_otra")),
            width=ancho_campo(),
        )

        def on_change_emocion(e):
            input_emocion_otra.visible = dropdown_emocion.value == "Otra"
            page.update()

        dropdown_emocion = ft.Dropdown(
            label="¿Qué es lo que más sentís ahora?",
            options=[ft.dropdown.Option(op) for op in EMOCIONES],
            value="Otra" if r.get("_emocion_es_otra") else r.get("emocion_inicial"),
            width=ancho_campo(),
            on_select=on_change_emocion,
        )
        texto_intensidad = ft.Text(f"¿Con qué intensidad lo sentís?: {r.get('intensidad_inicial', 5)}/10")
        slider_intensidad = ft.Slider(
            min=0, max=10, divisions=10, value=r.get("intensidad_inicial", 5),
            width=ancho_campo(),
            on_change=lambda e: (texto_intensidad.__setattr__("value", f"¿Con qué intensidad lo sentís?: {int(e.control.value)}/10"), page.update()),
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        # Solo tiene sentido preguntar esto si hubo una vez anterior (y
        # por lo tanto ya se le mostraron recomendaciones): cierra el
        # círculo de la activación conductual, que es justamente probar
        # la sugerencia, no solo leerla.
        input_feedback_recomendacion = None
        input_feedback_porque = None
        if anterior:
            input_feedback_porque = ft.TextField(
                label="¿Por qué creés que te funcionó (o no)?",
                hint_text="Lo que se te ocurra, no hace falta que sea elaborado",
                width=ancho_campo(),
                multiline=True,
                min_lines=2,
                max_lines=4,
                visible=False,
            )

            def on_change_feedback(e):
                input_feedback_porque.visible = bool((input_feedback_recomendacion.value or "").strip())
                page.update()

            input_feedback_recomendacion = ft.TextField(
                label="¿Llegaste a probar alguna sugerencia de la vez pasada? ¿Te sirvió?",
                hint_text="No hace falta responder esto si no llegaste a probar nada",
                width=ancho_campo(),
                multiline=True,
                min_lines=2,
                max_lines=4,
                on_change=on_change_feedback,
            )

        def continuar(e):
            situacion = (input_situacion.value or "").strip()
            feedback = (input_feedback_recomendacion.value or "").strip() if input_feedback_recomendacion else ""
            feedback_porque = (input_feedback_porque.value or "").strip() if input_feedback_porque else ""
            emocion_otra_detalle = (input_emocion_otra.value or "").strip()
            if not situacion:
                mostrar_error(texto_error, "Contame aunque sea brevemente qué te está pasando.")
                return
            if detectar_riesgo_suicida(situacion, feedback, feedback_porque, emocion_otra_detalle):
                r["situacion"] = situacion
                if input_feedback_recomendacion:
                    r["feedback_recomendacion_anterior"] = feedback
                    r["feedback_recomendacion_porque"] = feedback_porque
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(situacion, feedback, feedback_porque, emocion_otra_detalle):
                r["situacion"] = situacion
                if input_feedback_recomendacion:
                    r["feedback_recomendacion_anterior"] = feedback
                    r["feedback_recomendacion_porque"] = feedback_porque
                ir_a(mostrar_paso_riesgo_terceros)
                return
            tipo_valor = tipo_bloqueado or (dropdown_tipo.value if dropdown_tipo else None)
            if not tipo_valor:
                mostrar_error(texto_error, "Elegí qué tipo de situación es, así te hago las preguntas más indicadas.")
                return
            if not dropdown_emocion.value:
                mostrar_error(texto_error, "Elegí la emoción que más sentís.")
                return
            if dropdown_emocion.value == "Otra" and not emocion_otra_detalle:
                mostrar_error(texto_error, "Contanos qué emoción sentís.")
                return
            r["situacion"] = situacion
            if input_feedback_recomendacion:
                r["feedback_recomendacion_anterior"] = feedback
                r["feedback_recomendacion_porque"] = feedback_porque
            r["tipo_situacion"] = tipo_valor
            r["_emocion_es_otra"] = dropdown_emocion.value == "Otra"
            r["emocion_inicial"] = emocion_otra_detalle if dropdown_emocion.value == "Otra" else dropdown_emocion.value
            r["intensidad_inicial"] = int(slider_intensidad.value)

            # Si eligió "Otra situación", puede ser que en realidad
            # describa algo que ya tratamos de forma más específica (sin
            # saberlo, o sin reconocerse en las opciones) — si hay
            # coincidencia, se redirige directo a esas preguntas (ver
            # mostrar_paso_sugerencia_tipo). Solo sigue con las genéricas
            # si no se pudo categorizar. No aplica si el tipo ya está
            # bloqueado (ya sabemos de qué se trata, no hace falta
            # volver a detectarlo).
            if not tipo_bloqueado and tipo_valor == "Otra situación":
                tipo_sugerido = detectar_tipo_sugerido(situacion)
                if tipo_sugerido:
                    ir_a(lambda: mostrar_paso_sugerencia_tipo(tipo_sugerido))
                    return

            ir_a(mostrar_paso_pensamiento)

        controles_paso1 = [
            ft.Text("Paso 1 de 4", size=14, color=COLOR_TEXTO_SUAVE),
        ]
        if r.get("tema_obj"):
            controles_paso1.append(
                ft.Text(
                    f"Estás retomando: \"{r['tema_obj'].get('titulo', '')}\"",
                    size=13,
                    color=COLOR_PRIMARIO_OSCURO,
                    text_align=ft.TextAlign.CENTER,
                )
            )
        if anterior:
            fecha_ant = (anterior.get("fecha") or "")[:10]
            if anterior.get("tipo_situacion") == TIPO_OBSESION:
                texto_anterior = (
                    f"La última vez ({fecha_ant}) esto te generó {anterior.get('emocion_inicial', '')} "
                    f"({anterior.get('intensidad_inicial', '')}/10), y el impulso te quedó en un {anterior.get('creencia_final_pct', '')}%. "
                    f"El impulso que habías identificado era: \"{anterior.get('evidencia_a_favor', '')}\". Contame qué pasó esta vez."
                )
            else:
                texto_anterior = (
                    f"La última vez ({fecha_ant}) esto te generó {anterior.get('emocion_inicial', '')} "
                    f"({anterior.get('intensidad_inicial', '')}/10), y terminaste con una creencia del {anterior.get('creencia_final_pct', '')}% "
                    f"en el pensamiento. Contame qué pasó esta vez."
                )
            controles_paso1.append(
                ft.Container(
                    content=ft.Text(
                        texto_anterior,
                        size=12,
                        color=COLOR_TEXTO_MEDIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=COLOR_CAJA_INFO,
                    width=ancho_campo(),
                )
            )
        if input_feedback_recomendacion:
            controles_paso1.append(input_feedback_recomendacion)
            controles_paso1.append(input_feedback_porque)
        controles_paso1.extend([
            ft.Text("Contame qué te está pasando" if not anterior else "¿Qué pasó esta vez?", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            control_tipo,
            input_situacion,
            dropdown_emocion,
            input_emocion_otra,
            texto_intensidad,
            slider_intensidad,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
        ])

        pantalla(*controles_paso1)

    def mostrar_paso_sugerencia_tipo(tipo_sugerido):
        # Si detectamos una coincidencia, se redirige directo (sin
        # ofrecer volver a las preguntas generales) — solo se avisa,
        # para que no sea una sorpresa que las preguntas cambien. La
        # descripción es siempre en criollo, sin nombrar ningún
        # diagnóstico. Si no se llega a categorizar bien, ni se pasa por
        # acá: sigue directo con las preguntas generales.
        r = estado["reporte_actual"]
        r["tipo_situacion"] = tipo_sugerido
        descripcion = DESCRIPCION_TIPO_SUGERIDO.get(tipo_sugerido, "")

        def continuar(e):
            ir_a(mostrar_paso_pensamiento)

        pantalla(
            ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=40, color=COLOR_DORADO),
            ft.Text("Una idea antes de seguir", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                f"Por lo que contás, {descripcion}. Vamos a seguir con preguntas pensadas especialmente para esto.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
            mostrar_volver=False,
        )

    def mostrar_paso_pensamiento():
        r = estado["reporte_actual"]
        es_hecho = r.get("tipo_situacion") in TIPOS_HECHO_CONSUMADO
        es_obsesion = r.get("tipo_situacion") == TIPO_OBSESION
        anterior = r.get("_anterior")

        # El hint "esto va a salir mal / soy un desastre" (pensamientos
        # que anticipan o interpretan algo) no encaja cuando la persona
        # ya está frente a un hecho consumado (una muerte, un
        # diagnóstico), ni cuando es un pensamiento repetitivo tipo TOC
        # (ahí suele ser más una duda o imagen intrusiva que una
        # predicción puntual). Se adapta en cada caso.
        if es_obsesion:
            hint_pensamiento = "Ej: \"me voy a contaminar\", \"le puedo hacer daño a alguien sin querer\", \"si no reviso, va a pasar algo malo\"..."
        elif es_hecho:
            hint_pensamiento = "Ej: \"nunca más voy a poder hablar con él/ella\", \"podría haber hecho algo distinto\"..."
        else:
            hint_pensamiento = "Ej: \"esto va a salir mal\", \"soy un desastre\"..."

        # Si es una segunda vez con este mismo pensamiento, no tiene
        # sentido preguntar todo desde cero: se orienta la pregunta hacia
        # si volvió igual o cambió, y la creencia se ancla a cómo había
        # quedado la última vez en vez de arrancar de un valor genérico.
        if anterior:
            label_pensamiento = "¿Volvió la misma idea/dudas, o cambió un poco esta vez?" if es_obsesion else "¿Volvió el mismo pensamiento, o cambió un poco esta vez?"
        elif es_obsesion:
            label_pensamiento = "Contame qué pensamiento, imagen o duda se te repite"
        else:
            label_pensamiento = "Ahora tratá de recordar: ¿qué pensamiento te pasó por la cabeza?"

        if anterior:
            if es_obsesion:
                texto_pct_anterior = f"La última vez el impulso te quedó en un {anterior.get('creencia_final_pct', 0)}%."
                label_creencia = f"{texto_pct_anterior} ¿Qué tan fuerte lo sentís ahora, de entrada?"
            else:
                texto_pct_anterior = f"La última vez terminaste con un {anterior.get('creencia_final_pct', 0)}%."
                label_creencia = f"{texto_pct_anterior} ¿Cuánto lo creés ahora, de entrada?"
        elif es_obsesion:
            label_creencia = "¿Qué tan fuerte sentís el impulso de hacer algo al respecto (revisar, lavar, pedir que te tranquilicen, etc.)?"
        elif es_hecho:
            label_creencia = "¿Cuánto peso sentís que tiene este pensamiento?"
        else:
            label_creencia = "¿Cuánto te lo creíste en ese momento?"

        valor_inicial_creencia = r.get("creencia_inicial_pct")
        if valor_inicial_creencia is None:
            valor_inicial_creencia = anterior.get("creencia_final_pct", 70) if anterior else 70

        input_pensamiento = ft.TextField(
            label=label_pensamiento,
            hint_text=hint_pensamiento,
            value=r.get("pensamiento_automatico", ""),
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        texto_creencia = ft.Text(f"{label_creencia}: {valor_inicial_creencia}%")
        slider_creencia = ft.Slider(
            min=0, max=100, divisions=20, value=valor_inicial_creencia,
            width=ancho_campo(),
            on_change=lambda e: (texto_creencia.__setattr__("value", f"{label_creencia}: {int(e.control.value)}%"), page.update()),
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def continuar(e):
            pensamiento = (input_pensamiento.value or "").strip()
            if not pensamiento:
                mostrar_error(texto_error, "Tratá de escribir el pensamiento que tuviste, aunque sea a grandes rasgos.")
                return
            if detectar_riesgo_suicida(pensamiento):
                r["pensamiento_automatico"] = pensamiento
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(pensamiento):
                r["pensamiento_automatico"] = pensamiento
                ir_a(mostrar_paso_riesgo_terceros)
                return
            r["pensamiento_automatico"] = pensamiento
            r["creencia_inicial_pct"] = int(slider_creencia.value)
            if es_obsesion:
                ir_a(mostrar_paso_obsesion_identificar)
            elif es_hecho:
                ir_a(mostrar_paso_evidencia_hecho)
            else:
                ir_a(mostrar_paso_evidencia)

        pantalla(
            ft.Text("Paso 2 de 4", size=14, color=COLOR_TEXTO_SUAVE),
            ft.Text("Ese pensamiento que te dio vueltas", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            input_pensamiento,
            texto_creencia,
            slider_creencia,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
        )

    # ==========================================================
    # FLUJO DE CRISIS — riesgo suicida detectado
    # ----------------------------------------------------------
    # Reemplaza el resto del cuestionario por completo (sin importar en
    # qué paso estaba ni qué tipo de situación había elegido). No pasa
    # por reestructuración cognitiva: en un momento de riesgo agudo no
    # corresponde debatir la evidencia de un pensamiento, corresponde
    # validar, chequear seguridad y conectar con ayuda profesional ya
    # mismo (evidencia: no discutir ni argumentar, preguntar directo no
    # aumenta el riesgo, validar reduce la sensación de soledad — y el
    # armado de "plan de seguridad" breve: con quién puede estar la
    # persona ahora, qué la sostiene). Ningún paso es obligatorio: se
    # puede ir directo a los teléfonos de ayuda en cualquier momento, y
    # esta sesión NO se guarda en la base de datos (no corresponde
    # persistir un relato de ideación suicida en esta app).
    # ==========================================================
    def mostrar_paso_crisis_1():
        def ir_a_recursos(e):
            ir_a(mostrar_paso_crisis_recursos)

        def elegir_seguridad(valor):
            def handler(e):
                estado["reporte_actual"]["crisis_seguro"] = valor
                ir_a(mostrar_paso_crisis_2)
            return handler

        pantalla(
            ft.Icon(ft.Icons.FAVORITE, size=42, color=ft.Colors.RED_400),
            ft.Text("Esto que compartiste me importa de verdad", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "No estás solo/a con esto, y no hace falta que lo resuelvas ahora vos mismo/a. Te voy a hacer un par de preguntas cortas y enseguida te paso contactos para hablar con alguien ya mismo.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Text("¿Estás en un lugar seguro en este momento?", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.ElevatedButton("Sí, estoy en un lugar seguro", on_click=elegir_seguridad("si"), width=ancho_campo(), height=50),
            ft.OutlinedButton("No estoy seguro/a de eso", on_click=elegir_seguridad("no"), width=ancho_campo(), height=50),
            ft.TextButton("Prefiero ir directo a los contactos de ayuda", on_click=ir_a_recursos),
            mostrar_volver=False,
        )

    def mostrar_paso_crisis_2():
        input_apoyo = ft.TextField(
            label="¿Hay alguien con quien puedas estar ahora, o a quien puedas llamar?",
            hint_text="Un familiar, un amigo, cualquier persona de confianza — no hace falta que sea perfecto, cualquiera que se te ocurra sirve",
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        input_razones = ft.TextField(
            label="¿Hay algo o alguien que te haga querer seguir, aunque ahora cueste verlo?",
            hint_text="No hace falta responder esto si en este momento no se te ocurre nada",
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        radio_medios = ft.RadioGroup(
            content=ft.Column([
                ft.Radio(value="si", label="Sí, tengo algo así cerca"),
                ft.Radio(value="no", label="No, o no lo tengo cerca"),
            ]),
        )

        def continuar(e):
            estado["reporte_actual"]["crisis_apoyo"] = (input_apoyo.value or "").strip()
            estado["reporte_actual"]["crisis_razones"] = (input_razones.value or "").strip()
            estado["reporte_actual"]["crisis_medios"] = radio_medios.value
            ir_a(mostrar_paso_crisis_recursos)

        pantalla(
            ft.Text("Un par de cosas más", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            input_apoyo,
            input_razones,
            ft.Text(
                "¿Tenés cerca en este momento algo con lo que podrías lastimarte (pastillas, un arma, u otra cosa)?",
                size=14,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            radio_medios,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
            ft.TextButton("Ir directo a los contactos de ayuda", on_click=lambda e: ir_a(mostrar_paso_crisis_recursos)),
            mostrar_volver=False,
        )

    def mostrar_paso_crisis_recursos():
        r = estado["reporte_actual"]

        controles = [
            ft.Icon(ft.Icons.PHONE_IN_TALK, size=44, color=ft.Colors.RED_400),
            ft.Text("Hablá con alguien ahora", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        ]

        if r.get("crisis_seguro") == "no":
            controles.append(
                ft.Container(
                    content=ft.Text(
                        "Si estás en peligro inmediato, llamá ya al 911, o pedile a alguien cerca tuyo que te acompañe a llamar.",
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.RED_900,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=12,
                    border_radius=10,
                    bgcolor=ft.Colors.RED_100,
                    width=ancho_campo(),
                )
            )

        if r.get("crisis_medios") == "si":
            controles.append(
                ft.Container(
                    content=ft.Text(
                        "Si podés, alejate ahora de eso o pedile a alguien de confianza que lo guarde por vos mientras tanto — poner distancia, aunque sea temporal, ayuda mucho a pasar este momento más seguro/a.",
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.RED_900,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=12,
                    border_radius=10,
                    bgcolor=ft.Colors.RED_100,
                    width=ancho_campo(),
                )
            )

        controles.append(
            ft.Text(
                "Lo que sentís ahora es real y muy doloroso, y merecés ayuda de verdad para atravesarlo — no tenés que hacerlo solo/a. "
                "Las personas de estas líneas están para escucharte sin juzgarte. Buscar ayuda ahora es un paso que podés dar, y no tenés que darlo solo/a.",
                color=COLOR_TEXTO_FUERTE,
                text_align=ft.TextAlign.CENTER,
                size=15,
            )
        )

        controles.extend([
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Línea Nacional de Salud Mental (Argentina, 24 hs, gratuita, todo el país)", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text("0800-999-0091", size=14),
                    ],
                    spacing=4,
                ),
                padding=15,
                border_radius=12,
                bgcolor=ft.Colors.RED_50,
                width=ancho_campo(),
            ),
            ft.ElevatedButton("Llamar al 0800-999-0091", icon=ft.Icons.CALL, url="tel:08009990091", width=ancho_campo(), height=50),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Línea de Prevención del Suicidio (Argentina, gratuita, de 8 a 0 hs)", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text("135 desde CABA/GBA · 0800-345-1435 desde todo el país", size=14),
                    ],
                    spacing=4,
                ),
                padding=15,
                border_radius=12,
                bgcolor=ft.Colors.RED_50,
                width=ancho_campo(),
            ),
            ft.ElevatedButton("Llamar al 0800-345-1435", icon=ft.Icons.CALL, url="tel:08003451435", width=ancho_campo(), height=50),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Línea 102 (para chicos, chicas y adolescentes, 24 hs, gratuita, todo el país)", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text("102", size=14),
                    ],
                    spacing=4,
                ),
                padding=15,
                border_radius=12,
                bgcolor=ft.Colors.RED_50,
                width=ancho_campo(),
            ),
            ft.ElevatedButton("Llamar al 102", icon=ft.Icons.CALL, url="tel:102", width=ancho_campo(), height=50),
            ft.OutlinedButton("Ver el sitio oficial (argentina.gob.ar)", icon=ft.Icons.OPEN_IN_NEW, url="https://www.argentina.gob.ar/dispositivo-0800", width=ancho_campo(), height=50),
        ])

        if r.get("crisis_seguro") != "no":
            controles.append(
                ft.Text("Si en algún momento estás en peligro inmediato, llamá al 911.", size=13, color=COLOR_TEXTO_SUAVE, text_align=ft.TextAlign.CENTER)
            )

        # Si tocó "Necesito ayuda ahora" desde el login (sin haber
        # iniciado sesión todavía), "volver" tiene que llevar de nuevo al
        # login, no simular una sesión iniciada que nunca pasó.
        hay_sesion = bool(estado.get("usuario_id"))

        def volver(e):
            historial.clear()
            ir_a(mostrar_menu_principal if hay_sesion else mostrar_login)

        controles.extend([
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.ElevatedButton(
                "Volver al menú principal" if hay_sesion else "Volver al inicio",
                on_click=volver,
                width=ancho_campo(),
                height=50,
            ),
        ])

        pantalla(*controles, mostrar_volver=False)

    # ==========================================================
    # RIESGO HACIA TERCEROS — distinto del flujo de crisis suicida
    # ----------------------------------------------------------
    # Se activa cuando el texto libre describe una intención real de
    # lastimar a otra persona (no el miedo obsesivo a hacerlo sin
    # querer). Igual que la crisis suicida, corta el flujo normal en
    # cualquier paso y esta sesión NO se guarda en la base de datos.
    # ==========================================================
    def mostrar_paso_riesgo_terceros():
        hay_sesion = bool(estado.get("usuario_id"))

        def volver(e):
            historial.clear()
            ir_a(mostrar_menu_principal if hay_sesion else mostrar_login)

        pantalla(
            ft.Icon(ft.Icons.PHONE_IN_TALK, size=44, color=ft.Colors.RED_400),
            ft.Text("Esto es serio, y no es algo para atravesar solo/a", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Por lo que contás, parece que hay una intención real de lastimar a alguien, no solo un miedo o un pensamiento que se repite. DRE no está preparada para acompañarte en esto — hace falta hablarlo ya mismo con un profesional de salud mental, o con la policía si hay peligro inmediato para alguien.",
                color=COLOR_TEXTO_FUERTE,
                text_align=ft.TextAlign.CENTER,
                size=15,
            ),
            ft.Container(
                content=ft.Text(
                    "Si hay peligro inmediato para vos o para otra persona, llamá ya al 911.",
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.RED_900,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=12,
                border_radius=10,
                bgcolor=ft.Colors.RED_100,
                width=ancho_campo(),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        ft.Text("Línea Nacional de Salud Mental (Argentina, 24 hs, gratuita, todo el país)", weight=ft.FontWeight.BOLD, size=14),
                        ft.Text("0800-999-0091", size=14),
                    ],
                    spacing=4,
                ),
                padding=15,
                border_radius=12,
                bgcolor=ft.Colors.RED_50,
                width=ancho_campo(),
            ),
            ft.ElevatedButton("Llamar al 0800-999-0091", icon=ft.Icons.CALL, url="tel:08009990091", width=ancho_campo(), height=50),
            ft.ElevatedButton(
                "Volver al menú principal" if hay_sesion else "Volver al inicio",
                on_click=volver,
                width=ancho_campo(),
                height=50,
            ),
            mostrar_volver=False,
        )

    def mostrar_paso_obsesion_identificar():
        # No se pregunta evidencia a favor/en contra: analizar de más el
        # contenido del pensamiento (o pedir "pruebas") es, en sí mismo,
        # parte de la compulsión (reassurance-seeking), y la evidencia
        # muestra que calma un rato pero refuerza el círculo. En cambio,
        # se identifica la compulsión/impulso, y se suma una pregunta
        # breve de "confusión inferencial" (I-CBT): notar si esto es algo
        # que está pasando de verdad o una posibilidad imaginada, sin
        # necesidad de resolver cuál de las dos es.
        r = estado["reporte_actual"]
        anterior = r.get("_anterior")
        es_retomada = anterior is not None and anterior.get("tipo_situacion") == TIPO_OBSESION

        input_compulsion = ft.TextField(
            label="¿Sigue siendo el mismo impulso, o cambió?" if es_retomada else "¿Qué sentís el impulso de hacer para calmar esto?",
            hint_text="Revisar algo, lavarte, repetir una acción o palabra, pedir que te tranquilicen, evitar algo...",
            value=r.get("evidencia_a_favor") if r.get("evidencia_a_favor") is not None else (anterior.get("evidencia_a_favor", "") if es_retomada else ""),
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        input_real_o_imaginado = ft.TextField(
            label="¿Esto es algo de lo que tenés evidencia clara, o es una duda/posibilidad que la mente trajo?",
            hint_text="No hace falta resolver cuál de las dos es, solo notar la diferencia",
            value=r.get("evidencia_en_contra") if r.get("evidencia_en_contra") is not None else (anterior.get("evidencia_en_contra", "") if es_retomada else ""),
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def continuar(e):
            compulsion = (input_compulsion.value or "").strip()
            real_o_imaginado = (input_real_o_imaginado.value or "").strip()
            if not compulsion:
                mostrar_error(texto_error, "Contame aunque sea brevemente qué impulso sentís, para poder seguir.")
                return
            if detectar_riesgo_suicida(compulsion, real_o_imaginado):
                r["evidencia_a_favor"] = compulsion
                r["evidencia_en_contra"] = real_o_imaginado
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(compulsion, real_o_imaginado):
                r["evidencia_a_favor"] = compulsion
                r["evidencia_en_contra"] = real_o_imaginado
                ir_a(mostrar_paso_riesgo_terceros)
                return
            r["evidencia_a_favor"] = compulsion
            r["evidencia_en_contra"] = real_o_imaginado
            ir_a(mostrar_paso_obsesion_alternativo)

        pantalla(
            ft.Text("Paso 3 de 4", size=14, color=COLOR_TEXTO_SUAVE),
            ft.Text("Identifiquemos el impulso", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Aliviar esto haciendo lo que el impulso pide (o pidiendo que te tranquilicen) suele calmar un rato, pero hace que vuelva más fuerte después. Por eso acá no vamos a intentar resolver ni confirmar el pensamiento, solo identificarlo.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
                size=13,
            ),
            ft.Text(
                "Este es un ejercicio puntual para acompañarte ahora, no reemplaza un tratamiento — si esto te pasa seguido o te complica mucho el día a día, lo mejor es también hablarlo con un profesional.",
                color=COLOR_TEXTO_SUAVE,
                text_align=ft.TextAlign.CENTER,
                size=12,
            ),
            input_compulsion,
            input_real_o_imaginado,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
        )

    def mostrar_paso_obsesion_alternativo():
        # No se busca "un pensamiento más justo": la meta con TOC no es
        # cambiar el contenido del pensamiento, es tolerar el malestar
        # sin hacer la compulsión (Prevención de Respuesta). Por eso se
        # pide un compromiso concreto en vez de una reformulación, y no
        # se entra al loop de reflexión (esas técnicas tampoco
        # corresponden acá).
        r = estado["reporte_actual"]
        anterior = r.get("_anterior")
        es_retomada = anterior is not None and anterior.get("tipo_situacion") == TIPO_OBSESION

        controles_recordatorio = []
        if es_retomada and anterior.get("pensamiento_alternativo"):
            controles_recordatorio.append(
                ft.Container(
                    content=ft.Text(
                        f"La vez pasada te habías propuesto: \"{anterior['pensamiento_alternativo']}\". ¿Pudiste sostenerlo, o fue distinto esta vez? Si no se pudo sostener, no es un fracaso — es información de que ese paso fue muy grande esta vez.",
                        size=12,
                        color=COLOR_TEXTO_MEDIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=COLOR_CAJA_INFO,
                    width=ancho_campo(),
                )
            )

        input_prevencion = ft.TextField(
            label="¿Por cuánto tiempo podés intentar NO hacer esa acción esta vez?",
            hint_text="Un tiempo concreto (5 minutos, 1 hora, todo el día) o directamente \"no la voy a hacer\"",
            value=r.get("pensamiento_alternativo") if r.get("pensamiento_alternativo") is not None else "",
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        input_alternativa = ft.TextField(
            label="¿Qué podés hacer en cambio mientras se pasa el impulso?",
            hint_text="Algo que no sea la compulsión: caminar, llamar a alguien, escuchar música. Si el ritual es mental (repetir una frase, rezar, revisar en tu cabeza), probá centrarte en algo sensorial concreto: contar objetos alrededor, tocar una textura...",
            value=r.get("perspectiva_amigo") if r.get("perspectiva_amigo") is not None else "",
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        texto_urgencia = ft.Text(f"¿Cómo sentís el impulso ahora, después de pensarlo así?: {r.get('creencia_final_pct', r.get('creencia_inicial_pct', 50))}%")
        slider_urgencia = ft.Slider(
            min=0, max=100, divisions=20, value=r.get("creencia_final_pct", r.get("creencia_inicial_pct", 50)),
            width=ancho_campo(),
            on_change=lambda e: (texto_urgencia.__setattr__("value", f"¿Cómo sentís el impulso ahora, después de pensarlo así?: {int(e.control.value)}%"), page.update()),
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def continuar(e):
            prevencion = (input_prevencion.value or "").strip()
            alternativa = (input_alternativa.value or "").strip()
            if not prevencion:
                mostrar_error(texto_error, "Tratá de escribir un compromiso concreto, aunque sea chico, para poder seguir.")
                return
            if detectar_riesgo_suicida(prevencion, alternativa):
                r["pensamiento_alternativo"] = prevencion
                r["perspectiva_amigo"] = alternativa
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(prevencion, alternativa):
                r["pensamiento_alternativo"] = prevencion
                r["perspectiva_amigo"] = alternativa
                ir_a(mostrar_paso_riesgo_terceros)
                return
            r["pensamiento_alternativo"] = prevencion
            r["perspectiva_amigo"] = alternativa
            r["creencia_final_pct"] = int(slider_urgencia.value)
            r["distorsiones_lista"] = []
            ir_a(mostrar_paso_elegir_recomendacion)

        pantalla(
            ft.Text("Paso 4 de 4", size=14, color=COLOR_TEXTO_SUAVE),
            ft.Text("Un compromiso posible", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            *controles_recordatorio,
            input_prevencion,
            input_alternativa,
            texto_urgencia,
            slider_urgencia,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
        )

    def armar_checklist_distorsiones(r):
        # Checklist de distorsiones cognitivas. Antes era una pantalla
        # propia (Paso 4 de 6); ahora vive adentro del Paso 3, para que
        # el registro completo sean 4 pasos en vez de 6 (una simulación
        # de uso realista mostró que ~30% de los registros se abandonaban
        # a mitad del flujo largo). Devuelve (checkboxes, controles) — el
        # caller lee las elegidas con leer_distorsiones_elegidas.
        anterior = r.get("_anterior")
        es_hecho = r.get("tipo_situacion") in TIPOS_HECHO_CONSUMADO
        if r.get("distorsiones_lista") is not None:
            seleccionadas = set(r["distorsiones_lista"])
        elif anterior and anterior.get("distorsiones"):
            seleccionadas = {n.strip() for n in anterior["distorsiones"].split(",") if n.strip()}
        else:
            seleccionadas = set()

        checkboxes = []
        controles = [
            ft.Divider(height=8, color=ft.Colors.TRANSPARENT),
            ft.Text("¿La mente te está jugando alguna de estas trampas?", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Marcá las que reconozcas (podés no marcar ninguna)." + (" Ya vienen marcadas las que habías notado la vez pasada." if seleccionadas else ""),
                size=13,
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
        ]
        if es_hecho:
            controles.append(
                ft.Text(
                    "Esto no es sobre lo que pasó (eso no está en discusión) — es sobre los pensamientos que a veces se le suman, como la culpa o el \"esto va a estar mal para siempre\".",
                    size=13,
                    color=COLOR_TEXTO_MEDIO,
                    text_align=ft.TextAlign.CENTER,
                )
            )
        for nombre, explicacion in DISTORSIONES:
            cb = ft.Checkbox(value=nombre in seleccionadas)
            checkboxes.append(cb)
            controles.append(
                ft.Container(
                    content=ft.Row(
                        [
                            cb,
                            ft.Column(
                                [
                                    ft.Text(nombre, size=16, weight=ft.FontWeight.BOLD),
                                    ft.Text(explicacion, size=13, color=COLOR_TEXTO_MEDIO),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    ),
                    width=ancho_campo(),
                    padding=10,
                    border_radius=12,
                    bgcolor=COLOR_CAJA_SUAVE,
                )
            )
        return checkboxes, controles

    def leer_distorsiones_elegidas(checkboxes):
        return [DISTORSIONES[i][0] for i, cb in enumerate(checkboxes) if cb.value]

    def mostrar_paso_evidencia_hecho():
        # Para duelo/pérdida o un diagnóstico ya confirmado NO se pregunta
        # por evidencia a favor/en contra: es un hecho, no una distorsión
        # a desafiar, y preguntarlo así puede sentirse invalidante. En
        # cambio, la literatura de CBT para duelo (y, de forma análoga,
        # para el proceso de adaptación a un diagnóstico) apunta la
        # reestructuración específicamente a la culpa/autorreproche
        # cuando aparece, y a los apoyos con los que cuenta la persona,
        # en vez de desafiar el hecho en sí.
        r = estado["reporte_actual"]
        es_duelo = r.get("tipo_situacion") == TIPO_DUELO
        anterior = r.get("_anterior")
        # El texto de introducción presuponía dolor fuerte ("duele",
        # "difícil") sin importar lo que la persona reportó en el Paso 1.
        # Para alguien que marcó una intensidad baja (ej: un diagnóstico
        # menor, una pérdida que no lo golpeó tanto), esa validación tan
        # marcada queda desproporcionada. Se adapta según la intensidad.
        intensidad_alta = r.get("intensidad_inicial", 0) >= UMBRAL_INTENSIDAD_PARA_INSISTIR

        if es_duelo:
            titulo_pantalla = "Acompañando este dolor" if intensidad_alta else "Pensando en esta pérdida"
            intro = (
                "Perder a alguien importante duele, y está bien que así sea. No vamos a intentar convencerte de lo contrario — sí queremos ver si hay culpa dando vueltas, porque eso a veces se puede aliviar."
                if intensidad_alta else
                "Aunque no haya sido un golpe enorme, a veces vale la pena revisar si quedó algo de culpa dando vueltas, porque eso a veces conviene mirarlo igual."
            )
            label_valorar = "¿Qué es lo que más valorás o extrañás de esa persona (o ese vínculo)?"
            hint_valorar = "No hace falta que sea algo grande, cualquier cosa que se te ocurra vale"
        else:
            titulo_pantalla = "Acompañando esta noticia" if intensidad_alta else "Pensando en esta noticia"
            intro = (
                "Recibir una noticia así de salud es difícil, y no vamos a intentar minimizarlo — sí queremos ver si hay culpa dando vueltas, porque eso a veces se puede aliviar."
                if intensidad_alta else
                "Aunque esta noticia no te haya movido tanto el piso, a veces vale la pena revisar si quedó algo de culpa o preocupación dando vueltas."
            )
            label_valorar = "¿En qué apoyos, personas o recursos sentís que podés apoyarte para atravesar esto?"
            hint_valorar = "Puede ser gente de tu entorno, tu equipo médico, algo que ya sepas que te ayuda, o algo concreto que sientas que está en tus manos hacer para cuidarte"

        if anterior:
            titulo_pantalla = "¿Cómo estás con esto ahora?"
            intro = "La vez pasada charlamos sobre esto. Contame si sigue igual o si algo cambió desde entonces."

        label_culpa = "¿Sigue esa culpa, o cambió algo desde la última vez?" if anterior else "¿Sentís algo de culpa, o que \"deberías\" haber hecho algo distinto?"
        hint_culpa = (
            "Contame cómo lo sentís ahora"
            if anterior else
            "Si es así, contame de qué se trata. Si sentís que no hay culpa, también podés decirlo"
        )

        def valor_o_anterior(campo):
            actual = r.get(campo)
            if actual is not None:
                return actual
            return (anterior.get(campo, "") if anterior else "") or ""

        input_culpa = ft.TextField(
            label=label_culpa,
            hint_text=hint_culpa,
            value=valor_o_anterior("evidencia_a_favor"),
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        input_valorar = ft.TextField(
            label=label_valorar,
            hint_text=hint_valorar,
            value=valor_o_anterior("evidencia_en_contra"),
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        # La pregunta de "¿qué le dirías a alguien que querés con esta
        # misma culpa?" se sacó como campo aparte (el flujo bajó de 6 a
        # 4 pasos): esa misma perspectiva ya se retoma como pista en el
        # paso del pensamiento alternativo.
        texto_error = ft.Text("", color=ft.Colors.RED)
        checkboxes_distorsiones, controles_distorsiones = armar_checklist_distorsiones(r)

        def continuar(e):
            culpa = (input_culpa.value or "").strip()
            valorar = (input_valorar.value or "").strip()
            if not culpa or not valorar:
                mostrar_error(texto_error, "Tratá de responder aunque sea con pocas palabras para poder seguir.")
                return
            r["distorsiones_lista"] = leer_distorsiones_elegidas(checkboxes_distorsiones)
            if detectar_riesgo_suicida(culpa, valorar):
                r["evidencia_a_favor"] = culpa
                r["evidencia_en_contra"] = valorar
                r["perspectiva_amigo"] = r.get("perspectiva_amigo") or ""
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(culpa, valorar):
                r["evidencia_a_favor"] = culpa
                r["evidencia_en_contra"] = valorar
                r["perspectiva_amigo"] = r.get("perspectiva_amigo") or ""
                ir_a(mostrar_paso_riesgo_terceros)
                return
            r["evidencia_a_favor"] = culpa
            r["evidencia_en_contra"] = valorar
            r["perspectiva_amigo"] = r.get("perspectiva_amigo") or ""
            ir_a(mostrar_paso_alternativo_hecho)

        pantalla(
            ft.Text("Paso 3 de 4", size=14, color=COLOR_TEXTO_SUAVE),
            ft.Text(titulo_pantalla, size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                intro,
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            input_culpa,
            input_valorar,
            *controles_distorsiones,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
        )

    def mostrar_paso_evidencia():
        r = estado["reporte_actual"]
        anterior = r.get("_anterior")

        # Si ya había una respuesta de la última vez, se precarga (la
        # persona la edita en vez de escribir todo de nuevo) y la
        # pregunta se orienta a qué cambió, no a empezar de cero.
        def valor_o_anterior(campo):
            actual = r.get(campo)
            if actual is not None:
                return actual
            return (anterior.get(campo, "") if anterior else "") or ""

        input_a_favor = ft.TextField(
            label="¿Sigue habiendo cosas que te hacen pensar que esto es cierto?" if anterior else "¿Qué cosas te hacen pensar que esto es cierto?",
            hint_text="Contá qué te lleva a creerlo así",
            value=valor_o_anterior("evidencia_a_favor"),
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        input_en_contra = ft.TextField(
            label="¿Cambió algo en lo que te hace dudar de que sea tan así?" if anterior else "¿Y qué cosas te hacen dudar de que sea tan así?",
            hint_text="Pensá en otras veces que creíste algo parecido y no pasó, o en algún dato que lo contradiga",
            value=valor_o_anterior("evidencia_en_contra"),
            width=ancho_campo(),
            multiline=True,
            min_lines=2,
            max_lines=4,
        )
        # La pregunta del "amigo/a en tu misma situación" se sacó como
        # campo obligatorio aparte (el flujo bajó de 6 a 4 pasos): esa
        # misma perspectiva ya aparece como pista en el paso del
        # pensamiento alternativo, así que acá quedaba redundante.
        texto_error = ft.Text("", color=ft.Colors.RED)
        checkboxes_distorsiones, controles_distorsiones = armar_checklist_distorsiones(r)

        def continuar(e):
            a_favor = (input_a_favor.value or "").strip()
            en_contra = (input_en_contra.value or "").strip()
            if not a_favor or not en_contra:
                mostrar_error(texto_error, "Tratá de responder las 2 preguntas para poder seguir, aunque sea con pocas palabras.")
                return
            r["distorsiones_lista"] = leer_distorsiones_elegidas(checkboxes_distorsiones)
            if detectar_riesgo_suicida(a_favor, en_contra):
                r["evidencia_a_favor"] = a_favor
                r["evidencia_en_contra"] = en_contra
                r["perspectiva_amigo"] = r.get("perspectiva_amigo") or ""
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(a_favor, en_contra):
                r["evidencia_a_favor"] = a_favor
                r["evidencia_en_contra"] = en_contra
                r["perspectiva_amigo"] = r.get("perspectiva_amigo") or ""
                ir_a(mostrar_paso_riesgo_terceros)
                return
            r["evidencia_a_favor"] = a_favor
            r["evidencia_en_contra"] = en_contra
            r["perspectiva_amigo"] = r.get("perspectiva_amigo") or ""
            ir_a(mostrar_paso_alternativo)

        pantalla(
            ft.Text("Paso 3 de 4", size=14, color=COLOR_TEXTO_SUAVE),
            ft.Text("¿Qué cambió desde la última vez?" if anterior else "Miremos esto con un poco más de distancia", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            input_a_favor,
            input_en_contra,
            *controles_distorsiones,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
        )

    # (La pantalla propia de distorsiones — el viejo "Paso 4 de 6" — se
    # eliminó: el checklist ahora vive adentro del Paso 3, ver
    # armar_checklist_distorsiones.)

    def mostrar_paso_alternativo_hecho():
        # Para un hecho consumado (duelo o diagnóstico) no se fuerza una
        # "creencia final" más baja: no es algo a corregir. Solo se
        # ofrece espacio para un pensamiento/acción más reconfortante
        # (útil sobre todo cuando había culpa de por medio), y se sigue
        # directo a las recomendaciones, sin el mecanismo de "seguir
        # insistiendo" que sí tiene sentido para pensamientos
        # distorsionados.
        r = estado["reporte_actual"]
        es_duelo = r.get("tipo_situacion") == TIPO_DUELO
        anterior = r.get("_anterior")
        intensidad_alta = r.get("intensidad_inicial", 0) >= UMBRAL_INTENSIDAD_PARA_INSISTIR
        hint_alternativo = (
            "Esto no significa dejar de extrañar a quien perdiste, ni que la culpa (si la hay) esté justificada"
            if es_duelo else
            "Esto no significa que la noticia deje de ser difícil, ni que la culpa (si la hay) esté justificada"
        )

        if anterior:
            titulo_pantalla = "¿Cambió algo en cómo lo pensás?"
        elif es_duelo:
            titulo_pantalla = "Un lugar más amable para este dolor" if intensidad_alta else "Pensándolo de otra forma"
        else:
            titulo_pantalla = "Un lugar más amable para esta noticia" if intensidad_alta else "Pensándolo de otra forma"

        controles_recordatorio = []
        if anterior and anterior.get("pensamiento_alternativo"):
            controles_recordatorio.append(
                ft.Container(
                    content=ft.Text(
                        f"La vez pasada habías escrito: \"{anterior['pensamiento_alternativo']}\". ¿Te sigue resultando útil, o hay algo que agregarías?",
                        size=12,
                        color=COLOR_TEXTO_MEDIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=COLOR_CAJA_INFO,
                    width=ancho_campo(),
                )
            )

        input_alternativo = ft.TextField(
            label="¿Hay algo que te gustaría pensar, recordar o hacer que te resulte un poco más reconfortante?",
            hint_text=hint_alternativo,
            value=r.get("pensamiento_alternativo") if r.get("pensamiento_alternativo") is not None else (anterior.get("pensamiento_alternativo", "") if anterior else ""),
            width=ancho_campo(),
            multiline=True,
            min_lines=3,
            max_lines=6,
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def continuar(e):
            alternativo = (input_alternativo.value or "").strip()
            if not alternativo:
                mostrar_error(texto_error, "Tratá de escribir aunque sea una idea breve para poder seguir.")
                return
            if detectar_riesgo_suicida(alternativo):
                r["pensamiento_alternativo"] = alternativo
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(alternativo):
                r["pensamiento_alternativo"] = alternativo
                ir_a(mostrar_paso_riesgo_terceros)
                return
            r["pensamiento_alternativo"] = alternativo
            r["creencia_final_pct"] = r.get("creencia_inicial_pct", 0)
            ir_a(mostrar_paso_elegir_recomendacion)

        pantalla(
            ft.Text("Paso 4 de 4", size=14, color=COLOR_TEXTO_SUAVE),
            ft.Text(titulo_pantalla, size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            *controles_recordatorio,
            input_alternativo,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
        )

    def mostrar_paso_alternativo():
        r = estado["reporte_actual"]
        anterior = r.get("_anterior")

        # Pista breve segun las distorsiones que marco en el Paso 3 (si
        # marco alguna) -- solo orienta, no cambia la validacion ni es
        # obligatorio tenerla en cuenta para escribir el pensamiento
        # alternativo.
        # Una sola pista, con una intro que explica de dónde sale — antes
        # se mostraban hasta 2 juntas sin explicación y se leían como dos
        # mensajes casi iguales caídos de la nada (feedback de Gabriel).
        controles_pistas = []
        tips_distorsion = [
            RECOMENDACIONES_POR_DISTORSION[d]
            for d in (r.get("distorsiones_lista") or [])
            if d in RECOMENDACIONES_POR_DISTORSION
        ]
        if tips_distorsion:
            controles_pistas.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("💡 Una pista, por la trampa que marcaste en el paso anterior:", size=12, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                            ft.Text(tips_distorsion[0], size=12, color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
                        ],
                        spacing=6,
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=COLOR_CAJA_INFO,
                    width=ancho_campo(),
                )
            )

        controles_recordatorio = []
        if anterior and anterior.get("pensamiento_alternativo"):
            controles_recordatorio.append(
                ft.Container(
                    content=ft.Text(
                        f"La vez pasada habías llegado a este pensamiento alternativo: \"{anterior['pensamiento_alternativo']}\". ¿Te sigue sirviendo, o lo cambiarías?",
                        size=12,
                        color=COLOR_TEXTO_MEDIO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=10,
                    border_radius=10,
                    bgcolor=COLOR_CAJA_INFO,
                    width=ancho_campo(),
                )
            )

        input_alternativo = ft.TextField(
            label="Con todo esto, ¿cómo lo pensarías de una forma más justa con vos?",
            hint_text="Pensá en qué le dirías a alguien que querés si estuviera en tu misma situación",
            value=r.get("pensamiento_alternativo") if r.get("pensamiento_alternativo") is not None else (anterior.get("pensamiento_alternativo", "") if anterior else ""),
            width=ancho_campo(),
            multiline=True,
            min_lines=3,
            max_lines=6,
        )
        # Se nombra "el pensamiento original" y se lo muestra textual:
        # leído rápido, "aquel pensamiento" parecía referirse a lo que la
        # persona acababa de escribir en esta misma pantalla.
        label_creencia_final = "Ahora que lo pensaste distinto, ¿cuánto te queda del pensamiento original?"
        recordatorio_original = ft.Text(
            f"Tu pensamiento original era: \"{r.get('pensamiento_automatico', '')}\"",
            size=12,
            color=COLOR_TEXTO_SUAVE,
            text_align=ft.TextAlign.CENTER,
        )
        # Antes arrancaba siempre en un 30% fijo, sin relación con lo
        # que la persona haya respondido como creencia inicial (podía
        # sentirse como si la app ya le estuviera sugiriendo una
        # respuesta). Ahora ancla al valor inicial, igual que ya hacía
        # la variante de TOC.
        valor_inicial_final = r.get("creencia_final_pct", r.get("creencia_inicial_pct", 50))
        texto_creencia = ft.Text(f"{label_creencia_final}: {valor_inicial_final}%")
        slider_creencia = ft.Slider(
            min=0, max=100, divisions=20, value=valor_inicial_final,
            width=ancho_campo(),
            on_change=lambda e: (texto_creencia.__setattr__("value", f"{label_creencia_final}: {int(e.control.value)}%"), page.update()),
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def continuar(e):
            alternativo = (input_alternativo.value or "").strip()
            if not alternativo:
                mostrar_error(texto_error, "Tratá de escribir, aunque sea una idea breve, cómo lo verías de otra forma.")
                return
            if detectar_riesgo_suicida(alternativo):
                r["pensamiento_alternativo"] = alternativo
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(alternativo):
                r["pensamiento_alternativo"] = alternativo
                ir_a(mostrar_paso_riesgo_terceros)
                return
            r["pensamiento_alternativo"] = alternativo
            r["creencia_final_pct"] = int(slider_creencia.value)
            decidir_tras_creencia()

        pantalla(
            ft.Text("Paso 4 de 4", size=14, color=COLOR_TEXTO_SUAVE),
            ft.Text("Busquemos un pensamiento más justo con vos", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            *controles_pistas,
            *controles_recordatorio,
            input_alternativo,
            recordatorio_original,
            texto_creencia,
            slider_creencia,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
        )

    def decidir_tras_creencia():
        # Si todavía cree con fuerza el pensamiento original (o no supo
        # qué contestar), no pasamos a recomendaciones todavía: la
        # guiamos por otra técnica de reflexión antes de volver a
        # preguntar. Tope de rondas para no dejarla nunca sin salida.
        r = estado["reporte_actual"]
        ronda = r.get("rondas_reflexion", 0)
        if necesita_reflexion_extra(r) and ronda < MAX_RONDAS_REFLEXION:
            ir_a(mostrar_paso_reflexion_extra)
        else:
            ir_a(mostrar_paso_elegir_recomendacion)

    def mostrar_paso_reflexion_extra():
        r = estado["reporte_actual"]
        ronda = r.get("rondas_reflexion", 0)
        tecnica = TECNICAS_REFLEXION[ronda % len(TECNICAS_REFLEXION)]

        input_reflexion = ft.TextField(
            label="Contame qué se te ocurre",
            hint_text=tecnica["hint"],
            width=ancho_campo(),
            multiline=True,
            min_lines=3,
            max_lines=6,
        )
        texto_creencia = ft.Text(f"Después de esto, ¿cuánto te queda del pensamiento original?: {r.get('creencia_final_pct', 70)}%")
        slider_creencia = ft.Slider(
            min=0, max=100, divisions=20, value=r.get("creencia_final_pct", 70),
            width=ancho_campo(),
            on_change=lambda e: (texto_creencia.__setattr__("value", f"Después de esto, ¿cuánto te queda del pensamiento original?: {int(e.control.value)}%"), page.update()),
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def continuar(e):
            reflexion = (input_reflexion.value or "").strip()
            if not reflexion:
                mostrar_error(texto_error, "Tratá de escribir aunque sea una idea breve para poder seguir.")
                return
            if detectar_riesgo_suicida(reflexion):
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(reflexion):
                ir_a(mostrar_paso_riesgo_terceros)
                return
            anteriores = r.get("reflexiones_extra", [])
            anteriores.append(f"[{tecnica['titulo']}] {reflexion}")
            r["reflexiones_extra"] = anteriores
            r["creencia_final_pct"] = int(slider_creencia.value)
            r["rondas_reflexion"] = ronda + 1
            decidir_tras_creencia()

        def terminar_igual(e):
            r["rondas_reflexion"] = ronda + 1
            ir_a(mostrar_paso_elegir_recomendacion)

        pantalla(
            ft.Text("Un momento más", size=14, color=COLOR_TEXTO_SUAVE),
            ft.Icon(ft.Icons.PSYCHOLOGY_ALT, size=40, color=COLOR_PRIMARIO),
            ft.Text(tecnica["titulo"], size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(tecnica["intro"], color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            ft.Text(tecnica["consigna"](r), text_align=ft.TextAlign.CENTER),
            input_reflexion,
            texto_creencia,
            slider_creencia,
            texto_error,
            ft.ElevatedButton("Continuar", on_click=continuar, width=ancho_campo(), height=50),
            ft.TextButton("Prefiero terminar por ahora", on_click=terminar_igual),
            ft.Text(
                "Si en este momento sentís que necesitás ayuda inmediata, no esperes: contactate con alguien de confianza o con una línea de ayuda de tu país.",
                size=11,
                color=COLOR_TEXTO_SUAVE,
                text_align=ft.TextAlign.CENTER,
            ),
            mostrar_volver=False,
        )

    def guardar_reporte_supabase(r):
        registro = {
            "usuario_id": estado["usuario_id"],
            "fecha": datetime.now().isoformat(),
            "situacion": r["situacion"],
            "tipo_situacion": r.get("tipo_situacion", ""),
            "emocion_inicial": r["emocion_inicial"],
            "intensidad_inicial": r["intensidad_inicial"],
            "pensamiento_automatico": r["pensamiento_automatico"],
            "creencia_inicial_pct": r["creencia_inicial_pct"],
            "evidencia_a_favor": r["evidencia_a_favor"],
            "evidencia_en_contra": r["evidencia_en_contra"],
            "perspectiva_amigo": r["perspectiva_amigo"],
            "distorsiones": ", ".join(r.get("distorsiones_lista", [])),
            "pensamiento_alternativo": r["pensamiento_alternativo"],
            "creencia_final_pct": r["creencia_final_pct"],
            "recomendaciones_dadas": ", ".join(r.get("recomendaciones", [])),
            "rondas_reflexion": r.get("rondas_reflexion", 0),
            "reflexiones_extra": " | ".join(r.get("reflexiones_extra", [])),
            "tema_id": r.get("tema_id"),
            "feedback_recomendacion_anterior": r.get("feedback_recomendacion_anterior", ""),
            "feedback_recomendacion_porque": r.get("feedback_recomendacion_porque", ""),
        }

        if estado["modo_local"]:
            # Acceso de prueba: se guarda solo en memoria (se pierde al
            # cerrar/recargar), así se puede probar el historial sin tocar
            # Supabase. Guardamos la referencia al dict para poder
            # actualizarle el tema_id más adelante si la persona decide
            # guardar este pensamiento recién después de terminar.
            estado["_reportes_locales"].insert(0, registro)
            r["_registro_local"] = registro
            return True

        try:
            resp = requests.post(
                SUPABASE_REPORTES_URL,
                headers={**HEADERS, "Prefer": "return=representation"},
                json=registro,
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase POST reportes_emocionales [{resp.status_code}]: {resp.text}")
                return False
            creados = resp.json()
            if creados:
                r["_reporte_id"] = creados[0].get("id")
            return True
        except Exception as e:
            print("Error de red (guardar reporte):", repr(e))
            return False

    def vincular_reporte_a_tema(r):
        # Se usa cuando la persona decide, ya al final, guardar el
        # pensamiento como un tema a seguir: el reporte ya se había
        # guardado sin tema_id, así que hay que actualizarlo.
        if estado["modo_local"]:
            registro = r.get("_registro_local")
            if registro is not None:
                registro["tema_id"] = r.get("tema_id")
            return True
        reporte_id = r.get("_reporte_id")
        if reporte_id is None:
            return False
        try:
            resp = requests.patch(
                f"{SUPABASE_REPORTES_URL}?id=eq.{reporte_id}",
                headers=HEADERS,
                json={"tema_id": r.get("tema_id")},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (vincular reporte a tema):", e)
            return False

    # ==========================================================
    # CRUD de "temas" (pensamientos a seguir trabajando)
    # ==========================================================
    def obtener_temas_usuario():
        if estado["modo_local"]:
            return estado["_temas_locales"]
        try:
            resp = requests.get(
                SUPABASE_TEMAS_URL,
                headers=HEADERS,
                params={"usuario_id": f"eq.{estado['usuario_id']}", "select": "*", "order": "actualizado_en.desc"},
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase GET temas_seguimiento [{resp.status_code}]: {resp.text}")
                return None
            return resp.json()
        except Exception as e:
            print("Error de red (temas):", repr(e))
            return None

    def crear_tema(titulo, color, color_automatico=True):
        if estado["modo_local"]:
            tema = {
                "id": f"local-{len(estado['_temas_locales']) + 1}",
                "usuario_id": estado["usuario_id"],
                "titulo": titulo,
                "color": color,
                "color_automatico": color_automatico,
                "estado": "",
                "resuelto": False,
                "reflexion_final": None,
                "fecha": datetime.now().isoformat(),
            }
            estado["_temas_locales"].insert(0, tema)
            return tema
        try:
            resp = requests.post(
                SUPABASE_TEMAS_URL,
                headers={**HEADERS, "Prefer": "return=representation"},
                json={"usuario_id": estado["usuario_id"], "titulo": titulo, "color": color, "color_automatico": color_automatico, "estado": ""},
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase POST temas_seguimiento [{resp.status_code}]: {resp.text}")
                return None
            creados = resp.json()
            return creados[0] if creados else None
        except Exception as e:
            print("Error de red (crear tema):", repr(e))
            return None

    def actualizar_tema(tema_id, color, estado_texto, color_automatico=False):
        if estado["modo_local"]:
            for t in estado["_temas_locales"]:
                if t["id"] == tema_id:
                    t["color"] = color
                    t["estado"] = estado_texto
                    t["color_automatico"] = color_automatico
            return True
        try:
            resp = requests.patch(
                f"{SUPABASE_TEMAS_URL}?id=eq.{tema_id}",
                headers=HEADERS,
                json={"color": color, "estado": estado_texto, "color_automatico": color_automatico, "actualizado_en": datetime.now().isoformat()},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (actualizar tema):", e)
            return False

    def actualizar_flor_tema(tema_id, flor):
        # flor=None vuelve a la flor general elegida en Personalización.
        if estado["modo_local"]:
            for t in estado["_temas_locales"]:
                if t["id"] == tema_id:
                    t["flor"] = flor
            return True
        try:
            resp = requests.patch(
                f"{SUPABASE_TEMAS_URL}?id=eq.{tema_id}",
                headers=HEADERS,
                json={"flor": flor, "actualizado_en": datetime.now().isoformat()},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (actualizar flor del tema):", e)
            return False

    def marcar_tema_resuelto(tema_id, reflexion, resuelto=True):
        # El mensaje ("reflexión final") solo tiene sentido guardarlo
        # cuando la persona da la situación/emoción por totalmente
        # solucionada — no se infiere del color ni del % de creencia,
        # porque esos son más difusos. Es una acción explícita.
        if estado["modo_local"]:
            for t in estado["_temas_locales"]:
                if t["id"] == tema_id:
                    t["resuelto"] = resuelto
                    t["reflexion_final"] = reflexion
            return True
        try:
            resp = requests.patch(
                f"{SUPABASE_TEMAS_URL}?id=eq.{tema_id}",
                headers=HEADERS,
                json={"resuelto": resuelto, "reflexion_final": reflexion, "actualizado_en": datetime.now().isoformat()},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (marcar tema resuelto):", e)
            return False

    def borrar_tema(tema_id):
        # "Quitar de mis temas" no borra el historial: los reportes ya
        # guardados quedan sueltos (tema_id=None), visibles en el
        # Historial general, pero dejan de agruparse bajo este
        # pensamiento. Se desvincula primero para no romper la foreign
        # key al borrar la fila del tema.
        if estado["modo_local"]:
            for r in estado["_reportes_locales"]:
                if r.get("tema_id") == tema_id:
                    r["tema_id"] = None
            estado["_temas_locales"] = [t for t in estado["_temas_locales"] if t["id"] != tema_id]
            return True
        try:
            resp = requests.patch(
                f"{SUPABASE_REPORTES_URL}?tema_id=eq.{tema_id}",
                headers=HEADERS,
                json={"tema_id": None},
                timeout=10,
            )
            resp.raise_for_status()
            resp2 = requests.delete(
                f"{SUPABASE_TEMAS_URL}?id=eq.{tema_id}",
                headers=HEADERS,
                timeout=10,
            )
            resp2.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (borrar tema):", e)
            return False

    def obtener_reportes_de_tema(tema_id):
        if estado["modo_local"]:
            return [r for r in estado["_reportes_locales"] if r.get("tema_id") == tema_id]
        try:
            resp = requests.get(
                SUPABASE_REPORTES_URL,
                headers=HEADERS,
                params={"tema_id": f"eq.{tema_id}", "select": "*", "order": "fecha.desc"},
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase GET reportes por tema [{resp.status_code}]: {resp.text}")
                return None
            return resp.json()
        except Exception as e:
            print("Error de red (reportes de tema):", repr(e))
            return None

    # ==========================================================
    # CRUD de chequeos de bienestar (WHO-5)
    # ==========================================================
    def obtener_chequeos_bienestar():
        if estado["modo_local"]:
            return estado["_bienestar_locales"]
        try:
            resp = requests.get(
                SUPABASE_BIENESTAR_URL,
                headers=HEADERS,
                params={"usuario_id": f"eq.{estado['usuario_id']}", "select": "*", "order": "fecha.desc"},
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase GET chequeos_bienestar [{resp.status_code}]: {resp.text}")
                return None
            return resp.json()
        except Exception as e:
            print("Error de red (chequeos_bienestar):", repr(e))
            return None

    def guardar_chequeo_bienestar(respuestas):
        puntaje_total = sum(respuestas)
        porcentaje = puntaje_total * 4
        datos = {
            "usuario_id": estado["usuario_id"],
            "p1": respuestas[0],
            "p2": respuestas[1],
            "p3": respuestas[2],
            "p4": respuestas[3],
            "p5": respuestas[4],
            "puntaje_total": puntaje_total,
            "porcentaje": porcentaje,
        }
        if estado["modo_local"]:
            datos["id"] = f"local-{len(estado['_bienestar_locales']) + 1}"
            datos["fecha"] = datetime.now().isoformat()
            estado["_bienestar_locales"].insert(0, datos)
            return datos
        try:
            resp = requests.post(
                SUPABASE_BIENESTAR_URL,
                headers={**HEADERS, "Prefer": "return=representation"},
                json=datos,
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase POST chequeos_bienestar [{resp.status_code}]: {resp.text}")
                return None
            creados = resp.json()
            return creados[0] if creados else None
        except Exception as e:
            print("Error de red (guardar chequeo bienestar):", repr(e))
            return None

    def _dias_desde_ultimo_chequeo_bienestar(chequeos):
        # None = todavía no hizo ninguno (distinto de "0 días", que sí es
        # un chequeo reciente) — mostrar_menu_principal usa esa distinción
        # para elegir el mensaje del aviso.
        if not chequeos:
            return None
        try:
            fecha_ultimo = datetime.fromisoformat(chequeos[0]["fecha"])
            if fecha_ultimo.tzinfo is not None:
                # Supabase devuelve timestamptz con offset (aware);
                # datetime.now() es naive — se saca el tzinfo para poder
                # restar (alcanza con un conteo aproximado de días).
                fecha_ultimo = fecha_ultimo.replace(tzinfo=None)
            return (datetime.now() - fecha_ultimo).days
        except Exception:
            return None

    # ==========================================================
    # CRUD de ejercicios de reappraisal
    # ==========================================================
    def obtener_ejercicios_reappraisal():
        if estado["modo_local"]:
            return estado["_reappraisal_locales"]
        try:
            resp = requests.get(
                SUPABASE_REAPPRAISAL_URL,
                headers=HEADERS,
                params={"usuario_id": f"eq.{estado['usuario_id']}", "select": "*", "order": "fecha.desc"},
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase GET ejercicios_reappraisal [{resp.status_code}]: {resp.text}")
                return None
            return resp.json()
        except Exception as e:
            print("Error de red (ejercicios_reappraisal):", repr(e))
            return None

    def guardar_ejercicio_reappraisal(modo, categoria, situacion_texto, paso_pensamiento, paso_hechos, paso_tercero, paso_temporal, tema_id=None):
        datos = {
            "usuario_id": estado["usuario_id"],
            "tema_id": tema_id,
            "modo": modo,
            "categoria": categoria,
            "situacion_texto": situacion_texto,
            "paso_pensamiento": paso_pensamiento,
            "paso_hechos": paso_hechos,
            "paso_tercero": paso_tercero,
            "paso_temporal": paso_temporal,
        }
        if estado["modo_local"]:
            datos["id"] = f"local-{len(estado['_reappraisal_locales']) + 1}"
            datos["fecha"] = datetime.now().isoformat()
            estado["_reappraisal_locales"].insert(0, datos)
            return datos
        try:
            resp = requests.post(
                SUPABASE_REAPPRAISAL_URL,
                headers={**HEADERS, "Prefer": "return=representation"},
                json=datos,
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase POST ejercicios_reappraisal [{resp.status_code}]: {resp.text}")
                return None
            creados = resp.json()
            return creados[0] if creados else None
        except Exception as e:
            print("Error de red (guardar ejercicio reappraisal):", repr(e))
            return None

    def contar_inventadas_completadas():
        ejercicios = obtener_ejercicios_reappraisal()
        if ejercicios is None:
            return 0
        return sum(1 for e in ejercicios if e.get("modo") == "inventada")

    # ==========================================================
    # JARDÍN INTERIOR + COLECCIÓN DE ENSEÑANZAS (gamificación)
    # ----------------------------------------------------------
    # Dos capas elegidas por Gabriel (2026-07-14) sobre la evidencia de
    # BIBLIOGRAFIA.md sección 9: (1) una colección de enseñanzas que se
    # desbloquean con cada trabajo real completado — la recompensa es
    # contenido con sentido, no puntos; (2) un jardín donde cada
    # pensamiento trabajado es una planta que crece con el trabajo y
    # florece al darse por resuelto. Regla de oro de ambas: NUNCA se
    # castiga la ausencia (nada se marchita, nada se pierde, no hay
    # rachas). El progreso se calcula contando lo ya guardado — no hay
    # tablas nuevas en Supabase y el modo local funciona igual.
    # ==========================================================
    def contar_trabajos_completados():
        reportes = obtener_reportes_usuario()
        ejercicios = obtener_ejercicios_reappraisal()
        chequeos = obtener_chequeos_bienestar()
        if reportes is None and ejercicios is None and chequeos is None:
            return None
        return len(reportes or []) + len(ejercicios or []) + len(chequeos or [])

    def controles_recompensa(texto):
        # Cajita que se suma a las pantallas de cierre de cada flujo,
        # avisando que la colección/el jardín crecieron con ese trabajo.
        return [
            ft.Container(
                content=ft.Text(texto, size=13, color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
                padding=12,
                border_radius=10,
                bgcolor=COLOR_CAJA_INFO,
                width=ancho_campo(),
            ),
            ft.TextButton("Ver mi colección de enseñanzas", on_click=lambda _: ir_a(mostrar_coleccion_perlas)),
        ]

    def mostrar_coleccion_perlas():
        pantalla(ft.ProgressRing(), ft.Text("Cargando...", color=COLOR_PRIMARIO), mostrar_volver=True)

        total = contar_trabajos_completados()
        if total is None:
            pantalla(
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED),
                ft.Text("No pudimos cargar tu colección. Revisá tu conexión e intentá de nuevo.", text_align=ft.TextAlign.CENTER),
            )
            return

        desbloqueadas = min(total, len(PERLAS_SABIDURIA))

        controles = [
            ft.Icon(ft.Icons.AUTO_AWESOME, size=50, color=COLOR_DORADO),
            ft.Text("Tu colección de enseñanzas", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Cada registro, ejercicio o chequeo que completás desbloquea una enseñanza nueva. Son tuyas para siempre.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
        ]

        if desbloqueadas == 0:
            controles.append(
                ft.Container(
                    content=ft.Text(
                        "Tu primera enseñanza te está esperando: se desbloquea apenas completes tu primer trabajo (un registro, un ejercicio o un chequeo).",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=COLOR_CAJA_SUAVE,
                    width=ancho_campo(),
                )
            )
        else:
            # La más nueva primero, destacada — las anteriores debajo.
            for i in range(desbloqueadas - 1, -1, -1):
                titulo, texto = PERLAS_SABIDURIA[i]
                es_ultima = i == desbloqueadas - 1
                controles.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(f"{i + 1}. {titulo}", weight=ft.FontWeight.BOLD, size=16),
                                ft.Text(texto, size=14, color=COLOR_TEXTO_FUERTE),
                            ],
                            spacing=4,
                        ),
                        padding=15,
                        border_radius=12,
                        bgcolor=COLOR_CAJA_INFO if es_ultima else COLOR_CAJA_SUAVE,
                        width=ancho_campo(),
                    )
                )

        restantes = len(PERLAS_SABIDURIA) - desbloqueadas
        if restantes > 0:
            controles.append(
                ft.Row(
                    [
                        ft.Icon(ft.Icons.LOCK_OUTLINE, size=16, color=COLOR_TEXTO_SUAVE),
                        ft.Text(
                            f"Te quedan {restantes} por descubrir — la próxima llega con tu próximo trabajo." if restantes != 1 else "Te queda 1 por descubrir — llega con tu próximo trabajo.",
                            size=13,
                            color=COLOR_TEXTO_SUAVE,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=6,
                )
            )
        elif desbloqueadas > 0:
            controles.append(
                ft.Text(
                    "Completaste toda la colección (por ahora). Gracias por todo ese trabajo con vos mismo/a.",
                    size=13,
                    color=COLOR_TEXTO_SUAVE,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        pantalla(*controles)

    def flor_actual():
        return estado.get("cosmetico_planta") or FLOR_POR_DEFECTO

    def fondo_actual():
        return estado.get("cosmetico_fondo") or FONDO_POR_DEFECTO

    def planta_en_flor(veces, resuelto):
        return bool(resuelto) or veces >= 6

    def etapa_planta(veces, resuelto, flor_propia=None):
        # Nunca hay etapa "marchita": las plantas solo crecen, y florecen
        # al dar el pensamiento por resuelto. La flor es la propia del
        # tema si eligió una, si no la general de Personalización, y si
        # no FLOR_POR_DEFECTO.
        if planta_en_flor(veces, resuelto):
            return flor_propia or flor_actual()
        if veces >= 4:
            return "🪴"
        if veces >= 2:
            return "🌿"
        return "🌱"

    def nivel_pase():
        # 1 nivel por cada ejercicio de "Otra perspectiva" completado.
        ejercicios = obtener_ejercicios_reappraisal()
        if ejercicios is None:
            return None
        return len(ejercicios)

    def guardar_cosmetico_supabase(campo, valor):
        if estado["modo_local"]:
            return True
        try:
            resp = requests.patch(
                f"{SUPABASE_USUARIOS_URL}?id=eq.{estado['usuario_id']}",
                headers=HEADERS,
                json={campo: valor},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print(f"Error de red (guardar {campo}):", e)
            return False

    def mostrar_elegir_flor_tema(tema):
        pantalla(ft.ProgressRing(), ft.Text("Cargando...", color=COLOR_PRIMARIO), mostrar_volver=True)

        nivel = nivel_pase()
        if nivel is None:
            pantalla(
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED),
                ft.Text("No pudimos cargar tus flores. Revisá tu conexión e intentá de nuevo.", text_align=ft.TextAlign.CENTER),
            )
            return

        def elegir(flor):
            def handler(e):
                actualizar_flor_tema(tema["id"], flor)
                tema["flor"] = flor
                ir_a(lambda: mostrar_detalle_tema(tema))
            return handler

        flor_del_tema = tema.get("flor")
        chips = []
        for item in CATALOGO_COSMETICOS:
            if nivel < item["nivel"]:
                continue
            es_actual = item["emoji"] == flor_del_tema
            chips.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(item["emoji"], size=34),
                            ft.Text(item["nombre"], size=9, color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
                        ],
                        spacing=2,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=8,
                    border_radius=12,
                    bgcolor=COLOR_CAJA_INFO if es_actual else COLOR_CAJA_SUAVE,
                    border=ft.Border.all(2, COLOR_PRIMARIO) if es_actual else None,
                    width=76,
                    on_click=elegir(item["emoji"]),
                )
            )

        pantalla(
            ft.Text(etapa_planta(6, True, flor_del_tema), size=44, text_align=ft.TextAlign.CENTER),
            ft.Text("La flor de esta planta", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                f"Elegí con qué flor va a florecer \"{(tema.get('titulo') or '')[:60]}\". "
                "Desbloqueás más flores subiendo de nivel en \"Otra perspectiva\".",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Row(chips, wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=8, run_spacing=8, width=ancho_campo()),
            ft.TextButton("Volver a mi flor general", on_click=elegir(None)) if flor_del_tema else ft.Container(),
        )

    def mostrar_personalizacion():
        pantalla(ft.ProgressRing(), ft.Text("Cargando...", color=COLOR_PRIMARIO), mostrar_volver=True)

        nivel = nivel_pase()
        if nivel is None:
            pantalla(
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED),
                ft.Text("No pudimos cargar tu nivel. Revisá tu conexión e intentá de nuevo.", text_align=ft.TextAlign.CENTER),
            )
            return

        def elegir(campo, emoji):
            def handler(e):
                estado[campo] = emoji
                guardar_cosmetico_supabase(campo, emoji)
                mostrar_personalizacion()
            return handler

        def elegir_color(hex_color):
            def handler(e):
                estado["color_fondo"] = hex_color
                page.bgcolor = hex_color
                guardar_cosmetico_supabase("color_fondo", hex_color)
                mostrar_personalizacion()
            return handler

        color_elegido = estado.get("color_fondo") or COLOR_FONDO
        swatches = []
        for c in CATALOGO_COLORES_FONDO:
            desbloqueado_color = nivel >= c["nivel"]
            es_actual = c["hex"] == color_elegido
            circulo = ft.Container(
                content=ft.Icon(ft.Icons.CHECK, size=18, color=COLOR_TEXTO_FUERTE) if es_actual else (
                    ft.Icon(ft.Icons.LOCK_OUTLINE, size=15, color=COLOR_TEXTO_SUAVE) if not desbloqueado_color else None
                ),
                width=44,
                height=44,
                border_radius=22,
                bgcolor=c["hex"],
                border=ft.Border.all(3, COLOR_PRIMARIO) if es_actual else ft.Border.all(1, COLOR_TEXTO_SUAVE),
                alignment=ft.Alignment.CENTER,
                opacity=1.0 if desbloqueado_color else 0.45,
                on_click=elegir_color(c["hex"]) if desbloqueado_color else None,
            )
            swatches.append(
                ft.Column(
                    [
                        circulo,
                        ft.Text(c["nombre"], size=10, color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
                        ft.Text("" if desbloqueado_color else f"Nivel {c['nivel']}", size=9, color=COLOR_TEXTO_SUAVE, text_align=ft.TextAlign.CENTER),
                    ],
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    width=64,
                )
            )

        proxima = next((c for c in CATALOGO_COSMETICOS if nivel < c["nivel"]), None)

        controles = [
            ft.Icon(ft.Icons.PALETTE_OUTLINED, size=50, color=COLOR_PRIMARIO),
            ft.Text("Personalización", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Para obtener nuevas opciones de personalización, practicá otras perspectivas.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                f"Tu nivel: {nivel}",
                size=13,
                color=COLOR_TEXTO_SUAVE,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(
                content=ft.Text(
                    f"En uso ahora: {flor_actual()} para tus plantas en flor · {fondo_actual()} para el fondo del menú",
                    size=13,
                    text_align=ft.TextAlign.CENTER,
                ),
                padding=12,
                border_radius=10,
                bgcolor=COLOR_CAJA_INFO,
                width=ancho_campo(),
            ),
        ]
        if proxima:
            controles.append(
                ft.Text(
                    f"Próximo desbloqueo: {proxima['emoji']} {proxima['nombre']} (nivel {proxima['nivel']} — te faltan {proxima['nivel'] - nivel}).",
                    size=12,
                    color=COLOR_TEXTO_SUAVE,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        controles.extend(
            [
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                ft.Text("Color de fondo", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Row(swatches, wrap=True, alignment=ft.MainAxisAlignment.CENTER, spacing=8, run_spacing=8, width=ancho_campo()),
                ft.Divider(height=6, color=ft.Colors.TRANSPARENT),
                ft.Text("Flores y plantas", size=16, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ]
        )

        for item in CATALOGO_COSMETICOS:
            desbloqueado = nivel >= item["nivel"]
            usos = []
            if item["emoji"] == flor_actual():
                usos.append("en uso: plantas")
            if item["emoji"] == fondo_actual():
                usos.append("en uso: fondo")

            if desbloqueado:
                filas_item = [
                    ft.Row(
                        [
                            ft.Text(item["emoji"], size=32),
                            ft.Column(
                                [
                                    ft.Text(item["nombre"], weight=ft.FontWeight.BOLD, size=14),
                                    ft.Text(" · ".join(usos) if usos else "Desbloqueada", size=11, color=COLOR_EXITO if usos else COLOR_TEXTO_SUAVE),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    ft.Row(
                        [
                            ft.TextButton("Usar en mis plantas", on_click=elegir("cosmetico_planta", item["emoji"])),
                            ft.TextButton("Usar de fondo", on_click=elegir("cosmetico_fondo", item["emoji"])),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=4,
                    ),
                ]
            else:
                # La flor bloqueada se muestra igual (apagadita), así se
                # ve QUÉ es lo que se puede desbloquear en cada nivel.
                filas_item = [
                    ft.Row(
                        [
                            ft.Container(content=ft.Text(item["emoji"], size=32), opacity=0.35),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.LOCK_OUTLINE, size=14, color=COLOR_TEXTO_SUAVE),
                                            ft.Text(item["nombre"], weight=ft.FontWeight.BOLD, size=14, color=COLOR_TEXTO_SUAVE),
                                        ],
                                        spacing=5,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Text(
                                        f"Se desbloquea en el nivel {item['nivel']} (te faltan {item['nivel'] - nivel} ejercicios)",
                                        size=11,
                                        color=COLOR_TEXTO_SUAVE,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                ]

            controles.append(
                ft.Container(
                    content=ft.Column(filas_item, spacing=2),
                    padding=12,
                    border_radius=12,
                    bgcolor=COLOR_CAJA_SUAVE if desbloqueado else ft.Colors.with_opacity(0.5, COLOR_CAJA_SUAVE),
                    width=ancho_campo(),
                )
            )

        pantalla(*controles)

    def _sesion_riega(rep):
        # Una sesión "riega" la planta solo si dejó a la persona un poco
        # mejor que como empezó (la creencia/impulso bajó, o ya quedó
        # baja) — trabajarlo y salir peor no hace crecer la planta
        # (observación de Gabriel, 2026-07-14). PERO nunca la hace
        # retroceder: una sesión difícil simplemente no suma, la planta
        # espera la próxima. En duelo/diagnóstico toda sesión cuenta:
        # ahí no hay una creencia a bajar, el trabajo mismo es el avance.
        if rep.get("tipo_situacion") in TIPOS_HECHO_CONSUMADO:
            return True
        ini = rep.get("creencia_inicial_pct")
        fin = rep.get("creencia_final_pct")
        if ini is None or fin is None:
            return True
        return fin < ini or fin <= 30

    def riegos_por_tema(reportes):
        riegos = {}
        for rep in reportes or []:
            tid = rep.get("tema_id")
            if tid is not None and _sesion_riega(rep):
                riegos[tid] = riegos.get(tid, 0) + 1
        return riegos

    def mostrar_jardin():
        pantalla(ft.ProgressRing(), ft.Text("Cargando tu jardín...", color=COLOR_PRIMARIO), mostrar_volver=True)

        temas = obtener_temas_usuario()
        reportes = obtener_reportes_usuario()

        if temas is None or reportes is None:
            pantalla(
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED),
                ft.Text("No pudimos cargar tu jardín. Revisá tu conexión e intentá de nuevo.", text_align=ft.TextAlign.CENTER),
            )
            return

        veces_por_tema = riegos_por_tema(reportes)

        controles = [
            ft.Icon(ft.Icons.LOCAL_FLORIST, size=50, color=COLOR_PRIMARIO),
            ft.Text("Tu jardín interior", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Cada pensamiento que trabajás es una planta: crece cuando trabajarlo te va dejando un poco mejor, y florece cuando lo das por resuelto. Acá nada se marchita — si un día sale difícil, la planta no retrocede: espera la próxima.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
        ]

        if not temas:
            controles.append(
                ft.Container(
                    content=ft.Text(
                        "Tu jardín está esperando su primera semilla — se planta sola cuando completás tu primer registro en \"Trabajo emocional\".",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=COLOR_CAJA_SUAVE,
                    width=ancho_campo(),
                )
            )
        else:
            # Las que están en flor van primero y con un tratamiento
            # visual bien distinto (más grandes, fondo de éxito, borde):
            # florecer es el momento importante del jardín y tiene que
            # notarse de un vistazo (pedido de Gabriel, 2026-07-14).
            temas_ordenados = sorted(
                temas,
                key=lambda t: 0 if planta_en_flor(veces_por_tema.get(t.get("id"), 0), t.get("resuelto")) else 1,
            )
            for tema in temas_ordenados:
                veces = veces_por_tema.get(tema.get("id"), 0)
                emoji = etapa_planta(veces, tema.get("resuelto"), tema.get("flor"))
                en_flor = planta_en_flor(veces, tema.get("resuelto"))
                if tema.get("resuelto"):
                    detalle = "¡Está en flor! Lo diste por resuelto."
                elif en_flor:
                    detalle = "¡Floreció de tanto trabajarla!"
                elif veces == 0:
                    detalle = "Recién plantada, juntando fuerzas."
                elif veces == 1:
                    detalle = "La regaste 1 vez."
                else:
                    detalle = f"La regaste {veces} veces."

                def abrir(e, tema=tema):
                    ir_a(lambda: mostrar_detalle_tema(tema))

                controles.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Text((f"✨{emoji}✨" if en_flor else emoji), size=44 if en_flor else 34),
                                ft.Column(
                                    [
                                        ft.Text(tema.get("titulo") or "", weight=ft.FontWeight.BOLD, size=16 if en_flor else 14),
                                        ft.Text(detalle, size=13 if en_flor else 12, color=COLOR_EXITO if en_flor else COLOR_TEXTO_SUAVE, weight=ft.FontWeight.BOLD if en_flor else None),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=12,
                        ),
                        padding=16 if en_flor else 12,
                        border_radius=12,
                        bgcolor=COLOR_EXITO_CAJA if en_flor else COLOR_CAJA_SUAVE,
                        border=ft.Border.all(2, COLOR_EXITO) if en_flor else None,
                        width=ancho_campo(),
                        on_click=abrir,
                    )
                )

        if temas and any(not planta_en_flor(veces_por_tema.get(t.get("id"), 0), t.get("resuelto")) for t in temas):
            controles.append(
                ft.Text(
                    "💧 ¿Regamos alguna? Tocá una planta para retomar ese pensamiento — cuando trabajarlo te deja mejor, crece un poco más.",
                    size=13,
                    color=COLOR_TEXTO_SUAVE,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        controles.append(
            ft.OutlinedButton(
                "Tu colección de enseñanzas",
                icon=ft.Icons.AUTO_AWESOME,
                on_click=lambda _: ir_a(mostrar_coleccion_perlas),
                width=ancho_campo(),
                height=50,
            )
        )

        pantalla(*controles)

    # ==========================================================
    # BIBLIOTECA DE CONSEJOS (accesible desde el menú principal)
    # ----------------------------------------------------------
    # A diferencia del Paso 6 (que elige consejos según la emoción/
    # situación que la persona acaba de cargar), acá puede explorar TODOS
    # los consejos disponibles libremente, sin tener que completar un
    # reporte nuevo.
    # ==========================================================
    # Cada categoría lleva su lista CBT y su lista budista, para poder
    # elegir la situación/emoción primero y recién después la filosofía.
    CATEGORIAS_CONSEJOS = [
        ("Tristeza", RECOMENDACIONES_POR_EMOCION["Tristeza"], RECOMENDACIONES_BUDISTA_POR_EMOCION["Tristeza"]),
        ("Ansiedad", RECOMENDACIONES_POR_EMOCION["Ansiedad"], RECOMENDACIONES_BUDISTA_POR_EMOCION["Ansiedad"]),
        ("Enojo", RECOMENDACIONES_POR_EMOCION["Enojo"], RECOMENDACIONES_BUDISTA_POR_EMOCION["Enojo"]),
        ("Culpa", RECOMENDACIONES_POR_EMOCION["Culpa"], RECOMENDACIONES_BUDISTA_POR_EMOCION["Culpa"]),
        ("Vergüenza", RECOMENDACIONES_POR_EMOCION["Vergüenza"], RECOMENDACIONES_BUDISTA_POR_EMOCION["Vergüenza"]),
        ("General", RECOMENDACIONES_POR_EMOCION["General"], RECOMENDACIONES_BUDISTA_POR_EMOCION["General"]),
        ("Duelo o pérdida", RECOMENDACIONES_DUELO, RECOMENDACIONES_BUDISTA_DUELO),
        ("Diagnóstico de salud", RECOMENDACIONES_DIAGNOSTICO, RECOMENDACIONES_BUDISTA_DIAGNOSTICO),
        ("Pensamientos que se repiten mucho", RECOMENDACIONES_OBSESION, RECOMENDACIONES_BUDISTA_OBSESION),
    ]

    def mostrar_consejos_lista(titulo, recomendaciones):
        lista = [
            ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=COLOR_EXITO, size=18), ft.Text(rec, width=ancho_campo(280))])
            for rec in recomendaciones
        ]
        pantalla(
            ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=40, color=COLOR_DORADO),
            ft.Text(titulo, size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            *lista,
        )

    def mostrar_consejos_elegir_filosofia(nombre, cbt, budista):
        pantalla(
            ft.Text(nombre, size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("¿Qué tipo de consejos preferís ver?", color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            ft.ElevatedButton(
                "Terapia Cognitivo Conductual",
                on_click=lambda _: ir_a(lambda: mostrar_consejos_lista(f"Consejos para {nombre.lower()}", cbt)),
                width=ancho_campo(),
                height=60,
            ),
            ft.ElevatedButton(
                "Filosofía budista tibetana",
                on_click=lambda _: ir_a(lambda: mostrar_consejos_lista(f"Consejos budistas para {nombre.lower()}", budista)),
                width=ancho_campo(),
                height=60,
            ),
        )

    def mostrar_consejos_biblioteca():
        def abrir(nombre, cbt, budista):
            def handler(e):
                ir_a(lambda: mostrar_consejos_elegir_filosofia(nombre, cbt, budista))
            return handler

        botones = [
            ft.OutlinedButton(nombre, on_click=abrir(nombre, cbt, budista), width=ancho_campo(), height=50)
            for nombre, cbt, budista in CATEGORIAS_CONSEJOS
        ]

        pantalla(
            ft.Icon(ft.Icons.MENU_BOOK, size=40, color=COLOR_PRIMARIO),
            ft.Text("Consejos", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Elegí qué tipo de situación o emoción te interesa, sin necesidad de cargar un reporte.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            *botones,
        )

    def mostrar_paso_elegir_recomendacion():
        def elegir(tipo):
            def handler(e):
                ir_a(lambda: mostrar_paso_recomendaciones(tipo))
            return handler

        pantalla(
            ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=40, color=COLOR_DORADO),
            ft.Text("¿Qué tipo de consejos preferís ver?", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Podés ver los dos si querés, uno después del otro.",
                text_align=ft.TextAlign.CENTER,
                color=COLOR_TEXTO_MEDIO,
            ),
            ft.ElevatedButton(
                "Consejos de Terapia Cognitivo Conductual",
                on_click=elegir(TIPO_RECOMENDACION_CBT),
                width=ancho_campo(),
                height=60,
            ),
            ft.ElevatedButton(
                "Consejos desde la filosofía budista tibetana",
                on_click=elegir(TIPO_RECOMENDACION_BUDISTA),
                width=ancho_campo(),
                height=60,
            ),
            mostrar_volver=False,
        )

    def mostrar_paso_recomendaciones(tipo=TIPO_RECOMENDACION_CBT):
        r = estado["reporte_actual"]

        if tipo == TIPO_RECOMENDACION_BUDISTA:
            if r.get("tipo_situacion") == TIPO_DUELO:
                recomendaciones = mezclar_recomendaciones(RECOMENDACIONES_BUDISTA_DUELO)
            elif r.get("tipo_situacion") == TIPO_DIAGNOSTICO:
                recomendaciones = mezclar_recomendaciones(RECOMENDACIONES_BUDISTA_DIAGNOSTICO)
            elif r.get("tipo_situacion") == TIPO_OBSESION:
                recomendaciones = mezclar_recomendaciones(RECOMENDACIONES_BUDISTA_OBSESION)
            else:
                recomendaciones = mezclar_recomendaciones(recomendaciones_budistas_para(r["emocion_inicial"]))
        else:
            en_tratamiento = estado.get("en_tratamiento")
            # Lo que marcó en el checklist del Paso 3 también alimenta esto: se
            # suma (hasta 2, para no saturar la lista) un consejo
            # puntual por cada distorsión marcada, además del banco de
            # recomendaciones por emoción/situación de siempre. Con TOC
            # nunca hay distorsiones marcadas (ese paso se salta), así
            # que ahí queda como una lista vacía sin efecto.
            tips_distorsion = [
                RECOMENDACIONES_POR_DISTORSION[d]
                for d in (r.get("distorsiones_lista") or [])
                if d in RECOMENDACIONES_POR_DISTORSION
            ][:2]
            if r.get("tipo_situacion") == TIPO_DUELO:
                recomendaciones = mezclar_recomendaciones(tips_distorsion + recomendaciones_con_tratamiento(RECOMENDACIONES_DUELO, FRASE_PROFESIONAL_DUELO_EN_TRATAMIENTO, en_tratamiento), mantener_ultima=True)
            elif r.get("tipo_situacion") == TIPO_DIAGNOSTICO:
                recomendaciones = mezclar_recomendaciones(tips_distorsion + recomendaciones_con_tratamiento(RECOMENDACIONES_DIAGNOSTICO, FRASE_PROFESIONAL_DIAGNOSTICO_EN_TRATAMIENTO, en_tratamiento), mantener_ultima=True)
            elif r.get("tipo_situacion") == TIPO_OBSESION:
                recomendaciones = mezclar_recomendaciones(tips_distorsion + recomendaciones_con_tratamiento(RECOMENDACIONES_OBSESION, FRASE_PROFESIONAL_OBSESION_EN_TRATAMIENTO, en_tratamiento), mantener_ultima=True)
            else:
                recomendaciones = mezclar_recomendaciones(tips_distorsion + recomendaciones_para(r["emocion_inicial"])[:5])

        # El reporte se guarda una sola vez (con las recomendaciones que
        # se le mostraron primero), aunque después la persona alterne
        # entre los dos tipos de consejo — así no se duplica ni se
        # sobreescribe en cada toque de "ver el otro".
        if not r.get("_guardado"):
            r["recomendaciones"] = recomendaciones
            r["_guardado_ok"] = guardar_reporte_supabase(r)
            r["_guardado"] = True

            tema_vinculado = r.get("tema_obj")
            if r["_guardado_ok"] and not tema_vinculado:
                # Primera vez con este pensamiento: se registra
                # automáticamente como un pensamiento a seguir, sin
                # preguntar — el título es el propio pensamiento
                # automático, y el color siempre lo calcula la app
                # sola según el avance (ya no se elige a mano).
                titulo_tema = (r.get("pensamiento_automatico") or r.get("situacion") or "Pensamiento")[:80]
                color_inicial = color_por_avance(r.get("creencia_final_pct"))
                nuevo_tema = crear_tema(titulo_tema, color_inicial, color_automatico=True)
                if nuevo_tema:
                    r["tema_id"] = nuevo_tema["id"]
                    r["tema_obj"] = nuevo_tema
                    vincular_reporte_a_tema(r)
                    tema_vinculado = nuevo_tema
            elif r["_guardado_ok"] and tema_vinculado:
                # Ya era un pensamiento en seguimiento: el color se
                # actualiza siempre solo, con la creencia final de esta
                # sesión — así queda al día aunque la persona no toque
                # nada y vuelva directo al menú.
                nuevo_color = color_por_avance(r.get("creencia_final_pct"))
                actualizar_tema(tema_vinculado["id"], nuevo_color, tema_vinculado.get("estado") or "", color_automatico=True)
                tema_vinculado["color"] = nuevo_color
        guardado_ok = r.get("_guardado_ok", True)

        lista_recomendaciones = [
            ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=COLOR_EXITO, size=18), ft.Text(rec, width=ancho_campo(280))])
            for rec in recomendaciones
        ]

        titulo_paso = "Ahora, algo para vos" if tipo == TIPO_RECOMENDACION_CBT else "Una mirada distinta para esto"
        if r.get("tipo_situacion") == TIPO_OBSESION:
            # Acá el objetivo no es "levantar el ánimo": es tolerar el
            # impulso sin hacer la compulsión, así que la intro no habla
            # de ánimo sino de eso.
            intro_paso = (
                "Estas son algunas ideas concretas para tolerar el impulso sin hacer la compulsión. Elegí una y probala la próxima vez que aparezca."
                if tipo == TIPO_RECOMENDACION_CBT else
                "Estas son algunas prácticas de la tradición budista tibetana para acompañar el impulso sin pelear con él."
            )
        else:
            intro_paso = (
                "Estas son algunas ideas concretas que suelen ayudar a levantar el ánimo. Elegí una que te cierre y probala hoy, a tu ritmo."
                if tipo == TIPO_RECOMENDACION_CBT else
                "Estas son algunas prácticas de la tradición budista tibetana para acompañar este momento."
            )

        controles = [
            ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=40, color=COLOR_DORADO),
            ft.Text(titulo_paso, size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(intro_paso, text_align=ft.TextAlign.CENTER, color=COLOR_TEXTO_MEDIO),
            *lista_recomendaciones,
        ]

        if r.get("rondas_reflexion", 0) > 0 and r.get("creencia_final_pct", 0) >= UMBRAL_CREENCIA_ALTA:
            controles.append(
                ft.Text(
                    "A veces un pensamiento no afloja del todo en una sola sesión, y está bien — lo importante es haberle dado varias vueltas distintas. Este registro queda guardado para que lo puedas retomar más adelante.",
                    text_align=ft.TextAlign.CENTER,
                    color=COLOR_TEXTO_MEDIO,
                    size=13,
                )
            )

        if not guardado_ok:
            controles.append(
                ft.Text(
                    "No pudimos guardar este reporte en tu historial (revisá tu conexión), pero las recomendaciones son igual de válidas.",
                    color=ft.Colors.RED,
                    text_align=ft.TextAlign.CENTER,
                )
            )

        if r.get("tema_obj") and r.get("_anterior"):
            # Solo tiene sentido si ya venía de antes (retoma): la
            # primera vez que se completa un reporte, la persona recién
            # acaba de contar cómo está con esto en los pasos previos
            # (creencia final, pensamiento alternativo) — preguntarle
            # de nuevo ahí mismo era redundante.
            controles.append(
                ft.OutlinedButton(
                    "Contar cómo estoy con esto",
                    on_click=lambda _: ir_a(lambda: mostrar_paso_actualizar_tema(r["tema_obj"], volver_a_menu=True, creencia_reciente=r.get("creencia_final_pct"))),
                    width=ancho_campo(),
                    height=50,
                )
            )

        otro_tipo = TIPO_RECOMENDACION_BUDISTA if tipo == TIPO_RECOMENDACION_CBT else TIPO_RECOMENDACION_CBT
        texto_otro = (
            "Ver los consejos budistas tibetanos"
            if otro_tipo == TIPO_RECOMENDACION_BUDISTA else
            "Ver los consejos cognitivo conductuales"
        )
        controles.append(
            ft.OutlinedButton(
                texto_otro,
                on_click=lambda _: ir_a(lambda: mostrar_paso_recomendaciones(otro_tipo)),
                width=ancho_campo(),
                height=50,
            )
        )

        controles.extend(controles_recompensa("🌱 Tu jardín y tu colección de enseñanzas crecieron con este registro."))
        controles.append(
            ft.ElevatedButton(
                "Volver al menú principal",
                on_click=lambda _: (historial.clear(), ir_a(mostrar_menu_principal)),
                width=ancho_campo(),
                height=50,
            )
        )

        pantalla(*controles, mostrar_volver=False)

    def mostrar_paso_actualizar_tema(tema, volver_a_menu=True, creencia_reciente=None):
        # El color ya no se elige a mano en ningún lado: la app lo
        # calcula siempre sola según el avance (creencia_final_pct de
        # la sesión más reciente vinculada a este tema). Acá solo se
        # invita a poner en palabras cómo está la persona con esto.
        input_estado = ft.TextField(
            label="¿Cómo dirías que estás con este pensamiento ahora?",
            hint_text="Ej: \"Sigo igual\", \"Mejorando de a poco\", \"Bastante mejor\", \"Resuelto\"...",
            value=tema.get("estado") or "",
            width=ancho_campo(),
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def guardar(e):
            texto_estado = (input_estado.value or "").strip()
            if detectar_riesgo_suicida(texto_estado):
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(texto_estado):
                ir_a(mostrar_paso_riesgo_terceros)
                return
            creencia_para_calcular = creencia_reciente
            if creencia_para_calcular is None:
                reportes_tema = obtener_reportes_de_tema(tema["id"]) or []
                if reportes_tema:
                    mas_reciente = max(reportes_tema, key=lambda x: x.get("fecha") or "")
                    creencia_para_calcular = mas_reciente.get("creencia_final_pct")
            color_final = color_por_avance(creencia_para_calcular)
            ok = actualizar_tema(tema["id"], color_final, texto_estado, color_automatico=True)
            if not ok:
                mostrar_error(texto_error, "No pudimos guardar el cambio. Revisá tu conexión e intentá de nuevo.")
                return
            tema["color"] = color_final
            tema["color_automatico"] = True
            tema["estado"] = texto_estado
            if volver_a_menu:
                historial.clear()
                ir_a(mostrar_menu_principal)
            else:
                ir_a(lambda: mostrar_detalle_tema(tema))

        pantalla(
            ft.Text("¿Cómo venís con este pensamiento?", size=18, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "El color se calcula solo, según tu avance — acá podés contar con tus palabras cómo te sentís.",
                size=12,
                color=COLOR_TEXTO_SUAVE,
                text_align=ft.TextAlign.CENTER,
            ),
            input_estado,
            texto_error,
            ft.ElevatedButton("Guardar", on_click=guardar, width=ancho_campo(), height=50),
        )

    # ==========================================================
    # PENSAMIENTOS QUE ESTOY TRABAJANDO (temas)
    # ==========================================================
    def guardar_instrucciones_temas_vistas_supabase():
        if estado["modo_local"]:
            return True
        try:
            resp = requests.patch(
                f"{SUPABASE_USUARIOS_URL}?id=eq.{estado['usuario_id']}",
                headers=HEADERS,
                json={"vio_instrucciones_temas": True},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (guardar vio_instrucciones_temas):", e)
            return False

    def mostrar_instrucciones_temas(temas, permitir_volver=False):
        # Se muestra una sola vez, la primera vez que hay al menos un
        # pensamiento guardado (ver mostrar_temas), con la flechita de
        # volver ya habilitada para poder salir sin tocar "Entendido".
        # Después queda disponible a mano con el ícono de instrucciones
        # de esta pantalla (ver _mostrar_lista_temas).
        def continuar(e):
            estado["vio_instrucciones_temas"] = True
            guardar_instrucciones_temas_vistas_supabase()
            ir_a(lambda: _mostrar_lista_temas(temas))

        pantalla(
            ft.Icon(ft.Icons.PALETTE_OUTLINED, size=60, color=COLOR_PRIMARIO),
            ft.Text("Cómo leer tus pensamientos guardados", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Acá vas a encontrar todas las situaciones, pensamientos o emociones que fuiste registrando. Cada uno tiene un color que muestra cómo venís: va de rojo (recién empezando) a celeste (que ya casi no te pesa). Si en algún momento sentís que lo resolviste del todo, también podés marcarlo vos mismo/a como \"resuelto\" — no hace falta esperar a que el color cambie solo. Y las veces que haga falta, podés volver a trabajar sobre el mismo pensamiento.",
                size=18,
                color=COLOR_TEXTO_FUERTE,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.ElevatedButton("Entendido", on_click=continuar, width=ancho_campo(), height=50),
            mostrar_volver=permitir_volver,
        )

    def _mostrar_lista_temas(temas):
        # La planta de cada pensamiento (la misma del jardín) también se
        # muestra acá: Gabriel quiere que sea el ancla visual de la app.
        # El punto de color (avance) queda chiquito al lado del estado.
        veces_por_tema = riegos_por_tema(obtener_reportes_usuario())

        tarjetas = []
        for tema in temas:
            def abrir(e, tema=tema):
                ir_a(lambda: mostrar_detalle_tema(tema))

            desde_txt = (tema.get("creado_en") or tema.get("fecha") or "")[:10]
            veces = veces_por_tema.get(tema.get("id"), 0)
            emoji = etapa_planta(veces, tema.get("resuelto"), tema.get("flor"))
            en_flor = planta_en_flor(veces, tema.get("resuelto"))

            tarjetas.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(f"✨{emoji}✨" if en_flor else emoji, size=38 if en_flor else 30),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(tema.get("titulo") or "", weight=ft.FontWeight.BOLD, size=15 if en_flor else 14),
                                            ft.Icon(ft.Icons.CHECK_CIRCLE, color=COLOR_EXITO, size=15) if tema.get("resuelto") else ft.Container(),
                                        ],
                                        spacing=6,
                                    ),
                                    ft.Row(
                                        [
                                            ft.Container(width=10, height=10, bgcolor=color_hex(tema.get("color")), border_radius=5),
                                            ft.Text(tema.get("estado") or "Sin estado todavía", size=12, color=COLOR_TEXTO_MEDIO),
                                        ],
                                        spacing=6,
                                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    ),
                                    ft.Text(f"Desde {desde_txt}" if desde_txt else "", size=11, color=COLOR_TEXTO_SUAVE),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=COLOR_EXITO_CAJA if en_flor else COLOR_CAJA_SUAVE,
                    border=ft.Border.all(2, COLOR_EXITO) if en_flor else None,
                    width=ancho_campo(),
                    on_click=abrir,
                )
            )

        pantalla(
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        tooltip="Instrucciones",
                        on_click=lambda _: ir_a(lambda: mostrar_instrucciones_temas(temas, permitir_volver=True)),
                        icon_color=ft.Colors.WHITE,
                        bgcolor=COLOR_PRIMARIO,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            ft.Text("Pensamientos que estás trabajando", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("Tocá uno para ver cómo venís avanzando, o para retomarlo.", color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "🌱 Hacé crecer tu jardín: cuando trabajar un pensamiento sin resolver te deja un poco mejor, su planta crece.",
                size=13,
                color=COLOR_TEXTO_SUAVE,
                text_align=ft.TextAlign.CENTER,
            ),
            *tarjetas,
        )

    def mostrar_temas():
        pantalla(ft.ProgressRing(), ft.Text("Cargando...", color=COLOR_PRIMARIO), mostrar_volver=True)

        temas = obtener_temas_usuario()

        if temas is None:
            pantalla(
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED),
                ft.Text("No pudimos cargar tus temas. Revisá tu conexión e intentá de nuevo.", text_align=ft.TextAlign.CENTER),
            )
            return

        if not temas:
            pantalla(
                ft.Icon(ft.Icons.TRACK_CHANGES, size=50, color=COLOR_TEXTO_SUAVE),
                ft.Text(
                    "Todavía no tenés ningún pensamiento acá. Se van a ir agregando solos cada vez que completes un reporte nuevo.",
                    text_align=ft.TextAlign.CENTER,
                ),
            )
            return

        if not estado.get("vio_instrucciones_temas"):
            mostrar_instrucciones_temas(temas, permitir_volver=True)
            return

        _mostrar_lista_temas(temas)

    # ==========================================================
    # CHEQUEO DE BIENESTAR (WHO-5)
    # ----------------------------------------------------------
    # A diferencia de "Pensamientos que estoy trabajando" (que sigue
    # situaciones puntuales), esto es un pulso general de cómo viene la
    # persona en su día a día, pensado para repetirse cada 1-2 semanas y
    # ver la evolución en el tiempo — por eso vive en su propia sección
    # del menú principal, no adentro de un reporte.
    # ==========================================================
    def guardar_instrucciones_bienestar_vistas_supabase():
        if estado["modo_local"]:
            return True
        try:
            resp = requests.patch(
                f"{SUPABASE_USUARIOS_URL}?id=eq.{estado['usuario_id']}",
                headers=HEADERS,
                json={"vio_instrucciones_bienestar": True},
                timeout=10,
            )
            resp.raise_for_status()
            return True
        except Exception as e:
            print("Error de red (guardar vio_instrucciones_bienestar):", e)
            return False

    def mostrar_instrucciones_bienestar(permitir_volver=False):
        def continuar(e):
            estado["vio_instrucciones_bienestar"] = True
            guardar_instrucciones_bienestar_vistas_supabase()
            ir_a(_mostrar_submenu_bienestar)

        pantalla(
            ft.Icon(ft.Icons.INSIGHTS, size=60, color=COLOR_PRIMARIO),
            ft.Text("Chequeo de bienestar", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Cada 1 o 2 semanas podés responder 5 preguntas cortas y validadas (WHO-5) sobre cómo te sentiste "
                "EN GENERAL últimamente — a diferencia de un registro de pensamiento, esto no es sobre una situación "
                "puntual. Con eso armamos un historial con colores para que puedas ver de un vistazo cómo fue "
                "cambiando tu bienestar con el tiempo.",
                size=18,
                color=COLOR_TEXTO_FUERTE,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.ElevatedButton("Entendido", on_click=continuar, width=ancho_campo(), height=50),
            mostrar_volver=permitir_volver,
        )

    def mostrar_bienestar():
        if not estado.get("vio_instrucciones_bienestar"):
            mostrar_instrucciones_bienestar(permitir_volver=True)
            return
        _mostrar_submenu_bienestar()

    def _mostrar_submenu_bienestar():
        pantalla(
            ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.HELP_OUTLINE,
                        tooltip="Instrucciones",
                        on_click=lambda _: ir_a(lambda: mostrar_instrucciones_bienestar(permitir_volver=True)),
                        icon_color=ft.Colors.WHITE,
                        bgcolor=COLOR_PRIMARIO,
                    ),
                ],
                alignment=ft.MainAxisAlignment.END,
            ),
            ft.Text("Chequeo de bienestar", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Un pulso corto de cómo venís en general, para ver tu evolución en el tiempo.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.ElevatedButton(
                "Completar un nuevo autorreporte",
                icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                on_click=lambda _: ir_a(mostrar_paso_bienestar),
                width=ancho_campo(),
                height=50,
            ),
            ft.OutlinedButton(
                "Ver historial",
                icon=ft.Icons.HISTORY,
                on_click=lambda _: ir_a(mostrar_historial_bienestar),
                width=ancho_campo(),
                height=50,
            ),
        )

    def mostrar_historial_bienestar():
        pantalla(ft.ProgressRing(), ft.Text("Cargando...", color=COLOR_PRIMARIO), mostrar_volver=True)

        chequeos = obtener_chequeos_bienestar()

        if chequeos is None:
            pantalla(
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED),
                ft.Text("No pudimos cargar tus chequeos. Revisá tu conexión e intentá de nuevo.", text_align=ft.TextAlign.CENTER),
            )
            return

        if not chequeos:
            pantalla(
                ft.Icon(ft.Icons.INSIGHTS, size=50, color=COLOR_TEXTO_SUAVE),
                ft.Text("Todavía no hiciste ningún autorreporte. Empezá con el de hoy.", text_align=ft.TextAlign.CENTER),
            )
            return

        tarjetas = []
        for c in chequeos:
            color = color_por_avance(100 - (c.get("porcentaje") or 0))
            fecha_txt = (c.get("fecha") or "")[:10]
            tarjetas.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(width=16, height=16, bgcolor=color_hex(color), border_radius=8),
                            ft.Column(
                                [
                                    ft.Text(DESCRIPCION_BIENESTAR_POR_COLOR.get(color, ""), weight=ft.FontWeight.BOLD),
                                    ft.Text(fecha_txt, size=11, color=COLOR_TEXTO_SUAVE),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Text(f"{c.get('porcentaje', 0)}%", size=13, color=COLOR_TEXTO_MEDIO),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=COLOR_CAJA_SUAVE,
                    width=ancho_campo(),
                )
            )

        pantalla(
            ft.Text("Historial de autorreportes", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            *tarjetas,
        )

    def mostrar_paso_bienestar():
        dropdowns = [
            ft.Dropdown(
                label=pregunta,
                options=[ft.dropdown.Option(key=str(valor), text=texto) for texto, valor in OPCIONES_BIENESTAR],
                width=ancho_campo(),
            )
            for pregunta in PREGUNTAS_BIENESTAR
        ]
        texto_error = ft.Text("", color=ft.Colors.RED)

        def guardar(e):
            respuestas = []
            for dd in dropdowns:
                if dd.value is None:
                    mostrar_error(texto_error, "Respondé las 5 preguntas para poder calcular tu chequeo.")
                    return
                respuestas.append(int(dd.value))
            chequeo = guardar_chequeo_bienestar(respuestas)
            if chequeo is None:
                mostrar_error(texto_error, "No pudimos guardar el chequeo. Revisá tu conexión e intentá de nuevo.")
                return
            ir_a(lambda: mostrar_paso_bienestar_resultado(chequeo))

        pantalla(
            ft.Text("¿Cómo te sentiste en las últimas 2 semanas?", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("Elegí la opción que mejor describa cada frase.", color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            *dropdowns,
            texto_error,
            ft.ElevatedButton("Ver mi resultado", on_click=guardar, width=ancho_campo(), height=50),
        )

    def mostrar_paso_bienestar_resultado(chequeo):
        porcentaje = chequeo.get("porcentaje", 0)
        color = color_por_avance(100 - porcentaje)

        # Regla pedida por Gabriel (2026-07-14): NUNCA decirle a alguien
        # que se siente mal que "está mal" — sería contraproducente. Para
        # cualquier resultado por debajo de verde, el mensaje valida el
        # gesto de cuidarse y alienta, sin nombrar cuán bajo salió. Para
        # los resultados buenos, el mensaje también es cálido y celebra.
        if color == "Celeste":
            mensaje = (
                "¡Qué bueno verte así! Tus respuestas muestran un momento muy luminoso. Sea lo que sea que "
                "estés haciendo, te está haciendo bien — seguí regalándote esos espacios."
            )
        elif color == "Verde":
            mensaje = (
                "Venís bien, y eso no es casualidad: cuidarse, prestarse atención y darse espacio también es un "
                "logro tuyo. Las ideas de abajo pueden ayudarte a sostener este buen momento."
            )
        elif color == "Amarillo":
            mensaje = (
                "Gracias por regalarte este momento para mirar cómo venís — eso ya es cuidarte. Hay semanas de "
                "todo tipo, y ninguna te define. Abajo te dejamos un par de ideas elegidas especialmente para "
                "darte una mano estos días."
            )
        elif color == "Naranja":
            mensaje = (
                "Frenar un momento para preguntarte cómo estás, como acabás de hacer, ya es un acto de cuidado "
                "enorme. Las cosas buenas se construyen de a poco: elegí una sola de las ideas de abajo y "
                "probala a tu ritmo, sin exigencias."
            )
        else:
            mensaje = (
                "Gracias por animarte a mirar cómo venís: ese gesto habla muy bien de vos. No estás solo/a en "
                "esto — probá alguna de las ideas de abajo, con la más chiquita alcanza para empezar. Y si en "
                "algún momento querés compañía, el botón \"Necesito ayuda ahora\" está siempre a mano."
            )

        # Consejos personalizados: se eligen según la(s) pregunta(s) del
        # WHO-5 donde salió más bajo (no un mensaje genérico), para que
        # apunten a lo que realmente le está costando a la persona.
        respuestas = [chequeo.get(f"p{i}", 0) for i in range(1, 6)]
        minimo = min(respuestas)
        indices_bajos = [i for i, v in enumerate(respuestas) if v == minimo][:2]
        tips = []
        for i in indices_bajos:
            tips.extend(mezclar_recomendaciones(RECOMENDACIONES_BIENESTAR_POR_PREGUNTA[i])[:2])

        lista_tips = [
            ft.Row([ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, color=COLOR_EXITO, size=18), ft.Text(tip, width=ancho_campo(280))])
            for tip in tips
        ]

        def volver_al_submenu_bienestar(e):
            historial.clear()
            historial.append(mostrar_menu_principal)
            ir_a(mostrar_bienestar)

        def ir_a_bloque(destino):
            def manejador(e):
                historial.clear()
                historial.append(mostrar_menu_principal)
                ir_a(destino)
            return manejador

        # Regla pedida por Gabriel (2026-07-14): si el puntaje da por
        # debajo de 60%, acá NO se muestra ni el punto de color ni el
        # porcentaje (verlo en frío puede desanimar justo a quien peor
        # la está pasando) — solo el mensaje cálido, los consejos y una
        # invitación a los otros dos bloques. El porcentaje sí queda
        # visible en el historial de autorreportes, como siempre.
        if porcentaje < 60:
            estado["apoyo_menu_pendiente"] = True
            controles = [
                ft.Icon(ft.Icons.VOLUNTEER_ACTIVISM, size=50, color=COLOR_PRIMARIO),
                ft.Text("Gracias por frenar a mirarte", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(mensaje, color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            ]
        else:
            controles = [
                ft.Container(width=60, height=60, bgcolor=color_hex(color), border_radius=30),
                ft.Text(f"{porcentaje}% de bienestar", size=24, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(mensaje, color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            ]
        if lista_tips:
            controles.append(ft.Text("Un par de ideas concretas para esta semana:", weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER))
            controles.extend(lista_tips)
        if porcentaje < 60:
            controles.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Y no tenés que hacerlo solo/a: DRE tiene dos herramientas pensadas justo "
                                "para días así. Podés probarlas ahora o cuando quieras.",
                                text_align=ft.TextAlign.CENTER,
                            ),
                            ft.OutlinedButton(
                                "Trabajo emocional",
                                icon=ft.Icons.SELF_IMPROVEMENT,
                                on_click=ir_a_bloque(mostrar_trabajo_emocional),
                                width=ancho_campo(240),
                                height=45,
                            ),
                            ft.OutlinedButton(
                                "Otra perspectiva",
                                icon=ft.Icons.AUTORENEW,
                                on_click=ir_a_bloque(mostrar_reappraisal),
                                width=ancho_campo(240),
                                height=45,
                            ),
                        ],
                        spacing=8,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=COLOR_CAJA_INFO,
                    width=ancho_campo(),
                )
            )
        controles.extend(controles_recompensa("✨ Tu colección de enseñanzas creció con este chequeo."))
        controles.append(ft.ElevatedButton("Volver", on_click=volver_al_submenu_bienestar, width=ancho_campo(), height=50))

        pantalla(*controles, mostrar_volver=False)

    def mostrar_paso_marcar_resuelto(tema):
        # Mensaje que la persona se escribe a sí misma sobre cómo
        # resolvió este tipo de situación/pensamiento, para poder leerlo
        # si le vuelve a pasar. Solo se guarda cuando lo da por
        # TOTALMENTE resuelto (acción explícita, no se infiere del color
        # ni del % de creencia).
        input_reflexion = ft.TextField(
            label="Tu mensaje para el futuro",
            hint_text="Escribite algo sobre cómo resolviste esto, que te sirva si te vuelve a pasar",
            value=tema.get("reflexion_final") or "",
            width=ancho_campo(),
            multiline=True,
            min_lines=4,
            max_lines=8,
        )
        texto_error = ft.Text("", color=ft.Colors.RED)

        def guardar(e):
            reflexion = (input_reflexion.value or "").strip()
            if not reflexion:
                mostrar_error(texto_error, "Escribí aunque sea unas líneas para poder guardarlo.")
                return
            if detectar_riesgo_suicida(reflexion):
                ir_a(mostrar_paso_crisis_1)
                return
            if detectar_riesgo_terceros(reflexion):
                ir_a(mostrar_paso_riesgo_terceros)
                return
            ok = marcar_tema_resuelto(tema["id"], reflexion, resuelto=True)
            if not ok:
                mostrar_error(texto_error, "No pudimos guardarlo. Revisá tu conexión e intentá de nuevo.")
                return
            tema["resuelto"] = True
            tema["reflexion_final"] = reflexion
            ir_a(lambda: mostrar_detalle_tema(tema))

        pantalla(
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=40, color=COLOR_EXITO),
            ft.Text("¡Diste esto por resuelto!", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Escribite un mensaje a vos mismo/a sobre cómo lo resolviste — algo que te sirva de guía si te vuelve a pasar más adelante.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            input_reflexion,
            texto_error,
            ft.ElevatedButton("Guardar", on_click=guardar, width=ancho_campo(), height=50),
        )

    def mostrar_paso_quitar_tema(tema):
        texto_error = ft.Text("", color=ft.Colors.RED)

        def confirmar(e):
            ok = borrar_tema(tema["id"])
            if not ok:
                mostrar_error(texto_error, "No pudimos quitarlo. Revisá tu conexión e intentá de nuevo.")
                return
            historial.clear()
            ir_a(mostrar_temas)

        pantalla(
            ft.Icon(ft.Icons.DELETE_OUTLINE, size=40, color=COLOR_TEXTO_MEDIO),
            ft.Text("¿Quitar este pensamiento de tu lista?", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                f"\"{tema.get('titulo') or ''}\" va a dejar de aparecer en \"Pensamientos que estoy trabajando\". "
                "Los registros que ya hiciste sobre esto no se borran: siguen estando en tu Historial general.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            texto_error,
            ft.ElevatedButton("Sí, quitarlo", on_click=confirmar, width=ancho_campo(), height=50),
        )

    def mostrar_detalle_tema(tema):
        pantalla(ft.ProgressRing(), ft.Text("Cargando...", color=COLOR_PRIMARIO), mostrar_volver=True)

        reportes = obtener_reportes_de_tema(tema["id"])

        filas_seguimiento = []
        if reportes:
            # De la primera vez a la más reciente: leído de arriba a
            # abajo, cuenta la evolución igual que la persona la vivió
            # (más fácil de leer que "más nuevo primero" para ver si la
            # creencia fue bajando).
            reportes_orden = sorted(reportes, key=lambda x: x.get("fecha") or "")

            for rep in reportes_orden:
                fecha_txt = (rep.get("fecha") or "")[:10]
                situacion_resumida = (rep.get("situacion") or "")[:50]
                if len(rep.get("situacion") or "") > 50:
                    situacion_resumida += "..."
                filas_seguimiento.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    f"{fecha_txt} · {rep.get('emocion_inicial') or ''} {rep.get('intensidad_inicial', '')}/10",
                                    size=12,
                                    color=COLOR_TEXTO_SUAVE,
                                ),
                                ft.Text(
                                    f"{'Impulso' if rep.get('tipo_situacion') == TIPO_OBSESION else 'Creencia'}: {rep.get('creencia_inicial_pct')}% → {rep.get('creencia_final_pct')}%",
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(situacion_resumida, size=12, color=COLOR_TEXTO_MEDIO) if situacion_resumida else ft.Container(),
                            ],
                            spacing=2,
                        ),
                        padding=10,
                        border_radius=10,
                        bgcolor=COLOR_CAJA_SUAVE,
                        width=ancho_campo(),
                        on_click=lambda e, rep=rep: ir_a(lambda: mostrar_detalle_reporte(rep)),
                    )
                )
        else:
            filas_seguimiento.append(
                ft.Text("Todavía no lo retomaste desde que lo guardaste.", size=13, color=COLOR_TEXTO_SUAVE)
            )

        veces_txt = f"Lo trabajaste {len(reportes or [])} vez" if len(reportes or []) == 1 else f"Lo trabajaste {len(reportes or [])} veces"

        def retomar(e):
            # Si ya lo había dado por resuelto y lo vuelve a enfrentar,
            # ya no tiene sentido que siga marcado como "resuelto" —
            # se desmarca solo (el mensaje que se había escrito no se
            # borra, puede volver a marcarlo resuelto más adelante).
            if tema.get("resuelto"):
                marcar_tema_resuelto(tema["id"], tema.get("reflexion_final") or "", resuelto=False)
                tema["resuelto"] = False
            page.run_task(iniciar_nuevo_reporte, tema)

        ultima_creencia = reportes_orden[-1].get("creencia_final_pct") if reportes else None

        def ir_a_actualizar(e):
            ir_a(lambda: mostrar_paso_actualizar_tema(tema, volver_a_menu=False, creencia_reciente=ultima_creencia))

        def ir_a_marcar_resuelto(e):
            ir_a(lambda: mostrar_paso_marcar_resuelto(tema))

        def ir_a_quitar(e):
            ir_a(lambda: mostrar_paso_quitar_tema(tema))

        # Puente hacia el bloque de Reappraisal: los dos bloques se
        # complementan (acá se procesa el malestar real, allá se entrena
        # el cambio de perspectiva en frío), así que desde un pensamiento
        # ya registrado se puede saltar directo a practicar con él — pero
        # solo si "situaciones propias" ya está desbloqueado, para no
        # romper el arco de práctica (inventadas primero) del bloque 3.
        reappraisal_desbloqueado = contar_inventadas_completadas() >= UMBRAL_REAPPRAISAL_PROPIAS

        def practicar_reappraisal(e):
            ir_a(lambda: mostrar_reappraisal_ejercicio("propia", None, tema.get("titulo") or "", tema_id=tema["id"]))

        def desmarcar_resuelto(e):
            marcar_tema_resuelto(tema["id"], tema.get("reflexion_final") or "", resuelto=False)
            tema["resuelto"] = False
            ir_a(lambda: mostrar_detalle_tema(tema))

        bloque_reflexion = []
        if tema.get("resuelto"):
            bloque_reflexion = [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Row(
                                [ft.Icon(ft.Icons.CHECK_CIRCLE, color=COLOR_EXITO, size=18), ft.Text("Diste esto por resuelto", weight=ft.FontWeight.BOLD, size=14)],
                            ),
                            ft.Text(tema.get("reflexion_final") or "", size=13),
                        ],
                        spacing=6,
                    ),
                    padding=15,
                    border_radius=12,
                    bgcolor=COLOR_EXITO_CAJA,
                    width=ancho_campo(),
                ),
                ft.Row(
                    [
                        ft.TextButton("Editar mensaje", on_click=ir_a_marcar_resuelto),
                        ft.TextButton("Ya no lo doy por resuelto", on_click=desmarcar_resuelto),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ]

        emoji_planta = etapa_planta(sum(1 for rep in (reportes or []) if _sesion_riega(rep)), tema.get("resuelto"), tema.get("flor"))
        en_flor = planta_en_flor(sum(1 for rep in (reportes or []) if _sesion_riega(rep)), tema.get("resuelto"))
        pantalla(
            ft.Text(f"✨{emoji_planta}✨" if en_flor else emoji_planta, size=54, text_align=ft.TextAlign.CENTER),
            ft.TextButton(
                "Cambiar la flor de esta planta",
                icon=ft.Icons.PALETTE_OUTLINED,
                on_click=lambda _: ir_a(lambda: mostrar_elegir_flor_tema(tema)),
            ),
            ft.Container(width=14, height=14, bgcolor=color_hex(tema.get("color")), border_radius=7),
            ft.Text(tema.get("titulo") or "", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(tema.get("estado") or "Sin estado todavía", color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            *bloque_reflexion,
            ft.Text("Cómo venís avanzando", weight=ft.FontWeight.BOLD, size=14),
            ft.Text(veces_txt if reportes else "", size=12, color=COLOR_TEXTO_SUAVE),
            *filas_seguimiento,
            ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
            ft.ElevatedButton("Enfrentar este pensamiento de nuevo", on_click=retomar, width=ancho_campo(), height=50),
            ft.OutlinedButton("Practicar otra perspectiva con esto", icon=ft.Icons.AUTORENEW, on_click=practicar_reappraisal, width=ancho_campo(), height=50) if reappraisal_desbloqueado else ft.Container(),
            ft.OutlinedButton("Contar cómo estoy con esto", on_click=ir_a_actualizar, width=ancho_campo(), height=50),
            ft.OutlinedButton("Dar esto por resuelto", on_click=ir_a_marcar_resuelto, width=ancho_campo(), height=50) if not tema.get("resuelto") else ft.Container(),
            ft.TextButton("Quitar de mis temas", on_click=ir_a_quitar, style=ft.ButtonStyle(color=ft.Colors.RED_700)),
        )

    # ==========================================================

    # ==========================================================
    # HISTORIAL DE SITUACIONES
    # ==========================================================
    def obtener_reportes_usuario():
        if estado["modo_local"]:
            return estado["_reportes_locales"]
        try:
            resp = requests.get(
                SUPABASE_REPORTES_URL,
                headers=HEADERS,
                params={"usuario_id": f"eq.{estado['usuario_id']}", "select": "*", "order": "fecha.desc"},
                timeout=10,
            )
            if not resp.ok:
                print(f"Error Supabase GET reportes_emocionales [{resp.status_code}]: {resp.text}")
                return None
            return resp.json()
        except Exception as e:
            print("Error de red (historial):", repr(e))
            return None

    def mostrar_compartir_historial(reportes):
        csv_contenido = generar_csv_historial(reportes)
        texto_resumen = generar_texto_resumen_historial(reportes)
        data_uri_csv = "data:text/csv;charset=utf-8," + urllib.parse.quote(csv_contenido)
        url_whatsapp = "https://wa.me/?text=" + urllib.parse.quote(texto_resumen)
        url_mail = "mailto:?subject=" + urllib.parse.quote("Mi evolución en DRE") + "&body=" + urllib.parse.quote(texto_resumen)

        pantalla(
            ft.Icon(ft.Icons.SHARE_OUTLINED, size=40, color=COLOR_PRIMARIO),
            ft.Text("Compartir tu evolución", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Podés descargar tu historial como planilla, o compartir un resumen directo por WhatsApp o mail. Vos elegís con quién.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.ElevatedButton("Descargar planilla (CSV)", icon=ft.Icons.DOWNLOAD, url=data_uri_csv, width=ancho_campo(), height=50),
            ft.OutlinedButton("Compartir resumen por WhatsApp", icon=ft.Icons.CHAT_OUTLINED, url=url_whatsapp, width=ancho_campo(), height=50),
            ft.OutlinedButton("Compartir resumen por mail", icon=ft.Icons.EMAIL_OUTLINED, url=url_mail, width=ancho_campo(), height=50),
            ft.Text(
                "El resumen por WhatsApp/mail incluye los últimos 15 registros. La planilla descargada tiene todo tu historial completo.",
                size=12,
                color=COLOR_TEXTO_SUAVE,
                text_align=ft.TextAlign.CENTER,
            ),
        )

    # El historial general de TODOS los reportes ("Ver como veniste
    # resolviendo esto") se elimino (2026-07-13): una simulacion de uso
    # mostro que casi nadie lo abria, y Gabriel ya lo sospechaba desde
    # antes. Los historiales POR BLOQUE siguen existiendo (el timeline de
    # cada pensamiento en Trabajo emocional, y el historial de chequeos
    # de bienestar). Lo unico que valia la pena conservar de esa pantalla
    # era "Compartir mi evolucion", que ahora tiene su propia entrada.
    def mostrar_compartir_evolucion():
        pantalla(ft.ProgressRing(), ft.Text("Cargando...", color=COLOR_PRIMARIO), mostrar_volver=True)

        reportes = obtener_reportes_usuario()

        if reportes is None:
            pantalla(
                ft.Icon(ft.Icons.ERROR_OUTLINE, size=50, color=ft.Colors.RED),
                ft.Text("No pudimos cargar tus registros. Revisá tu conexión e intentá de nuevo.", text_align=ft.TextAlign.CENTER),
            )
            return

        if not reportes:
            pantalla(
                ft.Icon(ft.Icons.AUTO_STORIES, size=50, color=COLOR_TEXTO_SUAVE),
                ft.Text("Todavía no registraste ninguna situación, así que no hay nada para compartir por ahora.", text_align=ft.TextAlign.CENTER),
            )
            return

        mostrar_compartir_historial(reportes)

    def mostrar_detalle_reporte(rep):
        fecha_txt = (rep.get("fecha") or "")[:10]

        def bloque(titulo, contenido):
            if not contenido:
                return ft.Container()
            return ft.Column(
                [ft.Text(titulo, weight=ft.FontWeight.BOLD, size=13, color=COLOR_TEXTO_MEDIO), ft.Text(contenido, width=ancho_campo())],
                spacing=2,
            )

        # Los campos "evidencia_a_favor/en_contra" y "pensamiento
        # alternativo" se reutilizan con otro sentido según el tipo de
        # situación (duelo/diagnóstico: culpa y apoyos; TOC: impulso y
        # compromiso de prevención), así que las etiquetas se adaptan
        # para que el historial se lea bien en cada caso.
        tipo_sit = rep.get("tipo_situacion")
        if tipo_sit == TIPO_OBSESION:
            label_a_favor, label_en_contra, label_alternativo, label_creencia = (
                "Impulso/compulsión identificada", "¿Real o imaginado?", "Compromiso de prevención + qué hizo en cambio", "Impulso inicial → final",
            )
        elif tipo_sit in TIPOS_HECHO_CONSUMADO:
            label_a_favor, label_en_contra, label_alternativo, label_creencia = (
                "Culpa/autorreproche", "Apoyos / qué valora", "Pensamiento o acción reconfortante", "Peso del pensamiento inicial → final",
            )
        else:
            label_a_favor, label_en_contra, label_alternativo, label_creencia = (
                "Evidencia a favor", "Evidencia en contra", "Pensamiento alternativo", "Creencia inicial → final",
            )

        pantalla(
            ft.Text(fecha_txt, size=14, color=COLOR_TEXTO_SUAVE),
            bloque("Tipo de situación", tipo_sit),
            bloque("Situación", rep.get("situacion")),
            bloque("Cómo le fue con lo de la vez pasada", rep.get("feedback_recomendacion_anterior")),
            bloque("Por qué cree que le funcionó (o no)", rep.get("feedback_recomendacion_porque")),
            bloque("Pensamiento automático", rep.get("pensamiento_automatico")),
            bloque("Emoción", f"{rep.get('emocion_inicial')} (intensidad {rep.get('intensidad_inicial')}/10)"),
            bloque(label_a_favor, rep.get("evidencia_a_favor")),
            bloque(label_en_contra, rep.get("evidencia_en_contra")),
            bloque("Distorsiones identificadas", rep.get("distorsiones")),
            bloque(label_alternativo, rep.get("pensamiento_alternativo")),
            bloque("Reflexiones adicionales", rep.get("reflexiones_extra")),
            bloque(label_creencia, f"{rep.get('creencia_inicial_pct')}% → {rep.get('creencia_final_pct')}%"),
            bloque("Recomendaciones dadas", rep.get("recomendaciones_dadas")),
        )

    # --- Arranque de la app ---
    ir_a(mostrar_login)


# ==========================================================
# --- ARRANQUE ---
# ----------------------------------------------------------
# Local (tu compu): "python app.py" abre la ventana de escritorio.
# Producción (Render): se define la variable de entorno FLET_WEB=1, y en
# ese caso este archivo expone "app" (una app ASGI) para que la sirva
# uvicorn con el comando: uvicorn app:app --host 0.0.0.0 --port $PORT
#
# Para producción se arma la app ASGI llamando directo a
# flet_web.fastapi.app(...) en vez de usar el atajo ft.app(...,
# export_asgi_app=True): ese atajo no deja pasar app_name/app_short_name/
# app_description, que son justo los que hacen que al "agregar a la
# pantalla de inicio" desde el celular aparezca como "DRE" (con el
# ícono propio en assets/icons/) en vez de "Flet".
# ==========================================================
if os.environ.get("FLET_WEB", "").lower() in ("1", "true", "yes"):
    import flet_web.fastapi as flet_web_fastapi
    from starlette.middleware.base import BaseHTTPMiddleware
    from starlette.responses import Response as _RespuestaHTTP

    ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")

    app = flet_web_fastapi.app(
        main,
        assets_dir=ASSETS_DIR,
        app_name="DRE",
        app_short_name="DRE",
        app_description="Diario de Reflexión Emocional — un espacio tranquilo para poner en palabras lo que sentís y acompañarte a pensarlo de otra forma.",
    )

    # ------------------------------------------------------------------
    # Guardián de reconexión (bug de celulares suspendidos): cuando el
    # teléfono se bloquea, el navegador mata el websocket que conecta la
    # app con el servidor. El servidor guarda la sesión igual (1 hora),
    # pero a veces el cliente de Flet no logra reconectarse solo y la
    # pantalla queda "sorda": se ve todo pero ningún botón responde.
    # Este script (inyectado en el index.html que sirve Flet) vigila el
    # websocket desde el navegador: al volver a primer plano espera unos
    # segundos a que Flet reconecte solo, y si la conexión sigue muerta
    # recarga la página automáticamente — lo mismo que hoy hay que hacer
    # a mano saliendo y volviendo a entrar. El borrador del reporte en
    # curso se recupera solo (ya se guarda en el navegador a cada paso).
    #
    # Pantallita de carga (pedido de Gabriel): mientras la app se
    # reconecta/recarga se muestra un arbolito que crece (semilla ->
    # arbol) sobre fondo crema, y se saca recien cuando el servidor
    # vuelve a hablar (primer mensaje por el websocket nuevo). Una marca
    # en sessionStorage ("dre_recargando") hace que la pagina recargada
    # muestre el arbolito desde el primer instante, tapando la carga
    # generica de Flet. (rb"": el bytes crudo deja pasar los \\uXXXX de
    # los emoji tal cual al JavaScript.)
    # ------------------------------------------------------------------
    _SCRIPT_GUARDIAN = rb"""<script>
(function () {
  var NativoWS = window.WebSocket;
  if (!NativoWS) return;
  var ultimo = null;
  var overlay = null;

  function leerMarca() {
    try { return sessionStorage.getItem("dre_recargando") === "1"; } catch (e) { return false; }
  }
  function ponerMarca() { try { sessionStorage.setItem("dre_recargando", "1"); } catch (e) {} }
  function sacarMarca() { try { sessionStorage.removeItem("dre_recargando"); } catch (e) {} }

  function mostrarOverlay() {
    if (overlay) return;
    window.__dre_overlay_visto = Date.now();  // diagnostico: quedo registrado si se llego a mostrar
    overlay = document.createElement("div");
    overlay.id = "dre-overlay-reconexion";
    overlay.style.cssText = "position:fixed;top:0;left:0;right:0;bottom:0;z-index:2147483647;" +
      "background:#E8DBC0;display:flex;flex-direction:column;align-items:center;justify-content:center;" +
      "font-family:sans-serif;";
    var emoji = document.createElement("div");
    emoji.style.cssText = "font-size:78px;line-height:1;";
    var texto = document.createElement("div");
    texto.style.cssText = "margin-top:22px;font-size:16px;color:#6B5D4A;";
    texto.textContent = "Volviendo a tu espacio...";
    overlay.appendChild(emoji);
    overlay.appendChild(texto);
    var etapas = ["\uD83C\uDF30", "\uD83C\uDF31", "\uD83C\uDF3F", "\uD83E\uDEB4", "\uD83C\uDF33"];
    var i = 0;
    emoji.textContent = etapas[0];
    overlay.__timer = setInterval(function () {
      i = (i + 1) % etapas.length;
      emoji.textContent = etapas[i];
    }, 550);
    (document.body || document.documentElement).appendChild(overlay);
    // Red de seguridad: si en 25 s el servidor no volvio (p. ej. sin
    // internet), se destapa la pantalla igual para no dejarla presa.
    setTimeout(function () { sacarMarca(); ocultarOverlay(); }, 25000);
  }
  function ocultarOverlay() {
    if (!overlay) return;
    clearInterval(overlay.__timer);
    if (overlay.parentNode) overlay.parentNode.removeChild(overlay);
    overlay = null;
  }
  window.__dre_probar_overlay = mostrarOverlay;   // manijas de diagnostico
  window.__dre_ocultar_overlay = ocultarOverlay;

  function WSEnvuelto(url, protocolos) {
    var ws = (protocolos === undefined) ? new NativoWS(url) : new NativoWS(url, protocolos);
    ultimo = ws;
    window.__dre_ws = ws;  // manija de diagnostico (leer readyState desde la consola)
    ws.addEventListener("message", function alPrimerMensaje() {
      ws.removeEventListener("message", alPrimerMensaje);
      // El servidor hablo por la conexion nueva: la app ya es funcional.
      sacarMarca();
      setTimeout(ocultarOverlay, 400);
    });
    return ws;
  }
  WSEnvuelto.prototype = NativoWS.prototype;
  WSEnvuelto.CONNECTING = NativoWS.CONNECTING;
  WSEnvuelto.OPEN = NativoWS.OPEN;
  WSEnvuelto.CLOSING = NativoWS.CLOSING;
  WSEnvuelto.CLOSED = NativoWS.CLOSED;
  window.WebSocket = WSEnvuelto;

  // Si esta pagina ES la recarga del guardian, arrancar tapado con el
  // arbolito (en vez de la pantalla de carga generica de Flet).
  if (leerMarca()) {
    if (document.body || document.documentElement) mostrarOverlay();
    else document.addEventListener("DOMContentLoaded", mostrarOverlay);
  }

  function chequear(intentos) {
    if (document.visibilityState !== "visible") { ocultarOverlay(); return; }
    if (!ultimo) return;
    if (ultimo.readyState === NativoWS.OPEN) { ocultarOverlay(); return; }
    mostrarOverlay();
    if (ultimo.readyState === NativoWS.CONNECTING && intentos > 0) {
      setTimeout(function () { chequear(intentos - 1); }, 3000);
      return;
    }
    ponerMarca();
    window.location.reload();
  }
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState !== "visible") return;
    setTimeout(function () { chequear(2); }, 3500);
  });
  window.addEventListener("pageshow", function (ev) {
    if (ev.persisted) setTimeout(function () { chequear(2); }, 3500);
  });
})();
</script>"""

    class _MiddlewareGuardian(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            respuesta = await call_next(request)
            if "text/html" not in (respuesta.headers.get("content-type") or ""):
                return respuesta
            cuerpo = b""
            async for parte in respuesta.body_iterator:
                cuerpo += parte
            if b"<head>" in cuerpo:
                # Va al principio del <head> para correr ANTES de que el
                # cliente de Flet abra su websocket (si no, no lo vería).
                cuerpo = cuerpo.replace(b"<head>", b"<head>" + _SCRIPT_GUARDIAN, 1)
            headers = dict(respuesta.headers)
            headers.pop("content-length", None)
            return _RespuestaHTTP(content=cuerpo, status_code=respuesta.status_code, headers=headers)

    app = _MiddlewareGuardian(app)
else:
    ft.app(target=main)
