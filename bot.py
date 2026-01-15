import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest

# Verileri saklamak için sözlük
# Yapı: {chat_id: {"user_roles": {user_id: "İsim: Rol"}, "last_msg_id": None}}
game_data = {}

async def start_ranked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game_data[chat_id] = {"user_roles": {}, "last_msg_id": None}
    await update.message.reply_text("🎮 Ranked oyun başladı! Herkes tek bir rol girebilir.")

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
    
    # Kullanıcının ID'sini anahtar yaparak rolü kaydediyoruz. 
    # Aynı kişi tekrar yazarsa bu satır eskisinin üzerine yazar (update eder).
    game_data[chat_id]["user_roles"][user_id] = f"👤 {user_name}: {rol_adi}"
    
    # Buton ve Liste Hazırlığı
    keyboard = [[InlineKeyboardButton("🗑️ Listeyi Temizle", callback_data="temizle_aksiyon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Sözlükteki tüm değerleri birleştirip listeyi oluşturuyoruz
    current_roles = list(game_data[chat_id]["user_roles"].values())
    liste_metni = "📜 **Güncel Roller:**\n" + "\n".join(current_roles)

    # Mesajı güncelleme veya yeni mesaj atma mantığı
    if game_data[chat_id]["last_msg_id"]:
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=game_data[chat_id]["last_msg_id"],
                text=liste_metni,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            # Grubun temiz kalması için kullanıcının yazdığı komutu siliyoruz
            await update.message.delete()
        except Exception:
            # Eğer mesaj silindiyse veya düzenlenemiyorsa yenisini at
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
        await query.edit_message_text("🗑️ Liste temizlendi! Yeni oyun için roller girilebilir.")

if __name__ == '__main__':
    # Token'ını buraya tırnak içine yapıştır
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("startranked", start_ranked))
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot aktif: Kişi başı tek rol sistemi devrede.")
    app.run_polling()