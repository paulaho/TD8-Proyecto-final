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

