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
from src.db_sheets import add_piece, add_canto, use_piece
from src.storage_drive import upload_photo

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Definición de Estados
(
    CHOOSING_MATERIAL, 
    CHOOSING_ACTION,
    
    # Estados Melamina
    MEDIDAS, 
    GROSOR, 
    GROSOR_CUSTOM, 
    COLOR, 
    VETA, 
    FOTO_MELAMINA, 
    
    # Estados Canto
    NOMBRE_CANTO,
    GROSOR_CANTO,
    ANCHO_CANTO,
    DIAMETRO_EXT,
    DIAMETRO_INT,
    FOTO_CANTO,
    
    # Común
    BAJA_ID
) = range(15)

# Teclados
MATERIAL_KEYBOARD = [['🪵 Melamina', '🎞️ Canto']]
ACTION_KEYBOARD = [['➕ Agregar', '➖ Dar de baja']]

GROSOR_MELAMINA_KEYBOARD = [
    ['3mm', '6mm', '10mm', '15mm'],
    ['16mm', '18mm', '19mm', '30mm'],
    ['36mm', '38mm', 'Otro...']
]

VETA_KEYBOARD = [['A lo largo', 'A lo ancho'], ['Sin veta']]

GROSOR_CANTO_KEYBOARD = [['0.4', '0.8', '1', '2']]
ANCHO_CANTO_KEYBOARD = [['22', '30', '44']]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando de bienvenida inicial."""
    context.user_data.clear()
    await update.message.reply_text(
        "👋 ¡Hola! Soy el Bot de Inventario GONZATARIO.\n"
        "¿Qué material deseas gestionar?",
        reply_markup=ReplyKeyboardMarkup(
            MATERIAL_KEYBOARD, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return CHOOSING_MATERIAL

async def handle_material_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '🪵 Melamina':
        context.user_data['material'] = 'melamina'
    elif text == '🎞️ Canto':
        context.user_data['material'] = 'canto'
    else:
        await update.message.reply_text("Por favor, selecciona una opción válida.")
        return CHOOSING_MATERIAL

    await update.message.reply_text(
        f"Has seleccionado {text}. ¿Qué deseas hacer?",
        reply_markup=ReplyKeyboardMarkup(
            ACTION_KEYBOARD, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return CHOOSING_ACTION

async def handle_action_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    material = context.user_data.get('material')
    
    if text == '➖ Dar de baja':
        await update.message.reply_text(
            "🗑 Dar de baja un material.\n"
            "Escribe el ID (Ej: M-A32 para melamina o C-A32 para canto):",
            reply_markup=ReplyKeyboardRemove()
        )
        return BAJA_ID
        
    elif text == '➕ Agregar':
        if material == 'melamina':
            await update.message.reply_text(
                "🛠 Vamos a registrar un nuevo retazo de melamina.\n"
                "Paso 1: ¿Cuáles son las medidas en milímetros? (Ej: 500x300)",
                reply_markup=ReplyKeyboardRemove()
            )
            return MEDIDAS
        elif material == 'canto':
            await update.message.reply_text(
                "🛠 Vamos a registrar un rollo de canto.\n"
                "Paso 1: ¿Cuál es el nombre o color? (Ej: Blanco, Café, etc.)",
                reply_markup=ReplyKeyboardRemove()
            )
            return NOMBRE_CANTO
    
    await update.message.reply_text("Selecciona una opción válida.")
    return CHOOSING_ACTION


# ==========================================
# FLUJO BAJA (COMÚN)
# ==========================================
async def baja_id_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pieza_id = update.message.text.strip().upper()
    try:
        exito = use_piece(pieza_id)
        if exito:
            await update.message.reply_text(f"✅ El material {pieza_id} ha sido marcado como USADO.")
        else:
            await update.message.reply_text(f"❌ No se encontró {pieza_id} o ya estaba usado.")
    except Exception as e:
        logger.error(f"Error al dar de baja: {e}")
        await update.message.reply_text("❌ Error de conexión con Google Sheets.")
    
    return await start(update, context)


# ==========================================
# FLUJO AGREGAR: MELAMINA
# ==========================================
async def medidas_recibidas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['medidas'] = update.message.text
    await update.message.reply_text(
        "Paso 2: Selecciona el grosor de la melamina:",
        reply_markup=ReplyKeyboardMarkup(GROSOR_MELAMINA_KEYBOARD, one_time_keyboard=True, resize_keyboard=True)
    )
    return GROSOR

async def grosor_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == 'Otro...':
        await update.message.reply_text("Escribe el grosor que necesitas (ej. 22mm):", reply_markup=ReplyKeyboardRemove())
        return GROSOR_CUSTOM
    else:
        context.user_data['grosor'] = text
        await update.message.reply_text("Paso 3: ¿Qué color o diseño tiene?", reply_markup=ReplyKeyboardRemove())
        return COLOR

async def grosor_custom_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['grosor'] = update.message.text
    await update.message.reply_text("Paso 3: ¿Qué color o diseño tiene?")
    return COLOR

async def color_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['color'] = update.message.text
    await update.message.reply_text(
        "Paso 4: ¿Hacia qué lado va la veta del diseño?",
        reply_markup=ReplyKeyboardMarkup(VETA_KEYBOARD, one_time_keyboard=True, resize_keyboard=True)
    )
    return VETA

async def veta_recibida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['veta'] = update.message.text
    await update.message.reply_text(
        "Paso 5: 📸 Envíame una foto clara del retazo.",
        reply_markup=ReplyKeyboardRemove()
    )
    return FOTO_MELAMINA

async def foto_melamina_recibida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    file_name = f"foto_mel_{update.message.message_id}.jpg"
    await photo_file.download_to_drive(file_name)
    await update.message.reply_text("⏳ Subiendo la imagen...")
    
    try:
        url_foto = upload_photo(file_name, f"retazos/{uuid.uuid4().hex[:8]}.jpg")
        if os.path.exists(file_name): os.remove(file_name)
            
        medidas = context.user_data['medidas']
        grosor = context.user_data['grosor']
        color = context.user_data['color']
        veta = context.user_data['veta']
        
        nuevo_id = add_piece(medidas, color, grosor, veta, url_foto)
        await update.message.reply_text(
            f"✅ ¡Melamina registrada!\n\n🆔 ID: {nuevo_id}\n📏 Medidas: {medidas}\n"
            f"📏 Grosor: {grosor}\n🎨 Color: {color}\n🪵 Veta: {veta}\n\n"
            f"⚠️ Anota este ID ({nuevo_id}) en la pieza física."
        )
    except Exception as e:
        logger.error(f"Error procesando melamina: {e}")
        await update.message.reply_text("❌ Error al guardar.")
        if os.path.exists(file_name): os.remove(file_name)

    return await start(update, context)


# ==========================================
# FLUJO AGREGAR: CANTO
# ==========================================
async def nombre_canto_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['nombre'] = update.message.text
    await update.message.reply_text(
        "Paso 2: Grosor del canto en mm (Ej: 0.8):",
        reply_markup=ReplyKeyboardMarkup(GROSOR_CANTO_KEYBOARD, one_time_keyboard=True, resize_keyboard=True)
    )
    return GROSOR_CANTO

async def grosor_canto_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['grosor'] = float(update.message.text.replace(',', '.'))
    except ValueError:
        await update.message.reply_text("Por favor, ingresa un número válido para el grosor.")
        return GROSOR_CANTO
        
    await update.message.reply_text(
        "Paso 3: Ancho del canto en mm (Ej: 22):",
        reply_markup=ReplyKeyboardMarkup(ANCHO_CANTO_KEYBOARD, one_time_keyboard=True, resize_keyboard=True)
    )
    return ANCHO_CANTO

async def ancho_canto_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['ancho'] = update.message.text
    await update.message.reply_text(
        "Paso 4: Diámetro EXTERIOR del rollo en milímetros (Ej: 270):",
        reply_markup=ReplyKeyboardRemove()
    )
    return DIAMETRO_EXT

async def diametro_ext_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['diam_ext'] = float(update.message.text.replace(',', '.'))
    except ValueError:
        await update.message.reply_text("Ingresa un número válido para el diámetro exterior.")
        return DIAMETRO_EXT
        
    await update.message.reply_text("Paso 5: Diámetro INTERIOR (hueco) en milímetros (Ej: 160):")
    return DIAMETRO_INT

async def diametro_int_recibido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        context.user_data['diam_int'] = float(update.message.text.replace(',', '.'))
    except ValueError:
        await update.message.reply_text("Ingresa un número válido para el diámetro interior.")
        return DIAMETRO_INT
        
    await update.message.reply_text("Paso 6: 📸 Envíame una foto clara del rollo de canto.")
    return FOTO_CANTO

async def foto_canto_recibida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    file_name = f"foto_canto_{update.message.message_id}.jpg"
    await photo_file.download_to_drive(file_name)
    await update.message.reply_text("⏳ Calculando metros y subiendo imagen...")
    
    try:
        url_foto = upload_photo(file_name, f"cantos/{uuid.uuid4().hex[:8]}.jpg")
        if os.path.exists(file_name): os.remove(file_name)
            
        nombre = context.user_data['nombre']
        grosor = context.user_data['grosor']
        ancho = context.user_data['ancho']
        diam_ext = context.user_data['diam_ext']
        diam_int = context.user_data['diam_int']
        
        nuevo_id, ml_total = add_canto(nombre, diam_ext, diam_int, grosor, ancho, url_foto)
        
        await update.message.reply_text(
            f"✅ ¡Rollo de canto registrado!\n\n"
            f"🆔 ID: {nuevo_id}\n"
            f"🎨 Nombre: {nombre}\n"
            f"📏 Ancho: {ancho}mm (Grosor: {grosor}mm)\n"
            f"📐 Diámetros: Ext {diam_ext}mm / Int {diam_int}mm\n"
            f"🔢 Total calculado: {ml_total} Metros Lineales\n\n"
            f"⚠️ Anota este ID ({nuevo_id}) en el rollo físico."
        )
    except Exception as e:
        logger.error(f"Error procesando canto: {e}")
        await update.message.reply_text("❌ Error al guardar. Verifica los datos o tu conexión a Google.")
        if os.path.exists(file_name): os.remove(file_name)

    return await start(update, context)


async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancela la conversación actual."""
    await update.message.reply_text("❌ Operación cancelada.", reply_markup=ReplyKeyboardRemove())
    return await start(update, context)


def get_conversation_handler():
    """Genera la máquina de estados principal."""
    return ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            MessageHandler(filters.Regex(r'(?i)^(hola|go|menu|menú)$'), start)
        ],
        states={
            CHOOSING_MATERIAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_material_choice)],
            CHOOSING_ACTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_action_choice)],
            BAJA_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, baja_id_recibido)],
            
            # Estados Melamina
            MEDIDAS: [MessageHandler(filters.TEXT & ~filters.COMMAND, medidas_recibidas)],
            GROSOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, grosor_recibido)],
            GROSOR_CUSTOM: [MessageHandler(filters.TEXT & ~filters.COMMAND, grosor_custom_recibido)],
            COLOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, color_recibido)],
            VETA: [MessageHandler(filters.TEXT & ~filters.COMMAND, veta_recibida)],
            FOTO_MELAMINA: [MessageHandler(filters.PHOTO, foto_melamina_recibida)],
            
            # Estados Canto
            NOMBRE_CANTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, nombre_canto_recibido)],
            GROSOR_CANTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, grosor_canto_recibido)],
            ANCHO_CANTO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ancho_canto_recibido)],
            DIAMETRO_EXT: [MessageHandler(filters.TEXT & ~filters.COMMAND, diametro_ext_recibido)],
            DIAMETRO_INT: [MessageHandler(filters.TEXT & ~filters.COMMAND, diametro_int_recibido)],
            FOTO_CANTO: [MessageHandler(filters.PHOTO, foto_canto_recibida)]
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
