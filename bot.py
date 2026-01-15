import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

# Rol ve Emoji Kütüphanesi
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
    "lycan": "🐺🌝", "yavru kurt": "🐶", "snow wolf": "❄️", "kuduz kurt": "🤢",
    "hızlı kurt": "💨", "hungry wolf": "🍖", "yaşlı kurt": "🐲", "falcı": "🔮",
    "taklitçi": "❌", "iblis": "👺", "survivor": "⛺️", "sk": "🔪", "seri katil": "🔪",
    "kundak": "🔥", "çg": "🎭", "çiftgiden": "🎭", "unutkan": "🤔", "tarikat": "👤",
    "guard": "🛡", "twin": "👯", "double agent": "👥","avci": "🎯",
    "polis": "👮", "burçin": "👮", "kocakafa": "😏", "kk": "😏" ,"kurucu":"🧔🏻‍♂️"
}
game_data = {}

def get_list_text(chat_id):
    if chat_id not in game_data or not game_data[chat_id]:
        return "ℹ️ Henüz hiç rol girilmemiş."
    living, dead = [], []
    for uid, data in game_data[chat_id].items():
        line = f"👤 {data['name']}: {data['role']} {data['emoji']}"
        if data['alive']: living.append(f"❤️ {line}")
        else: dead.append(f"☠️ {line}")
    text = "📜 **GÜNCEL DURUM LİSTESİ**\n\n"
    text += "✨ **YAŞAYANLAR**\n" + ("\n".join(living) if living else "*(Kimse yok)*") + "\n\n"
    text += "⚰️ **ÖLÜLER**\n" + ("\n".join(dead) if dead else "*(Henüz ölen yok)*")
    return text

# CAPERUBETA LİSTE ANALİZCİSİ
async def caperubeta_liste_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message.text: return
    text = update.effective_message.text
    chat_id = update.effective_chat.id

    if "💀 Ölü oyuncular:" in text:
        if chat_id not in game_data: return
        # ○ sembolünden sonraki ismi yakalar
        olu_isimleri = re.findall(r"○\s+([A-Za-z0-9İıĞğÜüŞşÖöÇç]+)", text)
        degisiklik = False
        for uid, data in game_data[chat_id].items():
            if data['name'] in olu_isimleri and data['alive']:
                game_data[chat_id][uid]['alive'] = False
                degisiklik = True
        if degisiklik:
            await update.message.reply_text("📢 **Caperubeta Senkronizasyonu:** Ölüler listeye işlendi.\n\n" + get_list_text(chat_id), parse_mode="Markdown")

# START RANKED TAKİBİ (Fonsiyon olarak)
async def startranked_takip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message.text: return
    if "startranked" in update.effective_message.text.lower():
        chat_id = update.effective_chat.id
        game_data[chat_id] = {} # Verileri sıfırla
        await update.message.reply_text("✅ Yeni oyun tespit edildi, roller temizlendi! \n Abd yeme :D ")

async def rol_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not context.args: return
    full_input = " ".join(context.args).lower()
    first_word = context.args[0].lower()
    emoji = ROLE_EMOJIS.get(first_word, "👤")
    if chat_id not in game_data: game_data[chat_id] = {}
    game_data[chat_id][user.id] = {"name": user.first_name, "role": full_input.capitalize(), "emoji": emoji, "alive": True}
    await update.message.reply_text(get_list_text(chat_id), parse_mode="Markdown")

async def temizle_komut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_data[update.effective_chat.id] = {}
    await update.message.reply_text("✅ Roller temizlendi!")

if __name__ == '__main__':
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CommandHandler("roller", lambda u, c: u.message.reply_text(get_list_text(u.effective_chat.id), parse_mode="Markdown")))
    app.add_handler(CommandHandler("temizle", temizle_komut))
    
    # Caperubeta listesini okuyan handler
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), caperubeta_liste_kontrol))
    
    # startranked takibi (Hem komut hem düz metin)
    app.add_handler(MessageHandler(filters.TEXT, startranked_takip))

    app.run_polling()