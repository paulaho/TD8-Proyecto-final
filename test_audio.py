import flet as ft
import flet_audio as fta

async def main(page: ft.Page):
    audio = fta.Audio(
        src="/audio/loving_kindness/sesion_1/fragmento1.mp3",
        autoplay=False,
    )
    page.services.append(audio)

    async def reproducir(e):
        print("Intentando reproducir...")
        await audio.play()
        print("Reproducción iniciada")

    page.add(ft.Button("Reproducir audio", on_click=reproducir))

ft.run(main, assets_dir="assets")