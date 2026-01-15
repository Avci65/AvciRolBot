import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

# Rolleri saklamak için sözlük {chat_id: [liste]}
game_roles = {}

async def start_ranked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    # Yeni oyun başladığında listeyi sıfırla
    game_roles[chat_id] = []
    await update.message.reply_text("🎮 Ranked oyun başladı! Rolleri girmeye başlayabilirsiniz.\nÖrnek: /rol mason")

async def rol_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_name = update.effective_user.first_name  # Mesajı atan kişinin adı
    
    if not context.args:
        await update.message.reply_text("Lütfen bir rol belirtin. Örn: /rol avcı")
        return
    
    rol_adi = " ".join(context.args)
    yeni_satir = f"{user_name}: {rol_adi}" # Örn: Abdullah: Mason
    
    if chat_id not in game_roles:
        game_roles[chat_id] = []
    
    # Listeye ekle
    game_roles[chat_id].append(yeni_satir)
    
    # Buton ekleyelim (Pratik temizlik için)
    keyboard = [[InlineKeyboardButton("🗑️ Listeyi Temizle", callback_data="temizle_aksiyon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Güncel listeyi oluştur
    liste_metni = "\n".join(game_roles[chat_id])
    
    await update.message.reply_text(
        f"✅ Rol kaydedildi.\n\n**Mevcut Roller:**\n{liste_metni}", 
        reply_markup=reply_markup
    )

async def temizle_komutu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game_roles[chat_id] = []
    await update.message.reply_text("🗑️ Tüm roller temizlendi!")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat_id = query.message.chat_id
    await query.answer()
    
    if query.data == "temizle_aksiyon":
        game_roles[chat_id] = []
        await query.edit_message_text("🗑️ Liste temizlendi! Yeni oyun başlatılabilir.")

if __name__ == '__main__':
    # Senin Token'ın
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("startranked", start_ranked))
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CommandHandler("temizle", temizle_komutu))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print("Bot aktif ve isim yazdırma özelliği eklendi...")
    app.run_polling()