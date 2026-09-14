import csv
import io

from dre.tipos_situacion import TIPO_OBSESION

def calcular_distorsiones_frecuentes(reportes, top_n=3):
    # Cuenta cuántas veces aparece cada distorsión marcada a lo largo de
    # TODOS los reportes de la persona (no por tema puntual), para mostrar
    # un patrón general en el resumen del historial.
    conteo = {}
    for rep in reportes:
        texto = rep.get("distorsiones") or ""
        for nombre in [n.strip() for n in texto.split(",") if n.strip()]:
            conteo[nombre] = conteo.get(nombre, 0) + 1
    return sorted(conteo.items(), key=lambda kv: kv[1], reverse=True)[:top_n]


# ==========================================================
# --- COMPARTIR EL HISTORIAL ---
# ----------------------------------------------------------
# Primera versión, sin backend propio para compartir: arma una planilla
# (CSV) descargable con todo el historial, y un resumen de texto corto
# para compartir directo por WhatsApp/mail (con el propio botón de
# WhatsApp/mail del celular, no se manda nada automáticamente — la
# persona elige el destinatario y confirma el envío ella misma). Cuando
# haya un backend propio (Supabase configurado del todo), esto se puede
# reemplazar por un link compartible de verdad.
# ==========================================================
def generar_csv_historial(reportes):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["Fecha", "Situación", "Tipo de situación", "Emoción", "Intensidad (0-10)", "% inicial", "% final", "Pensamiento alternativo / compromiso"])
    for rep in sorted(reportes, key=lambda x: x.get("fecha") or ""):
        writer.writerow([
            (rep.get("fecha") or "")[:10],
            rep.get("situacion") or "",
            rep.get("tipo_situacion") or "",
            rep.get("emocion_inicial") or "",
            rep.get("intensidad_inicial", ""),
            rep.get("creencia_inicial_pct", ""),
            rep.get("creencia_final_pct", ""),
            rep.get("pensamiento_alternativo") or "",
        ])
    return buffer.getvalue()


def generar_texto_resumen_historial(reportes, maximo=15):
    # Se limita a los últimos registros para que el link de WhatsApp/mail
    # no quede demasiado largo (los enlaces muy extensos pueden fallar).
    ordenados = sorted(reportes, key=lambda x: x.get("fecha") or "", reverse=True)[:maximo]
    ordenados.reverse()
    lineas = ["Mi evolución en DRE:", ""]
    for rep in ordenados:
        fecha = (rep.get("fecha") or "")[:10]
        situ = (rep.get("situacion") or "")[:60]
        etiqueta = "impulso" if rep.get("tipo_situacion") == TIPO_OBSESION else "creencia"
        lineas.append(f"{fecha} — {situ}: {etiqueta} {rep.get('creencia_inicial_pct')}% → {rep.get('creencia_final_pct')}%")
    return "\n".join(lineas)

