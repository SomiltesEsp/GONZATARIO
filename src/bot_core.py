import os
import logging
import uuid
from datetime import datetime
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    filters
)
from src.db_sheets import add_piece, use_piece
from src.storage_drive import upload_photo

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Definición de Estados
CHOOSING_ACTION, MEDIDAS, GROSOR, GROSOR_CUSTOM, COLOR, VETA, FOTO, BAJA_ID = range(8)

# Teclado Principal
MAIN_MENU_KEYBOARD = [['➕ Registrar Pieza', '➖ Dar de Baja']]

# Teclado de Grosor
GROSOR_KEYBOARD = [
    ['3mm', '6mm', '10mm', '15mm'],
    ['16mm', '18mm', '19mm', '30mm'],
    ['36mm', '38mm', 'Otro...']
]

# Teclado de Veta
VETA_KEYBOARD = [['A lo largo', 'A lo ancho'], ['Sin veta']]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando de bienvenida inicial o menú."""
    await update.message.reply_text(
        "👋 ¡Hola! Soy el Bot de Inventario GONZATARIO.\n"
        "¿Qué deseas hacer?",
        reply_markup=ReplyKeyboardMarkup(
            MAIN_MENU_KEYBOARD, one_time_keyboard=False, resize_keyboard=True
        )
    )
    return CHOOSING_ACTION

async def handle_menu_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja la selección del menú principal."""
    text = update.message.text
    if text == '➕ Registrar Pieza':
        await update.message.reply_text(
            "🛠 Vamos a registrar un nuevo retazo.\n"
            "Paso 1: ¿Cuáles son las medidas en milímetros? (Ej: 500x300)",
            reply_markup=ReplyKeyboardRemove()
        )
        return MEDIDAS
    elif text == '➖ Dar de Baja':
        await update.message.reply_text(
            "🗑 Dar de baja un retazo.\n"
            "Por favor, escribe el ID de la pieza que usaste (Ej: M-A32):",
            reply_markup=ReplyKeyboardRemove()
        )
        return BAJA_ID
    else:
        # Si escribe algo raro mientras espera selección de menú, forzamos menú
        await update.message.reply_text(
            "Por favor, selecciona una opción del menú.",
            reply_markup=ReplyKeyboardMarkup(
                MAIN_MENU_KEYBOARD, one_time_keyboard=False, resize_keyboard=True
            )
        )
        return CHOOSING_ACTION

# Flujo de BAJA
async def baja_id_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pieza_id = update.message.text.strip().upper()
    try:
        exito = use_piece(pieza_id)
        if exito:
            await update.message.reply_text(f"✅ La pieza {pieza_id} ha sido marcada como USADA.")
        else:
            await update.message.reply_text(f"❌ No se encontró la pieza {pieza_id} o ya estaba usada.")
    except Exception as e:
        logger.error(f"Error al dar de baja: {e}")
        await update.message.reply_text("❌ Error de conexión con Google Sheets.")
    
    # Volver al menú
    await start(update, context)
    return CHOOSING_ACTION

# Flujo de REGISTRO
async def medidas_recibidas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda medidas y pide grosor con menú."""
    context.user_data['medidas'] = update.message.text
    await update.message.reply_text(
        "Paso 2: Selecciona el grosor de la melamina:",
        reply_markup=ReplyKeyboardMarkup(
            GROSOR_KEYBOARD, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return GROSOR

async def grosor_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda grosor y pide color o pide grosor personalizado."""
    text = update.message.text
    if text == 'Otro...':
        await update.message.reply_text(
            "Escribe el grosor que necesitas (ej. 22mm):",
            reply_markup=ReplyKeyboardRemove()
        )
        return GROSOR_CUSTOM
    else:
        context.user_data['grosor'] = text
        await update.message.reply_text(
            "Paso 3: ¿Qué color o diseño tiene? (Ej: Blanco, Rovere, etc.)",
            reply_markup=ReplyKeyboardRemove()
        )
        return COLOR

async def grosor_custom_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['grosor'] = update.message.text
    await update.message.reply_text(
        "Paso 3: ¿Qué color o diseño tiene? (Ej: Blanco, Rovere, etc.)",
    )
    return COLOR

async def color_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda el color y pide la dirección de la veta."""
    context.user_data['color'] = update.message.text
    
    await update.message.reply_text(
        "Paso 4: ¿Hacia qué lado va la veta del diseño?",
        reply_markup=ReplyKeyboardMarkup(
            VETA_KEYBOARD, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return VETA

async def veta_recibida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Guarda la veta y pide la foto."""
    context.user_data['veta'] = update.message.text
    
    await update.message.reply_text(
        "Paso 5: ¡Casi listo! 📸 Envíame una foto clara del retazo para identificarlo mejor.",
        reply_markup=ReplyKeyboardRemove()
    )
    return FOTO

async def foto_recibida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Recibe la foto, la sube a Drive/GCS y guarda en Sheets."""
    photo_file = await update.message.photo[-1].get_file()
    
    file_name = f"foto_{update.message.message_id}.jpg"
    await photo_file.download_to_drive(file_name)
    
    await update.message.reply_text("⏳ Procesando y subiendo la imagen a la nube...")
    
    try:
        url_foto = upload_photo(file_name, f"retazos/{uuid.uuid4().hex[:8]}.jpg")
        
        if os.path.exists(file_name):
            os.remove(file_name)
            
        medidas = context.user_data['medidas']
        grosor = context.user_data['grosor']
        color = context.user_data['color']
        veta = context.user_data['veta']
        
        nuevo_id = add_piece(medidas, color, grosor, veta, url_foto)
        
        await update.message.reply_text(
            f"✅ ¡Pieza registrada exitosamente!\n\n"
            f"🆔 ID: {nuevo_id}\n"
            f"📏 Medidas: {medidas}\n"
            f"📏 Grosor: {grosor}\n"
            f"🎨 Color: {color}\n"
            f"🪵 Veta: {veta}\n\n"
            f"⚠️ Escribe este ID ({nuevo_id}) en la pieza física."
        )
    except Exception as e:
        logger.error(f"Error procesando la pieza: {e}")
        await update.message.reply_text("❌ Ocurrió un error al guardar. Verifica los permisos de Google.")
        if os.path.exists(file_name):
            os.remove(file_name)

    context.user_data.clear()
    await start(update, context) # Volvemos a mandar el menú al terminar
    return CHOOSING_ACTION

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación actual."""
    await update.message.reply_text("❌ Operación cancelada.")
    await start(update, context) # Volvemos a mandar el menú
    return CHOOSING_ACTION

def get_conversation_handler():
    """Genera la máquina de estados principal."""
    # start se activará con comandos /start, o con mensajes como "hola", "go", "menu"
    return ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex(r'(?i)^(hola|go|menu|menú)$'), start)
        ],
        states={
            CHOOSING_ACTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_choice)
            ],
            BAJA_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, baja_id_recibido)
            ],
            MEDIDAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, medidas_recibidas)],
            GROSOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, grosor_recibido)],
            GROSOR_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, grosor_custom_recibido)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, color_recibido)],
            VETA: [MessageHandler(filters.TEXT & ~filters.COMMAND, veta_recibida)],
            FOTO: [MessageHandler(filters.PHOTO, foto_recibida)]
        },
        fallbacks=[
            CommandHandler('cancelar', cancelar),
            CommandHandler('start', start),
            MessageHandler(filters.Regex(r'(?i)^(hola|go|menu|menú)$'), start)
        ]
    )

async def mensaje_desconocido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Responde a cualquier texto que no encaje."""
    await update.message.reply_text(
        "🤖 No entiendo ese mensaje.\n"
        "Escribe 'Hola' o 'GO' para ver el menú de opciones."
    )
