import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Rol ve Emoji Kütüphanesi
ROLE_EMOJIS = {
    "tavcı": "💂", "yancı": "💋", "melek": "👼", "mafya":"🤵🏽‍♂️", "gözcü": "👳‍♀️",
    "otacı": "🍃", "muhtar": "🎖", "silah": "🔫", "prens": "👑", "prenses": "👑",
    "çiftçi": "👨‍🌾", "barışcıl": "☮️", "demirci": "⚒", "çığırtkan": "📰",
    "uyutucu": "💤", "şifacı": "🌟", "korsan": "🏴‍☠️", "apps": "🙇", "kahin": "🌀",
    "tilki": "🦊", "avcı": "🎯", "yb": "👵🏻", "sarhoş": "🍻", "mason": "👷",
    "seyirci": "👁", "hayalet": "👻", "şaşı": "👀", "ug": "😴", "ateist": "👦",
    "oduncu": "🪓", "fırıncı": "🥖", "bec": "🤕", "eros": "🏹", "fool": "🃏",
    "gof": "🃏&👳‍♀️", "köylü": "👱", "kemal": "👱", "kapıcı": "🏘", "bileyici": "👨🏻‍🦳",
    "deli": "🤪", "hereje": "🦹‍♂️", "yabani çoçuk": "👶", "yç": "👶", "hain": "🖕",
    "lanetli": "😾", "kurtadam": "🐺", "kürt": "🐺", "alfa": "⚡️", "lycan": "🐺🌝",
    "yavru": "🐶", "kuduz": "🤢", "hızlı": "💨", "sk": "🔪", "kundak": "🔥",
    "çg": "🎭", "tarikat": "👤", "polis": "👮", "burçin": "👮", "kk": "😏",
    "kurucu": "🧔🏻‍♂️", "nöbet": "🦉", "hüs": "🕺🏿", "barış": "☮️", "kurdumsu": "👱🌚✨"
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

# CAPERUBETA ANALİZ SİSTEMİ
async def caperubeta_analiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message.text: return
    text = update.effective_message.text
    chat_id = update.effective_chat.id

    if "💀 Ölü oyuncular:" in text:
        if chat_id not in game_data: return
        
        # '○' sembolü ile başlayan isimleri yakala
        # Satırdaki tireden (-) önceki kısmı alır ve temizler
        satirlar = text.split('\n')
        olu_isimleri = []
        for satir in satirlar:
            if satir.strip().startswith('○'):
                # ○ Berke - Polis -> 'Berke' kısmını al
                isim = satir.replace('○', '').split('-')[0].strip()
                # İsmin içinde boşluk varsa sadece ilk kelimeyi (ana ismi) al
                isim = isim.split(' ')[0]
                olu_isimleri.append(isim.lower())

        degisiklik = False
        for uid, data in game_data[chat_id].items():
            if data['alive'] and data['name'].lower() in olu_isimleri:
                game_data[chat_id][uid]['alive'] = False
                degisiklik = True
        
        if degisiklik:
            await update.message.reply_text(
                "📢 **Caperubeta Güncellemesi:** Ölüler listeye işlendi.\n\n" + get_list_text(chat_id),
                parse_mode="Markdown"
            )

async def startranked_takip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message.text: return
    if "startranked" in update.effective_message.text.lower():
        chat_id = update.effective_chat.id
        game_data[chat_id] = {}
        await update.message.reply_text("✅ Yeni oyun! Roller temizlendi.\nAbd yeme :D 🤣😂")

async def rol_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not context.args: return
    
    full_input = " ".join(context.args).lower()
    first_word = context.args[0].lower()
    emoji = ROLE_EMOJIS.get(first_word, "👤")
    
    if chat_id not in game_data: game_data[chat_id] = {}
    
    game_data[chat_id][user.id] = {
        "name": user.first_name, 
        "role": full_input.capitalize(), 
        "emoji": emoji, 
        "alive": True
    }
    await update.message.reply_text(get_list_text(chat_id), parse_mode="Markdown")

if __name__ == '__main__':
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CommandHandler("roller", lambda u, c: u.message.reply_text(get_list_text(u.effective_chat.id), parse_mode="Markdown")))
    app.add_handler(CommandHandler("temizle", lambda u, c: (game_data.update({u.effective_chat.id: {}}), u.message.reply_text("✅ Temizlendi"))))
    
    # Caperubeta'nın ölü listesini tarar
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), caperubeta_analiz))
    # Startranked mesajını tarar
    app.add_handler(MessageHandler(filters.TEXT, startranked_takip))

    app.run_polling()