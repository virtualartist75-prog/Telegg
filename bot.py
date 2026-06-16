from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8779001843:AAGOpliQVvEoNXdSJYHTp-FLUldD4iQ1Src"


async def enviar_emojis(update: Update):
    await update.message.reply_text("😆⭐💕💦✨🎁")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_emojis(update)

    mensaje = """
Bienvenid@

Usa los siguientes comandos:

/catalogo - Ver catálogo
/vip - Información del canal VIP
/ayuda - Contacto
"""

    await update.message.reply_text(mensaje)


async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_emojis(update)

    mensaje = """
CATALOGO DE MI CONTENIDO

⭐ Opción 1

💕 Opción 2

💦 Opción 3

✨ Opción 4

🎁 Métodos de pago
"""

    await update.message.reply_text(mensaje)


async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = """
✨ CANAL VIP ✨

Incluye:
💕 Fotos
💦 Videos

Para más información usa /catalogo
"""

    await update.message.reply_text(mensaje)


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💕 Si tienes dudas, escríbeme directamente."
    )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalogo", catalogo))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(CommandHandler("ayuda", ayuda))

    print("Bot iniciado...")
    app.run_polling()


if __name__ == "__main__":
    main()
