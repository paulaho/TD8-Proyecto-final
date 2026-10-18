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
    Persiste en Supabase una sesión completa del modo texto libre / contraargumento.
    Devuelve el id generado (int/str) si fue exitoso, o None/False si falló.
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
                "Prefer": "return=representation",
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
                    "Prefer": "return=representation",
                },
                json=body,
                timeout=10,
            )

        if not resp.ok:
            print(
                f"Error Supabase POST sesiones_texto_libre "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        data = resp.json()
        print("Sesión texto libre guardada en Supabase")
        if isinstance(data, list) and len(data) > 0 and "id" in data[0]:
            return data[0]["id"]
        return True

    except Exception as e:
        print(
            "Error de red (guardar sesión texto libre):",
            repr(e),
        )
        return None


def actualizar_sesion_texto_libre_supabase(
    sesion_id,
    situaciones=None,
    fase1_respuestas=None,
    fase2_respuestas=None,
    correcciones=None,
    emociones=None,
):
    """
    Actualiza una sesión de texto libre existente (PATCH) cuando cambian los resultados tras reintentos.
    """
    if not sesion_id:
        return False
    try:
        body = {}
        if situaciones is not None:
            body["situaciones"] = situaciones
        if fase1_respuestas is not None:
            body["fase1_respuestas"] = fase1_respuestas
        if fase2_respuestas is not None:
            body["fase2_respuestas"] = fase2_respuestas
        if correcciones is not None:
            body["correcciones"] = correcciones
        if emociones is not None:
            body["emociones"] = emociones

        if not body:
            return True

        resp = requests.patch(
            SUPABASE_TEXTO_LIBRE_URL,
            headers={
                **HEADERS,
                "Prefer": "return=minimal",
            },
            params={"id": f"eq.{sesion_id}"},
            json=body,
            timeout=10,
        )

        if not resp.ok and "emociones" in body:
            body.pop("emociones", None)
            resp = requests.patch(
                SUPABASE_TEXTO_LIBRE_URL,
                headers={
                    **HEADERS,
                    "Prefer": "return=minimal",
                },
                params={"id": f"eq.{sesion_id}"},
                json=body,
                timeout=10,
            )

        if not resp.ok:
            print(
                f"Error Supabase PATCH sesiones_texto_libre [{resp.status_code}]: {resp.text}"
            )
            return False

        return True
    except Exception as e:
        print("Error de red (actualizar sesión texto libre):", repr(e))
        return False


def obtener_sesiones_texto_libre_supabase(usuario_id, categoria=None):
    """
    Recupera las sesiones de texto libre de un usuario desde Supabase,
    opcionalmente filtrando por categoría, ordenadas por fecha/id ascendente.
    """
    try:
        params = {
            "usuario_id": f"eq.{usuario_id}",
            "select": "*",
            "order": "id.asc",
        }
        if categoria:
            params["categoria"] = f"eq.{categoria}"

        resp = requests.get(
            SUPABASE_TEXTO_LIBRE_URL,
            headers=HEADERS,
            params=params,
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase GET sesiones_texto_libre [{resp.status_code}]: {resp.text}"
            )
            return None

        return resp.json()
    except Exception as e:
        print("Error de red (obtener sesiones texto libre):", repr(e))
        return None