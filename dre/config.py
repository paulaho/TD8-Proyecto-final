import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ==========================================================
# SUPABASE
# ==========================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

SUPABASE_BASE_URL = f"{SUPABASE_URL}/rest/v1"

SUPABASE_USUARIOS_URL = f"{SUPABASE_BASE_URL}/usuarios_regulacion"
SUPABASE_REPORTES_URL = f"{SUPABASE_BASE_URL}/reportes_emocionales"
SUPABASE_TEMAS_URL = f"{SUPABASE_BASE_URL}/temas_seguimiento"
SUPABASE_BIENESTAR_URL = f"{SUPABASE_BASE_URL}/chequeos_bienestar"
SUPABASE_REAPPRAISAL_URL = f"{SUPABASE_BASE_URL}/ejercicios_reappraisal"
SUPABASE_JUEGOS_REAPPRAISAL_URL = f"{SUPABASE_BASE_URL}/progreso_juegos_reappraisal"
SUPABASE_TEXTO_LIBRE_URL = f"{SUPABASE_BASE_URL}/sesiones_texto_libre"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

# ==========================================================
# GOOGLE OAUTH
# ==========================================================

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URL = os.environ.get("GOOGLE_REDIRECT_URL", "")

# ==========================================================
# SEGURIDAD
# ==========================================================

PBKDF2_ITERACIONES = 600_000