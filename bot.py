import os
import re
import random
import json

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    filters
)

# Rol ve Emoji Kütüphanesi
ROLE_EMOJIS = {
    "tavcı": "💂", "yancı": "💋", "melek": "👼", "mafya":"🤵🏽‍♂️", "gözcü": "👳‍♀️",
    "otacı": "🍃", "muhtar": "🎖", "silah": "🔫", "silahşör": "🔫","prens": "👑", "prenses": "👑",
    "çiftçi": "👨‍🌾", "barışcıl": "☮️", "demirci": "⚒", "çığırtkan": "📰","Tuğba":"🌲","tuğba":"🌲",
    "uyutucu": "💤", "şifacı": "🌟", "korsan": "🏴‍☠️", "apps": "🙇", "kahin": "🌀","oduncu1s":"🪓","histerik":"👨‍🎤",
    "tilki": "🦊", "avcı": "🎯", "yb": "👵🏻", "sarhoş": "🍻", "mason": "👷","ışıl":"🪄","avci": "🎯",
    "seyirci": "👁", "hayalet": "👻", "şaşı": "👀", "ug": "😴", "ateist": "👦",
    "oduncu": "🪓", "fırıncı": "🥖", "bec": "🤕", "eros": "🏹", "fool": "🃏",
    "gof": "🃏&👳‍♀️", "kemal": "👱", "kapıcı": "🏘", "deli": "🤪", "hain": "🖕",
    "lanetli": "😾", "kurtadam": "🐺", "kürt": "🐺", "alfa": "⚡️", "lycan": "🐺🌝","gül":"🌹BERKE",
    "yavru": "🐶", "kuduz": "🤢", "hızlı": "💨", "sk": "🔪", "kundak": "🔥","kyura" :"🕊","berke":"❤️❤️‍🔥🥰😍🫦👄💗💕😻",
    "çg": "🎭", "tarikat": "👤", "polis": "👮", "burçin": "👮", "kocakafa": "😏","sgy": "👁","sgv": "👁👳‍♀️",
    "kk": "😏", "kurucu": "🧔🏻‍♂️", "nöbet": "🦉", "hüs": "🕺🏿", "barış": "☮️", "kurdumsu": "👱🌚✨","köylü":"👱"
}

# Doğruluk ve Cesaret Soruları (SENİN LİSTELERİN AYNEN DURUYOR)
D_SORULARI = [
    "En büyük hayalin nedir?",
    "Hiç birinden nefret ettin mi?",
    # ... (SENİN TÜM SORULAR BURADA AYNEN KALACAK)
]

C_SORULARI = [
    "Gruba komik bir selfie at.",
    # ... (SENİN TÜM GÖREVLER BURADA AYNEN KALACAK)
]

# --- Railway ENV ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
GROUP_DB_FILE = os.getenv("GROUP_DB_FILE", "groups.json")


def load_groups():
    try:
        with open(GROUP_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_groups(data):
    with open(GROUP_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


BOT_GROUPS = load_groups()
game_data = {}


def get_list_text(chat_id):
    if chat_id not in game_data or not game_data[chat_id]:
        return "ℹ️ Henüz hiç rol girilmemiş."
    living, dead = [], []
    for uid, data in game_data[chat_id].items():
        line = f"👤 {data['name']}: {data['role']} {data['emoji']}"
        if data['alive']:
            living.append(f"❣️ {line}")
        else:
            dead.append(f"☠️ {line}")
    text = "📜 **GÜNCEL DURUM LİSTESİ**\n\n"
    text += "✨ **YAŞAYANLAR**\n" + ("\n".join(living) if living else "*(Kimse yok)*") + "\n\n"
    text += "⚰️ **ÖLÜLER**\n" + ("\n".join(dead) if dead else "*(Henüz ölen yok)*")
    return text


# ✅ Webhook temizle (polling update alamama sorunu fix)
async def post_init(application):
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook temizlendi.")
    except Exception as e:
        print("⚠️ Webhook temizlenemedi:", e)


# ✅ Debug: update geliyor mu?
async def debug_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat = update.effective_chat
        user = update.effective_user
        txt = update.effective_message.text if update.effective_message else None
        if txt:
            print(f"📩 UPDATE | chat={chat.id} type={chat.type} user={user.id} text={txt}")
    except Exception as e:
        print("DEBUG ERROR:", e)


# ✅ /ping test komutu
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot aktif çalışıyor!")


async def track_bot_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    my_member = update.my_chat_member
    if not chat or not my_member:
        return

    if chat.type not in ("group", "supergroup"):
        return

    new_status = my_member.new_chat_member.status

    if new_status in ("member", "administrator"):
        BOT_GROUPS[str(chat.id)] = {
            "title": chat.title or "NoTitle",
            "type": chat.type
        }
        save_groups(BOT_GROUPS)

    elif new_status in ("left", "kicked"):
        BOT_GROUPS.pop(str(chat.id), None)
        save_groups(BOT_GROUPS)


async def track_any_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if not chat:
        return

    if chat.type in ("group", "supergroup"):
        key = str(chat.id)
        if key not in BOT_GROUPS:
            BOT_GROUPS[key] = {
                "title": chat.title or "NoTitle",
                "type": chat.type
            }
            save_groups(BOT_GROUPS)


async def groups_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not user:
        return

    if user.id != OWNER_ID:
        return  # gizli

    if not BOT_GROUPS:
        await update.message.reply_text("📌 Kayıtlı grup yok.")
        return

    lines = [f"• {info['title']} | ID: `{gid}`" for gid, info in BOT_GROUPS.items()]
    text = "✅ Botun bulunduğu gruplar:\n\n" + "\n".join(lines)
    await update.message.reply_text(text, parse_mode="Markdown")


async def dc_komut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[
        InlineKeyboardButton("😇 Doğruluk", callback_data='dc_d'),
        InlineKeyboardButton("😈 Cesaret", callback_data='dc_c')
    ]]
    await update.message.reply_text("Seç bakalım:", reply_markup=InlineKeyboardMarkup(keyboard))


async def dc_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'dc_d':
        soru = random.choice(D_SORULARI)
        await query.edit_message_text(f"✨ **Doğruluk:**\n\n{soru}")
    elif query.data == 'dc_c':
        soru = random.choice(C_SORULARI)
        await query.edit_message_text(f"🔥 **Cesaret:**\n\n{soru}")


async def genel_mesaj_yoneticisi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_message or not update.effective_message.text:
        return

    text = update.effective_message.text
    chat_id = update.effective_chat.id

    if "startranked" in text.lower():
        game_data[chat_id] = {}
        await update.message.reply_text(
            "✅ Yeni oyun tespit edildi, roller temizlendi!\n"
            "Uyarı⚠️⚠️: KANITLI ROL DEĞİLSEN LİNÇ EDİLEBİLİRSİN İSİME OYNANMIYOR⚠️⚠️ "
        )
        return

    if "💀 Ölü oyuncular:" in text:
        if chat_id not in game_data:
            return

        satirlar = text.split('\n')
        olu_isimleri = [
            s.replace('○', '').split('-')[0].strip().split(' ')[0].lower()
            for s in satirlar if s.strip().startswith('○')
        ]

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
    if not context.args:
        return

    full_input = " ".join(context.args).lower()
    first_word = context.args[0].lower()
    emoji = ROLE_EMOJIS.get(first_word, "👤")

    if chat_id not in game_data:
        game_data[chat_id] = {}

    game_data[chat_id][user.id] = {
        "name": user.first_name,
        "role": full_input.capitalize(),
        "emoji": emoji,
        "alive": True
    }
    await update.message.reply_text(get_list_text(chat_id), parse_mode="Markdown")


async def temizle_komut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_data[update.effective_chat.id] = {}
    await update.message.reply_text("✅ Roller temizlendi!")


if __name__ == '__main__':
    print("✅ Bot başlatılıyor...")

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN env variable missing!")
    if OWNER_ID == 0:
        raise ValueError("OWNER_ID env variable missing!")

    print("✅ ENV okundu. OWNER_ID:", OWNER_ID)

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # Debug - update geliyor mu (Railway logs)
    app.add_handler(MessageHandler(filters.ALL, debug_all), group=-1)

    # Test
    app.add_handler(CommandHandler("ping", ping))

    # Grup kayıt sistemi
    app.add_handler(ChatMemberHandler(track_bot_membership, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_any_group_message))


    # Owner-only komut
    app.add_handler(CommandHandler("groups", groups_cmd))

    # Senin mevcut handlerların
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CommandHandler("roller", lambda u, c: u.message.reply_text(get_list_text(u.effective_chat.id), parse_mode="Markdown")))
    app.add_handler(CommandHandler("temizle", temizle_komut))
    app.add_handler(CommandHandler("dc", dc_komut))

    app.add_handler(CallbackQueryHandler(dc_button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, genel_mesaj_yoneticisi))


    print("✅ Polling başlıyor...")
    app.run_polling(drop_pending_updates=True)
