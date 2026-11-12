"""
excel_resumen.py — Excel adjunto al correo con las mismas filas del correo:
hoja "Alertas" (últimas N de alertas_digemid) y hoja "Modificatorias"
(últimas M de modificatorias_digemid). Cabecera estilo ConkoSafe IA.
"""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

AZUL = "0D1B8C"
FILL_URG = {"INMEDIATA": "FEE4E2", "PREVENTIVA": "FEF0C7"}
BORDE = Border(*(Side(style="thin", color="D0D5DD"),) * 4)

COLS_ALERTAS = [
    ("anio", "Año", 8), ("fecha_publicacion", "Fecha Pub.", 12), ("numero_alerta", "N° Alerta", 14),
    ("titulo", "Título", 28), ("producto", "Producto", 40), ("titular_registro_sanitario", "Titular impactado", 30),
    ("numero_lote", "N° Lote", 18), ("tipo_alerta", "Tipo de Alerta", 18), ("urgencia", "Urgencia", 13),
    ("accion_principal", "Acción Principal", 26), ("resumen_ia", "Resumen IA", 60),
    ("url_pagina_digemid", "URL DIGEMID", 30), ("url_pdf", "URL PDF", 30),
]
COLS_MODIF = [
    ("fecha_publicacion", "Fecha publicación", 12), ("n_modificacion", "N° modificación", 24),
    ("producto", "Producto", 30), ("principio_activo", "Principio activo", 30), ("titular_rs", "Titular RS", 40),
    ("tipo_modificacion", "Tipo", 22), ("urgencia", "Urgencia", 13), ("fecha_limite", "Fecha límite (15 d.h.)", 14),
    ("dh_restantes", "Días hábiles restantes", 12), ("accion_requerida", "Acción requerida", 40),
    ("indicador_tiempos", "Indicador tiempos", 40), ("base_legal", "Base legal", 30), ("resumen", "Resumen", 60),
    ("url_pagina_digemid", "URL publicación", 30), ("url_pdf_digemid", "URL PDF", 30),
]


def _hoja(ws, titulo, fecha_txt, filas, cols):
    n = len(cols)
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=n)
    ws.cell(1, 1, f"ConkoSafe IA — {titulo}").font = Font(bold=True, size=14, color="FFFFFF")
    ws.cell(1, 1).fill = PatternFill("solid", fgColor=AZUL)
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=n)
    ws.cell(2, 1, f"Generado: {fecha_txt} (hora Lima) | N° de registros: {len(filas)} | Fuente: DIGEMID / Alertas-analyzer")
    ws.cell(2, 1).font = Font(italic=True, size=9, color="475467")
    for j, (_, cab, ancho) in enumerate(cols, 1):
        c = ws.cell(4, j, cab)
        c.font, c.fill, c.border = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="2E3A8C"), BORDE
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(j)].width = ancho
    for i, f in enumerate(filas, 5):
        for j, (k, _, _) in enumerate(cols, 1):
            v = f.get(k)
            if k == "dh_restantes" and v is not None and v < 0:
                v = "Plazo cumplido"
            c = ws.cell(i, j, v)
            c.border, c.alignment = BORDE, Alignment(vertical="top", wrap_text=True)
            if k == "fecha_limite" and v:
                c.number_format = "DD/MM/YYYY"
            if k.startswith("url") and v:
                c.hyperlink, c.font = v, Font(color="1F4FD1", underline="single")
            if k == "urgencia" and (v or "").upper() in FILL_URG:
                c.fill, c.font = PatternFill("solid", fgColor=FILL_URG[v.upper()]), Font(bold=True)
    ws.freeze_panes = "A5"
    ws.auto_filter.ref = f"A4:{get_column_letter(n)}{4 + len(filas)}"


def construir_excel(alertas, modificatorias, ruta, fecha_txt):
    wb = Workbook()
    _hoja(wb.active, f"Últimas {len(alertas)} alertas DIGEMID", fecha_txt, alertas, COLS_ALERTAS)
    wb.active.title = "Alertas"
    _hoja(wb.create_sheet("Modificatorias"), f"Últimas {len(modificatorias)} modificatorias por seguridad",
          fecha_txt, modificatorias, COLS_MODIF)
    wb.save(ruta)
    return ruta
