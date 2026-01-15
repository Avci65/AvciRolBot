import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest

# Verileri saklamak için sözlük
# {chat_id: {"user_roles": {user_id: "İsim: Rol"}, "last_msg_id": None}}
game_data = {}

async def start_ranked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # O chat için verileri tamamen sıfırla
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
    
    # Aynı kişi girerse eskisini günceller
    game_data[chat_id]["user_roles"][user_id] = f"👤 {user_name}: {rol_adi}"
    
    # Buton Hazırlığı
    keyboard = [[InlineKeyboardButton("🗑️ Listeyi Temizle", callback_data="temizle_aksiyon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Liste Hazırlığı
    current_roles = list(game_data[chat_id]["user_roles"].values())
    liste_metni = "📜 **Güncel Roller:**\n" + "\n".join(current_roles)

    # Mesajı güncelleme veya yeni mesaj atma
    if game_data[chat_id]["last_msg_id"]:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=game_data[chat_id]["last_msg_id"],
                text=liste_metni,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            # Kullanıcının /rol komutunu sil (Grubun temiz kalması için)
            await update.message.delete()
        except Exception:
            # Mesaj silinmişse veya hata varsa yeni mesaj at
            sent_msg = await update.message.reply_text(liste_metni, reply_markup=reply_markup, parse_mode="Markdown")
            game_data[chat_id]["last_msg_id"] = sent_msg.message_id
    else:
        sent_msg = await update.message.reply_text(liste_metni, reply_markup=reply_markup, parse_mode="Markdown")
        game_data[chat_id]["last_msg_id"] = sent_msg.message_id

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()
    
    if query.data == "temizle_aksiyon":
        game_data[chat_id] = {"user_roles": {}, "last_msg_id": None}
        await query.edit_message_text("✅ Roller temizlendi, yeni oyun başladı!")

if __name__ == '__main__':
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Komutlar
    app.add_handler(CommandHandler("startranked", start_ranked))
    app.add_handler(CommandHandler("temizle", start_ranked)) # Temizle de aynı işlemi yapar
    app.add_handler(CommandHandler("rol", rol_ekle))
    
    # Buton tıklaması
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot güncellendi: StartRanked sıfırlama özelliği eklendi.")
    app.run_polling()