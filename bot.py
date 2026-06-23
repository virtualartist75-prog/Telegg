import os
import logging
import asyncio
import threading
from flask import Flask, request
import paypalrestsdk
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.request import HTTPXRequest

# ─── VARIABLES DE ENTORNO ───────────────────────────────────────────────────
BOT_TOKEN    = os.getenv("BOT_TOKEN")
ADMIN_ID     = int(os.getenv("ADMIN_ID", "7078845937"))
PP_CLIENT_ID = os.getenv("PP_CLIENT_ID")
PP_SECRET    = os.getenv("PP_SECRET")
BASE_URL     = os.getenv("BASE_URL", "https://telegg-wz7c.onrender.com")

paypalrestsdk.configure({
    "mode": "sandbox",   # <- Cambia a "live" en producción
    "client_id": PP_CLIENT_ID,
    "client_secret": PP_SECRET
})

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Pagos ya procesados (evita ejecutar el mismo pago dos veces)
pagos_procesados = set()

# ─── EVENT LOOP DEDICADO ────────────────────────────────────────────────────

loop = asyncio.new_event_loop()

def start_loop(l):
    asyncio.set_event_loop(l)
    l.run_forever()

threading.Thread(target=start_loop, args=(loop,), daemon=True).start()

def run_async(coro):
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    return future.result(timeout=60)

# ─── COMANDOS DEL BOT ───────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💕 Bienvenid@ a mi bot de contenido 💕\n\n"
        "/catalogo - Ver catálogo\n"
        "/comprar  - Comprar paquetes\n"
        "/ayuda    - Contacto"
    )

async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "CATÁLOGO\n\n"
        "⭐ $6  — 10 fotos y 5 videos\n"
        "💕 $9  — 25 fotos y 15 videos\n"
        "✨ $13 — Acceso especial\n"
        "🌟 $15 — Canal VIP\n\n"
        "Usa /comprar para generar tu link de pago."
    )

async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    teclado = [
        [InlineKeyboardButton("$6",  callback_data=f"paypal:6:{uid}"),
         InlineKeyboardButton("$9",  callback_data=f"paypal:9:{uid}")],
        [InlineKeyboardButton("$13", callback_data=f"paypal:13:{uid}"),
         InlineKeyboardButton("$15", callback_data=f"paypal:15:{uid}")]
    ]
    await update.message.reply_text(
        "Selecciona tu paquete:",
        reply_markup=InlineKeyboardMarkup(teclado)
    )

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Contacta conmigo @Sofi_ly19 si tienes dudas.")

# ─── PAYPAL ─────────────────────────────────────────────────────────────────

def crear_pago(monto, descripcion, usuario_id):
    return_url = f"{BASE_URL}/success?usuario_id={usuario_id}&monto={monto}"
    cancel_url  = f"{BASE_URL}/cancel?usuario_id={usuario_id}"

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

    logging.error(f"Error creando pago PayPal: {pago.error}")
    return None

async def manejar_boton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, precio, usuario_id = query.data.split(":")
    usuario_id = int(usuario_id)

    link = crear_pago(
        monto=precio,
        descripcion=f"Paquete ${precio}",
        usuario_id=usuario_id
    )

    if link:
        await context.bot.send_message(
            chat_id=usuario_id,
            text=f"✅ Paga aquí:\n{link}"
        )
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"🔗 Link generado\nCliente ID: {usuario_id}\nPaquete: ${precio}\n{link}"
        )
        await query.edit_message_text(f"Link de pago generado para paquete ${precio}.")
    else:
        await context.bot.send_message(
            chat_id=usuario_id,
            text="❌ Error generando link de pago. Intenta de nuevo o contacta @Sofi_ly19."
        )

# ─── ENVÍO AUTÓNOMO DE CONTENIDO ────────────────────────────────────────────

async def _enviar_archivos(usuario_id: int, carpeta: str):
    """Envía todos los archivos de una carpeta al usuario."""
    base = os.path.dirname(os.path.abspath(__file__))
    ruta = os.path.join(base, carpeta)
    logging.info(f"Buscando contenido en: {ruta}")

    if not os.path.exists(ruta):
        logging.error(f"Carpeta no encontrada: {ruta}")
        await application.bot.send_message(
            chat_id=usuario_id,
            text="❌ Error al cargar el contenido. Contacta @Sofi_ly19."
        )
        return

    archivos = sorted([f for f in os.listdir(ruta) if not f.startswith(".")])
    if not archivos:
        logging.warning(f"Carpeta vacía: {ruta}")
        await application.bot.send_message(
            chat_id=usuario_id,
            text="❌ No hay archivos disponibles aún. Contacta @Sofi_ly19."
        )
        return

    for nombre in archivos:
        ruta_archivo = os.path.join(ruta, nombre)
        if not os.path.isfile(ruta_archivo):
            continue
        ext = nombre.lower().rsplit(".", 1)[-1]
        try:
            with open(ruta_archivo, "rb") as f:
                if ext in ("jpg", "jpeg", "png", "webp"):
                    await application.bot.send_photo(chat_id=usuario_id, photo=f)
                elif ext in ("mp4", "mov", "avi"):
                    await application.bot.send_video(chat_id=usuario_id, video=f)
                else:
                    await application.bot.send_document(chat_id=usuario_id, document=f)
        except Exception as e:
            logging.error(f"Error enviando {nombre}: {e}")

async def enviar_contenido(usuario_id: str, monto: str):
    """Envía el contenido correspondiente al paquete comprado."""
    uid = int(usuario_id)

    if monto == "6":
        await application.bot.send_message(
            chat_id=uid,
            text="✅ ¡Pago recibido! Aquí está tu paquete de $6 💕"
        )
        await _enviar_archivos(uid, "contenido/precio6")

    elif monto == "9":
        await application.bot.send_message(
            chat_id=uid,
            text="✅ ¡Pago recibido! Aquí está tu paquete de $9 💕"
        )
        await _enviar_archivos(uid, "contenido/precio9")

    elif monto == "13":
        await application.bot.send_message(
            chat_id=uid,
            text="✅ ¡Pago recibido!\n\nTEST COMPLETADO ✨"
        )

    elif monto == "15":
        await application.bot.send_message(
            chat_id=uid,
            text=(
                "✅ ¡Pago recibido! Bienvenid@ al Canal VIP 🌟\n\n"
                "Únete aquí: https://t.me/+Y7ikb4pcNc01Y2Yx"
            )
        )

# ─── APPLICATION ────────────────────────────────────────────────────────────

http_request = HTTPXRequest(connection_pool_size=20, read_timeout=30)
application = (
    Application.builder()
    .token(BOT_TOKEN)
    .request(http_request)
    .updater(None)
    .build()
)
application.add_handler(CommandHandler("start",    start))
application.add_handler(CommandHandler("catalogo", catalogo))
application.add_handler(CommandHandler("comprar",  comprar))
application.add_handler(CommandHandler("ayuda",    ayuda))
application.add_handler(CallbackQueryHandler(manejar_boton))

run_async(application.initialize())
run_async(application.start())

# ─── RUTAS FLASK ────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return "Bot activo ✅", 200

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data   = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    run_async(application.process_update(update))
    return "OK", 200

@app.route("/success")
def success():
    payment_id = request.args.get("paymentId")
    payer_id   = request.args.get("PayerID")
    usuario_id = request.args.get("usuario_id")
    monto      = request.args.get("monto")

    if not payment_id or not payer_id:
        return "❌ Faltan datos del pago.", 400

    # Evitar procesar el mismo pago dos veces
    if payment_id in pagos_procesados:
        logging.info(f"Pago {payment_id} ya fue procesado, ignorando.")
        return """
            <html>
            <body style="font-family:sans-serif;text-align:center;padding:60px;background:#fff0f5;">
                <h2 style="color:#d63384;">✅ ¡Pago completado!</h2>
                <p>Gracias por tu compra 💕<br>El contenido ya está en el bot. Puedes cerrar esta ventana.</p>
            </body>
            </html>
        """, 200

    try:
        payment = paypalrestsdk.Payment.find(payment_id)

        # Si el pago ya está aprobado en PayPal, no intentar ejecutarlo de nuevo
        if payment.state == "approved":
            pagos_procesados.add(payment_id)
            if usuario_id and monto:
                run_async(enviar_contenido(usuario_id, monto))
            run_async(application.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"💰 ¡Venta confirmada!\n"
                    f"Cliente ID: {usuario_id}\n"
                    f"Monto: ${monto} USD\n"
                    f"Payment ID: {payment_id}"
                )
            ))
            return """
                <html>
                <body style="font-family:sans-serif;text-align:center;padding:60px;background:#fff0f5;">
                    <h2 style="color:#d63384;">✅ ¡Pago completado!</h2>
                    <p>Gracias por tu compra 💕<br>El contenido ya está en el bot. Puedes cerrar esta ventana.</p>
                </body>
                </html>
            """, 200

        if payment.execute({"payer_id": payer_id}):
            pagos_procesados.add(payment_id)

            if usuario_id and monto:
                run_async(enviar_contenido(usuario_id, monto))

            run_async(application.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    f"💰 ¡Venta confirmada!\n"
                    f"Cliente ID: {usuario_id}\n"
                    f"Monto: ${monto} USD\n"
                    f"Payment ID: {payment_id}"
                )
            ))
            return """
                <html>
                <body style="font-family:sans-serif;text-align:center;padding:60px;background:#fff0f5;">
                    <h2 style="color:#d63384;">✅ ¡Pago completado!</h2>
                    <p>Gracias por tu compra 💕<br>El contenido ya está en el bot. Puedes cerrar esta ventana.</p>
                </body>
                </html>
            """, 200

        else:
            logging.error(f"Error ejecutando pago: {payment.error}")
            return "❌ Error al ejecutar el pago.", 400

    except Exception as e:
        logging.error(f"Excepción en /success: {e}")
        return "❌ Error interno.", 500

@app.route("/cancel")
def cancel():
    usuario_id = request.args.get("usuario_id")

    if usuario_id:
        run_async(application.bot.send_message(
            chat_id=int(usuario_id),
            text="❌ Cancelaste el pago. Si fue un error, usa /comprar para intentarlo de nuevo."
        ))

    return """
        <html>
        <body style="font-family:sans-serif;text-align:center;padding:60px;background:#fff0f5;">
            <h2 style="color:#d63384;">❌ Pago cancelado</h2>
            <p>Puedes cerrar esta ventana y volver al bot.</p>
        </body>
        </html>
    """, 200

@app.route("/paypal", methods=["POST"])
def paypal_webhook():
    data       = request.json
    event_type = data.get("event_type")

    if event_type == "PAYMENT.CAPTURE.COMPLETED":
        cliente_id = data["resource"]["payer"]["payer_id"]
        monto      = data["resource"]["amount"]["value"]
        run_async(application.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"✅ Venta realizada\nCliente PayPal: {cliente_id}\nMonto: {monto} USD"
        ))

    elif event_type == "PAYMENT.CAPTURE.REFUNDED":
        cliente_id = data["resource"]["payer"]["payer_id"]
        run_async(application.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"⚠️ Reembolso detectado\nCliente PayPal: {cliente_id}"
        ))

    return "OK", 200

# ─── MAIN ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Bot con webhook iniciado...")
    print(f"BASE_URL: {BASE_URL}")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
