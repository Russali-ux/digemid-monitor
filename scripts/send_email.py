"""
send_email.py — Envía correo HTML con Excel de Alertas DIGEMID adjunto
(falsificados, retiros del mercado y control de calidad).
Remitente: conkosafe.ai@gmail.com
Destinatarios: ocultos (BCC via envelope SMTP, sin header Bcc en el mensaje)
"""
import os, glob, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# ✅ Se leen desde variables de entorno definidas en el YML
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'conkosafe.ai@gmail.com')
EMAIL_TO   = os.environ['EMAIL_TO']   # lista completa separada por comas

smtp_host   = os.environ['SMTP_HOST']
smtp_port   = int(os.environ.get('SMTP_PORT', '587'))
smtp_user   = os.environ['SMTP_USER']
smtp_pass   = os.environ['SMTP_PASS']
total       = os.environ.get('TOTAL', '0')
inmediatas  = os.environ.get('INMEDIATAS', '0')
preventivas = os.environ.get('PREVENTIVAS', '0')
fecha       = os.environ.get('FECHA', '')
excel_name  = os.environ.get('EXCEL_NAME', 'alertas_digemid.xlsx')
motor       = os.environ.get('MOTOR', 'Heuristico')

n_inm = int(inmediatas)
n_pre = int(preventivas)
n_tot = int(total)

# Badge de estado
if n_inm > 0:
    badge_color = "#C00000"
    badge_texto = f"ATENCION: {n_inm} alerta(s) con accion INMEDIATA requerida"
elif n_pre > 0:
    badge_color = "#ED7D31"
    badge_texto = f"{n_pre} alerta(s) PREVENTIVA(S) — Revisar y tomar medidas"
else:
    badge_color = "#2E75B6"
    badge_texto = f"{n_tot} alerta(s) sanitaria(s) — Sin urgencias criticas"

motor_txt = "Claude API" if motor == "Claude API" else "Motor Heuristico"

# Buscar Excel generado — el scraper de alertas nombra el archivo
# alertas_digemid_YYYYMMDD_HHMM.xlsx; si el patrón cambia, cae a cualquier .xlsx en /tmp
archivos = glob.glob('/tmp/alertas_digemid_*.xlsx') or glob.glob('/tmp/*.xlsx')
if not archivos:
    raise FileNotFoundError("No se encontro ningun Excel de alertas en /tmp/")
ruta_excel = sorted(archivos)[-1]

# Titulares de Registro Sanitario impactados (se lee del propio Excel generado
# por el scraper, columna "Titular Registro Sanitario")
titulares_html = ""
try:
    import pandas as pd
    df_rep = pd.read_excel(ruta_excel)
    col_tit = next((c for c in df_rep.columns if "titular" in c.lower()), None)
    col_urg = next((c for c in df_rep.columns if "urgencia" in c.lower()), None)
    if col_tit:
        df_rep[col_tit] = df_rep[col_tit].astype(str).str.strip()
        con_titular = df_rep[~df_rep[col_tit].str.upper().isin(["", "NAN", "NONE"])]
        if not con_titular.empty:
            filas = []
            for titular, grupo in con_titular.groupby(col_tit):
                n_alertas = len(grupo)
                es_inmediata = bool(
                    col_urg and (grupo[col_urg].astype(str).str.upper() == "INMEDIATA").any()
                )
                color = "#C00000" if es_inmediata else "#1F4E79"
                filas.append(
                    f'<li style="margin:4px 0;">'
                    f'<span style="color:{color};font-weight:bold;">{titular}</span>'
                    f' &mdash; {n_alertas} alerta(s)'
                    f'{" 🔴" if es_inmediata else ""}</li>'
                )
            titulares_html = (
                '<tr><td style="padding:0 32px 22px;">'
                '<div style="background:#F7F3FB;border-left:4px solid #6B3FA0;padding:14px 18px;'
                'border-radius:0 8px 8px 0;">'
                '<p style="margin:0 0 8px;font-size:13px;color:#4B2E7A;font-weight:bold;">'
                '&#127970; Titulares de Registro Sanitario impactados</p>'
                f'<ul style="margin:0;padding-left:18px;font-size:13px;color:#333;">'
                f'{"".join(filas)}</ul>'
                '</div></td></tr>'
            )
except Exception as e:
    print(f"[Aviso] No se pudo extraer titulares de registro sanitario del Excel: {e}")

html = (
    '<!DOCTYPE html><html lang="es"><head>'
    '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    '</head><body style="margin:0;padding:0;background:#F0F2F5;font-family:Arial,sans-serif;">'
    '<table width="100%" cellpadding="0" cellspacing="0" style="background:#F0F2F5;padding:28px 0;">'
    '<tr><td align="center">'
    '<table width="640" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;'
    'overflow:hidden;box-shadow:0 3px 16px rgba(0,0,0,.12);">'
    '<tr><td style="background:linear-gradient(135deg,#1F4E79 0%,#2E75B6 100%);padding:26px 32px;">'
    '<table width="100%" cellpadding="0" cellspacing="0"><tr><td>'
    '<p style="margin:0;color:#BDD7EE;font-size:11px;text-transform:uppercase;letter-spacing:1.2px;">'
    'CONKOSAFE IA &mdash; PV Intelligence</p>'
    '<h1 style="margin:6px 0 0;color:#fff;font-size:21px;font-weight:bold;line-height:1.3;">'
    'Alertas Sanitarias DIGEMID</h1>'
    '<p style="margin:4px 0 0;color:#BDD7EE;font-size:12px;">'
    f'Falsificados, Retiros y Calidad &mdash; {fecha} hora Lima</p>'
    '</td>'
    f'<td align="right" valign="middle" style="padding-left:16px;">'
    f'<span style="background:rgba(255,255,255,.15);color:#fff;font-size:11px;'
    f'padding:5px 12px;border-radius:20px;white-space:nowrap;">{motor_txt}</span>'
    '</td></tr></table></td></tr>'
    f'<tr><td style="padding:20px 32px 0;">'
    f'<div style="background:{badge_color};color:#fff;padding:13px 20px;border-radius:8px;'
    f'font-weight:bold;font-size:14px;text-align:center;letter-spacing:.3px;">'
    f'{badge_texto}</div></td></tr>'
    '<tr><td style="padding:18px 32px;">'
    '<table width="100%" cellspacing="10" cellpadding="0"><tr>'
    '<td width="33%" style="background:#F0F5FF;border-radius:10px;padding:16px 10px;'
    'text-align:center;border-top:4px solid #1F4E79;">'
    f'<div style="font-size:36px;font-weight:bold;color:#1F4E79;">{total}</div>'
    '<div style="font-size:12px;color:#555;margin-top:5px;">Alertas<br>Sanitarias</div></td>'
    '<td width="33%" style="background:#FFFBF0;border-radius:10px;padding:16px 10px;'
    'text-align:center;border-top:4px solid #ED7D31;">'
    f'<div style="font-size:36px;font-weight:bold;color:#ED7D31;">{preventivas}</div>'
    '<div style="font-size:12px;color:#555;margin-top:5px;">Preventivas<br>(seguimiento)</div></td>'
    '<td width="33%" style="background:#FFF5F5;border-radius:10px;padding:16px 10px;'
    'text-align:center;border-top:4px solid #C00000;">'
    f'<div style="font-size:36px;font-weight:bold;color:#C00000;">{inmediatas}</div>'
    '<div style="font-size:12px;color:#555;margin-top:5px;">Inmediatas<br>(acci&oacute;n urgente)</div></td>'
    '</tr></table></td></tr>'
    '<tr><td style="padding:4px 32px 18px;">'
    '<div style="background:#EBF3FB;border-left:4px solid #2E75B6;padding:14px 18px;'
    'border-radius:0 8px 8px 0;">'
    '<p style="margin:0 0 4px;font-size:13px;color:#1F4E79;font-weight:bold;">'
    '&#128206; Excel adjunto a este correo</p>'
    f'<p style="margin:0;font-size:12px;color:#555;">{excel_name}</p>'
    '<p style="margin:6px 0 0;font-size:11px;color:#888;">'
    'Contiene las alertas sanitarias m&aacute;s recientes publicadas por DIGEMID '
    '(productos falsificados, retiros del mercado y control de calidad)'
    '</p></div></td></tr>'
    '<tr><td style="padding:0 32px 22px;">'
    '<div style="background:#F4FBF0;border-left:4px solid #375623;padding:14px 18px;'
    'border-radius:0 8px 8px 0;">'
    '<p style="margin:0 0 8px;font-size:13px;color:#375623;font-weight:bold;">'
    '&#9989; Pasos de revisi&oacute;n recomendados</p>'
    '<ol style="margin:0;padding-left:18px;font-size:13px;color:#333;line-height:2;">'
    '<li>Abrir el Excel adjunto &mdash; columna <strong>Urgencia</strong> ya viene coloreada</li>'
    '<li>Revisar <strong>Acci&oacute;n Principal</strong> (retiro, no comercializar, suspensi&oacute;n, etc.)</li>'
    '<li>Verificar si el producto/laboratorio afecta tu cadena de distribuci&oacute;n o portafolio</li>'
    '<li>Comunicar a Almac&eacute;n / Compras / Direcci&oacute;n T&eacute;cnica seg&uacute;n corresponda</li>'
    '<li>Registrar la alerta y la acci&oacute;n tomada en el registro interno de farmacovigilancia/calidad</li>'
    '</ol></div></td></tr>'
    f'{titulares_html}'
    '<tr><td style="padding:0 32px 22px;">'
    '<div style="background:#FFFBF0;border-left:4px solid #ED7D31;padding:12px 18px;'
    'border-radius:0 8px 8px 0;">'
    '<p style="margin:0;font-size:12px;color:#7F4B00;">'
    '<strong>&#9201; Recordatorio:</strong> Las alertas de urgencia <strong>INMEDIATA</strong> '
    '(falsificaci&oacute;n, retiro del mercado) requieren verificaci&oacute;n y acci&oacute;n sin demora '
    'en almac&eacute;n y puntos de venta.'
    '</p></div></td></tr>'
    '<tr><td style="background:#F4F6F9;padding:14px 32px;border-top:1px solid #E5E8ED;">'
    '<table width="100%" cellpadding="0" cellspacing="0"><tr>'
    '<td style="font-size:11px;color:#999;">'
    'Monitoreo desarrollado para Conkomerco, y enviado automáticamente por Conkosafe, se recomienda siempre revisar la web de Digemid, ya que la IA puede cometer errores'
    '</td>'
    '<td align="right">'
    '<a href="https://www.digemid.minsa.gob.pe/webDigemid/publicaciones/alertas-modificaciones/alertas/" '
    'style="color:#1F4E79;text-decoration:none;font-size:11px;">Fuente:digemid.minsa.gob.pe</a>'
    '</td></tr></table></td></tr>'
    '</table></td></tr></table>'
    '</body></html>'
)

# Asunto — formato fijo: "CONKOMERCO Alertas (fecha del reporte)"
fecha_corta = fecha[:10] if fecha else ""
asunto = f"CONKOMERCO Alertas ({fecha_corta})" if fecha_corta else "CONKOMERCO Alertas"

# Construir mensaje
# ✅ Solo EMAIL_FROM en el header "To" — ningún destinatario es visible
# ✅ NO se agrega header "Bcc" — evita que los clientes de correo lo expongan
msg = MIMEMultipart('mixed')
msg['Subject']  = asunto
msg['From']     = f"Monitor DIGEMID CONKOMERCO <{EMAIL_FROM}>"
msg['To']       = EMAIL_FROM        # Solo el remitente visible en "Para"
msg['Reply-To'] = EMAIL_FROM
msg.attach(MIMEText(html, 'html'))

# Adjuntar Excel
with open(ruta_excel, 'rb') as f:
    adjunto = MIMEBase('application',
                       'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    adjunto.set_payload(f.read())
encoders.encode_base64(adjunto)
adjunto.add_header('Content-Disposition', f'attachment; filename="{excel_name}"')
msg.attach(adjunto)

# ✅ Lista de destinatarios solo para el envelope SMTP (no aparece en el correo)
destinatarios = [e.strip() for e in EMAIL_TO.split(',') if e.strip()]

with smtplib.SMTP(smtp_host, smtp_port) as server:
    server.ehlo()
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.sendmail(EMAIL_FROM, destinatarios, msg.as_string())

print(f"Correo enviado: {EMAIL_FROM} -> {len(destinatarios)} destinatarios (ocultos)")
print(f"Asunto: {asunto}")
