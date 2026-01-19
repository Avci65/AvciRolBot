import os
import re
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters

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

# Doğruluk ve Cesaret Soruları
D_SORULARI = [
    "En büyük hayalin nedir?",
    "Hiç birinden nefret ettin mi?",
    "En son kime yalan söyledin?",
    "En utanç verici anın nedir?",
    "Grupta en yakışıklı/güzel bulduğun kişi kim?",
    "Hiç bir arkadaşının sevgilisinden hoşlandın mı?",
    "Gelecekteki kendine bir not bırakacak olsan ne yazardın?",
    "En büyük korkunla yüzleşmek zorunda kalsan bu ne olurdu?",
    "Hiç hapse düşme riskin oldu mu?",
    "Gruptan birinin sırrını biliyor musun?",
    "Estetik yaptırmak istesen neren olurdu?",
    "En sevdiğin öğretmenin kimdi?",
    "Hiç kopya çekerken yakalandın mı?",
    "İlk öpücüğün nasıldı?",
    "En garip takıntın nedir?",
    "Kendinde en sevmediğin özellik?",
    "Hiç birine karşılıksız aşık oldun mu?",
    "Gizli kahramanım dediğin biri var mı?",
    "Para için yapmayacağın tek şey nedir?",
    "En son ne için ağladın?",
    "Hayatında yaptığın en büyük hata neydi?",
    "Hiç birinin arkasından konuştun mu?",
    "Birini kıskandığın en son an neydi?",
    "İlk aşkın kimdi?",
    "Şu ana kadar söylediğin en büyük yalan neydi?",
    "Ailenden sakladığın bir şey var mı?",
    "Hiç hırsızlık yaptın mı?",
    "Birine hiç bilerek zarar verdin mi?",
    "Birinin kalbini kırdığın en büyük olay neydi?",
    "En çok pişman olduğun kararın hangisi?",
    "Hayatında değiştirmek istediğin bir şey var mı?",
    "Hiç intikam almak istedin mi?",
    "İnsanların bilmesini istemediğin bir sırrın var mı?",
    "Kendini en çok ne zaman başarısız hissettin?",
    "Seni en çok üzen söz neydi?",
    "En sevdiğin insan kim?",
    "Birine aşık olunca ilk ne yaparsın?",
    "Hiç birini kullanıp sonra bıraktın mı?",
    "En büyük kıskançlığın ne?",
    "En sevmediğin huyun ne?",
    "Daha önce birinin sevgilisini kıskandın mı?",
    "Gizlice takip ettiğin biri var mı?",
    "Sosyal medyada stalk yaptığın kişi kim?",
    "Birinin seni sevdiğini bile bile onu oyaladın mı?",
    "Hiç birini kandırdın mı?",
    "Hangi konuda kendini yetersiz hissediyorsun?",
    "Biri sana hakaret etse en çok neye alınırdın?",
    "Çocukken yaptığın en saçma şey neydi?",
    "Şu anda en çok istediğin şey ne?",
    "Aşk mı para mı?",
    "Hayatında en çok güvendiğin kişi kim?",
    "Hiç birine küfür ettin mi?",
    "En sevdiğin yemek ne?",
    "En sevmediğin yemek ne?",
    "En çok korktuğun şey ne?",
    "En çok utandığın an hangisiydi?",
    "En son kime sinirlendin?",
    "En sevdiğin dizi/film hangisi?",
    "Hayatında biri için yaptığın en çılgın şey neydi?",
    "Hiç birini kıskançlıktan engelledin mi?",
    "İçinden geçen ama söyleyemediğin bir şey var mı?",
    "Bugüne kadar aldığın en pahalı şey ne?",
    "En büyük hayal kırıklığın nedir?",
    "Seni kim en çok ağlattı?",
    "En sevmediğin insan tipi nedir?",
    "En çok hangi konuda yalan söylersin?",
    "Hiç birini bilerek görmezden geldin mi?",
    "En son kimi özledin?",
    "En son kimi kıskandın?",
    "En son kime sitem ettin?",
    "Hiç birini küçümsedin mi?",
    "Kendini en güzel hissettiğin an neydi?",
    "Kendini en kötü hissettiğin an neydi?",
    "Birinin seni sevmediğini hissettiğinde ne yaparsın?",
    "Hiç birinden kaçtığın oldu mu?",
    "Hiç birinin özelini ifşa ettin mi?",
    "Biri seni terk etse ne yaparsın?",
    "En son neye kırıldın?",
    "Sana yapılan en büyük haksızlık neydi?",
    "En çok korktuğun kayıp nedir?",
    "Hayatında vazgeçemediğin şey ne?",
    "En büyük takıntın ne?",
    "Hiç birine aşıkmış gibi yaptın mı?",
    "Hiç birine bilerek umut verdin mi?",
    "En çok kimden nefret ettin?",
    "Şu an kime mesaj atmak isterdin?",
    "Bir günlüğüne görünmez olsan ne yapardın?",
    "En son aldığın hediye neydi?",
    "En çok aldığın iltifat ne?",
    "En çok aldığın eleştiri ne?",
    "Hiç birinin mesajına bilerek geç döndün mü?",
    "Birinin yanında en çok neyden utanırsın?",
    "En son kiminle kavga ettin?",
    "Hiç birine tokat attın mı?",
    "Hayatında seni en çok etkileyen kişi kim?",
    "En büyük gururun nedir?",
    "Kimsenin bilmediği bir yeteneğin var mı?",
    "Hiç birine aşırı bağlandın mı?",
    "Hangi konuda en çok pişmansın?",
    "Birine söylediğin en ağır söz neydi?",
    "Hiç birini kıskançlıktan ağlattın mı?",
    "Birini sevdiğini gizlediğin oldu mu?",
    "Hiç birine aşık olup söylemedin mi?",
    "Hayatında en çok utandığın olay neydi?",
    "Şu an bir dileğin olsa ne dilerdin?",
    "Hiç birini kıskandığın için kötü davrandın mı?",
    "En son kime sinirlenip sessiz kaldın?",
    "En sevmediğin kelime ne?",
    "Hiç kimseye söylemediğin bir hayalin var mı?",
    "Hiç birine yalan dolu bir iltifat yaptın mı?",
    "Hiç flört için yalan söyledin mi?",
    "Birini kendinden soğutmak için ne yaptın?",
    "En son kim sana yalan söyledi?",
    "En büyük kırgınlığın kimedir?",
    "Birini kaybetmekten en çok korktuğun kişi kim?",
    "İçinden geçen en garip düşünce neydi?",
    "Bugüne kadar seni en çok ne sinirlendirdi?",
    "Sana yapılan en büyük iyilik ne?",
    "Senin yaptığın en büyük iyilik ne?",
    "Hiç birine dua ettin mi?",
    "Hiç birine beddua ettin mi?",
    "Birine güvenmek senin için zor mu?",
    "En son kimden özür diledin?",
    "Hiç kimseye itiraf etmediğin bir şey var mı?",
    "En son ne zaman birine yalan söyledin?",
    "En son ne zaman gerçekten mutlu oldun?",
    "En son ne zaman gerçekten üzüldün?",
    "Hiç aşık olduğun birini unutamadın mı?",
    "Hayatında kimden ders aldın?",
    "Şu an hayatında en büyük sorun ne?",
    "Şu an hayatında en büyük mutluluk ne?",
    "En son neye güldün?",
    "En son neye ağladın?",
    "En son neye şaşırdın?",
    "En son neye pişman oldun?",
    "Şu an en çok kime güveniyorsun?",
    "Şu an en çok kimden şüpheleniyorsun?",
    "Şu an en çok kimi seviyorsun?",
    "Şu an en çok kimden nefret ediyorsun?",
    "Hayatındaki en büyük korkun ne?",
    "Hayatındaki en büyük hedefin ne?",
    "Hiç kendinden nefret ettin mi?",
    "Hiç kendini çok sevdin mi?",
    "Seni en çok motive eden şey ne?",
    "Seni en çok korkutan şey ne?",
    "Seni en çok heyecanlandıran şey ne?",
    "Birini sevdiğini nasıl belli edersin?",
    "Birine aşık olduğunda ilk değişen şey ne?",
    "En büyük kıskançlık sebebin ne?",
    "En büyük güvensizlik sebebin ne?",
    "Hayatında en çok hangi şeyi gizledin?",
    "Bugüne kadar en çok hangi şeyi sakladın?",
    "Bugüne kadar en çok hangi şeyi itiraf ettin?"
]

C_SORULARI = [
    "Gruba komik bir selfie at.",
    "Gruptan birine en sevdiğin şarkıyı armağan et.",
    "Bir dakika boyunca burnunla yazı yazmayı dene ve gruba at.",
    "En son aradığın kişiyi ara ve ona 'Seni seviyorum' de (Ses kaydı at).",
    "Gruptaki birinin fotoğrafını 5 dakika profil resmi yap.",
    "Gruba ses kaydı atarak 30 saniye boyunca kahkaha at.",
    "Telefonundaki 3. fotoğrafı gruba gönder.",
    "WhatsApp durumuna 'Çok mutluyum!' yaz ve 5 dakika tut.",
    "Gruptaki birine rastgele bir şiir oku.",
    "Gruptan birine iltifat yağdır.",
    "Gruba bir yemek tarifi ver (ama çok saçma olsun).",
    "Son 5 emoji geçmişini paylaş.",
    "Gözlerin kapalı bir şekilde 'Ben çok zekiyim' yazmaya çalış ve gruba at.",
    "Gruptan birinin ismini 10 kez arka arkaya yaz.",
    "En sevdiğin emojinin taklidini yapıp foto at.",
    "Gruba bir bilmece sor.",
    "Gruptaki en sessiz kişiye bir soru sor.",
    "10 saniye boyunca takla atıyormuş gibi ses çıkar.",
    "Gruptan birine 'Seninle gurur duyuyorum' yaz.",
    "Gruptaki biri için 5 satırlık komik bir rap yaz ve gönder.",
    "Kendi sesinle 10 saniye kedi taklidi yapıp at.",
    "Bir arkadaşına 'Seni özledim' yaz.",
    "Birini arayıp 'Nasılsın kral/kraliçe' de.",
    "10 dakika boyunca sadece emojiyle konuş.",
    "Gruptaki birinin adını değiştirip 3 dakika bekle (sonra geri al).",
    "Gruba çocukluk fotoğrafını at.",
    "Gruba en son çektiğin ekran görüntüsünü at.",
    "Gruptaki birinin sevdiği bir şeyi öğrenip ona mesaj at.",
    "Bir dakika boyunca telefonda tekerleme söyle ve ses kaydı at.",
    "Gruptaki birine komik bir lakap tak ve 5 dakika o lakapla hitap et.",
    "Bir şarkının nakaratını sesli şekilde söyleyip gönder.",
    "Kendi adınla ilgili komik bir hikaye uydur yaz.",
    "Gruptaki birinin yazdığı son mesajı büyük harfle tekrar yaz.",
    "10 saniye boyunca robot gibi konuşup ses kaydı at.",
    "Gruptaki birine rastgele bir motivasyon mesajı at.",
    "Gruba bir tane 'cringe' şaka yaz.",
    "Son attığın fotoğrafı ters çevirip tekrar gönder.",
    "En çok kullandığın uygulamayı söyle.",
    "Telefonda son yazdığın kişiye sadece '.' at.",
    "Gruptaki birine 3 tane iltifat yaz.",
    "Bir dakika boyunca aksanla konuşup ses kaydı gönder.",
    "Evdeki en ilginç eşyayı fotoğrafla ve at.",
    "Kendi adını 10 farklı şekilde yazıp gönder.",
    "Grupta birini seç ve onun hakkında 3 güzel şey yaz.",
    "Birine 'bugün çok havalısın' yaz.",
    "Kendi hakkında komik bir itiraf yap.",
    "Gruptaki birine meydan oku: o da görev yapsın.",
    "En sevdiğin şarkıyı söyle (hangi şarkı olduğunu).",
    "Bir dakika boyunca sadece fısıltıyla ses kaydı at.",
    "Kısa bir aşk şiiri yazıp gönder.",
    "Grupta biriyle 1 dakika tartışıyormuş gibi yap (şaka).",
    "Gruptaki bir kişiye 'senin enerjin güzel' yaz.",
    "Ses kaydıyla 10 saniye ağlıyormuş gibi yap.",
    "Bir kelime seç: herkes o kelimeyle cümle kursun diye başlat.",
    "Gruptaki bir kişiye 1 dakika boyunca sadece kalp emojisi at.",
    "Bir tane saçma atasözü uydur yaz.",
    "Kendi ismini tersten yaz ve gönder.",
    "Telefon klavyeni Türkçe yerine başka dile alıp 1 mesaj yaz.",
    "Gruptaki birine şarkı öner.",
    "Evin içinde en komik yürüyüşünü yapıp video çek (istersen kısa).",
    "Grupta birine “beni sinir etme :D” yaz.",
    "Bir dakika boyunca şive yaparak konuşup ses kaydı at.",
    "Kendi sesinle bir reklam cümlesi uydur ve oku.",
    "Gruptaki birine 10 saniyelik motivasyon konuşması yap.",
    "Yastıkla konuşuyormuş gibi ses kaydı at.",
    "Gruba son dinlediğin şarkının ekran görüntüsünü at.",
    "Grupta birine 'Bana 1 görev ver' yaz.",
    "Kendi hakkında 2 doğru 1 yalan yaz.",
    "Gruptaki herkes için 1 emoji seç ve yaz.",
    "Birine “kanka seni çok seviyorum” yaz.",
    "En sevdiğin çizgi film karakterini söyle.",
    "En sevdiğin küfürsüz hakaret kelimeni yaz :D",
    "Birine 1 dakika boyunca sadece 'hmm' yaz.",
    "Ses kaydıyla 5 saniye horoz taklidi yap.",
    "Evdeki bir objeye isim koy ve fotoğrafını at.",
    "Grupta birine komik bir soru sor.",
    "WhatsApp hakkında kısmına komik bir şey yaz (5 dk dur).",
    "En garip yeteneğini yaz.",
    "Bir arkadaşına “sana bir sır vereceğim” yazıp sonra vazgeç.",
    "Gruptaki birine yanlışlıkla yazmış gibi yapıp “pardon yanlış oldu” yaz.",
    "Kendi ismini 5 farklı font gibi yaz (örnek: A b D u L l A h).",
    "En son attığın emojiyi büyüterek 5 kez gönder.",
    "Bir dakikalık mini stand-up yaz ve gönder.",
    "Sadece capslockla 3 mesaj at.",
    "Bir dakika boyunca sadece soru işaretiyle konuş.",
    "Gruba komik bir anını yaz.",
    "Birine 'Bugün senin günün' yaz.",
    "En yakınındaki kişiye “seni seviyorum” de (sadece sonucu yaz).",
    "Ses kaydıyla 10 saniye spiker gibi konuş.",
    "Gruba en sevdiğin çocukluk oyununun adını yaz.",
    "Telefonundaki en saçma stickerı at.",
    "Grupta biri seç ve onun için 3 kelimelik slogan yaz.",
    "Bir dakika boyunca hızlı hızlı sayıları sayıp ses kaydı at.",
    "Grupta 1 kişiye teşekkür et.",
    "Bir tane komik söz uydur ve paylaş.",
    "Grupta birinin mesajını şiir yap.",
    "Kendi hakkında komik bir lakap yaz.",
    "Bir arkadaşını överek 2 cümle yaz.",
    "Gruba en çok güldüğün emojiyi 10 kez at.",
    "Bir dakika boyunca 'eee' diye konuşup ses kaydı at.",
    "Grupta birini seç: ona 1 tane soru sor.",
    "Bir şarkının sözünü yanlış söyleyerek yaz.",
    "Birine “Sen adamın dibisin” yaz.",
    "Kendi adını şarkı gibi yaz: La la la ...",
    "Bir dakika boyunca İngilizce konuşmaya çalış ve ses kaydı at.",
    "Bir dakika boyunca gülmeden durmaya çalış ve yaz.",
    "Gruptaki herkes için 1 kelimelik duygu yaz.",
    "Telefonun son arama geçmişinin ekran görüntüsünü at (numara kapatabilirsin).",
    "Gruptaki birine “Bugün senden enerji aldım” yaz.",
    "Kendi hakkında komik bir sır paylaş.",
    "Gruba 10 saniyelik dans videosu at (istersen sadece ayaklar).",
    "Grupta birine “Sana güveniyorum” yaz.",
    "Bir dakika boyunca şarkı mırıldanıp ses kaydı at.",
    "Gruptaki biri için 1 tane tatlı beddua uydur :D",
    "Birine 'Selam aşko' yaz (şaka amaçlı).",
    "Bir tane komik tekerleme yaz.",
    "Gruptaki birine sadece “yakışıyor” yaz.",
    "Kendi sesinle 5 saniye bebek gibi konuşup ses kaydı at.",
    "Gruba saçma bir tartışma konusu aç.",
    "Birine “Sen var ya sen...” yazıp 1 dakika beklet sonra tamamla.",
    "Grupta birine 3 tane random emoji at ve anlamını açıklama.",
    "En sevdiğin film karakteri gibi 1 cümle yaz.",
    "Bir arkadaşına “Bugün seni düşündüm” yaz.",
    "Grupta bir kişiye iltifat et ama çok abartılı olsun.",
    "5 saniye boyunca köpek havlaması yapıp ses kaydı at.",
    "Son mesajını tersten yazıp gruba at.",
    "Grupta birine “Senden korkuyorum” yaz (şaka).",
    "Gruba 5 kelimelik bir hikaye yaz.",
    "Birine “Sana bir şey soracağım” yazıp 2 dakika sonra sor.",
    "Kendi sesinle çizgi film karakteri taklidi yap.",
    "Grupta bir kişiye teşekkür mesajı yaz.",
    "Birini seç ve onun için “takım kaptanı sensin” yaz.",
    "Bir dakika boyunca sadece komik surat emojileri at.",
    "Gruba çocukken yaptığın yaramazlığı anlat.",
    "Birine 'Bence sen çok coolsun' yaz.",
    "10 saniye boyunca sessiz kalıp sonra 'tamam' yaz.",
    "Gruba bir tane garip bilgi yaz (fun fact).",
    "Telefonunda en sevdiğin fotoğrafı paylaş.",
    "Kendi hakkında “kimsenin bilmediği şey” yaz.",
    "Grupta biri seç: onun hakkında 1 güzel özellik yaz.",
    "Gruba 3 satır komik şiir yaz.",
    "Bir dakika boyunca şarkı söyler gibi konuşup ses kaydı at.",
    "Grupta birine “Bugün sana çok gıcığım” yaz (şaka).",
    "Birine “Sen iyi ki varsın” yaz.",
    "Son gülme emojini 15 kez at.",
    "Birine 1 tane şarkı sözü gönder.",
    "Birine “Seni düşünüyorum” yaz.",
    "Grupta herkes için 1 iltifat yaz.",
    "Ses kaydıyla 10 saniye “hihihi” gülüşü yap.",
    "Evdeki en saçma eşyayı göster.",
    "Birine “Sana söyleyeceklerim var” yazıp 1 dakika beklet.",
    "Gruba en sevdiğin tatlının adını yaz.",
]

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

async def dc_komut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("😇 Doğruluk", callback_data='dc_d'),
            InlineKeyboardButton("😈 Cesaret", callback_data='dc_c')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Seç bakalım:", reply_markup=reply_markup)

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
    if not update.effective_message or not update.effective_message.text: return
    text, chat_id = update.effective_message.text, update.effective_chat.id
    
    if "startranked" in text.lower():
        game_data[chat_id] = {}
        await update.message.reply_text("✅ Yeni oyun tespit edildi, roller temizlendi!\n Uyarı⚠️⚠️: KANITLI ROL DEĞİLSEN LİNÇ EDİLEBİLİRSİN İSİME OYNANMIYOR⚠️⚠️ ")
        return

    if "💀 Ölü oyuncular:" in text:
        if chat_id not in game_data: return
        satirlar = text.split('\n')
        olu_isimleri = [s.replace('○', '').split('-')[0].strip().split(' ')[0].lower() for s in satirlar if s.strip().startswith('○')]
        degisiklik = False
        for uid, data in game_data[chat_id].items():
            if data['alive'] and data['name'].lower() in olu_isimleri:
                game_data[chat_id][uid]['alive'] = False
                degisiklik = True
        if degisiklik:
            await update.message.reply_text("📢 **Caperubeta Güncellemesi:** Ölüler listeye işlendi.\n\n" + get_list_text(chat_id), parse_mode="Markdown")

async def rol_ekle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not context.args: return
    full_input, first_word = " ".join(context.args).lower(), context.args[0].lower()
    emoji = ROLE_EMOJIS.get(first_word, "👤")
    if chat_id not in game_data: game_data[chat_id] = {}
    game_data[chat_id][user.id] = {"name": user.first_name, "role": full_input.capitalize(), "emoji": emoji, "alive": True}
    await update.message.reply_text(get_list_text(chat_id), parse_mode="Markdown")

async def temizle_komut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_data[update.effective_chat.id] = {}
    await update.message.reply_text("✅ Roller temizlendi!")

if __name__ == '__main__':
    TOKEN = "8285121175:AAF9oSTRMr_XG4Xnk1kSR-UfA42kdy1C-nQ"
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("rol", rol_ekle))
    app.add_handler(CommandHandler("roller", lambda u, c: u.message.reply_text(get_list_text(u.effective_chat.id), parse_mode="Markdown")))
    app.add_handler(CommandHandler("temizle", temizle_komut))
    app.add_handler(CommandHandler("dc", dc_komut))
    
    app.add_handler(CallbackQueryHandler(dc_button_handler))
    app.add_handler(MessageHandler(filters.TEXT, genel_mesaj_yoneticisi))

    app.run_polling()