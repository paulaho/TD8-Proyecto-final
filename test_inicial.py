import flet as ft
import requests

# Ajustá las constates si usás importación o pasá las URLs / HEADERS
COLOR_PRIMARIO = "#3D7A7B"
COLOR_TEXTO_MEDIO = "#665C4C"
COLOR_TARJETA = "#FFFAF0"

OPCIONES_CONVIVENCIA = ["Solo/a", "Con mis padres", "Con pareja", "Con amigos/as / compañeros/as", "Con hijos/as"]
OPCIONES_HERMANOS = ["No tengo hermanos", "Sí, tengo hermanos/as"]
OPCIONES_OCUPACION = ["Estudio", "Trabajo", "Estudio y trabajo", "Ninguna por el momento"]

def mostrar_test_inicial(page: ft.Page, estado: dict, SUPABASE_USUARIOS_URL: str, HEADERS: dict, al_completar_callback):
    """
    Renderiza la pantalla del test de situación personal y guarda las respuestas.
    Al finalizar llama a `al_completar_callback()` para derivar al menú principal.
    """

    def ancho_campo(base=320):
        disponible = (page.width or (base + 70)) - 70
        return max(220, min(base, disponible))

    # Campos de la encuesta
    dropdown_convivencia = ft.Dropdown(
        label="¿Con quién vivís actualmente?",
        options=[ft.dropdown.Option(op) for op in OPCIONES_CONVIVENCIA],
        width=ancho_campo(),
    )

    dropdown_hermanos = ft.Dropdown(
        label="¿Tenés hermanos/as?",
        options=[ft.dropdown.Option(op) for op in OPCIONES_HERMANOS],
        width=ancho_campo(),
    )

    dropdown_ocupacion = ft.Dropdown(
        label="¿A qué te dedicás principalmente?",
        options=[ft.dropdown.Option(op) for op in OPCIONES_OCUPACION],
        width=ancho_campo(),
    )

    dropdown_pareja = ft.Dropdown(
        label="¿Estás en pareja?",
        options=[ft.dropdown.Option("Sí"), ft.dropdown.Option("No")],
        width=ancho_campo(),
    )

    texto_error = ft.Text("", color=ft.Colors.RED)

    def guardar_encuesta(e):
        if not dropdown_convivencia.value or not dropdown_hermanos.value or not dropdown_ocupacion.value or not dropdown_pareja.value:
            texto_error.value = "Por favor respondé todas las preguntas para personalizar tus ejercicios."
            page.update()
            return

        perfil_contexto = {
            "convivencia": dropdown_convivencia.value,
            "hermanos": dropdown_hermanos.value,
            "ocupacion": dropdown_ocupacion.value,
            "pareja": dropdown_pareja.value,
        }

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
                        "realizo_test_inicial": True
                    },
                    timeout=10,
                )
                resp.raise_for_status()
            except Exception as ex:
                print("Error guardando el test inicial en Supabase:", ex)

        # Derivar al menú principal mediante el callback
        al_completar_callback()

    # Construcción de la pantalla
    controles = [
        ft.Icon(ft.Icons.FAMILY_RESTROOM, size=50, color=COLOR_PRIMARIO),
        ft.Text("Queremos conocerte un poco mejor", size=22, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
        ft.Text(
            "Esta información ayuda a que la IA genere situaciones de práctica personalizadas sobre tu familia y entorno.",
            color=COLOR_TEXTO_MEDIO,
            text_align=ft.TextAlign.CENTER,
            size=14,
        ),
        dropdown_convivencia,
        dropdown_hermanos,
        dropdown_pareja,
        dropdown_ocupacion,
        texto_error,
        ft.ElevatedButton("Guardar y Continuar", on_click=guardar_encuesta, width=ancho_campo(), height=50)
    ]

    columna = ft.Column(
        controles,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=15,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
    )

    tarjeta = ft.Container(
        content=columna,
        padding=20,
        margin=15,
        border_radius=20,
        bgcolor=ft.Colors.with_opacity(0.97, COLOR_TARJETA),
        expand=True,
    )

    page.controls.clear()
    page.add(ft.Container(content=tarjeta, alignment=ft.Alignment.CENTER, expand=True))
    page.update()