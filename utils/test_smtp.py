"""
test_smtp.py - Verificar configuracion SMTP antes de activar el workflow.

Uso en Windows (PowerShell):
    $env:SMTP_HOST="smtp.gmail.com"
    $env:SMTP_PORT="587"
    $env:SMTP_USER="tu-cuenta@gmail.com"
    $env:SMTP_PASS="xxxx-xxxx-xxxx-xxxx"
    python utils/test_smtp.py
"""
import os, smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

EMAIL_FROM = "russbelt.aliaga@conkomerco.com"
EMAIL_TO   = "july.maita@conkomerco.com,finanzas@conkomerco.com"

def test():
    host = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
    port = int(os.environ.get('SMTP_PORT', '587'))
    user = os.environ['SMTP_USER']
    pwd  = os.environ['SMTP_PASS']

    html = """
    <div style="font-family:Arial;padding:20px;background:#EBF3FB;border-left:4px solid #1F4E79;">
        <h2 style="color:#1F4E79;">Test SMTP - Monitor DIGEMID CONKOMERCO</h2>
        <p>Si recibes este correo, la configuracion SMTP es correcta.</p>
        <p style="font-size:12px;color:#888;">
            De: russbelt.aliaga@conkomerco.com<br>
            Para: july.maita@conkomerco.com, finanzas@conkomerco.com
        </p>
    </div>"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Test SMTP - Monitor DIGEMID (verificacion)"
    msg['From']    = f"Monitor DIGEMID CONKOMERCO <{EMAIL_FROM}>"
    msg['To']      = EMAIL_TO
    msg.attach(MIMEText(html, 'html'))

    destinatarios = [e.strip() for e in EMAIL_TO.split(',')]

    print(f"Conectando a {host}:{port}...")
    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(EMAIL_FROM, destinatarios, msg.as_string())

    print(f"OK - Correo de prueba enviado a: {EMAIL_TO}")

if __name__ == "__main__":
    test()
