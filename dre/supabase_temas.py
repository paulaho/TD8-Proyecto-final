import requests

from dre.config import (
    SUPABASE_TEMAS_URL,
    HEADERS,
)


def crear_tema_supabase(registro):
    try:
        resp = requests.post(
            SUPABASE_TEMAS_URL,
            headers={
                **HEADERS,
                "Prefer": "return=representation",
            },
            json=registro,
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase POST temas_seguimiento "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        creados = resp.json()
        return creados[0] if creados else None

    except Exception as e:
        print("Error de red (crear tema):", repr(e))
        return None


def actualizar_tema_supabase(tema_id, cambios):
    try:
        resp = requests.patch(
            f"{SUPABASE_TEMAS_URL}?id=eq.{tema_id}",
            headers=HEADERS,
            json=cambios,
            timeout=10,
        )

        resp.raise_for_status()
        return True

    except Exception as e:
        print("Error de red (actualizar tema):", repr(e))
        return False


def obtener_temas_usuario_supabase(usuario_id):
    try:
        resp = requests.get(
            SUPABASE_TEMAS_URL,
            headers=HEADERS,
            params={
                "usuario_id": f"eq.{usuario_id}",
                "select": "*",
                "order": "created_at.desc",
            },
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase GET temas_seguimiento "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        return resp.json()

    except Exception as e:
        print("Error de red (obtener temas):", repr(e))
        return None


def obtener_tema_supabase(tema_id):
    try:
        resp = requests.get(
            SUPABASE_TEMAS_URL,
            headers=HEADERS,
            params={
                "id": f"eq.{tema_id}",
                "select": "*",
            },
            timeout=10,
        )

        if not resp.ok:
            return None

        resultados = resp.json()
        return resultados[0] if resultados else None

    except Exception as e:
        print("Error de red (obtener tema):", repr(e))
        return None

def borrar_tema_supabase(tema_id):
    try:
        resp = requests.delete(
            f"{SUPABASE_TEMAS_URL}?id=eq.{tema_id}",
            headers=HEADERS,
            timeout=10,
        )

        resp.raise_for_status()
        return True

    except Exception as e:
        print("Error de red (borrar tema):", repr(e))
        return False