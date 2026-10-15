"""
Módulo de dificultad progresiva y configuración por niveles
para el juego de Contraargumento (Categoría Familia).

Python puro, sin dependencias de Flet ni de Gemini.
"""

from typing import Optional, Dict, Any


# ==========================================================
# ESTRATEGIA ACTUAL
# ==========================================================

ESTRATEGIA_ACTUAL: Dict[str, str] = {
    "nombre": "Reconstrual",
    "definicion": "ampliar la mirada sobre lo que pasó, mirarlo con más distancia y más datos",
    "explicacion": (
        "Reconstrual consiste en ampliar la mirada sobre lo que pasó: tomar distancia, "
        "incorporar más datos y considerar interpretaciones alternativas plausibles que reduzcan el malestar "
        "sin caer en positivismo mágico ni negar lo ocurrido."
    ),
}


# ==========================================================
# ÁNGULOS DE CONTRAARGUMENTO
# ==========================================================

ANGULOS: Dict[int, Dict[str, Any]] = {
    1: {
        "numero": 1,
        "nombre": "Mirada de afuera",
        "descripcion": "Preguntarse si alguien de afuera se convencería con ese reappraisal.",
        "guia": "Si un amigo/a te dijera esto, ¿le creerías del todo?",
        "consigna_fase2": "Escribí un contraargumento desde una mirada de afuera: si un amigo/a te dijera esto, ¿le creerías del todo?",
    },
    2: {
        "numero": 2,
        "nombre": "Un dato que no cierra",
        "descripcion": "Señalar algo de la situación que no encaja con el reappraisal o que no tiene en cuenta.",
        "guia": "¿Qué dato de lo que pasó no encaja con esta forma de verlo?",
        "consigna_fase2": "Escribí un contraargumento: buscá un dato de lo que pasó que no encaje con esta forma de verlo.",
    },
    3: {
        "numero": 3,
        "nombre": "Otra explicación",
        "descripcion": "Proponer otra causa posible que no sea la peor (no puede ser la lectura negativa de vuelta).",
        "guia": "¿Qué otra explicación, que no sea la peor, podría haber?",
        "consigna_fase2": "Escribí un contraargumento: proponé otra explicación posible que no sea la peor.",
    },
    4: {
        "numero": 4,
        "nombre": "Lo que no resuelve",
        "descripcion": "Aceptar que el reappraisal puede ser cierto y señalar qué deja sin resolver.",
        "guia": "Aunque esto sea cierto, ¿qué deja sin resolver?",
        "consigna_fase2": "Escribí un contraargumento: aunque esto sea cierto, ¿qué deja sin resolver?",
    },
}


# ==========================================================
# FÓRMULAS DE DIFICULTAD Y NIVELES
# ==========================================================

def banda(nivel: int) -> int:
    """
    Calcula la banda de dificultad (1 a 5) según el nivel.
    banda(nivel) = min(5, 1 + (nivel - 1) // 3)
    """
    if nivel < 1:
        nivel = 1
    return min(5, 1 + (nivel - 1) // 3)


def fase(nivel: int) -> int:
    """
    fase(nivel) = 1 si nivel <= 13, 2 si nivel >= 14
    """
    return 1 if nivel <= 13 else 2


def tramo(nivel: int) -> Optional[int]:
    """
    tramo(nivel), solo si nivel >= 14:
    min(3, 1 + (nivel - 14) // 5)
    Para niveles 1 a 13 devuelve None.
    """
    if nivel < 14:
        return None
    return min(3, 1 + (nivel - 14) // 5)


def angulo_pedido(nivel: int) -> Optional[int]:
    """
    Ángulo pedido según el nivel:
    - Niveles 1 a 13: None (la persona elige el ángulo).
    - Nivel >= 14 (Fase 2):
      - Tramo 1 (14 a 18): 1 si (nivel - 14) es par, 2 si es impar.
      - Tramo 2 (19 a 23): 1 + ((nivel - 19) % 4).
      - Tramo 3 (24 en adelante): 3 si (nivel - 24) es par, 4 si es impar.
    """
    if nivel <= 13:
        return None

    t = tramo(nivel)
    if t == 1:
        return 1 if (nivel - 14) % 2 == 0 else 2
    elif t == 2:
        return 1 + ((nivel - 19) % 4)
    else:
        return 3 if (nivel - 24) % 2 == 0 else 4


# ==========================================================
# CONFIGURACIÓN POR BANDA
# ==========================================================

CONFIGURACION_BANDAS: Dict[int, Dict[str, Any]] = {
    1: {
        "banda": 1,
        "tipo_situacion": "Tipo A",
        "intensidad": "leve",
        "enfoque": "puntual",
        "descripcion_situacion": (
            "Tipo A (puntual): un episodio aislado con poca carga en el ámbito familiar "
            "(ej.: un familiar no contesta un mensaje, se olvida de algo, no te invita a un plan menor)."
        ),
        "tipo_lectura": "Tipo I",
        "descripcion_lectura": "Tipo I (exagerada, sin base): nada en la situación la sostiene; es la mente rellenando un vacío con lo peor.",
        "tipo_reappraisal": "Tipo I",
        "descripcion_reappraisal": (
            "Tipo I (punto débil visible): razonable pero afirma más de lo que se sabe. "
            "La exageración está en una palabra o frase señalable ('seguro', 'nada que ver', 'siempre')."
        ),
        "andamiaje": {
            "pregunta_guia_paso_c": "Si un amigo/a te dijera esto, ¿le creerías del todo?",
            "pregunta_guia_paso_d": "Si aceptás esa duda, ¿qué otra forma de verlo hay que no sea la peor?",
            "inicio_frase_paso_c": "Sí, pero...",
            "inicio_frase_paso_d": "Aunque...",
            "explicacion_estrategia": "visible",
        },
    },
    2: {
        "banda": 2,
        "tipo_situacion": "Tipo A",
        "intensidad": "leve-moderada",
        "enfoque": "puntual",
        "descripcion_situacion": "Tipo A (puntual): un episodio aislado con poca carga en el ámbito familiar.",
        "tipo_lectura": "Tipo I",
        "descripcion_lectura": "Tipo I (exagerada, sin base): nada en la situación la sostiene.",
        "tipo_reappraisal": "Tipo I",
        "descripcion_reappraisal": "Tipo I (punto débil visible): razonable pero afirma más de lo que se sabe.",
        "andamiaje": {
            "pregunta_guia_paso_c": "Si un amigo/a te dijera esto, ¿le creerías del todo?",
            "pregunta_guia_paso_d": "Si aceptás esa duda, ¿qué otra forma de verlo hay que no sea la peor?",
            "inicio_frase_paso_c": None,
            "inicio_frase_paso_d": None,
            "explicacion_estrategia": "visible",
        },
    },
    3: {
        "banda": 3,
        "tipo_situacion": "Tipo B",
        "intensidad": "moderada",
        "enfoque": "patrón",
        "descripcion_situacion": (
            "Tipo B (patrón / relación): algo que se repite o que toca una relación cercana, "
            "con algún dato concreto en la situación."
        ),
        "tipo_lectura": "Tipo II",
        "descripcion_lectura": (
            "Tipo II (con base parcial): hay un dato real que apunta en esa dirección, "
            "pero la lectura saca una conclusión más grande que el dato."
        ),
        "tipo_reappraisal": "Tipo II",
        "descripcion_reappraisal": (
            "Tipo II (se apoya en un supuesto): bien planteado, pero depende de algo que no se sabe "
            "o deja afuera un dato real. El dato real y el supuesto quedan claramente separados."
        ),
        "andamiaje": {
            "pregunta_guia_paso_c": "¿Qué tiene de débil esta forma de verlo?",
            "pregunta_guia_paso_d": "¿Cómo lo ves ahora?",
            "inicio_frase_paso_c": None,
            "inicio_frase_paso_d": None,
            "explicacion_estrategia": "demanda",
        },
    },
    4: {
        "banda": 4,
        "tipo_situacion": "Tipo B",
        "intensidad": "moderada-alta",
        "enfoque": "relación",
        "descripcion_situacion": "Tipo B (patrón / relación): toca una relación familiar importante con datos concretos.",
        "tipo_lectura": "Tipo II",
        "descripcion_lectura": "Tipo II (con base parcial).",
        "tipo_reappraisal": "Tipo II",
        "descripcion_reappraisal": "Tipo II (se apoya en un supuesto).",
        "andamiaje": {
            "pregunta_guia_paso_c": None,
            "pregunta_guia_paso_d": None,
            "inicio_frase_paso_c": None,
            "inicio_frase_paso_d": None,
            "explicacion_estrategia": "demanda",
        },
    },
    5: {
        "banda": 5,
        "tipo_situacion": "Tipo C",
        "intensidad": "alta",
        "enfoque": "relación",
        "descripcion_situacion": (
            "Tipo C (alta, relación): situación intensa, con una relación importante y con un dato real "
            "que sostiene en parte la lectura negativa."
        ),
        "tipo_lectura": "Tipo III",
        "descripcion_lectura": (
            "Tipo III (con base real): puede ser cierta, al menos en parte. "
            "No hay forma honesta de decir 'eso es falso'."
        ),
        "tipo_reappraisal": "Tipo III",
        "descripcion_reappraisal": (
            "Tipo III (sólido): una buena respuesta que un terapeuta aceptaría, sin error evidente: "
            "no afirma más de lo que se sabe y reconoce la parte cierta. Su límite es lo que deja afuera o no resuelve."
        ),
        "andamiaje": {
            "pregunta_guia_paso_c": None,
            "pregunta_guia_paso_d": None,
            "inicio_frase_paso_c": None,
            "inicio_frase_paso_d": None,
            "explicacion_estrategia": "ninguna",
        },
    },
}


def configuracion_nivel(nivel: int) -> Dict[str, Any]:
    """
    Retorna la configuración completa para un nivel específico.
    """
    b = banda(nivel)
    f = fase(nivel)
    t = tramo(nivel)
    ang = angulo_pedido(nivel)

    base = CONFIGURACION_BANDAS[b]

    # Consignas por defecto
    consigna_paso_c = "Escribí un contraargumento a esta forma de verlo (practicando Reconstrual):"
    consigna_paso_d = "Escribí un nuevo reappraisal que responda a tu contraargumento (practicando Reconstrual):"

    # En Fase 2 (nivel 14+), se utiliza el ángulo pedido
    if f == 2 and ang is not None:
        info_ang = ANGULOS[ang]
        consigna_paso_c = f"{info_ang['consigna_fase2']} (practicando Reconstrual):"

    return {
        "nivel": nivel,
        "banda": b,
        "fase": f,
        "tramo": t,
        "angulo_pedido": ang,
        "tipo_situacion": base["tipo_situacion"],
        "intensidad": base["intensidad"],
        "enfoque": base["enfoque"],
        "descripcion_situacion": base["descripcion_situacion"],
        "tipo_lectura": base["tipo_lectura"],
        "descripcion_lectura": base["descripcion_lectura"],
        "tipo_reappraisal": base["tipo_reappraisal"],
        "descripcion_reappraisal": base["descripcion_reappraisal"],
        "estrategia": ESTRATEGIA_ACTUAL["nombre"],
        "estrategia_explicacion": ESTRATEGIA_ACTUAL["explicacion"],
        "andamiaje": base["andamiaje"].copy(),
        "consigna_paso_c": consigna_paso_c,
        "consigna_paso_d": consigna_paso_d,
    }

