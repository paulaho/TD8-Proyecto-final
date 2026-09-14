import requests

from dre.config import (
    SUPABASE_USUARIOS_URL,
    HEADERS,
)


def buscar_usuario_por_email(email):
    try:
        resp = requests.get(
            SUPABASE_USUARIOS_URL,
            headers=HEADERS,
            params={"email": f"eq.{email}", "select": "*"},
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase GET usuarios_regulacion "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None, False

        resultados = resp.json()
        return (resultados[0], True) if resultados else (None, True)

    except Exception as e:
        print("Error de red (usuarios_regulacion):", repr(e))
        return None, False


def crear_usuario(email, password_hash, password_salt=None):
    try:
        resp = requests.post(
            SUPABASE_USUARIOS_URL,
            headers={
                **HEADERS,
                "Prefer": "return=representation",
            },
            json={
                "email": email,
                "password_hash": password_hash,
                "password_salt": password_salt,
            },
            timeout=10,
        )

        if not resp.ok:
            print(
                f"Error Supabase POST usuarios_regulacion "
                f"[{resp.status_code}]: {resp.text}"
            )
            return None

        creados = resp.json()
        return creados[0] if creados else None

    except Exception as e:
        print("Error de red (crear usuario):", repr(e))
        return None


def buscar_o_crear_usuario_google(email):
    usuario, ok = buscar_usuario_por_email(email)

    if not ok:
        return None

    if usuario:
        return usuario

    return crear_usuario(email, None)


def actualizar_password_supabase(
    usuario_id,
    password_hash,
    password_salt,
):
    try:
        resp = requests.patch(
            f"{SUPABASE_USUARIOS_URL}?id=eq.{usuario_id}",
            headers=HEADERS,
            json={
                "password_hash": password_hash,
                "password_salt": password_salt,
            },
            timeout=10,
        )

        resp.raise_for_status()
        return True

    except Exception as e:
        print("Error de red (actualizar password):", e)
        return False

def actualizar_usuario(usuario_id, cambios):
    try:
        resp = requests.patch(
            f"{SUPABASE_USUARIOS_URL}?id=eq.{usuario_id}",
            headers=HEADERS,
            json=cambios,
            timeout=10,
        )
        resp.raise_for_status()
        return True

    except Exception as e:
        print("Error de red (actualizar usuario):", e)
        return False


def guardar_perfil_supabase(
    usuario_id,
    nombre,
    edad,
    genero,
    en_tratamiento,
    pregunta_seguridad=None,
    respuesta_hash=None,
    respuesta_salt=None,
):
    datos = {
        "nombre": nombre,
        "edad": edad,
        "genero": genero,
        "en_tratamiento": en_tratamiento,
    }

    if pregunta_seguridad is not None:
        datos["pregunta_seguridad"] = pregunta_seguridad
        datos["respuesta_seguridad_hash"] = respuesta_hash
        datos["respuesta_seguridad_salt"] = respuesta_salt

    return actualizar_usuario(usuario_id, datos)