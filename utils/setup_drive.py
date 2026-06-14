"""
setup_drive.py - Verificar acceso a la carpeta Google Drive antes de activar el workflow.

Uso:
    set GOOGLE_SERVICE_ACCOUNT_JSON={ ... json completo ... }
    python utils/setup_drive.py
"""
import os, json, sys

def verificar():
    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError:
        print("Instala: pip install google-api-python-client google-auth")
        sys.exit(1)

    raw = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if not raw:
        print("ERROR: Variable GOOGLE_SERVICE_ACCOUNT_JSON no definida")
        sys.exit(1)

    creds = service_account.Credentials.from_service_account_info(
        json.loads(raw),
        scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=creds)

    FOLDER_ID = "1NinhrteZ0_J25nw_FrT7f_xPNPku4nXm"
    try:
        meta = service.files().get(
            fileId=FOLDER_ID,
            fields='name,id',
            supportsAllDrives=True
        ).execute()
        print(f"OK - Carpeta encontrada: '{meta['name']}' (ID: {meta['id']})")
        print("Configuracion Drive lista para GitHub Actions.")
    except Exception as e:
        print(f"ERROR - No se pudo acceder a la carpeta: {e}")
        print("Comparte la carpeta con el Service Account como Editor.")
        sys.exit(1)

if __name__ == "__main__":
    verificar()
