import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_FROM = "conkosafe.ai@gmail.com"
EMAIL_TO   = "finanzas@conkomerco.com,conkosafe.ai@gmail.com"
run_url    = os.environ.get('RUN_URL', '#')

html = (
    '<div style="font-family:Arial;padding:24px;background:#FFF5F5;'
    'border-left:5px solid #C00000;border-radius:4px;">'
    '<h2 style="color:#C00000;margin-top:0;">Monitor DIGEMID - Error en ejecucion</h2>'
    '<p>El workflow automatico de alertas DIGEMID fallo.</p>'
    f'<p><a href="{run_url}" style="background:#C00000;color:#fff;padding:10px 20px;'
    'border-radius:6px;text-decoration:none;font-weight:bold;">Ver log en GitHub Actions</a></p>'
    '<hr style="border:none;border-top:1px solid #FCCBCB;margin:16px 0;">'
    '<p style="font-size:11px;color:#999;">Monitor DIGEMID - CONKOMERCO S.A.C.</p>'
    '</div>'
)

msg = MIMEMultipart('alternative')
msg['Subject'] = "[ERROR] Monitor DIGEMID - Fallo en ejecucion automatica"
msg['From']    = f"Monitor DIGEMID CONKOMERCO <{EMAIL_FROM}>"
msg['To']      = EMAIL_TO
msg.attach(MIMEText(html, 'html'))

destinatarios = [e.strip() for e in EMAIL_TO.split(',')]

with smtplib.SMTP(os.environ['SMTP_HOST'], int(os.environ.get('SMTP_PORT', 587))) as s:
    s.ehlo()
    s.starttls()
    s.login(os.environ['SMTP_USER'], os.environ['SMTP_PASS'])
    s.sendmail(EMAIL_FROM, destinatarios, msg.as_string())

print("Alerta de fallo enviada")
