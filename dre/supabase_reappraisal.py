import requests

from dre.config import (
    SUPABASE_REAPPRAISAL_URL,
    HEADERS,
)


def obtener_ejercicios_reappraisal_supabase(usuario_id):
    try:
        resp = requests.get(
            SUPABASE_REAPPRAISAL_URL,
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
                f"Error Supabase GET ejercicios_reappraisal "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        return resp.json()

    except Exception as e:
        print("Error de red (ejercicios_reappraisal):", repr(e))
        return None


def guardar_ejercicio_reappraisal_supabase(datos):
    try:
        resp = requests.post(
            SUPABASE_REAPPRAISAL_URL,
            headers={
                **HEADERS,
                "Prefer": "return=representation",
            },
            json=datos,
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase POST ejercicios_reappraisal "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        creados = resp.json()
        return creados[0] if creados else None

    except Exception as e:
        print("Error de red (guardar ejercicio reappraisal):", repr(e))
        return None