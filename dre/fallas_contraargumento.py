"""
Catálogo de fallas y reglas de evaluación para el juego de Contraargumento.

Define las fallas que puede detectar la IA tanto en el contraargumento como en
el nuevo reappraisal (Reappraisal 2), así como qué fallas frenan o señalan según el nivel/banda.
"""

from typing import Dict, Any, Tuple, Set, Optional, List
from dre.dificultad_contraargumento import banda, fase


# ==========================================================
# CATÁLOGO DE FALLAS — CONTRAARGUMENTO
# ==========================================================

FALLAS_CONTRAARGUMENTO: Dict[str, Dict[str, Any]] = {
    "FC0": {
        "codigo": "FC0",
        "tipo": "contraargumento",
        "nombre": "No discute el reappraisal inicial",
        "descripcion": "Lo repite, le da la razón o lo reformula sin plantear ninguna duda u objeción.",
        "ejemplo": "Sí, seguro está ocupado/a.",
        "feedback_sugerido": "Esta forma de verlo te convence, y está bien. Pero el ejercicio es buscarle el punto débil. ¿Hay algo de lo que dice que no sepas con seguridad?",
    },
    "FC1": {
        "codigo": "FC1",
        "tipo": "contraargumento",
        "nombre": "Vuelve a la distorsión",
        "descripcion": "En vez de una duda razonable, vuelve a la lectura negativa o la exagera.",
        "ejemplo": "En realidad seguro está enojado/a y no me lo quiere decir.",
        "feedback_sugerido": "Eso vuelve al pensamiento del principio. La idea es encontrar una duda razonable sobre esta forma de verlo, no la peor explicación. ¿Qué parte de lo que dice no sabés con seguridad?",
    },
    "FCG": {
        "codigo": "FCG",
        "tipo": "contraargumento",
        "nombre": "Genérico",
        "descripcion": "Serviría para cualquier reappraisal, no usa nada de este ni de la situación concreta.",
        "ejemplo": "Eso no siempre es así.",
        "feedback_sugerido": "Va en la dirección correcta, pero serviría para cualquier cosa. ¿Qué parte de esta forma de verlo, puntualmente, no te termina de cerrar?",
    },
    "FCD": {
        "codigo": "FCD",
        "tipo": "contraargumento",
        "nombre": "Discute otra cosa",
        "descripcion": "Discute la lectura negativa o la situación en vez del reappraisal inicial que propone la app.",
        "ejemplo": "No tiene por qué estar enojado/a.",
        "feedback_sugerido": "Eso le responde al pensamiento del principio, y va bien encaminado. Pero acá la idea es discutir la otra forma de verlo que te propone la app. ¿Qué tiene de débil?",
    },
    "FCA": {
        "codigo": "FCA",
        "tipo": "contraargumento",
        "nombre": "Ángulo equivocado",
        "descripcion": "Discute el reappraisal desde un ángulo distinto al que pide el nivel (solo Fase 2, nivel 14+).",
        "ejemplo": "En un nivel que pide el ángulo 2: 'Puede estar pasando por algo personal' (eso es ángulo 3).",
        "feedback_sugerido": "Es una duda válida, pero este nivel pide buscar algo de lo que pasó que no encaje con esta forma de verlo. ¿Qué dato de la situación va en contra?",
    },
}


# ==========================================================
# CATÁLOGO DE FALLAS — NUEVO REAPPRAISAL
# ==========================================================

FALLAS_NUEVO_REAPPRAISAL: Dict[str, Dict[str, Any]] = {
    "F1": {
        "codigo": "F1",
        "tipo": "nuevo_reappraisal",
        "nombre": "Sigue en la distorsión",
        "descripcion": "Vuelve a la lectura negativa; toma el contraargumento como prueba de lo peor.",
        "ejemplo": "Contraargumento 'No sé si está ocupado/a' -> 'Entonces sí debe estar enojado/a.'",
        "feedback_sugerido": "Que no sepas si está ocupado/a no quiere decir que esté enojado/a. ¿Cómo se ve la situación si aceptás que no sabés por qué no responde?",
    },
    "F2": {
        "codigo": "F2",
        "tipo": "nuevo_reappraisal",
        "nombre": "Evitación",
        "descripcion": "Propone dejar de pensar en el tema en vez de responder a la duda.",
        "ejemplo": "Mejor no pienso más en eso.",
        "feedback_sugerido": "Dejar de pensarlo puede aliviar un rato, pero la idea es responder a la duda que planteaste. Si no sabés por qué no responde, ¿qué otra forma de verlo tenés?",
    },
    "F3": {
        "codigo": "F3",
        "tipo": "nuevo_reappraisal",
        "nombre": "Positividad forzada",
        "descripcion": "Salta a lo positivo sin reconocer la duda ni que la situación puede doler.",
        "ejemplo": "¡Seguro está todo bien, no hay que preocuparse!",
        "feedback_sugerido": "Buscás calmarte, y eso está bien. Pero salteás la duda que vos mismo/a planteaste. Probá reconocerla primero y después buscar otra forma de verlo.",
    },
    "FG": {
        "codigo": "FG",
        "tipo": "nuevo_reappraisal",
        "nombre": "Genérico",
        "descripcion": "Serviría para cualquier situación, no usa ningún dato concreto de esta.",
        "ejemplo": "No es para tanto.",
        "feedback_sugerido": "Va en la dirección correcta, pero serviría para cualquier cosa. ¿Qué dato de lo que pasó te hace pensar que no es para tanto?",
    },
    "F4": {
        "codigo": "F4",
        "tipo": "nuevo_reappraisal",
        "nombre": "Sin conexión o incompleto",
        "descripcion": "No responde al contraargumento (lo ignora) o deja afuera una parte importante de la situación.",
        "ejemplo": "Contraargumento 'No sé si está ocupado/a' -> 'Igual tengo otros amigos.'",
        "feedback_sugerido": "Tu segunda respuesta no usa lo que escribiste en la primera. Partí de 'no sé si está ocupado/a': si no lo sabés, ¿cómo cambia lo que sentís?",
    },
    "F5": {
        "codigo": "F5",
        "tipo": "nuevo_reappraisal",
        "nombre": "Estrategia equivocada",
        "descripcion": "Es un buen reappraisal pero no usa la estrategia del nivel (ej.: 'Aprovecho para hacer otras cosas' es distracción, no Reconstrual).",
        "ejemplo": "Aprovecho para ponerme al día con otras cosas.",
        "feedback_sugerido": "Es una buena idea, pero este nivel practica ampliar la mirada sobre lo que pasó, no cambiar de actividad. ¿Cómo se ve si lo mirás con más distancia?",
    },
    "FP": {
        "codigo": "FP",
        "tipo": "nuevo_reappraisal",
        "nombre": "No se hace cargo de la parte cierta",
        "descripcion": "Niega lo que el contraargumento señala con razón; con lectura Tipo III también cuenta negar la parte real de la situación.",
        "ejemplo": "Contraargumento 'Antes siempre se hacía un rato' -> 'No, es solo el trabajo.'",
        "feedback_sugerido": "Es entendible querer descartarlo, pero lo que notaste es real: antes se hacía un rato. Partí de eso: aunque haya algo más que el trabajo, ¿qué tan grave es y qué podrías hacer?",
    },
}

TODAS_LAS_FALLAS: Dict[str, Dict[str, Any]] = {
    **FALLAS_CONTRAARGUMENTO,
    **FALLAS_NUEVO_REAPPRAISAL,
}


# ==========================================================
# ORDEN DE PRIORIDAD DE FALLAS
# ==========================================================
# Las fallas del contraargumento tienen prioridad porque el nuevo reappraisal
# se construye sobre él.
PRIORIDAD_FALLAS: List[str] = [
    "FC0",
    "FC1",
    "FCD",
    "FCG",
    "FCA",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "FG",
    "FP",
]


# ==========================================================
# ESTADO DE FALLAS POR NIVEL (FRENA vs SEÑALA)
# ==========================================================

def estado_fallas(nivel: int) -> Tuple[Set[str], Set[str]]:
    """
    Devuelve (frena, señala) para un nivel determinado.

    Reglas por banda:
    - Banda 1: frena FC0, F1 · señala FC1, FCD, F2.
    - Banda 2: frena FC0, FC1, FCD, F1, F2 · señala FCG, F3, FG.
    - Banda 3: frena FC0, FC1, FCD, FCG, F1, F2, F3, FG · señala F4.
    - Banda 4: frena FC0, FC1, FCD, FCG, F1, F2, F3, F4, FG · señala F5, FP.
    - Banda 5: frena FC0, FC1, FCD, FCG, F1, F2, F3, F4, F5, FG, FP · señala nada.

    Regla para FCA (solo Fase 2):
    - Niveles 14 a 18: se señala (está en 'señala').
    - Niveles 19 en adelante: frena (está en 'frena').
    - Niveles 1 a 13 (Fase 1): no existe en ninguno de los dos.
    """
    b = banda(nivel)

    if b == 1:
        frena = {"FC0", "F1"}
        señala = {"FC1", "FCD", "F2"}
    elif b == 2:
        frena = {"FC0", "FC1", "FCD", "F1", "F2"}
        señala = {"FCG", "F3", "FG"}
    elif b == 3:
        frena = {"FC0", "FC1", "FCD", "FCG", "F1", "F2", "F3", "FG"}
        señala = {"F4"}
    elif b == 4:
        frena = {"FC0", "FC1", "FCD", "FCG", "F1", "F2", "F3", "F4", "FG"}
        señala = {"F5", "FP"}
    else:  # b == 5
        frena = {"FC0", "FC1", "FCD", "FCG", "F1", "F2", "F3", "F4", "F5", "FG", "FP"}
        señala = set()

    # FCA solo existe en Fase 2 (nivel >= 14)
    if fase(nivel) == 2:
        if 14 <= nivel <= 18:
            señala.add("FCA")
        elif nivel >= 19:
            frena.add("FCA")

    return frena, señala


def seleccionar_falla_principal(
    fallas_detectadas: List[str],
    frena_set: Set[str],
    señala_set: Set[str],
) -> Optional[str]:
    """
    Determina la falla principal a comunicar según la prioridad y si frena o señala.
    Primero busca en 'frena', luego en 'señala'.
    """
    # 1. Buscar en frena por prioridad
    for codigo in PRIORIDAD_FALLAS:
        if codigo in fallas_detectadas and codigo in frena_set:
            return codigo

    # 2. Buscar en señala por prioridad
    for codigo in PRIORIDAD_FALLAS:
        if codigo in fallas_detectadas and codigo in señala_set:
            return codigo

    return None

