from telegram import Update, MessageEntity
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "8779001843:AAHHL0RSbotUHUClEQt9BC7kor8C5TWqu7w"

# ==================================

# EMOJIS PERSONALIZADOS

# ==================================

EMOJIS = [
("😆", "5958408954374525870"),
("⭐️", "5958272022227194442"),
("💕", "5958529900653579813"),
("💦", "5958354614448296239"),
("✨", "5960700632959553580"),
("🎁", "5958423711882153648"),
]

def utf16_len(text):
return len(text.encode("utf-16-le")) // 2

EMOJIS_TEXTO = "".join(e[0] for e in EMOJIS)

EMOJIS_ENTIDADES = []

offset = 0

for emoji, emoji_id in EMOJIS:
length = utf16_len(emoji)

```
EMOJIS_ENTIDADES.append(
    MessageEntity(
        type="custom_emoji",
        offset=offset,
        length=length,
        custom_emoji_id=emoji_id,
    )
)

offset += length
```

# ==================================

# FUNCIONES

# ==================================

async def enviar_emojis(update: Update):
await update.message.reply_text(
text=EMOJIS_TEXTO,
entities=EMOJIS_ENTIDADES
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
await enviar_emojis(update)

```
await update.message.reply_text(
    """Bienvenid@
```

Usa los siguientes comandos:

/catalogo - Ver catálogo
/vip - Información VIP
/ayuda - Contacto
"""
)

async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
await enviar_emojis(update)

```
await update.message.reply_text(
    """CATÁLOGO
```

⭐ $6
💕 $9
💦 $13
✨ $15

🎁 Paypal / Bizum / Giftcard / Mercado Pago
"""
)

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
await enviar_emojis(update)

```
await update.message.reply_text(
    """✨ CANAL VIP ✨
```

💕 100
💦 30

Usa /catalogo para más información.
"""
)

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
await enviar_emojis(update)

```
await update.message.reply_text(
    "💕 Si tienes dudas, escríbeme directamente."
)
```

# ==================================

# MAIN

# ==================================

def main():
app = Application.builder().token(TOKEN).build()

```
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("catalogo", catalogo))
app.add_handler(CommandHandler("vip", vip))
app.add_handler(CommandHandler("ayuda", ayuda))

print("Bot iniciado...")
app.run_polling()
```

if **name** == "**main**":
main()
