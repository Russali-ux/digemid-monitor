"""
email_html.py — Plantilla HTML del correo "CONKOMERCO Alertas".
Tablas + estilos inline (compatible con Gmail, Outlook y móviles).
Contenido: últimas N alertas DIGEMID + últimas M modificatorias por seguridad,
con los mismos campos de las vistas de Alertas-analyzer.
"""
from html import escape

AZUL = "#0d1b8c"        # azul del logo ConkoSafe (igual que Alertas-analyzer)
AZUL_CLARO = "#E8EBFA"
ROJO, ROJO_BG = "#B42318", "#FEF3F2"
NARANJA, NARANJA_BG = "#B54708", "#FFFAEB"
VERDE, VERDE_BG = "#067647", "#ECFDF3"
GRIS, GRIS_BG, BORDE = "#475467", "#F9FAFB", "#EAECF0"

URL_ALERTAS = "https://russali-ux.github.io/Alertas-analyzer/"
URL_MODIF = "https://russali-ux.github.io/Alertas-analyzer/modificatorias/"
URL_DIGEMID = "https://www.digemid.minsa.gob.pe/webDigemid/publicaciones/alertas-modificaciones/alertas/"


def e(v, vacio="—"):
    v = ("" if v is None else str(v)).strip()
    return escape(v) if v else f'<span style="color:#98A2B3;">{vacio}</span>'


def fmt_fecha(iso):
    iso = (iso or "")[:10]
    return f"{iso[8:10]}/{iso[5:7]}/{iso[:4]}" if len(iso) == 10 else "—"


def pill(texto, color, bg):
    return (f'<span style="display:inline-block;background:{bg};color:{color};border:1px solid {color}33;'
            f'font-size:11px;font-weight:bold;padding:2px 8px;border-radius:10px;white-space:nowrap;">'
            f'{escape(texto)}</span>')


def pill_urgencia(u):
    u = (u or "").upper()
    if u == "INMEDIATA":
        return pill("INMEDIATA", ROJO, ROJO_BG)
    if u == "PREVENTIVA":
        return pill("PREVENTIVA", NARANJA, NARANJA_BG)
    return pill(u or "SIN EVALUAR", GRIS, GRIS_BG)


def boton(texto, url, color=AZUL):
    return (f'<a href="{escape(url)}" style="display:inline-block;color:{color};font-size:12px;font-weight:bold;'
            f'text-decoration:none;border:1px solid {color}55;border-radius:6px;padding:5px 10px;margin:0 6px 0 0;">'
            f'{texto}</a>')


def fila_campo(etiqueta, valor_html):
    return (f'<tr><td valign="top" style="width:140px;padding:5px 10px 5px 0;font-size:11px;color:#667085;'
            f'text-transform:uppercase;letter-spacing:.4px;">{etiqueta}</td>'
            f'<td valign="top" style="padding:5px 0;font-size:13px;color:#101828;line-height:1.45;'
            f'word-break:break-word;overflow-wrap:anywhere;">{valor_html}</td></tr>')


def tarjeta(cabecera_izq, cabecera_der, titulo, campos, enlaces, color_borde):
    return (
        f'<tr><td style="padding:0 28px 14px;">'
        f'<table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDE};'
        f'border-left:4px solid {color_borde};border-radius:8px;background:#fff;">'
        f'<tr><td style="padding:12px 16px 4px;">'
        f'<table width="100%" cellpadding="0" cellspacing="0"><tr>'
        f'<td style="font-size:12px;color:{GRIS};font-weight:bold;">{cabecera_izq}</td>'
        f'<td align="right" style="white-space:nowrap;">{cabecera_der}</td></tr></table>'
        f'<p style="margin:8px 0 6px;font-size:15px;font-weight:bold;color:#101828;line-height:1.35;">{titulo}</p>'
        f'<table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed;">'
        f'<colgroup><col width="140"><col></colgroup>{"".join(campos)}</table>'
        f'</td></tr>'
        f'<tr><td style="padding:6px 16px 12px;">{"".join(enlaces)}</td></tr>'
        f'</table></td></tr>'
    )


def seccion(titulo, subtitulo, url, color=AZUL):
    return (
        f'<tr><td style="padding:22px 28px 12px;">'
        f'<table width="100%" cellpadding="0" cellspacing="0"><tr>'
        f'<td><p style="margin:0;font-size:17px;font-weight:bold;color:{color};">{titulo}</p>'
        f'<p style="margin:2px 0 0;font-size:12px;color:#667085;">{subtitulo}</p></td>'
        f'<td align="right" valign="bottom"><a href="{url}" style="font-size:12px;color:{color};'
        f'font-weight:bold;text-decoration:none;white-space:nowrap;">Ver todo &rarr;</a></td>'
        f'</tr></table></td></tr>'
    )


def bloque_alerta(a):
    lotes = a.get("lotes") or []
    lotes_html = " ".join(
        f'<span style="display:inline-block;font-family:Consolas,monospace;font-size:12px;background:{GRIS_BG};'
        f'border:1px solid {BORDE};border-radius:4px;padding:1px 6px;margin:0 3px 3px 0;">{escape(l)}</span>'
        for l in lotes) if lotes else e(None, "Sin lote")
    tipo = a.get("tipo_alerta") or "General"
    der = pill(tipo, AZUL, AZUL_CLARO) + "&nbsp;" + pill_urgencia(a.get("urgencia"))
    izq = f'ALERTA DIGEMID {escape(a.get("numero_alerta") or "")} &middot; {fmt_fecha(a.get("fecha_publicacion"))}'
    campos = [
        fila_campo("Titular impactado", e(a.get("titular_registro_sanitario"), "Sin titular")),
        fila_campo("N° Lote", lotes_html),
        fila_campo("Acción principal", f'<strong>{e(a.get("accion_principal"), "Sin analizar")}</strong>'),
        fila_campo("Resumen IA", e(a.get("resumen_ia"), "Sin resumen")),
    ]
    enlaces = []
    if a.get("url_pagina_digemid"):
        enlaces.append(boton("Ver en DIGEMID", a["url_pagina_digemid"]))
    if a.get("url_pdf"):
        enlaces.append(boton("PDF de la alerta", a["url_pdf"], GRIS))
    color = ROJO if (a.get("urgencia") or "").upper() == "INMEDIATA" else NARANJA
    return tarjeta(izq, der, e(a.get("producto"), "Producto no especificado"), campos, enlaces, color)


def plazo_html(d):
    lim, r = d.get("fecha_limite"), d.get("dh_restantes")
    if lim is None:
        return e(None)
    base = f'{lim.strftime("%d/%m/%Y")} (15 días hábiles)'
    if r < 0:
        return f'{base} &middot; <span style="color:#667085;">plazo cumplido</span>'
    if r <= 5:
        return f'{base} &middot; <strong style="color:{ROJO};">quedan {r} d.h.</strong>'
    return f'{base} &middot; <strong style="color:{VERDE};">quedan {r} d.h.</strong>'


def bloque_modificatoria(d):
    titulares = [t.strip() for t in (d.get("titular_rs") or "").split("/") if t.strip()]
    titular_html = "<br>".join(escape(t) for t in titulares) if titulares else e(None, "Sin titular")
    izq = f'{escape(d.get("n_modificacion") or "")} &middot; {fmt_fecha(d.get("fecha_publicacion"))}'
    der = pill(d.get("tipo_modificacion") or "SEGURIDAD", AZUL, AZUL_CLARO) + "&nbsp;" + pill_urgencia(d.get("urgencia"))
    campos = [
        fila_campo("Principio activo", e(d.get("principio_activo"))),
        fila_campo("Titular RS", titular_html),
        fila_campo("Resumen", e(d.get("resumen"))),
        fila_campo("Acción requerida", f'<strong>{e(d.get("accion_requerida"))}</strong>'),
        fila_campo("Fecha límite", plazo_html(d)),
        fila_campo("Indicador tiempos", e(d.get("indicador_tiempos"))),
        fila_campo("Base legal", e(d.get("base_legal"))),
    ]
    enlaces = []
    if d.get("url_pagina_digemid"):
        enlaces.append(boton("Ver publicación", d["url_pagina_digemid"]))
    if d.get("url_pdf_digemid"):
        enlaces.append(boton("PDF DIGEMID", d["url_pdf_digemid"], GRIS))
    return tarjeta(izq, der, e(d.get("producto"), "Producto no especificado"), campos, enlaces, AZUL)


def kpi(valor, etiqueta, color, bg):
    return (f'<td width="25%" style="padding:4px;"><div style="background:{bg};border-radius:8px;padding:12px 6px;'
            f'text-align:center;border-top:3px solid {color};">'
            f'<div style="font-size:26px;font-weight:bold;color:{color};line-height:1;">{valor}</div>'
            f'<div style="font-size:11px;color:#475467;margin-top:5px;line-height:1.3;">{etiqueta}</div></div></td>')


def construir_html(alertas, modificatorias, fecha_txt, adjunto_nombre, estado_scraper=None):
    n_a, n_m = len(alertas), len(modificatorias)
    n_inm = sum(1 for a in alertas if (a.get("urgencia") or "").upper() == "INMEDIATA")
    n_pre = sum(1 for a in alertas if (a.get("urgencia") or "").upper() == "PREVENTIVA")
    ultima = fmt_fecha(alertas[0]["fecha_publicacion"]) if alertas else "—"

    aviso_scraper = ""
    if estado_scraper and estado_scraper != "success":
        aviso_scraper = (
            f'<tr><td style="padding:0 28px 10px;"><p style="margin:0;font-size:11px;color:{NARANJA};">'
            f'Nota: el scraping de esta ejecuci&oacute;n no termin&oacute; correctamente; el contenido proviene '
            f'de la base consolidada ConkoSafe IA.</p></td></tr>')

    partes = [
        '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1"></head>'
        '<body style="margin:0;padding:0;background:#F2F4F7;font-family:Arial,Helvetica,sans-serif;">'
        '<table width="100%" cellpadding="0" cellspacing="0" style="background:#F2F4F7;padding:24px 0;">'
        '<tr><td align="center">'
        '<table width="680" cellpadding="0" cellspacing="0" style="max-width:680px;width:100%;background:#fff;'
        'border-radius:12px;overflow:hidden;border:1px solid #EAECF0;">',
        # Encabezado
        f'<tr><td bgcolor="{AZUL}" style="background:{AZUL};padding:24px 28px;">'
        '<p style="margin:0;color:#C7CEF5;font-size:11px;text-transform:uppercase;letter-spacing:1.4px;">'
        'ConkoSafe IA &mdash; PV Intelligence</p>'
        '<h1 style="margin:6px 0 0;color:#fff;font-size:22px;line-height:1.3;">Alertas y Modificatorias DIGEMID</h1>'
        f'<p style="margin:4px 0 0;color:#C7CEF5;font-size:12px;">Reporte del {escape(fecha_txt)} (hora Lima)'
        f' &middot; &uacute;ltima alerta publicada: {ultima}</p></td></tr>',
        # KPIs
        '<tr><td style="padding:18px 24px 6px;"><table width="100%" cellpadding="0" cellspacing="0"><tr>'
        + kpi(n_a, "&Uacute;ltimas<br>alertas", AZUL, AZUL_CLARO)
        + kpi(n_inm, "Urgencia<br>inmediata", ROJO, ROJO_BG)
        + kpi(n_pre, "Urgencia<br>preventiva", NARANJA, NARANJA_BG)
        + kpi(n_m, "Modificatorias<br>por seguridad", VERDE, VERDE_BG)
        + '</tr></table></td></tr>',
        aviso_scraper,
        # Alertas
        seccion(f"&Uacute;ltimas {n_a} alertas DIGEMID",
                "Falsificados, retiros del mercado, control de calidad y seguridad", URL_ALERTAS),
        *[bloque_alerta(a) for a in alertas],
        # Modificatorias
        seccion(f"&Uacute;ltimas {n_m} modificatorias por seguridad",
                "Actualizaciones de inserto / ficha t&eacute;cnica &mdash; Art. 6, 13, 36, 37, 151 D.S. 016-2011-SA",
                URL_MODIF),
        *[bloque_modificatoria(d) for d in modificatorias],
        # Adjunto + pasos
        '<tr><td style="padding:10px 28px 6px;">'
        f'<div style="background:{AZUL_CLARO};border-radius:8px;padding:12px 16px;">'
        f'<p style="margin:0;font-size:13px;color:{AZUL};font-weight:bold;">&#128206; Excel adjunto</p>'
        f'<p style="margin:3px 0 0;font-size:12px;color:#475467;">{escape(adjunto_nombre)} &mdash; '
        'hojas &laquo;Alertas&raquo; y &laquo;Modificatorias&raquo; con todos los campos de este correo.</p>'
        '</div></td></tr>',
        '<tr><td style="padding:10px 28px 20px;">'
        f'<div style="background:{GRIS_BG};border-radius:8px;padding:12px 16px;">'
        '<p style="margin:0 0 6px;font-size:13px;color:#101828;font-weight:bold;">Pasos de revisi&oacute;n recomendados</p>'
        '<ol style="margin:0;padding-left:18px;font-size:12px;color:#344054;line-height:1.8;">'
        '<li>Verificar si el producto, lote o titular afecta su portafolio o cadena de distribuci&oacute;n.</li>'
        '<li>Alertas <strong>INMEDIATAS</strong>: inmovilizar / retirar sin demora en almac&eacute;n y puntos de venta.</li>'
        '<li>Modificatorias: evaluar impacto y comunicar posici&oacute;n a DIGEMID dentro de los 15 d&iacute;as h&aacute;biles.</li>'
        '<li>Registrar la alerta y la acci&oacute;n tomada (FT-69 / registro interno de farmacovigilancia).</li>'
        '</ol></div></td></tr>',
        # Pie
        f'<tr><td style="background:{GRIS_BG};padding:14px 28px;border-top:1px solid {BORDE};">'
        '<p style="margin:0;font-size:11px;color:#667085;line-height:1.6;">'
        'Monitoreo desarrollado para Conkomerco y enviado autom&aacute;ticamente por ConkoSafe IA. '
        'La IA puede cometer errores: confirme siempre en la fuente oficial. '
        f'<a href="{URL_DIGEMID}" style="color:{AZUL};">digemid.minsa.gob.pe</a> &middot; '
        f'<a href="{URL_ALERTAS}" style="color:{AZUL};">Alertas-analyzer</a></p></td></tr>',
        '</table></td></tr></table></body></html>',
    ]
    return "".join(partes)
