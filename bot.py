import os
import re
import random
import json
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo



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
    "çiftçi": "👨‍🌾", "barışcıl": "☮️", "demirci": "⚒", "çığırtkan": "📰","Tuğba":"🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🌲","tuğba":"🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🎄🌲🌲",
    "uyutucu": "💤", "şifacı": "🌟", "korsan": "🏴‍☠️", "apps": "🙇", "kahin": "🌀","oduncu1s":"🪓","histerik":"👨‍🎤",
    "tilki": "🦊", "avcı": "🎯", "yb": "👵🏻", "sarhoş": "🍻", "mason": "👷","ışıl":"🪄","avci": "🎯",
    "seyirci": "👁", "hayalet": "👻", "şaşı": "👀", "ug": "😴", "ateist": "👦",
    "oduncu": "🪓", "fırıncı": "🥖", "bec": "🤕", "eros": "🏹", "fool": "🃏",
    "gof": "🃏&👳‍♀️", "kemal": "👱", "kapıcı": "🏘", "deli": "🤪", "hain": "🖕",
    "lanetli": "😾", "kurtadam": "🐺", "kürt": "🐺", "alfa": "⚡️", "lycan": "🐺🌝","gül":"🌹BERKE",
    "yavru": "🐶", "kuduz": "🤢", "hızlı": "💨", "sk": "🔪", "kundak": "🔥","kyura" :"🕊","berke":"❤️❤️‍🔥🥰😍🫦👄💗💕😻",
    "çg": "🎭", "tarikat": "👤", "polis": "👮", "burçin": "👮", "kocakafa": "😏","sgy": "👁","sgv": "👁👳‍♀️",
    "kk": "😏", "kurucu": "🧔🏻‍♂️", "nöbet": "🦉", "hüs": "🕺🏿", "barış": "☮️", "kurdumsu": "👱🌚✨","köylü":"👱","sude":"🏃🏿🪠 🫵🏽🦧 🤱🏻","Alperen":"🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺","alperen":"🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺🇹🇷🐺"
}

# Doğruluk ve Cesaret Soruları (SENİN LİSTELERİN AYNEN DURUYOR)
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
    "Bugüne kadar en çok hangi şeyi itiraf ettin?",
    "Biri seni hiç tanımadan sadece mesajlarına baksa sence nasıl biri derdi?",
    "Hayatında 'keşke hiç yapmasaydım' dediğin bir şey var mı?",
    "Son 1 yılda en çok değiştiğin konu ne?",
    "Kendini en çok hangi konuda kandırdığını düşünüyorsun?",
    "Şu an hayatında en çok eksikliğini hissettiğin şey ne?",
    "Hiç biri seni seviyor sanıp sonra yanıldığın oldu mu?",
    "Birine bilinçsizce çok değer verip sonra pişman oldun mu?",
    "Seni en çok tetikleyen (sinirlendiren) cümle ne?",
    "Bir insanı senden soğutan en hızlı şey nedir?",
    "Bir gün herkes senin hakkında doğruyu öğrenecek olsa en çok hangi şey seni gererdi?",
    "En çok hangi konuda anlaşılmadığını hissediyorsun?",
    "Şu ana kadar aldığın en ağır ders neydi?",
    "Hayatında birini 'gereksiz yere' kaybettin mi?",
    "Kendini en son ne zaman gerçekten gururlandırdın?",
    "Bir şeyleri düzeltmek için geç kaldığını düşündüğün oldu mu?",
    "Bazen sırf sevilmek için rol yaptığın oluyor mu?",
    "Hiç 'ben aslında böyle biri değilim' dediğin bir an yaşadın mı?",
    "Birinin davranışını yanlış anlayıp gereksiz kırıldığın oldu mu?",
    "Seni en çok korkutan ihtimal ne: yalnız kalmak mı, yanlış biriyle kalmak mı?",
    "Kendinle ilgili değiştirmek isteyip de değiştiremediğin şey ne?",

    "Birine mesaj atmak isteyip gururundan atmadığın oldu mu?",
    "Birinin seni unutmasından korktuğun oldu mu?",
    "En son ne zaman 'ben haklıydım' diye içinden sevindin?",
    "En son ne zaman 'ben çok haksızmışım' dedin?",
    "Seni en çok rahatlatan şey ne?",
    "Geceleri en çok düşündüğün konu ne?",
    "Hayatında en çok hangi konuda şanssız olduğunu düşünüyorsun?",
    "Birinin hayatından çıkması sana iyi geldi mi hiç?",
    "Sevmediğin halde sırf yalnız kalmamak için birine katlandığın oldu mu?",
    "Şu an hayatındaki en büyük karmaşa ne?",

    "Bir şarkı seni anlatıyor olsa hangi duyguyu anlatırdı?",
    "Kendini en çok hangi ortamda sahte hissediyorsun?",
    "İnsanların senin hakkında en yanlış bildiği şey ne?",
    "Sence seni seven insanlar, hangi yanını sevse üzülürdün?",
    "Bir şeyleri fazla ciddiye aldığın için kaybettiğin oldu mu?",
    "Hangi konuda affedilmek istersin?",
    "Birini affedemediğin için hala içinde tuttuğun bir şey var mı?",
    "Sence aşk mı daha zor, arkadaşlık mı?",
    "Birini özleyip yine de geri dönmemek zorunda kaldın mı?",
    "Hiç sırf birinin dikkatini çekmek için farklı davrandığın oldu mu?",

    "Sence senin en tehlikeli yönün ne?",
    "Seni en kolay manipüle eden şey ne? (ilgi, sevgi, para, yalnızlık vs.)",
    "Biri sana 'sen değiştin' dese bu seni üzer mi yoksa mutlu mu eder?",
    "Şu an kalbin mi daha dolu, kafan mı?",
    "Biri seni 10 kelimeyle anlatsa, hangi kelimeler olurdu?",
    "Hayatında birine 'hak ettiğinden fazla' değer verdin mi?",
    "Kendini bir kelimeyle tarif etmen gerekse bu ne olurdu?",
    "Dışarıdan güçlü görünsen de içten içe kırıldığın şey ne?",
    "En son ne zaman birine 'gerçekten' güvenmek istedin?",
    "İçten içe keşke hiç tanışmasaydım dediğin biri var mı?",

    "Sence insanlar seni neden yanlış anlıyor?",
    "Kendini en çok ne zaman yalnız hissediyorsun?",
    "Hayatında en çok neye tutunuyorsun?",
    "Kendini toparlamak için gizlice yaptığın şey ne?",
    "Sence senin en güzel yanın hangisi ama kimse fark etmiyor?",
    "Kendini en çok hangi konuda yetersiz hissediyorsun?",
    "Sana göre 'gerçek mutluluk' ne?",
    "Şu an birini seçip hayatından tamamen çıkarabilecek olsan çıkarır mısın?",
    "Hiç 'ben bunu hak etmedim' dediğin bir olay yaşadın mı?",
    "Hiç sırf üzmemek için yalan söyleyip içinde kaldı mı?"
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
    "5 dakika boyunca FADİME'NİN KÖLESİ OL",
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
     "Grupta 1 mesaj yaz ama sadece 2 kelimeden oluşsun ve herkes anlam çıkarmaya çalışsın.",
    "Grupta birine 'bugün sana rol yapacağım' yaz ve 3 mesaj boyunca farklı bir karakter gibi konuş.",
    "Gruba bir 'kural' koy: 10 dakika herkes sadece olumlu cümle kuracak.",
    "Gruba tamamen uydurma bir haber yaz (ciddi dille) ve 1 dakika kimseye söyleme.",
    "Grupta birinin adını kullanmadan onu tarif et: herkes kim olduğunu tahmin etsin.",
    "Gruptaki en eski mesajını hatırlıyormuş gibi bir şey yaz (tamamen uydurabilirsin).",
    "Grupta birine 'Sana 30 saniyelik terapi yapacağım' yazıp kısa moral konuşması yap.",
    "Grupta bir kişiye 'Bugün seninle düşmanız (şaka)' yaz ve 2 mesaj atış.",
    "Bir mesaj yaz: 'Bunu yazmak yasak ama...' ve tamamen gereksiz bir şey söyle.",
    "Grupta kendini 1 günlüğüne farklı bir isimle tanıt (sadece grupta).",

    "Grupta '1 dakikalık sessizlik' ilan et ve kim bozarsa ona görev ver.",
    "Birine, onunla ilgili çok doğru bir tahmin yap (çaktırmadan psikolojik analiz).",
    "Grupta bir kelime seç ve herkes o kelimeyi kullanmadan konuşmaya çalışsın.",
    "Grupta biri hakkında '5 yıl sonra hayatı nasıl olur' diye mini senaryo yaz.",
    "Grupta herkes için 1 tane 'gizli güç' belirle (süper kahraman gibi).",
    "Gruba 1 cümlelik bir 'gerilim filmi giriş sahnesi' yaz.",
    "Kendini bir bilgisayar oyunu NPC'si gibi tanıt ve herkesle öyle konuş.",
    "Grupta birine 'şu an sana görünmez bir hediye veriyorum' yaz ve ne olduğunu hayal ettir.",
    "Gruba bir paragraf yaz ama her kelimenin ilk harfi senin ismini oluştursun (akrostiş).",
    "Birini seç: onun hakkında 3 tane 'yanlış ama komik' gerçek uydur.",

    "Grupta bir mesaj at: 'Ben bu grubun gizli ajanıyım' ve kendine görev uydur.",
    "Grupta birinin yazdığı son mesajı al ve onu 'atasözü' gibi yeniden yaz.",
    "Gruba 3 maddelik 'grup manifestosu' yaz (komik ama ciddi).",
    "Grupta birine 'sana soru sormadan önce izin istiyorum' yaz ve izin bekle.",
    "Birini seç: onun hakkında 1 dakika boyunca sadece olumlu şeyler söyle (spam değil, kaliteli).",
    "Gruba 'ben artık bir yapay zekayım' yaz ve 5 mesaj robot gibi cevap ver.",
    "Grupta biri için 'reklam filmi' yaz: ürün o kişi olsun.",
    "Gruba bir sahne yaz: herkesin rolü olsun (sen yönetmensin).",
    "Grupta birine 'bugün sana hayran kaldım' yaz ama nedenini 10 dakika sonra söyle.",

    "Gruba 'tarihte bugün' diye tamamen uydurma bir olay yaz.",
    "Grupta birini seç ve onun adına 1 cümlelik 'slogan' üret.",
    "Grupta bir mesaj at: 'Benimle konuşan herkes +10 şans alıyor' yaz.",
    "Grupta 5 dakika sadece zıt cevap ver: evete hayır, hayıra evet.",
    "Grupta birine 3 kelimelik gizemli mesaj gönder: 'Kapı. Saat. Sen.'",
    "Gruba bir bilmecenin cevabını yaz ama bilmecenin kendisini yazma.",
    "Grupta birine 'sana sadece 1 kere doğruyu söyleyeceğim' yaz ve gerçekten doğru bir şey söyle.",
    "Gruba kısa bir 'mahkeme' aç: birini komik suçla itham et (örn: fazla cool olmak).",
    "Grupta birine 'Seni suçlu buluyorum' yaz ve suçunu tamamen komik yaz.",
    "Gruptaki en ciddi kişiye saçma ama mantıklı bir soruyla meydan oku.",

    "Gruba 1 satır yaz: 'Bu mesajın altına kim yazarsa şansı açılır' yaz.",
    "Grupta birini seç: onunla ilgili bir 'efsane' yaz (mitoloji gibi).",
    "Grupta 'bugün herkes kendine yeni bir isim seçsin' diye başlat.",
    "Grupta birine 'senden özür dilemek istiyorum' yazıp sonra çok saçma bir şey için özür dile.",
    "Grupta 3 tur boyunca herkesin mesajının sonuna aynı kelimeyi ekle (örn: 'kanka').",
    "Gruba 1 paragraf yaz ama içinde hiç 'a' harfi olmasın.",
    "Grupta 1 kişiyi seç ve onun yerine konuş (o da seni düzeltsin).",
    "Grupta 'gizli görev dağıtıyorum' yaz ve herkese 1 küçük görev ver.",
    "Gruba '2 dakika boyunca sadece komik gerçekler yazıyoruz' yaz ve başlat.",
    "Gruba 1 cümlelik 'korku hikayesi' yaz ama komik bitir.",

    "Grupta birinin son yazdığı kelimeyi alıp 3 farklı anlam uydur.",
    "Grupta birine 'seni terfi ettirdim' yaz ve yeni ünvan ver.",
    "Gruba bir mesaj yaz ama her kelimenin harflerini karıştır (okumaya çalışsınlar).",
    "Grupta herkes için 1 tane 'yasak kelime' koy ve söyleyene ceza.",
    "Grupta birine 'senin hakkında gizli raporum var' yazıp 2 olumlu 1 komik şey yaz.",
    "Gruba bir 'büyü' uydur: kim yazarsa ne olacağını yaz.",
    "Gruba 'bugün sadece efsane insanlar konuşsun' yazıp sonra konuşmaya devam et 😂",
    "Grupta birinin adını al ve onun için 'gezegen özellikleri' yaz: atmosfer, iklim vs.",
    "Grupta birini seç: onunla ilgili 3 tane 'gizli yetenek' tahmini yap.",
    "Grupta bir mesaj at: 'Ben artık bu grubun moderatörüyüm' ve 1 kural koy."
]

# --- Railway ENV ---
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
GROUP_DB_FILE = os.getenv("GROUP_DB_FILE", "groups.json")
USER_CITY_FILE = "user_cities.json"

def load_user_cities():
    try:
        with open(USER_CITY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_user_cities(data):
    with open(USER_CITY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

USER_CITIES = load_user_cities()



def load_groups():
    try:
        with open(GROUP_DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_groups(data):
    with open(GROUP_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_prayer_times(city: str):
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=Turkey&method=13"
        r = requests.get(url, timeout=10)
        data = r.json()

        timings = data["data"]["timings"]
        tz = data["data"]["meta"]["timezone"]  # örn: "Europe/Istanbul"

        return {
            "imsak": timings["Imsak"][:5],
            "iftar": timings["Maghrib"][:5],
            "tz": tz
        }
    except Exception as e:
        print("Vakit API hata:", e)
        return None
    
def is_owner(user_id: int) -> bool:
    return user_id == OWNER_ID

def calculate_remaining(time_str: str, tz_name: str):
    tz = ZoneInfo(tz_name)
    now = datetime.now(tz)

    h, m = map(int, time_str.split(":"))
    target = now.replace(hour=h, minute=m, second=0, microsecond=0)

    if target <= now:
        target += timedelta(days=1)

    diff = target - now
    total_minutes = int(diff.total_seconds() // 60)
    hours = total_minutes // 60
    minutes = total_minutes % 60

    return f"{hours} saat {minutes} dakika"


BOT_GROUPS = load_groups()
game_data = {}
LAST_LIST_MSG = {}



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
async def send_updated_list(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int):
    # Eski liste mesajını sil
    old_id = LAST_LIST_MSG.get(chat_id)
    if old_id:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=old_id)
        except:
            pass  # Silinemeyebilir (yetki / eski msg vs)

    # Yeni listeyi gönder
    new_msg = await update.message.reply_text(get_list_text(chat_id), parse_mode="Markdown")
    LAST_LIST_MSG[chat_id] = new_msg.message_id


# ✅ Webhook temizle
async def post_init(application):
    try:
        await application.bot.delete_webhook(drop_pending_updates=True)
        print("✅ Webhook temizlendi.")
    except Exception as e:
        print("⚠️ Webhook temizlenemedi:", e)


# ✅ Debug
async def debug_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat = update.effective_chat
        user = update.effective_user
        msg = update.effective_message
        txt = msg.text if msg and msg.text else (msg.caption if msg and msg.caption else None)
        if txt:
            print(f"📩 UPDATE | chat={chat.id} type={chat.type} user={user.id} text={txt}")
    except Exception as e:
        print("DEBUG ERROR:", e)


# ✅ /ping
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot aktif çalışıyor!")



async def forcestart_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    chat = update.effective_chat
    msg = update.effective_message

    # ❌ owner değilse tamamen sessiz çık
    if user.id != OWNER_ID:
        return

    # 🧹 komutu sil (yetki varsa)
    try:
        await msg.delete()
    except:
        pass

async def track_bot_membership(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    my_member = update.my_chat_member
    if not chat or not my_member:
        return

    if chat.type not in ("group", "supergroup"):
        return

    new_status = my_member.new_chat_member.status

    if new_status in ("member", "administrator"):
        BOT_GROUPS[str(chat.id)] = {"title": chat.title or "NoTitle", "type": chat.type}
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
            BOT_GROUPS[key] = {"title": chat.title or "NoTitle", "type": chat.type}
            save_groups(BOT_GROUPS)
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

    await send_updated_list(update, context, chat_id)
async def roller_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await send_updated_list(update, context, chat_id)


async def groups_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not user:
        return

    if user.id != OWNER_ID:
        return

    if not BOT_GROUPS:
        await update.message.reply_text("📌 Kayıtlı grup yok.")
        return

    lines = [f"• {info['title']} | ID: `{gid}`" for gid, info in BOT_GROUPS.items()]
    text = "✅ Botun bulunduğu gruplar:\n\n" + "\n".join(lines)
    await send_updated_list(update, context,chat_id)


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
    msg = update.effective_message
    if not msg:
        return

    text = msg.text if msg.text else (msg.caption if msg.caption else "")
    if not text:
        return

    chat_id = update.effective_chat.id
    t = text.strip().lower()

    # ✅ STARTRANKEDİ MESAJDAN YAKALA (komut şart değil)
    # örnekler:
    # startranked
    # /startranked
    # /startranked@caperubetabot
    if t == "startranked" or t.startswith("/startranked"):
        game_data[chat_id] = {}
        await msg.reply_text(
            "✅ Yeni oyun tespit edildi, roller temizlendi!\n"
            "Uyarı⚠️⚠️: KANITLI ROL DEĞİLSEN LİNÇ EDİLEBİLİRSİN İSİME OYNANMIYOR⚠️⚠️ \n" 
            "trip atan /kickme atsın yormasın."\
            ""
        )
        return

    # ✅ DİĞER KOMUTLARI BOŞVER (rol/dc/roller vs)
    # böylece CommandHandler’lar düzgün çalışır
    if t.startswith("/") and not t.startswith("/startranked"):
        return

    # ✅ Yeni format: "Ölü oyuncular: 1/5"
    if "ölü oyuncular:" in t:
        if chat_id not in game_data:
            return

        satirlar = text.splitlines()

        olu_isimleri = []
        for s in satirlar:
            s = s.strip()

            # örn: "💀 Abdullah ⁪⁬⁮⁮⁮⁮ - Sarhoş 🍻"
            if s.startswith("💀"):
                parca = s.replace("💀", "").strip()

                # "-" öncesi isim kısmı
                ad_kismi = parca.split("-")[0].strip()

                # fazla boşlukları düzelt
                ad_kismi = re.sub(r"\s+", " ", ad_kismi)

                # görünmez unicode karakterleri temizle (çok önemli)
                ad_kismi = re.sub(r"[\u200b-\u200f\u202a-\u202e\u2060-\u206f]", "", ad_kismi).strip()

                if ad_kismi:
                    olu_isimleri.append(ad_kismi.lower())

        print("☠️ Ölü tespit:", olu_isimleri)

        degisiklik = False
        for uid, data in game_data[chat_id].items():
            oyuncu_adi = (data.get("name") or "").lower().strip()

            for oluisim in olu_isimleri:
                # esnek eşleştirme
                if oyuncu_adi and (oyuncu_adi in oluisim or oluisim in oyuncu_adi):
                    if data.get("alive", True):
                        game_data[chat_id][uid]["alive"] = False
                        degisiklik = True

        if degisiklik:
            await msg.reply_text(
                "📢 **Caperubeta Güncellemesi:** Ölüler listeye işlendi.\n\n" + get_list_text(chat_id),
                parse_mode="Markdown"
            )



async def temizle_komut(update: Update, context: ContextTypes.DEFAULT_TYPE):
    game_data[update.effective_chat.id] = {}
    await update.message.reply_text("✅ Roller temizlendi!")

async def iftar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if context.args:
        city = context.args[0].lower()
        USER_CITIES[user_id] = city
        save_user_cities(USER_CITIES)
    else:
        city = USER_CITIES.get(user_id)

    if not city:
        await update.message.reply_text("❌ Önce şehir gir.\nÖrnek: /iftar van")
        return

    vakit = get_prayer_times(city)
    if not vakit:
        await update.message.reply_text("❌ Şehir bulunamadı.")
        return

    kalan = calculate_remaining(vakit["iftar"], vakit["tz"])


    text = (
        "🌙 **İftar ve Sahur Vakitleri**\n"
        f"📍 **{city.title()}**\n\n"
        f"🌇 İftar Saati: {vakit['iftar']}\n"
        f"⏳ Kalan Süre: {kalan}"
    )

    await update.message.reply_text(text, parse_mode="Markdown")
async def sahur_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)

    if context.args:
        city = context.args[0].lower()
        USER_CITIES[user_id] = city
        save_user_cities(USER_CITIES)
    else:
        city = USER_CITIES.get(user_id)

    if not city:
        await update.message.reply_text("❌ Önce şehir gir.\nÖrnek: /sahur van")
        return

    vakit = get_prayer_times(city)
    if not vakit:
        await update.message.reply_text("❌ Şehir bulunamadı.")
        return

    kalan = calculate_remaining(vakit["imsak"], vakit["tz"])


    text = (
        f"📍 **{city.title()}**\n\n"
        f"🌅 Sahur (İmsak): {vakit['imsak']}\n"
        f"⏳ Kalan Süre: {kalan}"
    )

    await update.message.reply_text(text, parse_mode="Markdown")



if __name__ == '__main__':
    print("✅ Bot başlatılıyor...")

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN env variable missing!")
    if OWNER_ID == 0:
        raise ValueError("OWNER_ID env variable missing!")

    print("✅ ENV okundu. OWNER_ID:", OWNER_ID)

    app = ApplicationBuilder().token(BOT_TOKEN).post_init(post_init).build()

    # Debug update log
    app.add_handler(MessageHandler(filters.ALL, debug_all), group=-1)

    # Test
    app.add_handler(CommandHandler("ping", ping))

   


    # Grup kayıt
    app.add_handler(ChatMemberHandler(track_bot_membership, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_any_group_message))

    # Owner-only
    app.add_handler(CommandHandler("groups", groups_cmd))

    # Mevcut komutlar
    app.add_handler(CommandHandler(["rol", "r","claim"], rol_ekle))
    app.add_handler(CommandHandler("roller", roller_cmd))
    app.add_handler(CommandHandler("iftar", iftar_cmd)) 
    app.add_handler(CommandHandler("sahur", sahur_cmd))
    app.add_handler(CommandHandler("forcestart", forcestart_cmd))



    app.add_handler(CommandHandler("temizle", temizle_komut))
    app.add_handler(CommandHandler("dc", dc_komut))

    app.add_handler(CallbackQueryHandler(dc_button_handler))

    # ✅ komut olmayan yazılar
    app.add_handler(MessageHandler(filters.TEXT, genel_mesaj_yoneticisi))


    print("✅ Polling başlıyor...")
    app.run_polling(drop_pending_updates=True)
