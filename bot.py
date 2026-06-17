import requests
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

TOKEN = "8779001843:AAF2JSDzoMLxj8jtcUfbY72-hMqKfiINq2c"
ADMIN_ID = 7078845937

# Links directos para 13 y 15
LINK_13 = "https://tuservidor.com/link13"
LINK_15 = "https://t.me/+Y7ikb4pcNc01Y2Yx"

# API base de tu repo en GitHub
GITHUB_API_BASE = "https://api.github.com/repos/virtualartist75-prog/Telegg/contents/contenido/contenido"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = """
Bienvenid@

/catalogo - Ver catálogo
/vip - Información VIP
/ayuda - Contacto
"""
    await update.message.reply_text(mensaje)


async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = """
CATÁLOGO

⭐ $6
💕 $9
💦 $13
✨ $15

Envía tu comprobante de pago para revisión.
"""
    await update.message.reply_text(mensaje)


async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mensaje = """
VIP

1. Realiza el pago.
2. Envía el comprobante.
3. Espera la aprobación.
"""
    await update.message.reply_text(mensaje)


async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Contacta al administrador si tienes dudas.")


async def enviar_paquete(context: ContextTypes.DEFAULT_TYPE, usuario_id: int, precio: str):
    if precio in ["6", "9"]:
        url_api = f"{GITHUB_API_BASE}/precio{precio}"
        try:
            resp = requests.get(url_api)
            archivos = resp.json()

            for item in archivos:
                nombre = item["name"]
                enlace = item["download_url"]
                extension = nombre.lower()

                data = requests.get(enlace).content

                if extension.endswith((".jpg", ".jpeg", ".png", ".webp")):
                    await context.bot.send_photo(chat_id=usuario_id, photo=data)
                elif extension.endswith((".mp4", ".mov", ".mkv")):
                    await context.bot.send_video(chat_id=usuario_id, video=data)
                else:
                    await context.bot.send_document(chat_id=usuario_id, document=data, filename=nombre)

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
        [
            InlineKeyboardButton("$6", callback_data=f"6:{usuario.id}"),
            InlineKeyboardButton("$9", callback_data=f"9:{usuario.id}")
        ],
        [
            InlineKeyboardButton("$13", callback_data=f"13:{usuario.id}"),
            InlineKeyboardButton("$15", callback_data=f"15:{usuario.id}")
        ],
        [
            InlineKeyboardButton("❌ Rechazar", callback_data=f"rechazar:{usuario.id}")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(teclado)

    texto_admin = (
        f"📥 Nuevo comprobante\n\n"
        f"ID: {usuario.id}\n"
        f"Usuario: @{usuario.username}\n"
        f"Nombre: {usuario.first_name}"
    )

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=texto_admin,
        reply_markup=reply_markup
    )

    await context.bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=update.effective_chat.id,
        message_id=update.message.message_id
    )

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

    await context.bot.send_message(
        chat_id=usuario_id,
        text=f"✅ Pago aprobado.\nPreparando paquete ${accion}..."
    )

    await enviar_paquete(context, usuario_id, accion)

    await query.edit_message_text(f"Paquete ${accion} enviado.")


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalogo", catalogo))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(CommandHandler("ayuda", ayuda))
    app.add_handler(MessageHandler(filters.PHOTO, recibir_comprobante))
    app.add_handler(CallbackQueryHandler(manejar_boton))

    print("Bot iniciado...")
    app.run_polling()


if __name__ == "__main__":
    main()
