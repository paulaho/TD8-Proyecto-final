import requests

from dre.config import (
    SUPABASE_JUEGOS_REAPPRAISAL_URL,
    SUPABASE_TEXTO_LIBRE_URL,
    HEADERS,
)


def obtener_progreso_juegos_supabase(usuario_id):
    try:
        resp = requests.get(
            SUPABASE_JUEGOS_REAPPRAISAL_URL,
            headers=HEADERS,
            params={
                "usuario_id": f"eq.{usuario_id}",
                "select": "*",
            },
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase GET progreso_juegos_reappraisal "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        return resp.json()

    except Exception as e:
        print(
            "Error de red (progreso_juegos_reappraisal):",
            repr(e),
        )
        return None


def marcar_nivel_juego_completado_supabase(
    usuario_id,
    categoria,
    nivel,
):
    try:
        resp = requests.post(
            SUPABASE_JUEGOS_REAPPRAISAL_URL,
            headers={
                **HEADERS,
                "Prefer": "resolution=ignore-duplicates",
            },
            params={
                "on_conflict": "usuario_id,categoria,nivel",
            },
            json={
                "usuario_id": usuario_id,
                "categoria": categoria,
                "nivel": nivel,
            },
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase POST progreso_juegos_reappraisal "
                f"[{resp.status_code}]: {resp.text}"
            )
            return False

        return True

    except Exception as e:
        print(
            "Error de red (guardar progreso juego reappraisal):",
            repr(e),
        )
        return False


def guardar_sesion_texto_libre_supabase(
    usuario_id,
    situaciones,
    fase1_respuestas,
    fase2_respuestas,
    correcciones,
    emociones=None,
    categoria="familia",
):
    """
    Persiste en Supabase una sesión completa del modo texto libre / contraargumento:
    las 5 situaciones generadas por la IA, los 5 contraargumentos,
    las 5 emociones registradas, los 5 nuevos reappraisals y las 5 correcciones.
    """
    try:
        body = {
            "usuario_id": usuario_id,
            "categoria": categoria,
            "situaciones": situaciones,
            "fase1_respuestas": fase1_respuestas,
            "fase2_respuestas": fase2_respuestas,
            "correcciones": correcciones,
        }
        if emociones is not None:
            body["emociones"] = emociones

        resp = requests.post(
            SUPABASE_TEXTO_LIBRE_URL,
            headers={
                **HEADERS,
                "Prefer": "return=minimal",
            },
            json=body,
            timeout=10,
        )

        if not resp.ok and "emociones" in body:
            # Reintento sin emociones en caso de que la columna aún no exista en Supabase
            body.pop("emociones", None)
            resp = requests.post(
                SUPABASE_TEXTO_LIBRE_URL,
                headers={
                    **HEADERS,
                    "Prefer": "return=minimal",
                },
                json=body,
                timeout=10,
            )

        if not resp.ok:
            print(
                f"Error Supabase POST sesiones_texto_libre "
                f"[{resp.status_code}]: {resp.text}"
            )
            return False

        print("Sesión texto libre guardada en Supabase")
        return True

    except Exception as e:
        print(
            "Error de red (guardar sesión texto libre):",
            repr(e),
        )
        return False