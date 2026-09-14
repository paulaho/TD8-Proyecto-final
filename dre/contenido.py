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

UMBRAL_REAPPRAISAL_PROPIAS = 1
