import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Rol ve Emoji Eşleşmeleri
ROLE_EMOJIS = {
    "tavcı": "💂", "tarikat avcisi": "💂", "yancı": "💋", "melek": "👼", 
    "koruyucu melek": "👼", "detective": "🕵️","dete": "🕵️", "gözcü": "👳‍♀️",
    "otacı": "🍃", "muhtar": "🎖", "silah": "🔫", "prens": "👑", "prenses": "👑",
    "çiftçi": "👨‍🌾", "barışcıl": "☮️", "demirci": "⚒", "çığırtkan": "📰",
    "uyutucu": "💤", "şifacı": "🌟", "korsan": "🏴‍☠️", "gözcü çırağı": "🙇",
    "apps": "🙇", "kahin": "🌀", "tilki": "🦊", "avcı": "🎯", "yaşlı bilge": "👵🏻",
    "yb": "👵🏻", "sarhoş": "🍻", "mason": "👷", "masontek": "👷", "seyirci": "👁",
    "sgy": "👁","sgv": "👁👳‍♀️", "hayalet": "👻", "şaşı": "👀", "bizca": "👀",
    "uyurgezer": "😴","ug": "😴", "ateist": "👦", "oduncu": "🪓", "fırıncı": "🥖",
    "beceriksiz": "🤕","bec": "🤕", "kütüphaneci": "📚", "eros": "🏹", "fool": "🃏",
    "gof": "🃏&👳‍♀️", "köylü": "👱", "kemal": "👱", "kapıcı": "🏘", "bileyici": "👨🏻‍🦳",
    "deli": "🤪", "hereje": "🦹‍♂️", "yabani çoçuk": "👶", "yç": "👶", "hain": "🖕",
    "lanetli": "😾", "kurtadam": "🐺", "kürt": "🐺", "alfa kurt": "⚡️",
    "lycan": "🐺🌝", "yavru kurt": "🐶", "snow wolf": "🐺❄️", "kuduz kurt": "🐺🤢",
    "hızlı kurt": "🐺💨", "hungry wolf": "🐺🍖", "yaşlı kurt": "🐲", "falcı": "🔮",
    "taklitçi": "❌", "iblis": "👺", "survivor": "⛺️", "sk": "🔪", "seri katil": "🔪",
    "kundak": "🔥", "çg": "🎭", "çiftgiden": "🎭", "unutkan": "🤔", "tarikat": "👤",
    "guard": "🛡", "twin": "👯", "double agent": "👥",
    # Yeni Eklenenler
    "polis": "👮", "burçin": "👮",
    "kocakafa": "😏", "kk": "😏"
}

# Veri yapısı: {chat_id: {user_id: {"name": str, "role": str, "emoji": str, "alive": bool}}}
game_data = {}

def get_list_text(chat_id):
    if chat_id not in game_data or not game_data[chat_id]:
        return "ℹ️ Henüz hiç rol girilmemiş."
    
    living = []
    dead = []
    
    # Kişileri duruma göre listele
    for uid, data in game_data[chat_id].items():
        line = f"👤 {data['name']}: {data['role']} {data['emoji']}"
        if data['alive']:
            living.append(f"❤️ {line}")
        else:
            dead.append(f"☠️ {line}")
    
    text = "📜 **GÜNCEL DURUM LİSTESİ**\n\n"
    text += "✨ **YAŞAYANLAR**\n" + ("\n".join(living) if living else "*(Kimse yok)*") + "\n\n"
    text += "⚰️ **ÖLÜLER**\n" + ("\n".join(dead) if dead else "*(Henüz ölen yok)*")
    return text

async def startranked_takip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message.text: return
    if "startranked" in update.effective_message.text.lower():
        chat_id = update.effective_chat.id
        game_data[chat_id] = {}
        await update.message.reply_text("✅ Yeni oyun başlatıldı, tüm listeler sıfırlandı!")

async def rol_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not context.args:
        await update.message.reply_text("Lütfen bir rol belirtin. Örn: `/rol kk`", parse_mode="Markdown")
        return

    full_input = " ".join(context.args).lower()
    first_word = context.args[0].lower()
    emoji = ROLE_EMOJIS.get(first_word, "👤")
    
    if chat_id not in game_data: game_data[chat_id] = {}
    
    # Yeni eklenen kişi yaşıyor olarak kaydedilir
    game_data[chat_id][user.id] = {
        "name": user.first_name,
        "role": full_input.capitalize(),
        "emoji": emoji,
        "alive": True
    }
    
    await update.message.reply_text(get_list_text(chat_id), parse_mode="Markdown")

async def olu_atala(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Lütfen ölecek kişiyi **yanıtlayarak** (reply) `/ölü` yazın!")
        return
    
    target_user = update.message.reply_to_message.from_user
    if chat_id in game_data and target_user.id in game_data[chat_id]:
        game_data[chat_id][target_user.id]['alive'] = False
        await update.message.reply_text(f"☠️ {target_user.first_name} ölüler listesine taşındı.\n\n" + get_list_text(chat_id), parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Bu kişi sistemde kayıtlı değil!")

async def yasa_atala(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not update.message.reply_to_message: return
    
    target_user = update.message.reply_to_message.from_user
    if chat_id in game_data and target_user.id in game_data[chat_id]:
        game_data[chat_id][target_user.id]['alive'] = True
        await update.message.reply_text(f"❤️ {target_user.first_name} hayata döndü!\n\n" + get_list_text(chat_id), parse_mode="Markdown")

async def roller_listele(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(get_list_text(update.effective_chat.id), parse_mode="Markdown")

async def temizle_komut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game_data[chat_id] = {}
    await update.message.reply_text("✅ Roller temizlendi!")

if __name__ == '__main__':
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CommandHandler("roller", roller_listele))
    app.add_handler(CommandHandler("ölü", olu_atala))
    app.add_handler(CommandHandler("yaşa", yasa_atala))
    app.add_handler(CommandHandler("temizle", temizle_komut))
    app.add_handler(MessageHandler(filters.TEXT, startranked_takip))
    
    app.run_polling()