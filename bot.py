import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters

game_data = {}

async def yeni_oyun_baslat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Mesajın içeriğini kontrol et (küçük harfe çevirerek bakıyoruz)
    msg_text = update.effective_message.text.lower() if update.effective_message.text else ""
    
    # Eğer mesaj /startranked ile başlıyorsa veya içinde bu metin geçiyorsa
    if "startranked" in msg_text or "temizle" in msg_text:
        chat_id = update.effective_chat.id
        game_data[chat_id] = {"user_roles": {}, "last_msg_id": None}
        await update.message.reply_text("✅ Roller temizlendi, yeni oyun başladı!")

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
    
    # Aynı kullanıcı girerse eskisini siler, sadece son rolü tutar
    game_data[chat_id]["user_roles"][user_id] = f"👤 {user_name}: {rol_adi}"
    
    keyboard = [[InlineKeyboardButton("🗑️ Listeyi Temizle", callback_data="temizle_aksiyon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    current_roles = list(game_data[chat_id]["user_roles"].values())
    liste_metni = "📜 **Güncel Roller:**\n" + "\n".join(current_roles)

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
    
    # Mesajları dinleyen handler (Hem komutları hem normal metinleri yakalar)
    app.add_handler(MessageHandler(filters.Regex(r"(?i)startranked|temizle"), yeni_oyun_baslat))
    
    # Rol ekleme komutu
    app.add_handler(CommandHandler("rol", rol_ekle))
    
    # Buton tıklaması
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot yayında: Mesaj okuma modu aktif.")
    app.run_polling()