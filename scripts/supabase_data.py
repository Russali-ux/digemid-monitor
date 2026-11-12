"""
supabase_data.py — Lee de Supabase (proyecto Alertas-analyzer) las últimas
alertas DIGEMID y las últimas modificatorias por seguridad, con los mismos
campos que muestran las vistas web:

  https://russali-ux.github.io/Alertas-analyzer/                 (alertas_digemid)
  https://russali-ux.github.io/Alertas-analyzer/modificatorias/  (modificatorias_digemid)

Usa la API REST (PostgREST) con la anon key, igual que el frontend público.
"""
import os
import re
from datetime import date, datetime, timedelta, timezone

import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://ggbnfdaxtsngsjssrwrl.supabase.co").rstrip("/")
# La anon key ya es pública (está en el HTML de Alertas-analyzer); se prefiere el secret si existe.
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY") or (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnYm5mZGF4dHNuZ3Nqc3Nyd3JsIiwi"
    "cm9sZSI6ImFub24iLCJpYXQiOjE3ODQ4ODAzODIsImV4cCI6MjEwMDQ1NjM4Mn0.126hhMpakcOlzp5KyyWdMU56UjwLwn5Xn4Nc13OIjgU"
)

COLS_ALERTAS = (
    "id,titulo,producto,titular_registro_sanitario,numero_lote,tipo_alerta,urgencia,"
    "accion_principal,resumen_ia,fecha_publicacion,anio_publicacion,"
    "url_pagina_digemid,url_pdf_github,url_pdf_digemid"
)
COLS_MODIF = (
    "id,n_modificacion,producto,principio_activo,titular_rs,fecha_publicacion,tipo_modificacion,"
    "urgencia,accion_requerida,indicador_tiempos,base_legal,resumen,url_pagina_digemid,url_pdf_digemid"
)

PLAZO_DH = 15  # días hábiles para evaluar e informar a DIGEMID


def _get(tabla, cols, limit):
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/{tabla}",
        params={"select": cols, "order": "fecha_publicacion.desc", "limit": str(limit)},
        headers={"apikey": SUPABASE_ANON_KEY, "Authorization": f"Bearer {SUPABASE_ANON_KEY}"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def _num(texto):
    """Extrae (número, año) de 'ALERTA DIGEMID N°133-2026' o 'MODIFICACIONES N° 19 – 2026'."""
    m = re.search(r"N[°ºo]\s*(\d+)\s*[-–]\s*(\d{4})", texto or "", re.I)
    return (int(m.group(2)), int(m.group(1))) if m else (0, 0)


# ── Alertas ─────────────────────────────────────────────────────────────────
def ultimas_alertas(n=10):
    filas = _get("alertas_digemid", COLS_ALERTAS, n + 20)
    filas.sort(key=lambda a: (a.get("fecha_publicacion") or "", _num(a.get("titulo"))), reverse=True)
    out = []
    for a in filas[:n]:
        anio_n, num = _num(a.get("titulo"))
        a["numero_alerta"] = f"N° {num:03d}-{anio_n}" if num else ""
        a["lotes"] = [l.strip() for l in (a.get("numero_lote") or "").split("|") if l.strip()]
        a["url_pdf"] = a.get("url_pdf_github") or a.get("url_pdf_digemid") or ""
        a["anio"] = a.get("anio_publicacion") or (a.get("fecha_publicacion") or "")[:4]
        out.append(a)
    return out


# ── Modificatorias ──────────────────────────────────────────────────────────
def _pascua(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mes = (h + l - 7 * m + 114) // 31
    dia = ((h + l - 7 * m + 114) % 31) + 1
    return date(y, mes, dia)


_FER = {}


def _feriados(y):
    """Feriados nacionales de Perú (mismo listado que la vista web de modificatorias)."""
    if y not in _FER:
        s = {date(y, int(md[:2]), int(md[3:])) for md in
             ["01-01", "05-01", "06-07", "06-29", "07-23", "07-28", "07-29",
              "08-06", "08-30", "10-08", "11-01", "12-08", "12-09", "12-25"]}
        p = _pascua(y)
        s |= {p - timedelta(days=3), p - timedelta(days=2)}  # Jueves y Viernes Santo
        _FER[y] = s
    return _FER[y]


def _es_habil(d):
    return d.weekday() < 5 and d not in _feriados(d.year)


def fecha_limite(desde, dh=PLAZO_DH):
    d, n = desde, 0
    while n < dh:
        d += timedelta(days=1)
        if _es_habil(d):
            n += 1
    return d


def dias_habiles_restantes(desde, hoy, dh=PLAZO_DH):
    d, n = desde, 0
    while d < hoy:
        d += timedelta(days=1)
        if _es_habil(d):
            n += 1
    return dh - n


def ultimas_modificatorias(n=4, hoy=None):
    hoy = hoy or datetime.now(timezone(timedelta(hours=-5))).date()  # hora Lima
    filas = _get("modificatorias_digemid", COLS_MODIF, n + 20)
    filas.sort(key=lambda d: (d.get("fecha_publicacion") or "", _num(d.get("n_modificacion"))), reverse=True)
    out = []
    for d in filas[:n]:
        if d.get("fecha_publicacion"):
            pub = date.fromisoformat(d["fecha_publicacion"][:10])
            d["fecha_limite"] = fecha_limite(pub)
            d["dh_restantes"] = dias_habiles_restantes(pub, hoy)
        else:
            d["fecha_limite"], d["dh_restantes"] = None, None
        out.append(d)
    return out


if __name__ == "__main__":
    for a in ultimas_alertas():
        print(a["fecha_publicacion"], a["numero_alerta"], a["urgencia"], (a["producto"] or "")[:60])
    print("---")
    for d in ultimas_modificatorias():
        print(d["fecha_publicacion"], d["n_modificacion"], d["fecha_limite"], d["dh_restantes"])
