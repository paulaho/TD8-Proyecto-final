import requests

from dre.config import (
    SUPABASE_REPORTES_URL,
    HEADERS,
)


def crear_reporte(registro):
    try:
        resp = requests.post(
            SUPABASE_REPORTES_URL,
            headers={
                **HEADERS,
                "Prefer": "return=representation",
            },
            json=registro,
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase POST reportes_emocionales "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        creados = resp.json()
        return creados[0] if creados else None

    except Exception as e:
        print("Error de red (guardar reporte):", repr(e))
        return None


def actualizar_reporte(reporte_id, cambios):
    try:
        resp = requests.patch(
            f"{SUPABASE_REPORTES_URL}?id=eq.{reporte_id}",
            headers=HEADERS,
            json=cambios,
            timeout=10,
        )

        resp.raise_for_status()
        return True

    except Exception as e:
        print("Error de red (actualizar reporte):", e)
        return False


def obtener_reportes_usuario_supabase(usuario_id):
    try:
        resp = requests.get(
            SUPABASE_REPORTES_URL,
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
                f"Error Supabase GET reportes_emocionales "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        return resp.json()

    except Exception as e:
        print("Error de red (historial):", repr(e))
        return None


def obtener_reportes_de_tema_supabase(tema_id):
    try:
        resp = requests.get(
            SUPABASE_REPORTES_URL,
            headers=HEADERS,
            params={
                "tema_id": f"eq.{tema_id}",
                "select": "*",
                "order": "fecha.desc",
            },
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase GET reportes por tema "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        return resp.json()

    except Exception as e:
        print("Error de red (reportes de tema):", repr(e))
        return None