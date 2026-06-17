import os
import urllib.request
import json
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# Token seguro desde variable de entorno
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 7078845937

# Links directos para 13 y 15
LINK_13 = "https://tuservidor.com/link13"
LINK_15 = "https://tuservidor.com/link15"

# API base de tu repo en GitHub
GITHUB_API_BASE = "https://api.github.com/repos/virtualartist75-prog/Telegg/contents/contenido/contenido"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bienvenid@\n\n/catalogo - Ver catálogo\n/comprar - Información de compra\n/ayuda - Contacto"
    )


async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = """
CATÁLOGO

⭐ $6 por 10 fotos y 5 videos ⭐

💕 $9 por 25 fotos y 15 videos 💕

💦 $13 chat hot (SOLO SI ESTOY CONECTADA) 💦

✨ $15 Canal VIP 100 fotos y 30 videos ✨

SI QUIERES COMPRAR UNO PORFAVOR ESCRIBE /comprar
"""
    await update.message.reply_text(mensaje)


async def comprar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = """
1. Realiza el pago aquí:
   https://www.paypal.com/paypalme/sofiafernandez112
   
2. Envía la foto del pago.

3. Espera la aprobación.

4. Se enviara automaticamente mi contenido rico

5. Disfruta
"""
    await update.message.reply_text(mensaje)


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Contacta al administrador si tienes dudas.")


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


async def recibir_comprobante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usuario = update.effective_user

    teclado = [
        [InlineKeyboardButton("$6", callback_data=f"6:{usuario.id}"),
         InlineKeyboardButton("$9", callback_data=f"9:{usuario.id}")],
        [InlineKeyboardButton("$13", callback_data=f"13:{usuario.id}"),
         InlineKeyboardButton("$15", callback_data=f"15:{usuario.id}")],
        [InlineKeyboardButton("❌ Rechazar", callback_data=f"rechazar:{usuario.id}")]
    ]

    reply_markup = InlineKeyboardMarkup(teclado)

    texto_admin = (
        f"📥 Nuevo comprobante\n\n"
        f"ID: {usuario.id}\n"
        f"Usuario: @{usuario.username}\n"
        f"Nombre: {usuario.first_name}"
    )

    await context.bot.send_message(chat_id=ADMIN_ID, text=texto_admin, reply_markup=reply_markup)
    await context.bot.forward_message(chat_id=ADMIN_ID, from_chat_id=update.effective_chat.id,
                                      message_id=update.message.message_id)
    await update.message.reply_text("✅ Comprobante recibido.")


async def manejar_boton(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("No autorizado", show_alert=True)
        return

    accion, usuario_id = query.data.split(":")
    usuario_id = int(usuario_id)

    if accion == "rechazar":
        await context.bot.send_message(chat_id=usuario_id, text="❌ Pago rechazado.")
        await query.edit_message_text("Pago rechazado.")
        return

    await context.bot.send_message(chat_id=usuario_id, text=f"✅ Pago aprobado.\nPreparando paquete ${accion}...")
    await enviar_paquete(context, usuario_id, accion)
    await query.edit_message_text(f"Paquete ${accion} enviado.")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalogo", catalogo))
    app.add_handler(CommandHandler("comprar", comprar))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(MessageHandler(filters.PHOTO, recibir_comprobante))
    app.add_handler(CallbackQueryHandler(manejar_boton))

    print("Bot iniciado en Render como worker...")
    app.run_polling()


if __name__ == "__main__":
    main()
