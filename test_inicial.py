import flet as ft
import requests

# Constantes visuales acordes al diseño de la app
COLOR_PRIMARIO = "#3D7A7B"
COLOR_TEXTO_MEDIO = "#665C4C"
COLOR_TARJETA = "#FFFAF0"

OPCIONES_CONVIVENCIA = ["Solo/a", "Con mis padres", "Con pareja", "Con amigos/as / compañeros/as", "Con hijos/as"]
OPCIONES_HERMANOS = ["No tengo hermanos", "Sí, tengo hermanos/as"]
OPCIONES_OCUPACION = ["Estudio", "Trabajo", "Estudio y trabajo", "Ninguna por el momento"]

OPCIONES_REGULACION = [
    {
        "nivel": 1,
        "label": "Nunca lo escuché o tengo muy poca idea.",
        "titulo": "¡Bienvenido/a! No te preocupes, es algo muy simple:",
        "texto": (
            "La regulación emocional no es más que la capacidad que todos tenemos para cambiar "
            "cómo nos sentimos ante una situación, en lugar de reaccionar en automático.\n\n"
            "En esta app no vas a encontrar teorías difíciles: vas a entrenar a tu mente con ejercicios "
            "rápidos para aprender a 'darle la vuelta' a los pensamientos que te generan malestar."
        ),
    },
    {
        "nivel": 2,
        "label": "Escuché el tema y entiendo la idea general, pero no suelo practicarlo a conciencia.",
        "titulo": "¡Bárbaro! Tenés la base clara:",
        "texto": (
            "Como sabrás, regular las emociones no significa reprimirlas ni 'pensar en positivo' "
            "de forma mágica, sino notar cuándo un pensamiento nos está jugando una mala pasada "
            "y buscar una lectura más útil de lo que pasa.\n\n"
            "A través de situaciones breves de la vida cotidiana, acá vas a entrenar la flexibilidad "
            "para encontrar esa otra perspectiva de forma rápida y natural."
        ),
    },
    {
        "nivel": 3,
        "label": "Conozco bastante del tema y suelo intentar aplicarlo en mi día a día.",
        "titulo": "¡Genial! Vas a sacarle mucho provecho a esto:",
        "texto": (
            "La regulación emocional abarca varias estrategias, pero esta app se enfoca en el "
            "entrenamiento de la reevaluación cognitiva (cognitive reappraisal): la habilidad de modificar "
            "la interpretación que le damos a un estresor para regular su impacto emocional.\n\n"
            "Los ejercicios están diseñados para poner a prueba tu flexibilidad mental frente a sesgos "
            "automáticos, ayudándote a ejercitar encuadres más realistas y funcionales en segundos."
        ),
    },
]

def mostrar_test_inicial(page: ft.Page, estado: dict, SUPABASE_USUARIOS_URL: str, HEADERS: dict, al_completar_callback):
    """
    Renderiza el test inicial guiado:
      Paso 1: Entorno familiar y contexto cotidiano.
      Paso 2: Nivel de familiaridad con el concepto de Regulación Emocional.
      Paso 3: Pantalla de confirmación y bienvenida con la explicación personalizada según el nivel.
    Al finalizar, persiste las respuestas y ejecuta `al_completar_callback()`.
    """

    def ancho_campo(base=340):
        disponible = (page.width or (base + 70)) - 70
        return max(260, min(base, disponible))

    respuestas = {
        "convivencia": None,
        "hermanos": None,
        "ocupacion": None,
        "pareja": None,
        "nivel_regulacion": None,
        "familiaridad_regulacion_texto": None,
    }

    def render_contenedor(controles):
        columna = ft.Column(
            controles,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        tarjeta = ft.Container(
            content=columna,
            padding=24,
            margin=15,
            border_radius=20,
            bgcolor=ft.Colors.with_opacity(0.97, COLOR_TARJETA),
            expand=True,
        )
        page.controls.clear()
        page.add(ft.Container(content=tarjeta, alignment=ft.Alignment.CENTER, expand=True))
        page.update()

    # -------------------------------------------------------------
    # PASO 1: Contexto familiar y cotidiano
    # -------------------------------------------------------------
    def mostrar_paso_familia():
        dd_convivencia = ft.Dropdown(
            label="¿Con quién vivís actualmente?",
            options=[ft.dropdown.Option(op) for op in OPCIONES_CONVIVENCIA],
            value=respuestas["convivencia"],
            width=ancho_campo(),
        )
        dd_hermanos = ft.Dropdown(
            label="¿Tenés hermanos/as?",
            options=[ft.dropdown.Option(op) for op in OPCIONES_HERMANOS],
            value=respuestas["hermanos"],
            width=ancho_campo(),
        )
        dd_ocupacion = ft.Dropdown(
            label="¿A qué te dedicás principalmente?",
            options=[ft.dropdown.Option(op) for op in OPCIONES_OCUPACION],
            value=respuestas["ocupacion"],
            width=ancho_campo(),
        )
        dd_pareja = ft.Dropdown(
            label="¿Estás en pareja?",
            options=[ft.dropdown.Option("Sí"), ft.dropdown.Option("No")],
            value=respuestas["pareja"],
            width=ancho_campo(),
        )
        txt_error = ft.Text("", color=ft.Colors.RED, size=13, text_align=ft.TextAlign.CENTER)

        def validar_y_avanzar(e):
            if not dd_convivencia.value or not dd_hermanos.value or not dd_ocupacion.value or not dd_pareja.value:
                txt_error.value = "Por favor respondé todas las preguntas para personalizar tus ejercicios."
                page.update()
                return

            respuestas["convivencia"] = dd_convivencia.value
            respuestas["hermanos"] = dd_hermanos.value
            respuestas["ocupacion"] = dd_ocupacion.value
            respuestas["pareja"] = dd_pareja.value
            mostrar_extras_personalizacion(
                page,
                respuestas,
                lambda extras: (respuestas.update(extras), mostrar_paso_regulacion()),
            )

        controles = [
            ft.Icon(ft.Icons.FAMILY_RESTROOM, size=48, color=COLOR_PRIMARIO),
            ft.Text("Queremos conocerte un poco mejor", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "Esta información ayuda a que la IA genere situaciones de práctica personalizadas sobre tu entorno real.",
                color=COLOR_TEXTO_MEDIO,
                text_align=ft.TextAlign.CENTER,
                size=14,
            ),
            dd_convivencia,
            dd_hermanos,
            dd_pareja,
            dd_ocupacion,
            txt_error,
            ft.ElevatedButton("Siguiente", on_click=validar_y_avanzar, width=ancho_campo(), height=48),
        ]
        render_contenedor(controles)

    # -------------------------------------------------------------
    # PASO 2: Pregunta sobre Regulación Emocional
    # -------------------------------------------------------------
    def mostrar_paso_regulacion():
        rg_opciones = ft.RadioGroup(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Radio(
                                value=str(op["nivel"]),
                            ),
                            ft.Text(
                                f"Opción {chr(64 + op['nivel'])}: {op['label']}",
                                size=14,
                                color=COLOR_TEXTO_MEDIO,
                                expand=True,
                            ),
                        ],
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.START,
                    )
                    for op in OPCIONES_REGULACION
                ],
                spacing=12,
            ),
            value=(
                str(respuestas["nivel_regulacion"])
                if respuestas["nivel_regulacion"]
                else None
            ),
        )
        txt_error = ft.Text(
            "",
            color=ft.Colors.RED,
            size=13,
            text_align=ft.TextAlign.CENTER,
        )

        def validar_y_mostrar_explicacion(e):
            if not rg_opciones.value:
                txt_error.value = "Por favor elegí la opción que mejor describa tu situación."
                page.update()
                return

            nivel_elegido = int(rg_opciones.value)
            op_data = next(op for op in OPCIONES_REGULACION if op["nivel"] == nivel_elegido)
            respuestas["nivel_regulacion"] = nivel_elegido
            respuestas["familiaridad_regulacion_texto"] = op_data["label"]
            mostrar_paso_explicacion(op_data)

        controles = [
            ft.Icon(ft.Icons.PSYCHOLOGY_OUTLINED, size=48, color=COLOR_PRIMARIO),
            ft.Text("Punto de partida", size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text(
                "¿Qué tan familiarizado/a estás con el término 'Regulación Emocional'?",
                size=16,
                weight=ft.FontWeight.W_600,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(content=rg_opciones, width=ancho_campo(460)),
            txt_error,
            ft.Row(
                [
                    ft.TextButton("Volver", on_click=lambda _: mostrar_paso_familia()),
                    ft.ElevatedButton("Continuar", on_click=validar_y_mostrar_explicacion, width=160, height=48),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
            ),
        ]
        render_contenedor(controles)

    # -------------------------------------------------------------
    # PASO 3: Explicación Personalizada según la respuesta elegida
    # -------------------------------------------------------------
    def mostrar_paso_explicacion(op_data):
        def finalizar_y_guardar(e):
            perfil_contexto = {
                "convivencia": respuestas["convivencia"],
                "hermanos": respuestas["hermanos"],
                "ocupacion": respuestas["ocupacion"],
                "pareja": respuestas["pareja"],
                "nivel_regulacion": respuestas["nivel_regulacion"],
                "familiaridad_regulacion": respuestas["familiaridad_regulacion_texto"],
            }

            perfil_contexto["extras_completados"] = True
            for k in ("estudio_nivel", "trabajo_modalidad", "salud_temas", "vinculos_temas", "amigos_satisfaccion", "apoyo_cuando_solo"):
                if respuestas.get(k):
                    perfil_contexto[k] = respuestas[k]

            # Guardar en el estado local en memoria
            estado["perfil_contexto"] = perfil_contexto
            estado["realizo_test_inicial"] = True

            # Guardar en Supabase si no es modo local
            if not estado.get("modo_local"):
                try:
                    resp = requests.patch(
                        f"{SUPABASE_USUARIOS_URL}?id=eq.{estado['usuario_id']}",
                        headers=HEADERS,
                        json={
                            "perfil_contexto": perfil_contexto,
                            "realizo_test_inicial": True,
                        },
                        timeout=10,
                    )
                    resp.raise_for_status()
                except Exception as ex:
                    print("Error guardando el test inicial en Supabase:", ex)

            # Derivar al flujo principal mediante el callback
            al_completar_callback()

        controles = [
            ft.Icon(ft.Icons.AUTO_AWESOME, size=48, color=COLOR_PRIMARIO),
            ft.Text(op_data["titulo"], size=20, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Container(
                content=ft.Text(
                    op_data["texto"],
                    size=15,
                    color=COLOR_TEXTO_MEDIO,
                    text_align=ft.TextAlign.CENTER,
                ),
                width=ancho_campo(460),
                padding=10,
            ),
            ft.Row(
                [
                    ft.TextButton("Cambiar opción", on_click=lambda _: mostrar_paso_regulacion()),
                    ft.ElevatedButton("¡Empezar a entrenar!", on_click=finalizar_y_guardar, width=200, height=48),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
            ),
        ]
        render_contenedor(controles)

    # Iniciar en el primer paso
    mostrar_paso_familia()

OPCIONES_ESTUDIO_NIVEL = ["Secundaria", "Terciario o universitario", "Posgrado", "Cursos o idiomas"]
OPCIONES_TRABAJO_MODALIDAD = [
    "En relación de dependencia (tengo jefe/a o equipo)",
    "Por cuenta propia (trabajo con clientes)",
    "Un poco de ambas",
]
OPCIONES_SALUD_TEMAS = [
    "Sueño y descanso",
    "Actividad física y rutinas",
    "Consultas y controles médicos",
    "Dolores o molestias físicas",
    "Cansancio y energía",
]
OPCIONES_VINCULOS_TEMAS = [
    "Grupos de amigos y juntadas",
    "Conocer gente nueva",
    "Poner límites o decir que no",
    "Mensajes y redes sociales",
    "Mi pareja",
]

OPCIONES_AMIGOS_SATISFACCION = ["Muy conforme", "Conforme", "Poco conforme", "Nada conforme"]
OPCIONES_APOYO_SOLEDAD = ["Siempre", "Casi siempre", "A veces", "Casi nunca"]


def mostrar_extras_personalizacion(page: ft.Page, perfil_base: dict, al_terminar):
    """
    Pantalla opcional para personalizar Salud, Vínculos y Trabajo/estudio.
    perfil_base: dict con al menos "ocupacion" y "pareja".
    al_terminar(extras: dict): recibe solo lo que la persona eligió ({} si omitió).
    """
    ocupacion = perfil_base.get("ocupacion") or ""
    estudia = ocupacion in ("Estudio", "Estudio y trabajo")
    trabaja = ocupacion in ("Trabajo", "Estudio y trabajo")
    en_pareja = perfil_base.get("pareja") == "Sí"

    def ancho_campo(base=340):
        disponible = (page.width or (base + 70)) - 70
        return max(260, min(base, disponible))

    dd_estudio = (
        ft.Dropdown(
            label="¿Qué estás estudiando?",
            options=[ft.dropdown.Option(op) for op in OPCIONES_ESTUDIO_NIVEL],
            width=ancho_campo(),
        )
        if estudia else None
    )
    dd_trabajo = (
        ft.Dropdown(
            label="¿Cómo trabajás?",
            options=[ft.dropdown.Option(op) for op in OPCIONES_TRABAJO_MODALIDAD],
            width=ancho_campo(),
        )
        if trabaja else None
    )
    checks_salud = [ft.Checkbox(label=op) for op in OPCIONES_SALUD_TEMAS]
    checks_vinculos = [
        ft.Checkbox(label=op) for op in OPCIONES_VINCULOS_TEMAS if en_pareja or op != "Mi pareja"
    ]

    dd_amigos = ft.Dropdown(
        label="¿Qué tan conforme estás con la cantidad de amigos/as que tenés?",
        options=[ft.dropdown.Option(op) for op in OPCIONES_AMIGOS_SATISFACCION],
        width=ancho_campo(),
    )
    dd_apoyo = ft.Dropdown(
        label="Cuando te sentís solo/a, ¿tenés a quién recurrir?",
        options=[ft.dropdown.Option(op) for op in OPCIONES_APOYO_SOLEDAD],
        width=ancho_campo(),
    )

    def terminar(guardar):
        extras = {}
        if guardar:
            if dd_estudio is not None and dd_estudio.value:
                extras["estudio_nivel"] = dd_estudio.value
            if dd_trabajo is not None and dd_trabajo.value:
                extras["trabajo_modalidad"] = dd_trabajo.value
            temas_salud = [c.label for c in checks_salud if c.value]
            if temas_salud:
                extras["salud_temas"] = temas_salud
            temas_vinculos = [c.label for c in checks_vinculos if c.value]
            if temas_vinculos:
                extras["vinculos_temas"] = temas_vinculos
            if dd_amigos is not None and dd_amigos.value:
                extras["amigos_satisfaccion"] = dd_amigos.value
            if dd_apoyo is not None and dd_apoyo.value:
                extras["apoyo_soledad"] = dd_apoyo.value
            if dd_amigos.value:
                extras["amigos_satisfaccion"] = dd_amigos.value
            if dd_apoyo.value:
                extras["apoyo_cuando_solo"] = dd_apoyo.value
        al_terminar(extras)

    controles = [
        ft.Icon(ft.Icons.TUNE, size=48, color=COLOR_PRIMARIO),
        ft.Text("Un último paso (opcional)", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        ft.Text(
            "Es solo para que los ejercicios se parezcan más a tu día a día. Podés saltearlo.",
            color=COLOR_TEXTO_MEDIO,
            text_align=ft.TextAlign.CENTER,
            size=14,
        ),
    ]
    if dd_estudio is not None:
        controles.append(dd_estudio)
    if dd_trabajo is not None:
        controles.append(dd_trabajo)
    controles += [
        ft.Text("Salud: ¿qué te gustaría practicar?", size=15, weight=ft.FontWeight.W_600),
        ft.Container(content=ft.Column(checks_salud, spacing=0), width=ancho_campo(460)),
        ft.Text("Vínculos", size=15, weight=ft.FontWeight.W_600),
        dd_amigos,
        dd_apoyo,
        ft.Text("¿En qué situaciones sociales te gustaría practicar?", size=14, color=COLOR_TEXTO_MEDIO),
        ft.Container(content=ft.Column(checks_vinculos, spacing=0), width=ancho_campo(460)),
        ft.Text("Podés elegir varias opciones o ninguna.", size=12, color=COLOR_TEXTO_MEDIO),
        ft.Row(
            [
                ft.TextButton("Omitir", on_click=lambda _: terminar(False)),
                ft.ElevatedButton("Listo", on_click=lambda _: terminar(True), width=160, height=48),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=15,
        ),
    ]

    columna = ft.Column(
        controles,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=14,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )
    tarjeta = ft.Container(
        content=columna,
        padding=24,
        margin=15,
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.97, COLOR_TARJETA),
        expand=True,
    )
    page.controls.clear()
    page.add(ft.Container(content=tarjeta, alignment=ft.Alignment.CENTER, expand=True))
    page.update()