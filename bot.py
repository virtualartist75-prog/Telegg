import os
import urllib.request
import json
import logging
from flask import Flask, request
import paypalrestsdk
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

# Token seguro desde variable de entorno
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7078845937

# Links directos para 13 y 15
LINK_13 = "@Sofi_ly19 hablame"
LINK_15 = "https://t.me/+Y7ikb4pcNc01Y2Yx"

# API base de tu repo en GitHub
GITHUB_API_BASE = "https://api.github.com/repos/virtualartist75-prog/Telegg/contents/contenido/contenido"

# Configuración de PayPal
paypalrestsdk.configure({
    "mode": "sandbox",  # Cambia a "live" en producción
    "client_id": "AY4tdbh4bKjdwn_ipn1O3Fa5TSC1Q2WEIzmvRStKg1_C0g5OSPnIpsVzbgS0TQgHvon72j6bU2aroXG3",
    "client_secret": os.getenv("PP_Key")
})

# Flask para webhook
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# ---------------- BOT ----------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💕 Bienvenid@ a mi bot de contenido 💕 \n\n/catalogo - Ver catálogo\n/comprar - Comprar paquetes\n/ayuda - Contacto"
    )

async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = """
CATÁLOGO

💋 $6 por 10 fotos y 5 videos 💋
💕 $9 por 25 fotos y 15 videos 💕
✨ $13 acceso especial ✨
🌟 $15 canal VIP 🌟

Usa /comprar para generar tu link de pago.
"""
    await update.message.reply_text(mensaje)

async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    teclado = [
        [InlineKeyboardButton("$6", callback_data=f"paypal:6:{update.effective_user.id}"),
         InlineKeyboardButton("$9", callback_data=f"paypal:9:{update.effective_user.id}")],
        [InlineKeyboardButton("$13", callback_data=f"paypal:13:{update.effective_user.id}"),
         InlineKeyboardButton("$15", callback_data=f"paypal:15:{update.effective_user.id}")]
    ]
    reply_markup = InlineKeyboardMarkup(teclado)
    await update.message.reply_text("Selecciona tu paquete:", reply_markup=reply_markup)

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Contacta conmigo @Sofi_ly19 si tienes dudas.")

# ---------------- ENTREGA ----------------

async def enviar_paquete(context: ContextTypes.DEFAULT_TYPE, usuario_id: int, precio: str):
    if precio in ["6", "9"]:
        url_api = f"{GITHUB_API_BASE}/precio{precio}"
        try:
            with urllib.request.urlopen(url_api, timeout=15) as resp:
                archivos = json.loads(resp.read().decode())

            total = len(archivos)
            for idx, item in enumerate(archivos, start=1):
                enlace = item["download_url"]
                extension = item["name"].lower()

                await context.bot.send_message(chat_id=usuario_id, text=f"📦 Enviando archivo {idx}/{total}...")

                try:
                    with urllib.request.urlopen(enlace, timeout=30) as f:
                        data = f.read()

                    if extension.endswith((".jpg", ".jpeg", ".png", ".webp")):
                        await context.bot.send_photo(chat_id=usuario_id, photo=data)
                    elif extension.endswith((".mp4", ".mov", ".mkv")):
                        await context.bot.send_video(chat_id=usuario_id, video=data)
                    else:
                        await context.bot.send_document(chat_id=usuario_id, document=data)

                except Exception:
                    await context.bot.send_message(chat_id=usuario_id, text="❌ Error enviando un archivo")

        except Exception as e:
            await context.bot.send_message(chat_id=usuario_id, text=f"❌ Error leyendo carpeta: {e}")
            return

        await context.bot.send_message(chat_id=usuario_id, text="✅ Entrega completada.")

    elif precio == "13":
        await context.bot.send_message(chat_id=usuario_id, text=f"✅ Aquí está tu acceso: {LINK_13}")
    elif precio == "15":
        await context.bot.send_message(chat_id=usuario_id, text=f"✅ Aquí está tu acceso: {LINK_15}")

# ---------------- PAYPAL ----------------

def crear_pago(monto, descripcion, return_url, cancel_url):
    pago = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {"payment_method": "paypal"},
        "redirect_urls": {
            "return_url": return_url,
            "cancel_url": cancel_url
        },
        "transactions": [{
            "amount": {"total": str(monto), "currency": "USD"},
            "description": descripcion
        }]
    })

    if pago.create():
        for link in pago.links:
            if link.rel == "approval_url":
                return str(link.href)
    else:
        logging.error(pago.error)
        return None

async def manejar_boton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    accion, precio, usuario_id = query.data.split(":")
    usuario_id = int(usuario_id)

    if accion == "paypal":
        descripcion = f"Paquete ${precio}"
        link = crear_pago(
            monto=precio,
            descripcion=descripcion,
            return_url="https://tuservidor.com/success",
            cancel_url="https://tuservidor.com/cancel"
        )
        if link:
            # Enviar link al cliente
            await context.bot.send_message(chat_id=usuario_id, text=f"✅ Paga aquí:\n{link}")
            # Avisar al admin
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔗 Link generado para cliente {usuario_id}: {link}")
            await query.edit_message_text(f"Link de pago generado para paquete ${precio}.")
        else:
            await context.bot.send_message(chat_id=usuario_id, text="❌ Error generando link de pago.")

# ---------------- WEBHOOK ----------------

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event_type = data.get("event_type")

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        cliente_id = data["resource"]["payer"]["payer_id"]
        monto = data["resource"]["amount"]["value"]

        # Aquí deberías mapear cliente_id con usuario_id de Telegram
        # enviar_paquete(context, usuario_id, precio)

        bot.send_message(chat_id=ADMIN_ID,
                         text=f"✅ Venta realizada\nCliente PayPal: {cliente_id}\nMonto: {monto} USD")

    elif event_type == "PAYMENT.CAPTURE.REFUNDED":
        cliente_id = data["resource"]["payer"]["payer_id"]
        bot.send_message(chat_id=ADMIN_ID,
                         text=f"⚠️ Reembolso detectado\nCliente PayPal: {cliente_id}")

    return "OK", 200

# ---------------- MAIN ----------------

def main():
    app_tg = Application.builder().token(TOKEN).build()

    app_tg.add_handler(CommandHandler("start", start))
    app_tg.add_handler(CommandHandler("catalogo", catalogo))
    app_tg.add_handler(CommandHandler("comprar", comprar))
    app_tg.add_handler(CommandHandler("ayuda", ayuda))
    app_tg.add_handler(CallbackQueryHandler(manejar_boton))

    print("Bot iniciado...")
    app_tg.run_polling()

if __name__ == "__main__":
    main()
    app.run(port=5000)
