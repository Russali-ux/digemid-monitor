# Monitor DIGEMID - Alertas Sanitarias

Ejecuta el scraper de alertas DIGEMID **cada 3 dias a las 8:00 AM hora Lima**,
sube el Excel a Google Drive y envia un correo HTML de confirmacion.

## Flujo

```
Cada 3 dias - 8:00 AM Lima
        |
        v
[1] Scraping DIGEMID  -->  alertas_digemid_YYYYMMDD_HHMM.xlsx  --> [2] Google Drive
        |
        v   (corre aunque el scraping falle)
[3] Correo HTML  <-- Supabase (base de Alertas-analyzer)
      - ultimas 10 alertas      (tabla alertas_digemid)
      - ultimas 4 modificatorias (tabla modificatorias_digemid)
      - Excel adjunto conkosafe_alertas_modificatorias_YYYYMMDD.xlsx
        (hojas "Alertas" y "Modificatorias", mismos campos que la web)
        |
        v
[4] Si algo falla -> correo de error automatico
```

Campos del correo (iguales a las vistas de Alertas-analyzer):

| Alertas | Modificatorias |
|---------|----------------|
| N° alerta, fecha, producto, titular impactado, N° lote, tipo, urgencia, accion principal, resumen IA, link DIGEMID, PDF | N° modificacion, fecha, producto, principio activo, titular RS, tipo, urgencia, accion requerida, fecha limite 15 d.h. (sin feriados Peru), indicador de tiempos, base legal, resumen, link publicacion, PDF |

## Estructura

```
digemid-monitor/
 .github/workflows/monitor_digemid.yml  <- workflow principal
 scripts/
   scraper.py / run_scraper.py          <- scraper DIGEMID (Excel -> Drive)
   upload_drive.py                      <- subida a Google Drive
   supabase_data.py                     <- lee ultimas alertas/modificatorias de Supabase
   email_html.py                        <- plantilla HTML del correo
   excel_resumen.py                     <- Excel adjunto (2 hojas)
   send_email.py                        <- arma y envia el correo (o vista previa en dry run)
   notify_failure.py                    <- correo de error
 utils/                                 <- pruebas de Drive y SMTP
```

Probar el correo localmente sin enviar:
```
DRY_RUN=true python3 scripts/send_email.py   # genera /tmp/preview_email.html
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
| `SUPABASE_ANON_KEY` | (Opcional) anon key de Alertas-analyzer; si no existe se usa la publica de la web |

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
- `dry_run`: true = no envia el correo; deja `preview-correo` (HTML + Excel) como artifact
- `n_alertas` / `n_modificatorias`: cantidad en el correo (default 10 / 4)

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
