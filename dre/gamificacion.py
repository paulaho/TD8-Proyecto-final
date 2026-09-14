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
