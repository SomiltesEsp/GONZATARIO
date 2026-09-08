import os
import sys

# Inyectar el directorio raíz al path para que Python encuentre 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from src.bot_core import get_conversation_handler, mensaje_desconocido

def main():
    # Cargar las variables desde el archivo .env (Token, IDs de Google)
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not TOKEN or TOKEN == "AQUI_TU_TOKEN":
        print("ERROR: No se ha configurado el Token de Telegram en .env", file=sys.stderr)
        sys.exit(1)

    print("Iniciando aplicacion de Telegram...")
    # Crear el núcleo del bot
    application = Application.builder().token(TOKEN).build()
    
    # Flujo de registro paso a paso (ahora contiene el menú principal)
    application.add_handler(get_conversation_handler())

    # Manejador para textos sueltos (como mensajes que no activen el flujo)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensaje_desconocido))

    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    PORT = int(os.getenv("PORT", "8080"))

    if WEBHOOK_URL:
        print(f"Modo Webhook activado. Escuchando en el puerto {PORT}")
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"{WEBHOOK_URL}/{TOKEN}"
        )
    else:
        print("Bot iniciado en modo Polling (Pruebas locales). Escríbele a tu bot en Telegram.")
        application.run_polling()

if __name__ == '__main__':
    main()
