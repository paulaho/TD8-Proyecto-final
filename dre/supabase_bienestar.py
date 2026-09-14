import requests

from dre.config import (
    SUPABASE_BIENESTAR_URL,
    HEADERS,
)


def obtener_chequeos_bienestar_supabase(usuario_id):
    try:
        resp = requests.get(
            SUPABASE_BIENESTAR_URL,
            headers=HEADERS,
            params={
                "usuario_id": f"eq.{usuario_id}",
                "select": "*",
                "order": "fecha.desc",
            },
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase GET chequeos_bienestar "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        return resp.json()

    except Exception as e:
        print("Error de red (chequeos_bienestar):", repr(e))
        return None


def guardar_chequeo_bienestar_supabase(datos):
    try:
        resp = requests.post(
            SUPABASE_BIENESTAR_URL,
            headers={
                **HEADERS,
                "Prefer": "return=representation",
            },
            json=datos,
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase POST chequeos_bienestar "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        creados = resp.json()
        return creados[0] if creados else None

    except Exception as e:
        print("Error de red (guardar chequeo bienestar):", repr(e))
        return None

