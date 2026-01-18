import os
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Rol ve Emoji Kütüphanesi
ROLE_EMOJIS = {
    "tavcı": "💂", "yancı": "💋", "melek": "👼", "mafya":"🤵🏽‍♂️", "gözcü": "👳‍♀️",
    "otacı": "🍃", "muhtar": "🎖", "silah": "🔫", "silahşör": "🔫","prens": "👑", "prenses": "👑",
    "çiftçi": "👨‍🌾", "barışcıl": "☮️", "demirci": "⚒", "çığırtkan": "📰","Tuğba":"🌲","tuğba":"🌲",
    "uyutucu": "💤", "şifacı": "🌟", "korsan": "🏴‍☠️", "apps": "🙇", "kahin": "🌀","oduncu1s":"🪓",
    "tilki": "🦊", "avcı": "🎯", "yb": "👵🏻", "sarhoş": "🍻", "mason": "👷","ışıl":"🪄",
    "seyirci": "👁", "hayalet": "👻", "şaşı": "👀", "ug": "😴", "ateist": "👦",
    "oduncu": "🪓", "fırıncı": "🥖", "bec": "🤕", "eros": "🏹", "fool": "🃏",
    "gof": "🃏&👳‍♀️", "kemal": "👱", "kapıcı": "🏘", "deli": "🤪", "hain": "🖕",
    "lanetli": "😾", "kurtadam": "🐺", "kürt": "🐺", "alfa": "⚡️", "lycan": "🐺🌝","gül":"🌹BERKE",
    "yavru": "🐶", "kuduz": "🤢", "hızlı": "💨", "sk": "🔪", "kundak": "🔥","kyura" :"🕊","berke":"❤️❤️‍🔥🥰😍🫦👄💗💕😻",
    "çg": "🎭", "tarikat": "👤", "polis": "👮", "burçin": "👮", "kocakafa": "😏","sgy": "👁","sgv": "👁👳‍♀️",
    "kk": "😏", "kurucu": "🧔🏻‍♂️", "nöbet": "🦉", "hüs": "🕺🏿", "barış": "☮️", "kurdumsu": "👱🌚✨","köylü":"👱"
}

game_data = {}

def get_list_text(chat_id):
    if chat_id not in game_data or not game_data[chat_id]:
        return "ℹ️ Henüz hiç rol girilmemiş."
    living, dead = [], []
    for uid, data in game_data[chat_id].items():
        line = f"👤 {data['name']}: {data['role']} {data['emoji']}"
        if data['alive']: living.append(f"❣️ {line}")
        else: dead.append(f"☠️ {line}")
    text = "📜 **GÜNCEL DURUM LİSTESİ**\n\n"
    text += "✨ **YAŞAYANLAR**\n" + ("\n".join(living) if living else "*(Kimse yok)*") + "\n\n"
    text += "⚰️ **ÖLÜLER**\n" + ("\n".join(dead) if dead else "*(Henüz ölen yok)*")
    return text

# TÜM MESAJLARI VE KOMUTLARI DİNLEYEN ANA FONKSİYON
async def genel_mesaj_yoneticisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return

    text = update.effective_message.text
    chat_id = update.effective_chat.id
    
    # 1. START RANKED KONTROLÜ (Mesajın içinde geçmesi yeterli)
    if "startranked" in text.lower():
        game_data[chat_id] = {}
        await update.message.reply_text("✅ Yeni oyun tespit edildi, roller temizlendi!\n Uyarı⚠️⚠️: KANITLI ROL DEĞİLSEN LİNÇ EDİLEBİLİRSİN İSİME OYNANMIYOR⚠️⚠️ ")
        return # İşlem bittiği için diğer kontrollere geçme

    # 2. CAPERUBETA LİSTE ANALİZİ
    if "💀 Ölü oyuncular:" in text:
        if chat_id not in game_data: return
        satirlar = text.split('\n')
        olu_isimleri = []
        for satir in satirlar:
            if satir.strip().startswith('○'):
                # İsmi ayıkla (Sembolü kaldır, tireden öncesini al, ilk kelimeyi seç)
                isim = satir.replace('○', '').split('-')[0].strip().split(' ')[0]
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
    chat_id = update.effective_chat.id
    game_data[chat_id] = {}
    await update.message.reply_text("✅ Roller temizlendi!")

if __name__ == '__main__':
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Resmi Komutlar
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CommandHandler("roller", lambda u, c: u.message.reply_text(get_list_text(u.effective_chat.id), parse_mode="Markdown")))
    app.add_handler(CommandHandler("temizle", temizle_komut))
    
    # Tüm metin trafiğini (startranked ve Caperubeta listesi dahil) dinleyen tek handler
    app.add_handler(MessageHandler(filters.TEXT, genel_mesaj_yoneticisi))

    app.run_polling()