# Monitor DIGEMID - Alertas Sanitarias

Ejecuta el scraper de alertas DIGEMID **cada 3 dias a las 8:00 AM hora Lima**,
sube el Excel a Google Drive y envia un correo HTML de confirmacion.

## Flujo

```
Cada 3 dias - 8:00 AM Lima
        |
        v
[1] Scraping DIGEMID  -->  alertas_digemid_YYYYMMDD_HHMM.xlsx
        |
   _____|_____
  |           |
  v           v
[2] Drive   [3] Correo HTML
  Carpeta     De:   russbelt.aliaga@conkomerco.com
  Monitoreo   Para: july.maita@conkomerco.com
  de alertas        finanzas@conkomerco.com
        |
        v
[4] Si falla -> correo de error automatico
```

## Estructura

```
digemid-monitor/
 .gitattributes                          <- evita warning CRLF en Windows
 .github/
   workflows/
     monitor_digemid.yml                <- workflow principal
 scripts/
   scraper.py                           <- scraper DIGEMID
 utils/
   setup_drive.py                       <- verificar acceso Drive
   test_smtp.py                         <- verificar SMTP
 README.md
```

## Valores hardcodeados (no necesitan secret)

| Parametro | Valor |
|-----------|-------|
| Carpeta Drive | `1NinhrteZ0_J25nw_FrT7f_xPNPku4nXm` (Monitoreo de alertas) |
| Remitente | `russbelt.aliaga@conkomerco.com` |
| Destinatarios | `july.maita@conkomerco.com`, `finanzas@conkomerco.com` |
| Frecuencia | Cada 3 dias a las 8:00 AM Lima |

## Secrets requeridos en GitHub

Ir a: **Settings -> Secrets and variables -> Actions -> New repository secret**

| Secret | Descripcion |
|--------|-------------|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | JSON completo del Service Account de Google Cloud |
| `SMTP_HOST` | Servidor SMTP - ej: `smtp.gmail.com` |
| `SMTP_PORT` | Puerto SMTP - ej: `587` |
| `SMTP_USER` | Cuenta de correo que envia (Gmail o Outlook) |
| `SMTP_PASS` | App Password de Gmail (16 caracteres) |
| `ANTHROPIC_API_KEY` | (Recomendado) Activa analisis con Claude IA |

## Configuracion paso a paso

### 1. Google Drive - Service Account

1. Ir a console.cloud.google.com
2. Crear proyecto -> Activar Google Drive API
3. IAM & Admin -> Service Accounts -> Create
4. Generar clave JSON -> descargar
5. En Google Drive: clic derecho en la carpeta "Monitoreo de alertas"
   -> Compartir -> agregar el email del Service Account como Editor
6. Verificar localmente:
   ```
   set GOOGLE_SERVICE_ACCOUNT_JSON=<contenido del json>
   python utils/setup_drive.py
   ```

### 2. Gmail App Password

1. Cuenta Google -> Seguridad -> Verificacion en 2 pasos (activar)
2. Buscar "Contrasenas de aplicaciones" -> Crear
3. Nombre: Monitor DIGEMID -> copiar los 16 caracteres

Verificar:
```
set SMTP_HOST=smtp.gmail.com
set SMTP_PORT=587
set SMTP_USER=tu-cuenta@gmail.com
set SMTP_PASS=xxxx-xxxx-xxxx-xxxx
python utils/test_smtp.py
```

### 3. Agregar secrets en GitHub

Settings -> Secrets -> Actions -> New repository secret
(agregar los 5 o 6 secrets de la tabla de arriba)

### 4. Probar manualmente

Actions -> Monitor DIGEMID - Alertas Diarias -> Run workflow

Parametros opcionales:
- `max_paginas`: 1 (default) = ultimas 10 alertas
- `dry_run`: true = solo scrapea, no envia mail ni sube a Drive

## Que cambia con ANTHROPIC_API_KEY

| Campo Excel     | Sin API key (Heuristico) | Con API key (Claude IA) |
|-----------------|--------------------------|-------------------------|
| Urgencia        | Palabras clave fijas     | Inferida del PDF        |
| Accion Principal| 5 categorias             | Texto extraido del doc  |
| Resumen IA      | Vacio                    | Parrafo por alerta      |
| Motor Analisis  | `Heuristico`             | `Claude API`            |

## Troubleshooting

| Error | Solucion |
|-------|----------|
| 403 en scraping | Normal, el script reintenta automaticamente |
| HttpError 403 Drive | Compartir la carpeta con el Service Account como Editor |
| SMTPAuthenticationError | Regenerar App Password en Google |
| Workflow no corre a las 8am | GitHub Actions puede tener delay de hasta 15 min |
