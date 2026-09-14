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

