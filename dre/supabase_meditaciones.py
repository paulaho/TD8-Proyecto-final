# ==========================================================
# PERSISTENCIA DE SESIONES DE MEDITACIÓN EN SUPABASE
# ==========================================================

import requests

from dre.config import (
    SUPABASE_MEDITACIONES_URL,
    HEADERS,
)


def guardar_sesion_meditacion_supabase(usuario_id, practica, sesion):
    """
    Registra una sesión de meditación completada en Supabase.
    Devuelve True si se guardó correctamente, False si falló.
    """
    try:
        resp = requests.post(
            SUPABASE_MEDITACIONES_URL,
            headers=HEADERS,
            json={
                "usuario_id": usuario_id,
                "practica": practica,
                "sesion": sesion,
            },
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase POST sesiones_meditacion [{resp.status_code}]: {resp.text}"
            )
            return False

        return True

    except Exception as e:
        print("Error de red (sesiones_meditacion):", repr(e))
        return False


def obtener_sesiones_meditacion_supabase(usuario_id, practica=None):
    """
    Recupera el historial de sesiones de meditación del usuario.
    Si se especifica practica, filtra por esa práctica.
    Devuelve una lista de registros o None si hubo error.
    """
    try:
        params = {
            "usuario_id": f"eq.{usuario_id}",
            "select": "*",
            "order": "completada_en.asc",
        }
        if practica:
            params["practica"] = f"eq.{practica}"

        resp = requests.get(
            SUPABASE_MEDITACIONES_URL,
            headers=HEADERS,
            params=params,
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase GET sesiones_meditacion [{resp.status_code}]: {resp.text}"
            )
            return None

        return resp.json()

    except Exception as e:
        print("Error de red (obtener sesiones_meditacion):", repr(e))
        return None

