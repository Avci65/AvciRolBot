import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Rolleri saklamak için sözlük
game_roles = {}

async def start_ranked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game_roles[chat_id] = []
    await update.message.reply_text("🎮 Ranked oyun başladı! Rolleri girmeye başlayabilirsiniz.\nÖrnek: /rol mason")

async def rol_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    
    # Komutun yanında rol yazılıp yazılmadığını kontrol et
    if not context.args:
        await update.message.reply_text("Lütfen bir rol belirtin. Örn: /rol avcı")
        return
    
    rol = " ".join(context.args)
    
    if chat_id not in game_roles:
        game_roles[chat_id] = []
    
    game_roles[chat_id].append(rol)
    
    # Listeyi kullanıcıya göster
    liste_metni = "\n".join([f"- {r}" for r in game_roles[chat_id]])
    await update.message.reply_text(f"✅ Rol eklendi: {rol}\n\n**Mevcut Roller:**\n{liste_metni}")

async def temizle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    game_roles[chat_id] = []
    await update.message.reply_text("🗑️ Tüm roller temizlendi. Yeni oyun için hazır!")

if __name__ == '__main__':
    # Token'ı doğrudan buraya yazıyoruz (Railway Variables kısmında hata almamak için en kesin yol)
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    
    # Uygulamayı başlat
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Komutları kaydet
    app.add_handler(CommandHandler("startranked", start_ranked))
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CommandHandler("temizle", temizle))
    
    print("Bot çalışıyor...")
    app.run_polling()