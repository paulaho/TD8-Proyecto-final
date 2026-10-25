# ==========================================================
# CATÁLOGO DE MEDITACIONES Y PRÁCTICAS GUIADAS
# ----------------------------------------------------------
# Datos puros (sin dependencias de UI/Flet).
# Para sumar nuevas prácticas o sesiones futuras solo se agregan
# datos a esta estructura sin modificar la lógica de la app.
# ==========================================================

PRACTICAS_MEDITACION = [
    {
        "clave": "loving_kindness",
        "nombre": "Bondad amorosa",
        "descripcion": "Cultivar una actitud de buena voluntad y cuidado hacia uno mismo y hacia los demás.",
        "icono": "FAVORITE_OUTLINE",
        "sesiones": [
            {
                "numero": 1,
                "titulo": "Bondad hacia uno mismo",
                "descripcion": (
                    "Orientá tu mente hacia el cuidado y el bienestar propio a través "
                    "de frases guía simples."
                ),
                "fragmentos": [
                    {
                        "audio": "audio/loving_kindness/sesion_1/fragmento1.mp3",
                        "silencio_seg": 8,
                        "texto": (
                            "Acomodá la postura en un lugar donde puedas estar cómodo. "
                            "Podés cerrar los ojos o mantener la mirada suave sobre un punto fijo. "
                            "Tómate unos segundos para registrar tu cuerpo en este momento... "
                            "simplemente notando tu respiración tal como es."
                        ),
                    },
                    {
                        "audio": "audio/loving_kindness/sesion_1/fragmento2.mp3",
                        "silencio_seg": 6,
                        "texto": (
                            "Cultivar una actitud de buena voluntad y cuidado hacia uno mismo es "
                            "una habilidad que se entrena. No se trata de forzar una emoción o "
                            "sentir algo mágico, sino de orientar la mente con una intención clara."
                        ),
                    },
                    {
                        "audio": "audio/loving_kindness/sesion_1/fragmento3.mp3",
                        "silencio_seg": 4,
                        "texto": (
                            "Traé a la mente la intención de desearte bienestar. Vas a repetir "
                            "mentalmente las siguientes frases, conectando de forma simple con su "
                            "significado:"
                        ),
                    },
                    {
                        "audio": "audio/loving_kindness/sesion_1/fragmento4.mp3",
                        "silencio_seg": 8,
                        "texto": "Que pueda estar a salvo y libre de peligro.",
                    },
                    {
                        "audio": "audio/loving_kindness/sesion_1/fragmento5.mp3",
                        "silencio_seg": 8,
                        "texto": "Que pueda tener paz mental.",
                    },
                    {
                        "audio": "audio/loving_kindness/sesion_1/fragmento6.mp3",
                        "silencio_seg": 8,
                        "texto": "Que mi cuerpo tenga salud y fuerza.",
                    },
                    {
                        "audio": "audio/loving_kindness/sesion_1/fragmento7.mp3",
                        "silencio_seg": 10,
                        "texto": "Que pueda vivir con tranquilidad y bienestar en mi día a día.",
                    },
                    {
                        "audio": "audio/loving_kindness/sesion_1/fragmento8.mp3",
                        "silencio_seg": 4,
                        "texto": (
                            "Si notás que la mente se distrae o aparece algún juicio automático, "
                            "es completamente normal. Solo reconocé la distracción y volvé a "
                            "repetir suavemente para vos:"
                        ),
                    },
                    {
                        "audio": "audio/loving_kindness/sesion_1/fragmento9.mp3",
                        "silencio_seg": 12,
                        "texto": "Que pueda estar bien. Que pueda tener paz.",
                    },
                    {
                        "audio": "audio/loving_kindness/sesion_1/fragmento10.mp3",
                        "silencio_seg": 0,
                        "texto": (
                            "Para terminar, hacé una respiración un poco más profunda. Notá cómo "
                            "se siente haberle dedicado estos minutos a tu mente... Y cuando "
                            "quieras, podés abrir los ojos."
                        ),
                    },
                ],
            }
        ],
    }
]


def obtener_practicas():
    """Devuelve la lista de todas las prácticas de meditación disponibles."""
    return PRACTICAS_MEDITACION


def obtener_practica(clave):
    """Devuelve la práctica correspondiente a la clave dada, o None si no existe."""
    for p in PRACTICAS_MEDITACION:
        if p.get("clave") == clave:
            return p
    return None


def obtener_sesion(clave_practica, numero_sesion):
    """Devuelve la sesión correspondiente, o None si no existe."""
    practica = obtener_practica(clave_practica)
    if not practica:
        return None
    for s in practica.get("sesiones", []):
        if s.get("numero") == numero_sesion:
            return s
    return None

