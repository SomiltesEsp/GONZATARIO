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
MEDIDAS, GROSOR, COLOR, FOTO = range(4)

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
    """Guarda medidas y pide grosor."""
    context.user_data['medidas'] = update.message.text
    await update.message.reply_text(
        "Paso 2: ¿Cuál es el grosor de la melamina? (Ej: 15mm o 18mm)"
    )
    return GROSOR

async def grosor_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda grosor y pide color."""
    context.user_data['grosor'] = update.message.text
    await update.message.reply_text(
        "Paso 3: ¿Qué color o diseño tiene? (Ej: Blanco, Rovere, etc.)"
    )
    return COLOR

async def color_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda el color y pide la foto (Estado 4)."""
    context.user_data['color'] = update.message.text
    await update.message.reply_text(
        "Paso 4: Por favor, envíame una foto de referencia de la pieza."
    )
    return FOTO

async def foto_recibida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la foto, la sube a Drive/GCS y guarda en Sheets."""
    photo_file = await update.message.photo[-1].get_file()
    
    # Nombre temporal del archivo
    file_name = f"foto_{update.message.message_id}.jpg"
    await photo_file.download_to_drive(file_name)
    
    await update.message.reply_text("⏳ Procesando y subiendo la imagen a la nube...")
    
    try:
        # Aquí subimos a Cloud Storage
        url_foto = upload_photo(file_name, file_name)
        
        # Eliminar archivo local para no ocupar espacio
        if os.path.exists(file_name):
            os.remove(file_name)
            
        # Combinar el nombre con el grosor para guardar en la hoja
        medidas = context.user_data['medidas']
        grosor = context.user_data['grosor']
        color = context.user_data['color']
        
        # Como db_sheets espera (medidas, color, url_foto), uniremos color y grosor.
        color_con_grosor = f"{color} ({grosor})"
        
        nuevo_id = add_piece(medidas, color_con_grosor, url_foto)
        
        await update.message.reply_text(
            f"✅ ¡Pieza registrada exitosamente!\n\n"
            f"🆔 ID: {nuevo_id}\n"
            f"📏 Medidas: {medidas}\n"
            f"🛠 Grosor: {grosor}\n"
            f"🎨 Color: {color}\n\n"
            f"Escribe este ID ({nuevo_id}) en la pieza física."
        )
    except Exception as e:
        logger.error(f"Error procesando la pieza: {e}")
        await update.message.reply_text("❌ Ocurrió un error al guardar. Verifica los permisos de Google.")
        if os.path.exists(file_name):
            os.remove(file_name)

    context.user_data.clear()
    return ConversationHandler.END

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación actual."""
    await update.message.reply_text("🚫 Registro cancelado.", reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END

async def baja_pieza(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando para descontar una pieza."""
    if not context.args:
        await update.message.reply_text("⚠️ Debes proporcionar el ID. Uso: /baja <ID>")
        return
        
    pieza_id = context.args[0].upper()
    try:
        exito = use_piece(pieza_id)
        if exito:
            await update.message.reply_text(f"✅ La pieza {pieza_id} ha sido marcada como USADA.")
        else:
            await update.message.reply_text(f"❌ No se encontró la pieza {pieza_id} o ya estaba usada.")
    except Exception as e:
        logger.error(f"Error al dar de baja: {e}")
        await update.message.reply_text("❌ Error de conexión con Google Sheets.")

def get_conversation_handler():
    """Genera la máquina de estados para el comando /nuevo"""
    return ConversationHandler(
        entry_points=[CommandHandler('nuevo', nuevo_start)],
        states={
            MEDIDAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, medidas_recibidas)],
            GROSOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, grosor_recibido)],
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


