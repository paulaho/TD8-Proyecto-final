import random

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
