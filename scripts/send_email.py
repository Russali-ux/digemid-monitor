import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_FROM = "conkosafe.ai@gmail.com"
EMAIL_TO   = "july.maita@conkomerco.com,finanzas@conkomerco.com,conkosafe.ai@gmail.com"
FOLDER_URL = "https://drive.google.com/drive/folders/1LOygkKnbednAw-eCPLM0-9TXLGj16hw4"

smtp_host      = os.environ['SMTP_HOST']
smtp_port      = int(os.environ.get('SMTP_PORT', '587'))
smtp_user      = os.environ['SMTP_USER']
smtp_pass      = os.environ['SMTP_PASS']
drive_file_url = os.environ.get('DRIVE_FILE_URL', '')
total          = os.environ.get('TOTAL', '0')
inmediatas     = os.environ.get('INMEDIATAS', '0')
preventivas    = os.environ.get('PREVENTIVAS', '0')
fecha          = os.environ.get('FECHA', '')
excel_name     = os.environ.get('EXCEL_NAME', 'alertas_digemid.xlsx')
motor          = os.environ.get('MOTOR', 'Heuristico')
drive_ok       = os.environ.get('DRIVE_STATUS', 'failure') == 'success'

n_inm = int(inmediatas)
n_pre = int(preventivas)

if n_inm > 0:
    badge_color = "#C00000"
    badge_texto = f"ALERTA: {n_inm} alerta(s) INMEDIATA(S) - ACCION REQUERIDA"
elif n_pre > 0:
    badge_color = "#ED7D31"
    badge_texto = f"{n_pre} alerta(s) preventiva(s) - Revisar"
else:
    badge_color = "#2E75B6"
    badge_texto = "Sin alertas urgentes en este periodo"

motor_txt = "Claude API" if motor == "Claude API" else "Motor Heuristico"

if drive_ok and drive_file_url:
    botones = (
        '<table cellpadding="0" cellspacing="0" style="margin:0 auto;">'
        '<tr>'
        '<td style="padding:0 8px;">'
        f'<a href="{drive_file_url}" style="display:inline-block;background:#1F4E79;color:#fff;'
        'padding:13px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;">'
        'Abrir Excel del periodo</a></td>'
        '<td style="padding:0 8px;">'
        f'<a href="{FOLDER_URL}" style="display:inline-block;background:#217346;color:#fff;'
        'padding:13px 24px;border-radius:6px;text-decoration:none;font-weight:bold;font-size:14px;">'
        'Ver carpeta completa</a></td>'
        '</tr></table>'
    )
else:
    botones = (
        f'<p style="color:#C00000;font-size:13px;text-align:center;">'
        f'El archivo no pudo subirse a Drive.<br>'
        f'<a href="{FOLDER_URL}" style="color:#1F4E79;">Ver carpeta en Drive</a></p>'
    )

html = (
    '<!DOCTYPE html><html lang="es"><head>'
    '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    '</head><body style="margin:0;padding:0;background:#F0F2F5;font-family:Arial,sans-serif;">'
    '<table width="100%" cellpadding="0" cellspacing="0" style="background:#F0F2F5;padding:28px 0;">'
    '<tr><td align="center">'
    '<table width="620" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;'
    'overflow:hidden;box-shadow:0 3px 16px rgba(0,0,0,.12);">'

    # HEADER
    '<tr><td style="background:linear-gradient(135deg,#1F4E79 0%,#2E75B6 100%);padding:26px 32px;">'
    '<table width="100%" cellpadding="0" cellspacing="0"><tr><td>'
    '<p style="margin:0;color:#BDD7EE;font-size:11px;text-transform:uppercase;letter-spacing:1px;">'
    'CONKOMERCO S.A.C. - Monitor Regulatorio</p>'
    '<h1 style="margin:6px 0 0;color:#fff;font-size:20px;font-weight:bold;">'
    'Alertas Sanitarias DIGEMID</h1>'
    f'<p style="margin:5px 0 0;color:#BDD7EE;font-size:13px;">Reporte del {fecha} - hora Lima</p>'
    '</td>'
    f'<td align="right" valign="middle"><span style="background:rgba(255,255,255,.15);color:#fff;'
    f'font-size:11px;padding:5px 10px;border-radius:20px;">{motor_txt}</span></td>'
    '</tr></table></td></tr>'

    # BADGE
    f'<tr><td style="padding:20px 32px 0;">'
    f'<div style="background:{badge_color};color:#fff;padding:12px 20px;border-radius:8px;'
    f'font-weight:bold;font-size:14px;text-align:center;">{badge_texto}</div></td></tr>'

    # METRICAS
    '<tr><td style="padding:18px 32px;">'
    '<table width="100%" cellspacing="10" cellpadding="0"><tr>'
    '<td width="33%" style="background:#F0F5FF;border-radius:10px;padding:16px 10px;'
    'text-align:center;border-top:4px solid #1F4E79;">'
    f'<div style="font-size:34px;font-weight:bold;color:#1F4E79;">{total}</div>'
    '<div style="font-size:12px;color:#555;margin-top:4px;">Total alertas</div></td>'
    '<td width="33%" style="background:#FFF5F5;border-radius:10px;padding:16px 10px;'
    'text-align:center;border-top:4px solid #C00000;">'
    f'<div style="font-size:34px;font-weight:bold;color:#C00000;">{inmediatas}</div>'
    '<div style="font-size:12px;color:#555;margin-top:4px;">Inmediatas</div></td>'
    '<td width="33%" style="background:#FFFBF0;border-radius:10px;padding:16px 10px;'
    'text-align:center;border-top:4px solid #ED7D31;">'
    f'<div style="font-size:34px;font-weight:bold;color:#ED7D31;">{preventivas}</div>'
    '<div style="font-size:12px;color:#555;margin-top:4px;">Preventivas</div></td>'
    '</tr></table></td></tr>'

    # BOTONES
    f'<tr><td style="padding:4px 32px 22px;text-align:center;">{botones}'
    f'<p style="margin:12px 0 0;font-size:11px;color:#999;">Archivo: '
    f'<code style="background:#F4F6F9;padding:2px 6px;border-radius:3px;">{excel_name}</code>'
    '</p></td></tr>'

    # PASOS
    '<tr><td style="padding:0 32px 22px;">'
    '<div style="background:#EBF3FB;border-left:4px solid #2E75B6;padding:14px 18px;'
    'border-radius:0 8px 8px 0;">'
    '<p style="margin:0 0 8px;font-size:13px;color:#1F4E79;font-weight:bold;">Pasos de revision</p>'
    '<ol style="margin:0;padding-left:18px;font-size:13px;color:#333;line-height:1.9;">'
    '<li>Abrir el Excel y filtrar columna <strong>Urgencia = INMEDIATA</strong> primero</li>'
    '<li>Revisar <strong>Accion Principal</strong> y columna <strong>Dirigido a</strong></li>'
    '<li>Comunicar internamente a CONKOMERCO / SOLTON PHARMA si corresponde</li>'
    '<li>Registrar en sistema de farmacovigilancia si aplica</li>'
    '</ol></div></td></tr>'

    # FOOTER
    '<tr><td style="background:#F4F6F9;padding:14px 32px;border-top:1px solid #E5E8ED;">'
    '<table width="100%" cellpadding="0" cellspacing="0"><tr>'
    '<td style="font-size:11px;color:#999;">Enviado automaticamente por Monitor DIGEMID via GitHub Actions</td>'
    '<td align="right"><a href="https://www.digemid.minsa.gob.pe/alertas" '
    'style="color:#1F4E79;text-decoration:none;font-size:11px;">digemid.minsa.gob.pe</a></td>'
    '</tr></table></td></tr>'

    '</table></td></tr></table></body></html>'
)

fecha_corta = fecha[:10] if fecha else ""
if n_inm > 0:
    asunto = f"[DIGEMID {fecha_corta}] {n_inm} alerta(s) INMEDIATA(S) - Accion requerida"
elif n_pre > 0:
    asunto = f"[DIGEMID {fecha_corta}] {n_pre} alerta(s) preventiva(s)"
else:
    asunto = f"[DIGEMID {fecha_corta}] {total} alertas - Sin urgencias"

msg = MIMEMultipart('alternative')
msg['Subject'] = asunto
msg['From']    = f"Monitor DIGEMID CONKOMERCO <{EMAIL_FROM}>"
msg['To']      = EMAIL_TO
msg['Reply-To']= EMAIL_FROM
msg.attach(MIMEText(html, 'html'))

destinatarios = [e.strip() for e in EMAIL_TO.split(',')]

with smtplib.SMTP(smtp_host, smtp_port) as server:
    server.ehlo()
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.sendmail(EMAIL_FROM, destinatarios, msg.as_string())

print(f"Correo enviado: {EMAIL_FROM} -> {EMAIL_TO}")
print(f"Asunto: {asunto}")
