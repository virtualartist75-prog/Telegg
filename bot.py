from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "TU_TOKEN_AQUI"



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

```
mensaje = """
```

Bienvenid@ a mi tienda de contenido

Usa los siguientes comandos:

/catalogo - Ver catálogo
/vip - Información del canal VIP
/ayuda - Contacta personalmente conmigo
"""

```
await update.message.reply_text(mensaje)
```

async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):


```
mensaje = """
```

CATÁLOGO DE MI CONTENIDO

⭐ $6 por 10 fotos y 5 videos ⭐

💕 $9 por 25 fotos y 15 videos 💕

💦 $13 por Chat Hot (Disponible solo si estoy conectada) 💦

✨ $15 Canal VIP 100 fotos y 30 videos PARA SIEMPRE ✨

🎁 Recibo Paypal / Bizum / Giftcard / Mercado Pago 🎁
"""

```
await update.message.reply_text(mensaje)
```

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):


```
mensaje = """
```

✨ CANAL VIP ✨

Incluye:

💎 100 Fotos y 30 videos sola y follando 💎

✨LINK PARA ENTRAR: https://t.me/+qygd9d_bqRo2ZmQx ✨

🎁 Seras aceptado al momento de pagar 🎁

Para comprar, escríbeme directamente @Sofi_ly19
"""

```
await update.message.reply_text(mensaje)
```

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):


```
await update.message.reply_text(
    "💕 Si tienes dudas, escríbeme directamente @Sofi_ly19."
)
```

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
