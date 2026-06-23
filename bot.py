import os
import logging
import asyncio
from flask import Flask, request   # <-- este request es el de Flask
import paypalrestsdk
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# Variables de entorno seguras
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "7078845937"))
PP_CLIENT_ID = os.getenv("PP_CLIENT_ID")
PP_SECRET = os.getenv("PP_SECRET")

# Configuración de PayPal
paypalrestsdk.configure({
    "mode": "sandbox",  # Cambia a "live" en producción
    "client_id": PP_CLIENT_ID,
    "client_secret": PP_SECRET
})

# Flask app
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

⭐ $6 por 10 fotos y 5 videos ⭐
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
            return_url=os.getenv("PAYPAL_RETURN_URL", "https://example.com/success"),
            cancel_url=os.getenv("PAYPAL_CANCEL_URL", "https://example.com/cancel")
        )
        if link:
            await context.bot.send_message(chat_id=usuario_id, text=f"✅ Paga aquí:\n{link}")
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔗 Link generado para cliente {usuario_id}: {link}")
            await query.edit_message_text(f"Link de pago generado para paquete ${precio}.")
        else:
            await context.bot.send_message(chat_id=usuario_id, text="❌ Error generando link de pago.")

# ---------------- APPLICATION ----------------

# Configuramos el cliente HTTP con pool más grande
http_request = HTTPXRequest(connection_pool_size=20, read_timeout=30)

application = Application.builder().token(BOT_TOKEN).request(http_request).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("catalogo", catalogo))
application.add_handler(CommandHandler("comprar", comprar))
application.add_handler(CommandHandler("ayuda", ayuda))
application.add_handler(CallbackQueryHandler(manejar_boton))

# Inicializamos la aplicación (solo initialize, sin start para evitar warnings de polling)
asyncio.run(application.initialize())

# ---------------- WEBHOOKS ----------------

@app.route("/")
def home():
    return "Bot activo", 200

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    # Aquí request es el de Flask
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "OK", 200

@app.route("/paypal", methods=["POST"])
def paypal_webhook():
    data = request.json
    event_type = data.get("event_type")

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        cliente_id = data["resource"]["payer"]["payer_id"]
        monto = data["resource"]["amount"]["value"]
        asyncio.run(application.bot.send_message(chat_id=ADMIN_ID,
                         text=f"✅ Venta realizada\nCliente PayPal: {cliente_id}\nMonto: {monto} USD"))

    elif event_type == "PAYMENT.CAPTURE.REFUNDED":
        cliente_id = data["resource"]["payer"]["payer_id"]
        asyncio.run(application.bot.send_message(chat_id=ADMIN_ID,
                         text=f"⚠️ Reembolso detectado\nCliente PayPal: {cliente_id}"))

    return "OK", 200

# ---------------- MAIN ----------------

if __name__ == "__main__":
    print("Bot con webhook iniciado...")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
