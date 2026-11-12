"""
send_email.py — Correo "CONKOMERCO Alertas".

El contenido YA NO sale del Excel del scraper: se lee de Supabase
(base consolidada de Alertas-analyzer):
  • últimas N_ALERTAS (10) de alertas_digemid
  • últimas N_MODIFICATORIAS (4) de modificatorias_digemid
con los mismos campos de las vistas web, y se adjunta un Excel con ambas hojas.

Remitente: conkosafe.ai@gmail.com
Destinatarios: ocultos (BCC vía envelope SMTP, sin header Bcc en el mensaje)
DRY_RUN=true → NO envía a la lista: deja el correo en Borradores de Gmail (cuenta SMTP_USER,
               vía IMAP) y guarda /tmp/preview_email.html + Excel como artifact.
"""
import imaplib
import os
import re
import smtplib
import time
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

# 3. Mensaje (idéntico para envío real y para borrador)
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



def carpeta_borradores(imap):
    """Carpeta con atributo \\Drafts (en Gmail en español es '[Gmail]/Borradores')."""
    typ, carpetas = imap.list()
    for f in (carpetas or []) if typ == "OK" else []:
        linea = f.decode(errors="ignore") if isinstance(f, bytes) else f
        if "\\Drafts" in linea:
            m = re.search(r'"([^"]+)"\s*$', linea) or re.search(r"(\S+)\s*$", linea)
            if m:
                return '"' + m.group(1).strip('"') + '"'
    return '"[Gmail]/Drafts"'


if DRY_RUN:
    # Vista previa local (logo embebido en base64) para el artifact
    import base64
    with open(LOGO, "rb") as fh:
        logo_b64 = "data:image/png;base64," + base64.b64encode(fh.read()).decode()
    with open("/tmp/preview_email.html", "w", encoding="utf-8") as fh:
        fh.write(construir_html(alertas, modificatorias, fecha_txt, excel_name, ESTADO_SCRAPER, logo_src=logo_b64))
    print(f"[DRY RUN] Vista previa: /tmp/preview_email.html | Excel: {ruta_excel}")

    msg.replace_header("Subject", f"[PRUEBA] {asunto}")
    imap_user = os.environ.get("IMAP_USER") or os.environ.get("SMTP_USER", "")
    imap_pass = os.environ.get("IMAP_PASS") or os.environ.get("SMTP_PASS", "")
    if not (imap_user and imap_pass):
        print("[DRY RUN] Sin credenciales: no se creó borrador en Gmail (solo artifact).")
        sys.exit(0)
    imap_host = os.environ.get("IMAP_HOST") or "imap.gmail.com"
    try:
        with imaplib.IMAP4_SSL(imap_host, 993) as imap:
            imap.login(imap_user, imap_pass)
            carpeta = carpeta_borradores(imap)
            typ, _ = imap.append(carpeta, "\\Draft", imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        if typ != "OK":
            raise RuntimeError(f"respuesta IMAP {typ}")
        print(f"[DRY RUN] No se envió a la lista. Borrador guardado en {carpeta} de {imap_user}")
    except Exception as exc:
        # El dry run no falla por esto: la vista previa queda igual en el artifact preview-correo
        print(f"::warning::No se pudo crear el borrador en Gmail ({imap_user} @ {imap_host}): {exc}. "
              "Configure los secrets IMAP_USER (cuenta Gmail) e IMAP_PASS (contraseña de aplicación) "
              "y verifique que IMAP esté habilitado en Gmail. La vista previa está en el artifact preview-correo.")
    print(f"Asunto: [PRUEBA] {asunto}")
    sys.exit(0)

# 4. Envío real a la lista (BCC)
smtp_host = os.environ["SMTP_HOST"]
smtp_port = int(os.environ.get("SMTP_PORT", "587"))
smtp_user = os.environ["SMTP_USER"]
smtp_pass = os.environ["SMTP_PASS"]
destinatarios = [x.strip() for x in os.environ["EMAIL_TO"].split(",") if x.strip()]

with smtplib.SMTP(smtp_host, smtp_port) as server:
    server.ehlo()
    server.starttls()
    server.login(smtp_user, smtp_pass)
    server.sendmail(EMAIL_FROM, destinatarios, msg.as_string())

print(f"Correo enviado: {EMAIL_FROM} -> {len(destinatarios)} destinatarios (ocultos)")
print(f"Asunto: {asunto}")
