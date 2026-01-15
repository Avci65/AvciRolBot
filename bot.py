import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest

# Rolleri ve son mesaj ID'lerini saklamak için sözlük
game_data = {} # {chat_id: {"roles": [], "last_msg_id": None}}

async def start_ranked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game_data[chat_id] = {"roles": [], "last_msg_id": None}
    await update.message.reply_text("🎮 Ranked oyun başladı! Rolleri girmeye başlayabilirsiniz.")

async def rol_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name
    
    if not context.args:
        await update.message.reply_text("Lütfen bir rol belirtin. Örn: /rol mason")
        return
    
    rol_adi = " ".join(context.args)
    yeni_satir = f"👤 {user_name}: {rol_adi}"
    
    if chat_id not in game_data:
        game_data[chat_id] = {"roles": [], "last_msg_id": None}
    
    # Listeye ekle
    game_data[chat_id]["roles"].append(yeni_satir)
    
    # Buton ve Liste Hazırlığı
    keyboard = [[InlineKeyboardButton("🗑️ Listeyi Temizle", callback_data="temizle_aksiyon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    liste_metni = "📜 **Güncel Roller:**\n" + "\n".join(game_data[chat_id]["roles"])

    # EĞER daha önce bir liste mesajı atılmışsa, onu güncelle
    if game_data[chat_id]["last_msg_id"]:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=game_data[chat_id]["last_msg_id"],
                text=liste_metni,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            # Kullanıcının yazdığı /rol komutunu silerek grubu temiz tutalım (opsiyonel)
            await update.message.delete()
        except BadRequest:
            # Mesaj çok eskiyse veya silinmişse yeni mesaj at
            sent_msg = await update.message.reply_text(liste_metni, reply_markup=reply_markup, parse_mode="Markdown")
            game_data[chat_id]["last_msg_id"] = sent_msg.message_id
    else:
        # İlk kez mesaj atılıyorsa
        sent_msg = await update.message.reply_text(liste_metni, reply_markup=reply_markup, parse_mode="Markdown")
        game_data[chat_id]["last_msg_id"] = sent_msg.message_id

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()
    
    if query.data == "temizle_aksiyon":
        game_data[chat_id] = {"roles": [], "last_msg_id": None}
        await query.edit_message_text("🗑️ Liste temizlendi! Yeni oyun için /startranked yazabilirsiniz.")

if __name__ == '__main__':
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("startranked", start_ranked))
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot güncellendi: Mesaj düzenleme aktif.")
    app.run_polling()