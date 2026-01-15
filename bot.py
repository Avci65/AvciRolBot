import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

game_roles = {}

async def start_ranked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game_roles[chat_id] = []
    await update.message.reply_text("🎮 Ranked oyun başladı! Rolleri girmeye başlayabilirsiniz.")

async def rol_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not context.args:
        await update.message.reply_text("Lütfen bir rol belirtin. Örn: /rol avcı")
        return
    
    rol = " ".join(context.args)
    if chat_id not in game_roles: game_roles[chat_id] = []
    game_roles[chat_id].append(rol)
    
    # "Temizle" butonu oluşturma
    keyboard = [[InlineKeyboardButton("🗑️ Listeyi Temizle", callback_data="temizle_aksiyon")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    liste_metni = "\n".join([f"- {r}" for r in game_roles[chat_id]])
    await update.message.reply_text(f"✅ Eklendi: {rol}\n\n**Güncel Liste:**\n{liste_metni}", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "temizle_aksiyon":
        game_roles[query.message.chat_id] = []
        await query.edit_message_text("🗑️ Liste temizlendi! Yeni roller ekleyebilirsiniz.")

if __name__ == '__main__':
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("startranked", start_ranked))
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CommandHandler("temizle", start_ranked)) # Manuel komut için
    app.add_handler(CallbackQueryHandler(button_handler)) # Buton tıklamaları için
    
    app.run_polling()