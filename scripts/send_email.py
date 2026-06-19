import os, glob, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

EMAIL_FROM = os.environ.get('EMAIL_FROM', 'conkosafe.ai@gmail.com')
EMAIL_TO   = os.environ['EMAIL_TO']

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

html = (
    '<!DOCTYPE html><html lang="es"><head>'
    '<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
    '</head><body style="margin:0;padding:0;background:#F0F2F5;font-family:Arial,sans-serif;">'
    '<table width="100%" cellpadding="0" cellspacing="0" style="background:#F0F2F5;padding:28px 0;">'
    '<tr><td align="center">'
    '<table width="620" cellpadding="0" cellspacing="0" style="background:#fff;border-radius:12px;'
    'overflow:hidden;box-shadow:0 3px 16px rgba(0,0,0,.12);">'
    '<tr><td style="background:linear-gradient(135deg,#1F4E79 0%,#2E75B6 100%);padding:26px 32px;">'
    '<table width="100%" cellpadding="0" cellspacing="0"><tr><td>'
    '<p style="margin:0;color:#BDD7EE;font-size:11px;text-transform:uppercase;letter-spacing:1px;">'
    'CONKOSAFE IA - PV INTELligence</p>'
    '<h1 style="margin:6px 0 0;color:#fff;font-size:20px;font-weight:bold;">'
    'Alertas Sanitarias DIGEMID</h1>'
    f'<p style="margin:5px 0 0;color:#BDD7EE;font-size:13px;">Reporte del {fecha} - hora Lima</p>'
    f'</td><td align="right" valign="middle"><span style="background:rgba(255,255,255,.15);'
    f'color:#fff;font-size:11px;padding:5px 10px;border-radius:20px;">{motor_txt}</span></td>'
    '</tr></table></td></tr>'
    f'<tr><td style="padding:20px 32px 0;"><div style="background:{badge_color};color:#fff;'
    f'padding:12px 20px;border-radius:8px;font-weight:bold;font-size:14px;text-align:center;">'
    f'{badge_texto}</div></td></tr>'
    '<tr><td style="padding:18px 32px;"><table width="100%" cellspacing="10" cellpadding="0"><tr>'
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
    '<tr><td style="padding:8px 32px 22px;">'
    '<div style="background:#EBF3FB;border-left:4px solid #2E75B6;padding:14px 18px;'
    'border-radius:0 8px 8px 0;">'
    '<p style="margin:0 0 4px;font-size:13px;color:#1F4E79;font-weight:bold;">'
    'Excel adjunto a este correo</p>'
    f'<p style="margin:0;font-size:12px;color:#555;">{excel_name}</p></div></td></tr>'
    '<tr><td style="padding:0 32px 22px;">'
    '<div style="background:#EBF3FB;border-left:4px solid #2E75B6;padding:14px 18px;'
    'border-radius:0 8px 8px 0;">'
    '<p style="margin:0 0 8px;font-size:13px;color:#1F4E79;font-weight:bold;">Pasos de revision</p>'
    '<ol style="margin:0;padding-left:18px;font-size:13px;color:#333;line-height:1.9;">'
    '<li>Abrir el Excel adjunto y filtrar columna <strong>Urgencia = INMEDIATA</strong> primero</li>'
    '<li>Revisar <strong>Accion Principal</strong> y columna <strong>Dirigido a</strong></li>'
    '<li>Comunicar internamente a Dirección Técnica/Asuntos <strong>Regulatorios/Área médica/Calidad si corresponde</li>'
    '<li>Registrar en sistema de farmacovigilancia si aplica</li>'
    '</ol></div></td></tr>'
    '<tr><td style="background:#F4F6F9;padding:14px 32px;border-top:1px solid #E5E8ED;">'
    '<table width="100%" cellpadding="0" cellspacing="0"><tr>'
    '<td style="font-size:11px;color:#999;">Enviado automaticamente por agente ConkosafeIA</td>'
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

# Buscar Excel
archivos = glob.glob('/tmp/alertas_digemid_*.xlsx')
if not archivos:
    raise FileNotFoundError("No se encontro el Excel en /tmp/")
ruta_excel = sorted(archivos)[-1]

msg = MIMEMultipart('mixed')
msg['Subject'] = asunto
msg['From']    = f"Alertas Sanitarias - PV Intelligence <{EMAIL_FROM}>"
msg['To']       = EMAIL_FROM
msg['Bcc']      = EMAIL_TO
msg['Reply-To']= EMAIL_FROM
msg.attach(MIMEText(html, 'html'))

# Adjunto Excel
with open(ruta_excel, 'rb') as f:
    adjunto = MIMEBase('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    adjunto.set_payload(f.read())
encoders.encode_base64(adjunto)
adjunto.add_header('Content-Disposition', f'attachment; filename="{excel_name}"')
msg.attach(adjunto)

destinatarios = [e.strip() for e in EMAIL_TO.split(',')]

with smtplib.SMTP(smtp_host, smtp_port) as server:
    server.ehlo()
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.sendmail(EMAIL_FROM, destinatarios, msg.as_string())

print(f"Correo con adjunto enviado: {EMAIL_FROM} -> {EMAIL_TO}")
print(f"Asunto: {asunto}")
