from telegram import Update
from telegram.ext import (
Application,
CommandHandler,
MessageHandler,
ContextTypes,
filters
)

TOKEN = "TU_TOKEN_AQUI"

ADMIN_ID = 7078845937

=========================
COMANDOS PUBLICOS
=========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

mensaje = """

Bienvenid@

Usa los siguientes comandos:

/catalogo - Ver catálogo
/vip - Información
/ayuda - Contacto
/id - Ver tu ID
"""

await update.message.reply_text(mensaje)

async def catalogo(update: Update, context: ContextTypes.DEFAULT_TYPE):

mensaje = """

CATÁLOGO

⭐ Producto 1

💕 Producto 2

💦 Producto 3

✨ Acceso VIP

🎁 Pago mediante PayPal
"""

await update.message.reply_text(mensaje)

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):

mensaje = """

VIP

Realiza el pago.
Envía tu comprobante.
Espera la revisión.

Cuando se revise tu pago recibirás una respuesta.
"""

await update.message.reply_text(mensaje)

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):

await update.message.reply_text(
    "Si tienes dudas, contacta al administrador."
)

async def mi_id(update: Update, context: ContextTypes.DEFAULT_TYPE):

usuario = update.effective_user

await update.message.reply_text(
    f"Tu ID es: {usuario.id}"
)
=========================
RECEPCION DE COMPROBANTES
=========================

async def recibir_comprobante(
update: Update,
context: ContextTypes.DEFAULT_TYPE
):

usuario = update.effective_user

texto_admin = (
    f"📥 Nuevo comprobante\n\n"
    f"ID: {usuario.id}\n"
    f"Usuario: @{usuario.username}\n"
    f"Nombre: {usuario.first_name}\n\n"
    f"/aprobar {usuario.id}\n"
    f"/rechazar {usuario.id}"
)

await context.bot.send_message(
    chat_id=ADMIN_ID,
    text=texto_admin
)

await context.bot.forward_message(
    chat_id=ADMIN_ID,
    from_chat_id=update.effective_chat.id,
    message_id=update.message.message_id
)

await update.message.reply_text(
    "✅ Comprobante recibido. Será revisado manualmente."
)
=========================
COMANDOS DE ADMINISTRADOR
=========================

async def aprobar(
update: Update,
context: ContextTypes.DEFAULT_TYPE
):

if update.effective_user.id != ADMIN_ID:
    return

if len(context.args) != 1:

    await update.message.reply_text(
        "Uso: /aprobar ID_USUARIO"
    )
    return

usuario_id = int(context.args[0])

try:

    await context.bot.send_message(
        chat_id=usuario_id,
        text=(
            "✅ Pago aprobado.\n\n"
            "Tu solicitud ha sido aprobada."
        )
    )

    await update.message.reply_text(
        "Usuario aprobado."
    )

except Exception as e:

    await update.message.reply_text(
        f"Error: {e}"
    )

async def rechazar(
update: Update,
context: ContextTypes.DEFAULT_TYPE
):

if update.effective_user.id != ADMIN_ID:
    return

if len(context.args) != 1:

    await update.message.reply_text(
        "Uso: /rechazar ID_USUARIO"
    )
    return

usuario_id = int(context.args[0])

try:

    await context.bot.send_message(
        chat_id=usuario_id,
        text="❌ No fue posible verificar el pago."
    )

    await update.message.reply_text(
        "Usuario notificado."
    )

except Exception as e:

    await update.message.reply_text(
        f"Error: {e}"
    )
=========================
MAIN
=========================

def main():

app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("catalogo", catalogo))
app.add_handler(CommandHandler("vip", vip))
app.add_handler(CommandHandler("ayuda", ayuda))
app.add_handler(CommandHandler("id", mi_id))

app.add_handler(CommandHandler("aprobar", aprobar))
app.add_handler(CommandHandler("rechazar", rechazar))

app.add_handler(
    MessageHandler(
        filters.PHOTO,
        recibir_comprobante
    )
)

print("Bot iniciado...")
app.run_polling()

if name == "main":
main()
