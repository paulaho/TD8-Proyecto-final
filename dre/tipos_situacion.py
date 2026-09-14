from dre.seguridad import _normalizar_riesgo

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
