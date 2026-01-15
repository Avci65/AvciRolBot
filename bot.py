import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Rol ve Emoji Eşleşmeleri
ROLE_EMOJIS = {
    "tavcı": "💂", "tarikat avcisi": "💂",
    "yancı": "💋", "hood": "💋",
    "melek": "👼", "koruyucu melek": "👼",
    "detective": "🕵️","dete": "🕵️",
    "gözcü": "👳‍♀️",
    "otacı": "🍃",
    "muhtar": "🎖",
    "silah": "🔫",
    "prens": "👑", "prenses": "👑",
    "çiftçi": "👨‍🌾", "aldeanisimo": "👨‍🌾",
    "barışcıl": "☮️",
    "demirci": "⚒",
    "çığırtkan": "📰", "pregonero": "📰",
    "uyutucu": "💤",
    "şifacı": "🌟",
    "korsan": "🏴‍☠️",
    "gözcü çırağı": "🙇", "apps": "🙇",
    "kahin": "🌀",
    "tilki": "🦊",
    "avcı": "🎯",
    "yaşlı bilge": "👵🏻","yb": "👵🏻",
    "sarhoş": "🍻",
    "mason": "👷", "masontek": "👷",
    "seyirci": "👁", "sgy": "👁","sgv": "👁👳‍♀️",
    "hayalet": "👻",
    "şaşı": "👀", "bizca": "👀",
    "uyurgezer": "😴","ug": "😴",
    "ateist": "👦",
    "oduncu": "🪓",
    "fırıncı": "🥖",
    "beceriksiz": "🤕","bec": "🤕",
    "kütüphaneci": "📚", "bibliotecaria": "📚",
    "kurdumsu": "👱🌚", "wolfman": "👱🌚",
    "eros": "🏹",
    "fool": "🃏", "gof": "🃏&👳‍♀️",
    "köylü": "👱", "kemal": "👱",
    "kapıcı": "🏘",
    "bileyici": "👨🏻‍🦳", "afilador": "👨🏻‍🦳",
    "deli": "🤪",
    "hereje": "🦹‍♂️",
    "yabani çoçuk": "👶", "yç": "👶",
    "hain": "🖕",
    "lanetli": "😾",
    "kurtadam": "🐺", "kürt": "🐺",
    "alfa kurt": "⚡️","alfa kürt": "⚡️",
    "lycan": "🐺🌝",
    "yavru kurt": "🐶","yavru kürt": "🐶",
    "snow wolf": "🐺❄️",
    "kuduz kurt": "🐺🤢",
    "hızlı kurt": "🐺💨", "hızlı kürt": "🐺💨",
    "hungry wolf": "🐺🍖",
    "yaşlı kurt": "🐲",
    "falcı": "🔮",
    "taklitçi": "❌",
    "iblis": "👺",
    "survivor": "⛺️",
    "sk": "🔪", "seri katil": "🔪",
    "kundak": "🔥", "kundakçı": "🔥",
    "çg": "🎭", "çiftgiden": "🎭",
    "unutkan": "🤔",
    "tarikat": "👤", "tarikatçı": "👤",
    "guard": "🛡",
    "twin": "👯",
    "double agent": "👥"
}

game_data = {}

# 1. Metin Mesajı Dinleyici (/startranked@... için)
async def metin_mesaj_takip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message.text: return
    msg_text = update.effective_message.text.lower()
    
    if "startranked@caperubetabot" in msg_text:
        chat_id = update.effective_chat.id
        game_data[chat_id] = {"user_roles": {}, "last_msg_id": None}
        await update.message.reply_text("✅ Yeni oyun başlatıldı, roller temizlendi!", parse_mode="Markdown")

# 2. /temizle Komutu Dinleyici
async def temizle_komut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game_data[chat_id] = {"user_roles": {}, "last_msg_id": None}
    await update.message.reply_text("✅ Roller temizlendi!", parse_mode="Markdown")

async def rol_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    if not context.args:
        await update.message.reply_text("Lütfen bir rol belirtin. Örn: `/rol mason`", parse_mode="Markdown")
        return
    
    rol_input = " ".join(context.args).lower()
    emoji = ROLE_EMOJIS.get(rol_input, "👤")
    
    if chat_id not in game_data:
        game_data[chat_id] = {"user_roles": {}, "last_msg_id": None}
    
    game_data[chat_id]["user_roles"][user_id] = f"👤 {user_name}: {rol_input.capitalize()} {emoji}"
    
    keyboard = [[InlineKeyboardButton("🗑️ Listeyi Temizle", callback_data="temizle_aksiyon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    current_roles = list(game_data[chat_id]["user_roles"].values())
    liste_metni = "📜 **GÜNCEL ROL LİSTESİ**\n\n" + "\n".join(current_roles)

    if game_data[chat_id]["last_msg_id"]:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=game_data[chat_id]["last_msg_id"],
                text=liste_metni,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            await update.message.delete()
        except:
            sent_msg = await update.message.reply_text(liste_metni, reply_markup=reply_markup, parse_mode="Markdown")
            game_data[chat_id]["last_msg_id"] = sent_msg.message_id
    else:
        sent_msg = await update.message.reply_text(liste_metni, reply_markup=reply_markup, parse_mode="Markdown")
        game_data[chat_id]["last_msg_id"] = sent_msg.message_id

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "temizle_aksiyon":
        game_data[query.message.chat_id] = {"user_roles": {}, "last_msg_id": None}
        await query.edit_message_text("✅ Roller temizlendi!")

if __name__ == '__main__':
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Metin filtreleri (Komut olmayan düz mesajları okur)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), metin_mesaj_takip))
    
    # Komut filtreleri
    app.add_handler(CommandHandler("temizle", temizle_komut))
    app.add_handler(CommandHandler("rol", rol_ekle))
    
    # Buton tıklama
    app.add_handler(CallbackQueryHandler(button_handler))
    
    app.run_polling()