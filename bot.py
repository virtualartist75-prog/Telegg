from telegram import Update, MessageEntity
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8779001843:AAGOpliQVvEoNXdSJYHTp-FLUldD4iQ1Src"

async def enviar_emojis(update: Update):
    texto = "😆⭐💕💦✨🎁"

    entidades = [
        MessageEntity(
            type="custom_emoji",
            offset=0,
            length=2,
            custom_emoji_id="5958408954374525870"
        ),
        MessageEntity(
            type="custom_emoji",
            offset=2,
            length=2,
            custom_emoji_id="5958272022227194442"
        ),
        MessageEntity(
            type="custom_emoji",
            offset=4,
            length=2,
            custom_emoji_id="5958529900653579813"
        ),
        MessageEntity(
            type="custom_emoji",
            offset=6,
            length=2,
            custom_emoji_id="5958354614448296239"
        ),
        MessageEntity(
            type="custom_emoji",
            offset=8,
            length=1,
            custom_emoji_id="5960700632959553580"
        ),
        MessageEntity(
            type="custom_emoji",
            offset=9,
            length=2,
            custom_emoji_id="5958423711882153648"
        )
    ]

    await update.message.reply_text(
        text=texto,
        entities=entidades
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await enviar_emojis(update)

    mensaje = """
Bienvenid@ 💕

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

⭐ $6 x 5 fotos y 5 videos

💕 $9 x 15 fotos y 10 videos

💦 $13 Chat creativo con fotos

✨ $15 Canal VIP 100 fotos 30 videos

🎁 Recibo Paypal / Bizum / Giftcard / Mercado Pago
"""

    await update.message.reply_text(mensaje)

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = """
✨ CANAL VIP ✨

Incluye:
💕 100 fotos
💦 30 videos

Para comprar, escríbeme o usa /catalogo
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
