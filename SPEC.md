# SPEC: GONZASaaS - Bot de Inventario de Melamina

## 1. Visión General
Bot de Telegram para registrar entradas y salidas de piezas de melamina en un taller. Actúa como puente entre los operarios y una base de datos centralizada en Google Sheets, respaldando imágenes en Google Drive.

## 2. Infraestructura
* **Cloud Provider:** Google Cloud Platform (GCP)
* **Project ID:** `gonzasaas`
* **Project Number:** `1060866881162`
* **Servidor de Aplicación:** Google Cloud Run (Modo Webhook con Tornado)
* **Base de Datos:** Google Sheets
* **Almacenamiento de Fotos:** Google Cloud Storage (Bucket: `gonzasaas-fotos-inventario`)
* **Plataforma Bot:** Telegram (usando `python-telegram-bot`)

## 3. Lógica de Negocio y Flujos (Máquina de Estados)

### Flujo de Ingreso (Botones Interactivos)
1. **Inicio (`Hola`, `GO` o `/start`):** El bot muestra un menú con botones interactivos `➕ Registrar Pieza` y `➖ Dar de Baja`.
2. **Estado 1 (Medidas):** Si elige "Registrar", pide medidas (Ej. 50x30).
3. **Estado 2 (Grosor):** Muestra teclado interactivo con medidas estándar (`3mm`, `6mm`, `10mm`, etc.) y la opción `Otro...`.
4. **Estado 3 (Color/Nombre):** Solicita el color o diseño.
5. **Estado 4 (Veta):** Solicita la dirección de la veta mediante botones (`A lo largo`, `A lo ancho`, `Sin veta`).
6. **Estado 5 (Foto):** El bot solicita una foto de la pieza.
7. **Procesamiento:** 
   - Sube la foto a Google Cloud Storage (obtiene URL pública directa).
   - Genera ID corto excluyendo letras confusas (I, O, 1, 0).
   - Escribe en Google Sheets: `[ID Corto, Color, Grosor, Medidas, Veta, URL Foto, Estado: DISPONIBLE, Fecha]`.
8. **Cierre:** El bot devuelve el ID Corto (Ej: `M-A32`) al operario para que lo anote físicamente en la pieza, y vuelve al menú.

### Flujo de Salida (Dar de Baja)
1. El usuario selecciona `➖ Dar de Baja` desde el menú principal.
2. El bot pregunta por el ID corto de la pieza.
3. El usuario envía el ID (Ej: `M-A32`).
4. El bot busca la fila con el ID y actualiza el estado en la columna 7 (G) a `USADO`.
5. Confirma al usuario el éxito o fracaso, y vuelve al menú principal.

## 4. Reglas de Spec-Driven Development
* **Test-Driven:** Ningún cambio al código productivo (`src/`) se considera completo sin que los arneses de prueba (`tests/`) se ejecuten y pasen exitosamente.
* **Separación de Responsabilidades:** El código de Telegram (`bot_core.py`) no debe tener llamadas directas a APIs de Google. Todo debe pasar por los módulos `db_sheets.py` y `storage_drive.py`.
* **Manejo de Errores:** Si las APIs fallan, notificar al usuario de forma amigable.

