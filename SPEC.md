# SPEC: GONZASaaS - Bot de Inventario de Melamina

## 1. Visión General
Bot de Telegram para registrar entradas y salidas de piezas de melamina en un taller. Actúa como puente entre los operarios y una base de datos centralizada en Google Sheets, respaldando imágenes en Google Drive.

## 2. Infraestructura
* **Cloud Provider:** Google Cloud Platform (GCP)
* **Project ID:** `gonzasaas`
* **Project Number:** `1060866881162`
* **Base de Datos:** Google Sheets
* **Almacenamiento de Fotos:** Google Drive
* **Plataforma Bot:** Telegram (usando `python-telegram-bot`)

## 3. Lógica de Negocio y Flujos (Máquina de Estados)

### Flujo de Ingreso (`/nuevo`)
1. **Estado 1 (Medidas):** El bot solicita las medidas. (Validación: debe contener números y la letra 'x', ej. 50x30).
2. **Estado 2 (Color/Nombre):** El bot solicita el color o nombre descriptivo.
3. **Estado 3 (Foto):** El bot solicita una foto. 
4. **Procesamiento:** 
   - El bot sube la foto a Google Drive (obtiene enlace público).
   - El bot escribe en Google Sheets: `[ID Corto, Fecha, Medidas, Color, Link Foto, Estado: DISPONIBLE]`.
5. **Cierre:** El bot devuelve el ID Corto (Ej: `M-12`) al operario para que lo anote físicamente en la pieza.

### Flujo de Salida (`/baja <ID>`)
1. El usuario envía `/baja M-12`.
2. El bot busca la fila con el ID `M-12`.
3. Actualiza el estado a `USADO`.
4. Confirma al usuario: "Pieza M-12 descontada del inventario".

## 4. Reglas de Spec-Driven Development
* **Test-Driven:** Ningún cambio al código productivo (`src/`) se considera completo sin que los arneses de prueba (`tests/`) se ejecuten y pasen exitosamente.
* **Separación de Responsabilidades:** El código de Telegram (`bot_core.py`) no debe tener llamadas directas a APIs de Google. Todo debe pasar por los módulos `db_sheets.py` y `storage_drive.py`.
* **Manejo de Errores:** Si las APIs fallan, notificar al usuario de forma amigable.

