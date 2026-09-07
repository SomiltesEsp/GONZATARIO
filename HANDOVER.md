# Notas de Progreso y Traspaso (Handover)

## Estado Actual (Día 1)
- **Bot Base:** La lógica conversacional del bot (GONZATARIO) está terminada (`src/bot_core.py` y `src/main.py`). El bot ya es capaz de encenderse y responder comandos.
- **Base de Datos:** La conexión con Google Sheets (`src/db_sheets.py`) está codificada usando el archivo `credentials.json`.
- **Almacenamiento:** Debido a restricciones de cuota en Google Drive para Cuentas de Servicio, migramos la lógica a **Google Cloud Storage**. El código ya fue actualizado (`src/storage_drive.py`).
- **Seguridad:** Las credenciales y variables de entorno están protegidas localmente (.env, .gitignore).

## Siguientes Pasos (Para Mañana)
1. **Configurar el Bucket:** El usuario debe terminar de crear el Bucket en Google Cloud Storage asegurándose de deshabilitar la prevención de acceso público y otorgando el rol de visualizador a `allUsers`.
2. **Actualizar el .env:** Añadir el nombre del bucket al archivo `.env` (ej. `GCS_BUCKET_NAME=gonzasaas-fotos-inventario`).
3. **Prueba End-to-End:** Encender el bot y simular una entrada completa (`/nuevo`) con una foto real para verificar que el enlace del bucket se guarda correctamente en Google Sheets.
4. **Arneses (Testing):** Una vez verificado, escribir los tests automáticos (`pytest`) en la carpeta `tests/`.
