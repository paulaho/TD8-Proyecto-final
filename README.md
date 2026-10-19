# Mento — Entrenamiento de regulación emocional con IA

Aplicación gamificada para practicar **reevaluación cognitiva (Reconstrual)**, con ejercicios generados dinámicamente por un modelo de lenguaje (Gemini) y progreso persistido en Supabase.

Proyecto final de TD8 — Licenciatura en Tecnología Digital, Universidad Torcuato Di Tella. Parte de la aplicación previa "Mento" y la extiende con generación de niveles con IA, escritura libre evaluada por IA, adaptación de dificultad y salvaguardas de seguridad.

## Funcionalidades

- **Opción múltiple:** niveles generados con IA en tandas de 10, con una única respuesta correcta y retroalimentación inmediata. La dificultad progresa en 5 bandas: a medida que el usuario avanza aumentan la cantidad de opciones (de 4 hasta un máximo de 7) y la calidad de los distractores.
- **Escritura libre:** bloques de 5 situaciones; el usuario escribe su contraargumento y una nueva reinterpretación, y la IA lo evalúa (hasta 3 intentos y ejemplo modelo).
- **Personalización:** test de contexto inicial (edad, convivencia, ocupación, familiaridad con la regulación emocional, etc.) cuyas respuestas orientan los escenarios generados.
- **Adaptación al desempeño:** los errores del usuario se usan como entrada para generar los ejercicios siguientes.
- **Precarga en segundo plano** de la siguiente tanda para evitar esperas.
- **Validación de lo generado por IA:** estructura del ejercicio, cantidad de opciones según el nivel, una única respuesta correcta y feedback que no revele la posición correcta.
- **Seguridad:** detección de señales de riesgo en el texto del usuario y acceso a recursos de ayuda.
- **Otras secciones:** trabajo emocional, autorreporte de bienestar, consejos, jardín de recompensas, personalización y perfil.
- **Inicio de sesión** con correo y contraseña o con Google.

## Tecnologías

- Python 3.13
- [Flet](https://flet.dev) (interfaz, versión 0.84 o superior)
- [Supabase](https://supabase.com) (base de datos, vía API REST)
- Google Gemini API, con la librería `google-genai` (generación y evaluación de ejercicios) y `pydantic` (validación de las respuestas)
- Render (despliegue web)

## Estructura del proyecto

```
TD8-Proyecto-final/
├── app.py                      # Aplicación principal: pantallas, navegación y flujo de juegos
├── test_inicial.py             # Test de contexto inicial
├── requirements.txt            # Dependencias
├── assets/                     # Recursos gráficos
├── dre/                        # Módulos de lógica y persistencia
│   ├── config.py               # Configuración: variables de entorno, URLs y headers de Supabase
│   ├── ia_niveles.py           # Generación y validación de niveles de opción múltiple con IA
│   ├── ia_texto_libre.py       # Generación y evaluación de escritura libre con IA
│   ├── dificultad_contraargumento.py
│   ├── fallas_contraargumento.py
│   ├── seguridad.py            # Detección de señales de riesgo
│   ├── gamificacion.py
│   ├── contenido.py            # Contenido psicoeducativo
│   ├── recomendaciones.py
│   ├── bienestar.py
│   ├── historial.py
│   └── supabase_*.py           # Acceso a cada tabla de Supabase
├── supabase_*.sql              # Scripts para crear las tablas
├── banco_situaciones_reappraisal.md
└── BIBLIOGRAFIA.md
```

## Instalación

1. Clonar el repositorio y entrar a la carpeta:

   ```bash
   git clone https://github.com/paulaho/TD8-Proyecto-final.git
   cd TD8-Proyecto-final
   ```

2. (Recomendado) Crear un entorno virtual:

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac / Linux
   ```

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

## Configuración

Las credenciales se leen desde variables de entorno. La forma más simple es crear un archivo **`.env`** en la raíz del proyecto (junto a `app.py`); se carga automáticamente al iniciar.

```env
# Supabase (obligatorias)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu_clave_de_supabase

# Gemini (obligatoria)
GEMINI_API_KEY=tu_clave_de_gemini

# Inicio de sesión con Google (solo si se quiere usar esa opción)
GOOGLE_CLIENT_ID=tu_client_id
GOOGLE_CLIENT_SECRET=tu_client_secret
GOOGLE_REDIRECT_URL=tu_url_de_redireccion
```

- **Supabase:** crear un proyecto propio en <https://supabase.com>. La URL y la clave están en *Project Settings → API*.
- **Gemini:** crear una API key en <https://ai.google.dev/gemini-api/docs/api-key>. Sin esta clave, la app abre pero no puede generar ejercicios.
- **Google OAuth:** las tres variables `GOOGLE_*` se usan únicamente para el inicio de sesión con Google.

> El archivo `.env` contiene claves privadas: **no debe subirse al repositorio**. Verificá que esté listado en `.gitignore`.

## Base de datos

En el **SQL Editor** de Supabase, ejecutar los scripts `.sql` de la raíz. Empezá por `supabase_usuarios_regulacion.sql`, que crea la tabla de usuarios:

1. `supabase_usuarios_regulacion.sql`
2. `supabase_ejercicios_reappraisal.sql`
3. `supabase_progreso_juegos_reappraisal.sql`
4. `supabase_juegos_texto_libre.sql`
5. `supabase_reportes_emocionales.sql`
6. `supabase_temas_seguimiento.sql`
7. `supabase_chequeos_bienestar.sql`

## Cómo correrla

```bash
python app.py
```

Para correrla como aplicación web en el navegador, definir la variable `FLET_WEB=true` antes de ejecutar.

## Despliegue

En producción la aplicación se despliega en Render como aplicación web. Las variables de entorno de la sección *Configuración* se cargan desde el panel de Render, junto con `FLET_WEB=true`.

## Documentación adicional

- `BIBLIOGRAFIA.md`: fuentes teóricas del proyecto (regulación emocional y reevaluación cognitiva).
- `banco_situaciones_reappraisal.md`: banco de situaciones de ejemplo.

## Autoras

- Josefina Casas Pardo
- Paula Ho

Profesor: Silvio Musolino
