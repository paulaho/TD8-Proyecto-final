import flet as ft
import requests

# Constantes visuales acordes al diseño de la app
COLOR_PRIMARIO = "#E95F83"
COLOR_TEXTO_MEDIO = "#555555"
COLOR_TARJETA = "#FFFFFF"

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
            alignment=ft.MainAxisAlignment.CENTER,
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
        page.bgcolor = ft.Colors.WHITE
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
        border_radius=24, bgcolor=ft.Colors.WHITE, color="#202020")
        dd_hermanos = ft.Dropdown(
            label="¿Tenés hermanos/as?",
            options=[ft.dropdown.Option(op) for op in OPCIONES_HERMANOS],
            value=respuestas["hermanos"],
            width=ancho_campo(),
        border_radius=24, bgcolor=ft.Colors.WHITE, color="#202020")
        dd_ocupacion = ft.Dropdown(
            label="¿A qué te dedicás principalmente?",
            label_style=ft.TextStyle(height=1.25),
            height=112,
            content_padding=ft.Padding(left=16, top=28, right=16, bottom=28),
            options=[ft.dropdown.Option(op) for op in OPCIONES_OCUPACION],
            value=respuestas["ocupacion"],
            width=ancho_campo(),
        border_radius=24, bgcolor=ft.Colors.WHITE, color="#202020")
        dd_pareja = ft.Dropdown(
            label="¿Estás en pareja?",
            options=[ft.dropdown.Option("Sí"), ft.dropdown.Option("No")],
            value=respuestas["pareja"],
            width=ancho_campo(),
        border_radius=24, bgcolor=ft.Colors.WHITE, color="#202020")
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
            ft.ElevatedButton("Siguiente", on_click=validar_y_avanzar, width=ancho_campo(), height=48, style=ft.ButtonStyle(bgcolor="#E95F83", color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=24))),
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
                    ft.ElevatedButton("Continuar", on_click=validar_y_mostrar_explicacion, width=160, height=48, style=ft.ButtonStyle(bgcolor="#E95F83", color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=24))),
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
                    ft.ElevatedButton("¡Empezar a entrenar!", on_click=finalizar_y_guardar, width=200, height=48, style=ft.ButtonStyle(bgcolor="#E95F83", color=ft.Colors.WHITE, shape=ft.RoundedRectangleBorder(radius=24))),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=15,
            ),
        ]
        render_contenedor(controles)

    # Iniciar en el primer paso
    mostrar_paso_familia()

OPCIONES_ESTUDIO_NIVEL = ["No estudio actualmente", "Secundaria", "Terciario o universitario", "Posgrado", "Cursos o idiomas"]
OPCIONES_TRABAJO_MODALIDAD = [
    "No trabajo actualmente",
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
    """Personalización opcional en pasos: Salud, Vínculos y Trabajo/estudio.

    Omitir saltea solamente la sección actual. Se conservan las respuestas
    de las secciones anteriores, y el botón Omitir aparece desde el inicio.
    """
    ocupacion = perfil_base.get("ocupacion") or ""
    estudia = ocupacion in ("Estudio", "Estudio y trabajo")
    trabaja = ocupacion in ("Trabajo", "Estudio y trabajo")
    en_pareja = perfil_base.get("pareja") == "Sí"
    extras = {}

    def ancho_campo(base=340):
        disponible = (page.width or (base + 70)) - 70
        return max(260, min(base, disponible))

    def dropdown(pregunta, opciones):
        return ft.Dropdown(
            label=pregunta,
            options=[ft.dropdown.Option(op) for op in opciones],
            width=ancho_campo(),
            border_radius=24,
            bgcolor=ft.Colors.WHITE,
            color="#202020",
        )

    checks_salud = [ft.Checkbox(label=op, shape=ft.CircleBorder()) for op in OPCIONES_SALUD_TEMAS]
    checks_vinculos = [
        ft.Checkbox(label=op, shape=ft.CircleBorder()) for op in OPCIONES_VINCULOS_TEMAS
        if en_pareja or op != "Mi pareja"
    ]
    dd_amigos = dropdown(
        "¿Qué tan conforme estás con la cantidad de amigos/as que tenés?",
        OPCIONES_AMIGOS_SATISFACCION,
    )
    dd_amigos.height = 112
    dd_amigos.label_style = ft.TextStyle(height=1.25)
    dd_amigos.content_padding = ft.Padding(left=16, top=28, right=16, bottom=28)
    dd_apoyo = dropdown(
        "Cuando te sentís solo/a, ¿tenés a quién recurrir?",
        OPCIONES_APOYO_SOLEDAD,
    )
    dd_apoyo.height = 100
    dd_apoyo.label_style = ft.TextStyle(height=1.25)
    dd_apoyo.content_padding = ft.Padding(left=16, top=24, right=16, bottom=24)
    dd_estudio = dropdown("¿Qué estás estudiando?", OPCIONES_ESTUDIO_NIVEL) if estudia else None
    dd_trabajo = dropdown("¿Cómo trabajás?", OPCIONES_TRABAJO_MODALIDAD) if trabaja else None

    secciones = ["Salud", "Vínculos"]
    if estudia or trabaja:
        secciones.append("Trabajo y estudio")

    def guardar_seccion(nombre):
        if nombre == "Salud":
            elegidos = [c.label for c in checks_salud if c.value]
            if elegidos:
                extras["salud_temas"] = elegidos
        elif nombre == "Vínculos":
            if dd_amigos.value:
                extras["amigos_satisfaccion"] = dd_amigos.value
            if dd_apoyo.value:
                extras["apoyo_cuando_solo"] = dd_apoyo.value
            elegidos = [c.label for c in checks_vinculos if c.value]
            if elegidos:
                extras["vinculos_temas"] = elegidos
        elif nombre == "Trabajo y estudio":
            if dd_estudio is not None and dd_estudio.value:
                extras["estudio_nivel"] = dd_estudio.value
            if dd_trabajo is not None and dd_trabajo.value:
                extras["trabajo_modalidad"] = dd_trabajo.value

    def avanzar(indice, guardar):
        if guardar:
            guardar_seccion(secciones[indice])
        if indice + 1 == len(secciones):
            al_terminar(extras)
        else:
            mostrar_seccion(indice + 1)

    def mostrar_seccion(indice):
        nombre = secciones[indice]
        controles = [
            ft.Text("Un último paso", size=22,
                    weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
            ft.Text("Es solo para que los ejercicios se parezcan más a tu día a día. Podés saltearlo.",
                    color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER, size=14),
            ft.Text(nombre, size=19, weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER),
        ]
        if nombre == "Salud":
            controles += [
                ft.Text("¿Qué te gustaría practicar?", size=16,
                        weight=ft.FontWeight.W_600, text_align=ft.TextAlign.CENTER),
                ft.Container(content=ft.Column(checks_salud, spacing=2), width=ancho_campo()),
            ]
        elif nombre == "Vínculos":
            controles += [
                ft.Column([dd_amigos, dd_apoyo], spacing=0),
                ft.Text("¿En qué situaciones sociales te gustaría practicar?",
                        size=14, color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
                ft.Container(content=ft.Column(checks_vinculos, spacing=2), width=ancho_campo()),
            ]
        else:
            if dd_estudio is not None:
                controles.append(dd_estudio)
            if dd_trabajo is not None:
                controles.append(dd_trabajo)
        controles += [
            ft.Text("Podés elegir varias opciones o ninguna.", size=12,
                    color=COLOR_TEXTO_MEDIO, text_align=ft.TextAlign.CENTER),
            ft.Row([
                ft.OutlinedButton("Omitir", on_click=lambda _: avanzar(indice, False),
                                  height=48, expand=True),
                ft.ElevatedButton(
                    "Listo" if indice == len(secciones) - 1 else "Siguiente",
                    on_click=lambda _: avanzar(indice, True), height=48, expand=True,
                    style=ft.ButtonStyle(bgcolor=COLOR_PRIMARIO, color=ft.Colors.WHITE,
                                         shape=ft.RoundedRectangleBorder(radius=24)),
                ),
            ], width=ancho_campo(), spacing=12,
                alignment=ft.MainAxisAlignment.CENTER),
        ]
        columna = ft.Column(
            controles,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=8 if nombre == "Vínculos" else 16,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        page.bgcolor = ft.Colors.WHITE
        page.controls.clear()
        page.add(ft.Container(content=columna, padding=24,
                              bgcolor=ft.Colors.WHITE, expand=True))
        page.update()

    mostrar_seccion(0)
