import flet as ft

from dre.tema import (
    MENTO_AMARILLO,
    MENTO_VERDE,
    MENTO_NARANJA,
    MENTO_CELESTE,
)

MENTO_CATEGORIAS = [
    {"clave": "familia", "nombre": "Familia", "color": MENTO_AMARILLO, "icono": ft.Icons.FAMILY_RESTROOM},
    {"clave": "salud", "nombre": "Salud", "color": MENTO_VERDE, "icono": ft.Icons.FAVORITE},
    {"clave": "vinculos", "nombre": "Vínculos", "color": MENTO_NARANJA, "icono": ft.Icons.GROUPS},
    {"clave": "trabajo", "nombre": "Trabajo o estudio", "color": MENTO_CELESTE, "icono": ft.Icons.WORK},
]

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
