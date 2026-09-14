import requests

from dre.config import (
    SUPABASE_JUEGOS_REAPPRAISAL_URL,
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