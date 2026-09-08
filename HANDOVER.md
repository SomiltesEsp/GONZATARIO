# Notas de Progreso y Traspaso (Handover)

## Estado Actual (Desplegado en Producción)
- **Despliegue Exitoso en Google Cloud Run:** El bot fue migrado de Polling local a modo Webhook y está corriendo 100% de manera serverless en Google Cloud Run.
- **Autenticación en la Nube:** Las credenciales de Google Service Account (`credentials.json`) ahora se inyectan dinámicamente como una variable de entorno (`GOOGLE_CREDS_JSON`) durante el despliegue para mantener la seguridad sin comprometer el código fuente en GitHub.
- **Flujo Interactivo Completado:** El bot maneja eficientemente toda la inserción (Medidas, Grosor, Color, Veta, Foto) a través de un `ConversationHandler` y `ReplyKeyboardMarkup`.
- **Integración con Sheets y Storage:** Las imágenes se suben al bucket `gonzasaas-fotos-inventario` y los datos se insertan con una URL pública en la columna "Foto Ref" en Google Sheets.

## Siguientes Pasos Pendientes (Backlog)
1. **Seguridad por Clave de Acceso (Password):** A petición del usuario, se debe implementar una capa de seguridad para que el bot no atienda a extraños. El diseño acordado será mediante una **clave de acceso (password)**. Solo los usuarios que conozcan y digiten la clave por primera vez podrán continuar hablando y usando los botones del bot.
2. **Uso Real:** El sistema arranca operaciones con datos reales el día de mañana. Monitorear el registro en Google Sheets para corroborar estabilidad.
