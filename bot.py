from telegram import Update, MessageEntity
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8779001843:AAHHL0RSbotUHUClEQt9BC7kor8C5TWqu7w"

# ==========================
# EMOJIS PERSONALIZADOS
# ==========================

EMOJIS_TEXTO = "😆⭐💕💦✨🎁"

EMOJIS_IDS = [
    "5958408954374525870",  # 😆
    "5958272022227194442",  # ⭐
    "5958529900653579813",  # 💕
    "5958354614448296239",  # 💦
    "5960700632959553580",  # ✨
    "5958423711882153648",  # 🎁
]

EMOJIS_ENTIDADES = [
    MessageEntity(
        type="custom_emoji",
        offset=0,
        length=2,
        custom_emoji_id=EMOJIS_IDS[0]
    ),
    MessageEntity(
        type="custom_emoji",
        offset=2,
        length=2,
        custom_emoji_id=EMOJIS_IDS[1]
    ),
    MessageEntity(
        type="custom_emoji",
        offset=4,
        length=2,
        custom_emoji_id=EMOJIS_IDS[2]
    ),
    MessageEntity(
        type="custom_emoji",
        offset=6,
        length=2,
        custom_emoji_id=EMOJIS_IDS[3]
    ),
    MessageEntity(
        type="custom_emoji",
        offset=8,
        length=1,
        custom_emoji_id=EMOJIS_IDS[4]
    ),
    MessageEntity(
        type="custom_emoji",
        offset=9,
        length=2,
        custom_emoji_id=EMOJIS_IDS[5]
    ),
]


# ==========================
# FUNCIONES
# ==========================

async def enviar_emojis(update: Update):
    await update.message.reply_text(
        text=EMOJIS_TEXTO,
        entities=EMOJIS_ENTIDADES
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_emojis(update)

    await update.message.reply_text(
        """
Bienvenid@

Usa los siguientes comandos:

/catalogo - Ver catálogo
/vip - Información del canal VIP
/ayuda - Contacto
"""
    )


async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_emojis(update)

    await update.message.reply_text(
        """
CATALOGO DE MI CONTENIDO

⭐ $6

💕 $9

💦 $13

✨ $15

🎁 Recibo Paypal / Bizum / Giftcard / Mercado Pago
"""
    )


async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_emojis(update)

    await update.message.reply_text(
        """
✨ CANAL VIP ✨

Incluye:

💕 100

💦 30

Para comprar, escríbeme o usa /catalogo
"""
    )


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await enviar_emojis(update)

    await update.message.reply_text(
        "💕 Si tienes dudas, escríbeme directamente."
    )


# ==========================
# MAIN
# ==========================

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
