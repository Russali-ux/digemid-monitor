"""
send_email.py — Correo "CONKOMERCO Alertas".

El contenido YA NO sale del Excel del scraper: se lee de Supabase
(base consolidada de Alertas-analyzer):
  • últimas N_ALERTAS (10) de alertas_digemid
  • últimas N_MODIFICATORIAS (4) de modificatorias_digemid
con los mismos campos de las vistas web, y se adjunta un Excel con ambas hojas.

Remitente: conkosafe.ai@gmail.com
Destinatarios: ocultos (BCC vía envelope SMTP, sin header Bcc en el mensaje)
DRY_RUN=true → no envía; guarda /tmp/preview_email.html y el Excel para revisión.
"""
import os
import smtplib
import sys
from datetime import datetime, timedelta, timezone
from email import encoders
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from email_html import construir_html            # noqa: E402
from excel_resumen import construir_excel        # noqa: E402
from supabase_data import ultimas_alertas, ultimas_modificatorias  # noqa: E402

DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"
N_ALERTAS = int(os.environ.get("N_ALERTAS", "10"))
N_MODIF = int(os.environ.get("N_MODIFICATORIAS", "4"))
EMAIL_FROM = os.environ.get("EMAIL_FROM", "conkosafe.ai@gmail.com")
LOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "logo_conkosafe.png")
ESTADO_SCRAPER = os.environ.get("ESTADO_SCRAPER", "")

ahora = datetime.now(timezone(timedelta(hours=-5)))   # hora Lima
fecha_txt = ahora.strftime("%d/%m/%Y %H:%M")

# 1. Datos desde Supabase
alertas = ultimas_alertas(N_ALERTAS)
modificatorias = ultimas_modificatorias(N_MODIF, hoy=ahora.date())
if not alertas and not modificatorias:
    raise RuntimeError("Supabase no devolvió alertas ni modificatorias; no se envía un correo vacío.")
print(f"Supabase: {len(alertas)} alertas | {len(modificatorias)} modificatorias")

# 2. Excel adjunto + HTML
excel_name = f"conkosafe_alertas_modificatorias_{ahora.strftime('%Y%m%d')}.xlsx"
ruta_excel = construir_excel(alertas, modificatorias, f"/tmp/{excel_name}", fecha_txt)
html = construir_html(alertas, modificatorias, fecha_txt, excel_name, ESTADO_SCRAPER)

asunto = f"CONKOMERCO Alertas ({ahora.strftime('%d/%m/%Y')})"

if DRY_RUN:
    import base64
    with open(LOGO, "rb") as fh:
        logo_b64 = "data:image/png;base64," + base64.b64encode(fh.read()).decode()
    with open("/tmp/preview_email.html", "w", encoding="utf-8") as fh:
        fh.write(construir_html(alertas, modificatorias, fecha_txt, excel_name, ESTADO_SCRAPER, logo_src=logo_b64))
    print(f"[DRY RUN] No se envió. Vista previa: /tmp/preview_email.html | Excel: {ruta_excel}")
    print(f"Asunto: {asunto}")
    sys.exit(0)

# 3. Envío
smtp_host = os.environ["SMTP_HOST"]
smtp_port = int(os.environ.get("SMTP_PORT", "587"))
smtp_user = os.environ["SMTP_USER"]
smtp_pass = os.environ["SMTP_PASS"]
destinatarios = [x.strip() for x in os.environ["EMAIL_TO"].split(",") if x.strip()]

msg = MIMEMultipart("mixed")
msg["Subject"] = asunto
msg["From"] = f"Monitor DIGEMID CONKOMERCO <{EMAIL_FROM}>"
msg["To"] = EMAIL_FROM          # solo el remitente visible en "Para"
msg["Reply-To"] = EMAIL_FROM
# Cuerpo HTML + logo incrustado (CID): se ve aunque el cliente bloquee imágenes externas
cuerpo = MIMEMultipart("related")
cuerpo.attach(MIMEText(html, "html", "utf-8"))
with open(LOGO, "rb") as fh:
    logo = MIMEImage(fh.read(), _subtype="png")
logo.add_header("Content-ID", "<logo_conkosafe>")
logo.add_header("Content-Disposition", "inline", filename="logo_conkosafe.png")
cuerpo.attach(logo)
msg.attach(cuerpo)

with open(ruta_excel, "rb") as f:
    adj = MIMEBase("application", "vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    adj.set_payload(f.read())
encoders.encode_base64(adj)
adj.add_header("Content-Disposition", f'attachment; filename="{excel_name}"')
msg.attach(adj)

with smtplib.SMTP(smtp_host, smtp_port) as server:
    server.ehlo()
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.sendmail(EMAIL_FROM, destinatarios, msg.as_string())

print(f"Correo enviado: {EMAIL_FROM} -> {len(destinatarios)} destinatarios (ocultos)")
print(f"Asunto: {asunto}")
