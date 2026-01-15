import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from telegram.error import BadRequest

# Veri saklama alanı
game_data = {}

async def yeni_oyun_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg_text = update.effective_message.text.lower() if update.effective_message.text else ""
    
    # Eğer mesajda startranked veya temizle geçiyorsa (komut veya düz metin)
    if "startranked" in msg_text or "temizle" in msg_text:
        chat_id = update.effective_chat.id
        game_data[chat_id] = {"user_roles": {}, "last_msg_id": None}
        await update.message.reply_text("✅ Roller temizlendi, yeni oyun başladı!")

async def roller_listele(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    if chat_id not in game_data or not game_data[chat_id]["user_roles"]:
        await update.message.reply_text("ℹ️ Henüz hiç rol girilmemiş.")
        return

    # Mevcut listeyi hazırla
    current_roles = list(game_data[chat_id]["user_roles"].values())
    liste_metni = "📜 **Mevcut Roller:**\n" + "\n".join(current_roles)
    
    # Temizle butonu ile birlikte gönder
    keyboard = [[InlineKeyboardButton("🗑️ Listeyi Temizle", callback_data="temizle_aksiyon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(liste_metni, reply_markup=reply_markup, parse_mode="Markdown")

async def rol_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name
    
    if not context.args:
        await update.message.reply_text("Lütfen bir rol belirtin. Örn: /rol mason")
        return
    
    rol_adi = " ".join(context.args)
    if chat_id not in game_data:
        game_data[chat_id] = {"user_roles": {}, "last_msg_id": None}
    
    # Kişi başı tek rol kaydı
    game_data[chat_id]["user_roles"][user_id] = f"👤 {user_name}: {rol_adi}"
    
    keyboard = [[InlineKeyboardButton("🗑️ Listeyi Temizle", callback_data="temizle_aksiyon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_roles = list(game_data[chat_id]["user_roles"].values())
    liste_metni = "📜 **Güncel Roller:**\n" + "\n".join(current_roles)

    # Mesaj düzenleme veya yeni mesaj
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
        except Exception:
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
        await query.edit_message_text("✅ Roller temizlendi, yeni oyun başladı!")

if __name__ == '__main__':
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Filtre ile startranked/temizle metinlerini yakala
    app.add_handler(MessageHandler(filters.Regex(r"(?i)startranked|temizle"), yeni_oyun_baslat))
    
    # Komutlar
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CommandHandler("roller", roller_listele)) # Yeni komut
    
    # Buton
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot yayında: /roller komutu eklendi.")
    app.run_polling()