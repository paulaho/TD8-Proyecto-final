import os
import hashlib
import unicodedata

from dre.config import PBKDF2_ITERACIONES


# ==========================================================
# DETECCIÓN DE RIESGO SUICIDA
# ==========================================================

def _sin_acentos(texto):
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c))


def _normalizar_riesgo(texto):
    return _sin_acentos((texto or "").strip().lower())


FRASES_RIESGO_SUICIDA = [
    "quiero morir", "quiero morirme", "prefiero estar muerto", "prefiero estar muerta",
    "no quiero vivir", "no quiero seguir viviendo", "no quiero seguir viva", "no quiero seguir vivo",
    "no quiero existir", "no quiero estar viva", "no quiero estar vivo",
    "me quiero matar", "quiero matarme", "matarme de una vez",
    "quiero suicidarme", "me quiero suicidar", "pensando en suicidarme", "pienso en suicidarme", "pense en suicidarme",
    "quitarme la vida", "quitarme mi vida", "quitarme la vida de una vez",
    "terminar con mi vida", "terminar con esta vida", "acabar con mi vida", "acabar con esta vida",
    "poner fin a mi vida",
    "no vale la pena seguir viviendo", "no tiene sentido seguir viviendo",
    "ya no aguanto mas vivir", "ya no aguanto mas seguir viviendo",
    "mejor estaria muerto", "mejor estaria muerta",
    "estarian mejor sin mi", "estarian todos mejor sin mi", "todos estarian mejor sin mi",
    "el mundo estaria mejor sin mi", "si yo no estuviera todo seria mejor",
    "quiero desaparecer para siempre", "yo desapareciera para siempre", "si yo desapareciera",
    "no quiero despertar", "no quiero despertarme mas",
    "tengo un plan para matarme", "como matarme", "como suicidarme",
    "hacerme dano de verdad", "lastimarme para terminar con esto",
]


def detectar_riesgo_suicida(*textos):
    for texto in textos:
        t = _normalizar_riesgo(texto)

        if not t:
            continue

        if any(frase in t for frase in FRASES_RIESGO_SUICIDA):
            return True

    return False


# ==========================================================
# DETECCIÓN DE RIESGO HACIA TERCEROS
# ==========================================================

FRASES_RIESGO_TERCEROS = [
    "voy a matar a", "quiero matar a", "voy a lastimar a", "quiero lastimar a",
    "le voy a hacer dano a", "le voy a hacer daño a", "tengo un plan para lastimar",
    "tengo ganas de matar a", "quiero hacerle dano de verdad a", "quiero hacerle daño de verdad a",
    "voy a atacar a", "quiero herir a", "voy a herir a", "me quiero vengar de",
    "tengo un plan para matar a", "tengo un plan para hacerle dano a",
    "tengo un plan para hacerle daño a",
    "tengo un plan para atacar a", "tengo un plan para herir a",
]


def detectar_riesgo_terceros(*textos):
    for texto in textos:
        t = _normalizar_riesgo(texto)

        if not t:
            continue

        if any(frase in t for frase in FRASES_RIESGO_TERCEROS):
            return True

    return False


# ==========================================================
# CONTRASEÑAS
# ==========================================================

def generar_salt():
    return os.urandom(16).hex()


def hash_contrasena(contrasena, salt_hex):
    salt = bytes.fromhex(salt_hex)

    derivado = hashlib.pbkdf2_hmac(
        "sha256",
        contrasena.encode("utf-8"),
        salt,
        PBKDF2_ITERACIONES,
    )

    return derivado.hex()