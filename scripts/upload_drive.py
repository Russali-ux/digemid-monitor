import os, json, glob
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2 import service_account

FOLDER_ID  = "1LOygkKnbednAw-eCPLM0-9TXLGj16hw4"
FOLDER_URL = "https://drive.google.com/drive/folders/1LOygkKnbednAw-eCPLM0-9TXLGj16hw4"

creds_info = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT_JSON'])
creds = service_account.Credentials.from_service_account_info(
    creds_info,
    scopes=['https://www.googleapis.com/auth/drive']
)
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
        f"Comparte la carpeta con: digemid-monitor@radiant-octane-424016-p0.iam.gserviceaccount.com como Editor.\n{e}"
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
