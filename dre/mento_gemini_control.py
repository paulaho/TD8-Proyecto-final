"""Coordinación de solicitudes Gemini entre los módulos de Mento."""
import random
import threading
import time

_lock = threading.Lock()
_siguiente = 0.0


def esperar_turno():
    global _siguiente
    with _lock:
        ahora = time.monotonic()
        espera = max(0.0, _siguiente - ahora)
        if espera:
            time.sleep(espera)
        _siguiente = time.monotonic() + 5.2


def es_temporal(error):
    codigo = getattr(error, 'status_code', None) or getattr(error, 'code', None)
    mensaje = str(error).lower()
    return str(codigo) in ('429', '500', '502', '503', '504') or any(
        s in mensaje for s in ('429', '503', 'resource_exhausted', 'rate limit',
                             'unavailable', 'high demand', 'timeout', 'timed out',
                             'deadline exceeded', 'bad gateway', 'connection reset'))


def generar(client, **kwargs):
    for intento in range(4):
        esperar_turno()
        try:
            return client.models.generate_content(**kwargs)
        except Exception as exc:
            if intento == 3 or not es_temporal(exc):
                raise
            demora = min(2 ** intento + random.uniform(0.2, 0.8), 8)
            print(f'Gemini: error temporal, reintento {intento + 1}/3 en {demora:.1f}s: {exc}', flush=True)
            time.sleep(demora)
