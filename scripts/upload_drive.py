import os, glob
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# FOLDER_ID: carpeta real "Alertas" en Drive.
FOLDER_ID  = "1tVXOQ0WgA3rzhPkNVtGhDoYlwopg44ko"
FOLDER_URL = "https://drive.google.com/drive/folders/1tVXOQ0WgA3rzhPkNVtGhDoYlwopg44ko"

# Antes usaba una cuenta de servicio (GOOGLE_SERVICE_ACCOUNT_JSON), pero las
# cuentas de servicio no tienen cuota de almacenamiento propia y Google
# rechaza la subida con "storageQuotaExceeded" al no ser una carpeta de
# Shared Drive. En su lugar, se autentica como un usuario real
# (conkosafe.ai@gmail.com) via OAuth con refresh token, que si tiene cuota.
creds = Credentials(
    token=None,
    refresh_token=os.environ['GOOGLE_OAUTH_REFRESH_TOKEN'],
    client_id=os.environ['GOOGLE_OAUTH_CLIENT_ID'],
    client_secret=os.environ['GOOGLE_OAUTH_CLIENT_SECRET'],
    token_uri='https://oauth2.googleapis.com/token',
    scopes=['https://www.googleapis.com/auth/drive'],
)
creds.refresh(Request())  # canjea el refresh_token por un access_token nuevo

service = build('drive', 'v3', credentials=creds)

# Verificar acceso a la carpeta
try:
    meta = service.files().get(
        fileId=FOLDER_ID,
        fields='id,name',
        supportsAllDrives=True
    ).execute()
    print(f"Carpeta Drive OK: {meta['name']}")
except Exception as e:
    raise RuntimeError(
        f"Sin acceso a la carpeta Drive {FOLDER_ID}.\n"
        f"Verifica que la cuenta autorizada (conkosafe.ai@gmail.com) tenga "
        f"acceso de Editor a la carpeta, y que el refresh token no haya "
        f"sido revocado.\n{e}"
    )

# Buscar Excel
archivos = glob.glob('/tmp/alertas_digemid_*.xlsx')
if not archivos:
    raise FileNotFoundError("No se encontro el Excel en /tmp/")
ruta_excel = sorted(archivos)[-1]
nombre     = os.environ['EXCEL_NAME']
print(f"Subiendo: {nombre} ({os.path.getsize(ruta_excel)/1024:.1f} KB)")

# Upload
metadata = {'name': nombre, 'parents': [FOLDER_ID]}
media    = MediaFileUpload(
    ruta_excel,
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    resumable=True
)
archivo = service.files().create(
    body=metadata,
    media_body=media,
    fields='id,webViewLink,name',
    supportsAllDrives=True
).execute()

file_id  = archivo['id']
file_url = archivo.get('webViewLink', f'https://drive.google.com/file/d/{file_id}/view')
print(f"Subido OK: {file_url}")

with open(os.environ['GITHUB_OUTPUT'], 'a') as fh:
    fh.write(f"drive_file_url={file_url}\n")
