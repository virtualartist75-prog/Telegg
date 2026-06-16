from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💕 Bienvenid@ 💕\n\n"
        "Usa /catalogo para ver todos mis planes ✨"
    )

async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto = """
😆 CATALOGO DE MI CONTENIDO 😆

⭐️ $6 x 5 fotos y 5 videos

💕 $9 x 15 fotos y 10 videos

💦 $13 Chat creativo con fotos

✨ $15 Canal VIP 100 fotos 30 videos

🎁 Recibo Paypal / Bizum / Giftcard / Mercado Pago 🎁
"""
    await update.message.reply_text(texto)

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✨ El canal VIP incluye 100 fotos y 30 videos ✨"
    )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💕 Escríbeme si tienes alguna duda 💕"
    )

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("catalogo", catalogo))
app.add_handler(CommandHandler("vip", vip))
app.add_handler(CommandHandler("ayuda", ayuda))

app.run_polling()
