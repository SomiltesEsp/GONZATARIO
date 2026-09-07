import os
import logging
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from src.db_sheets import add_piece, use_piece
from src.storage_drive import upload_photo

# Configuración de logging (Para ver errores si algo falla)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados de la conversación paso a paso
MEDIDAS, COLOR, FOTO = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando de bienvenida inicial."""
    mensaje = (
        "👋 ¡Hola! Soy el Bot de Inventario GONZATARIO.\n\n"
        "Comandos disponibles:\n"
        "🟢 /nuevo - Registrar un retazo de melamina.\n"
        "🔴 /baja <ID> - Descontar un retazo (Ej: /baja M-A32)."
    )
    await update.message.reply_text(mensaje)

async def nuevo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Inicia el flujo de registro de pieza (Estado 1)."""
    await update.message.reply_text(
        "📝 Vamos a registrar un nuevo retazo.\n"
        "Paso 1: ¿Cuáles son las medidas en milímetros? (Ej: 500x300)"
    )
    return MEDIDAS

async def medidas_recibidas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda las medidas y pide el color (Estado 2)."""
    context.user_data['medidas'] = update.message.text
    await update.message.reply_text(
        f"✅ Medidas guardadas: {context.user_data['medidas']}\n"
        "Paso 2: ¿Qué color o nombre de melamina es? (Ej: Blanco)"
    )
    return COLOR

async def color_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda el color y pide la foto (Estado 3)."""
    context.user_data['color'] = update.message.text
    await update.message.reply_text(
        f"✅ Color guardado: {context.user_data['color']}\n"
        "Paso 3: Por favor, toma o envía una FOTO del retazo."
    )
    return FOTO

async def foto_recibida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la foto, orquesta la subida a Drive y el guardado en Sheets."""
    await update.message.reply_text("⏳ Procesando foto y guardando en la base de datos de Google...")
    
    try:
        # Extraer la foto con mayor resolución (la última del array)
        photo_file = await update.message.photo[-1].get_file()
        file_name = f"foto_{update.message.message_id}.jpg"
        
        # En Windows descargamos en la carpeta actual temporalmente
        file_path = f"{file_name}"
        await photo_file.download_to_drive(file_path)
        
        # 1. Subir a Google Drive
        foto_url = upload_photo(file_path, file_name)
        
        # Borrar el archivo local porque ya está en Drive
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # 2. Guardar en Google Sheets
        medidas = context.user_data['medidas']
        color = context.user_data['color']
        piece_id = add_piece(medidas, color, foto_url)
        
        await update.message.reply_text(
            f"🎉 ¡Pieza registrada con éxito!\n\n"
            f"⚠️ **IMPORTANTE:**\n"
            f"Escribe este código en el canto de la pieza con un marcador:\n"
            f"👉 {piece_id} 👈"
        )
        
    except Exception as e:
        logger.error(f"Error procesando la pieza: {e}")
        await update.message.reply_text(
            "❌ Ocurrió un error al guardar la pieza. ¿Le diste permiso al bot en la hoja de Sheets?"
        )
    
    # Limpiar memoria de la conversación actual
    context.user_data.clear()
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando oculto para cancelar el registro a medias."""
    await update.message.reply_text("Registro cancelado.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

async def baja_pieza(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Busca el ID proporcionado y lo marca como USADO en Google Sheets."""
    if not context.args:
        await update.message.reply_text("⚠️ Uso correcto: /baja <ID>\nEjemplo: /baja M-A32")
        return
    
    piece_id = context.args[0]
    await update.message.reply_text(f"⏳ Buscando la pieza {piece_id} en el inventario...")
    
    try:
        exito = use_piece(piece_id)
        if exito:
            await update.message.reply_text(f"✅ La pieza {piece_id} ha sido marcada como USADA.")
        else:
            await update.message.reply_text(f"❌ No se encontró la pieza {piece_id} en el inventario.")
    except Exception as e:
        logger.error(f"Error al dar de baja: {e}")
        await update.message.reply_text("❌ Ocurrió un error al intentar actualizar la base de datos.")

def get_conversation_handler():
    """Genera la máquina de estados para el comando /nuevo"""
    return ConversationHandler(
        entry_points=[CommandHandler('nuevo', nuevo_start)],
        states={
            MEDIDAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, medidas_recibidas)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, color_recibido)],
            FOTO: [MessageHandler(filters.PHOTO, foto_recibida)]
        },
        fallbacks=[CommandHandler('cancelar', cancelar)]
    )

async def mensaje_desconocido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde a cualquier texto que no sea un comando."""
    await update.message.reply_text(
        "🤔 No entiendo ese mensaje.\n\n"
        "Solo respondo a comandos específicos.\n"
        "👉 Escribe /start para ver el menú de opciones."
    )


