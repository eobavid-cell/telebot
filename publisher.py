import os
import json
import random
import urllib.request
import urllib.error

# 1. سحب المفاتيح السرية وتنظيفها من أي مسافات مخفية
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

# 2. إعدادات القنوات
CHANNELS = {
    "chat": "@Sahran_Chat",
    "booh": "@Booh_Vip",
    "puzzle": "@IQ_Challenge0"
}

# 3. أزرار الشبكة
NETWORK_BUTTONS = {
    "inline_keyboard": [
        [{"text": "🎁 بوت الهدايا والرشق المجاني", "url": "https://t.me/MyGift_Stars_bot"}],
        [
            {"text": "💬 قروب دردشة وسهر", "url": "https://t.me/Sahran_Chat"},
            {"text": "🖤 همسات وبوح", "url": "https://t.me/Booh_Vip"}
        ],
        [
            {"text": "🧠 ألغاز وتحديات", "url": "https://t.me/IQ_Challenge0"},
            {"text": "🦅 حماية المجموعات مجاناً", "url": "https://t.me/shaheen_Pro_bot"}
        ]
    ]
}

# 4. محتوى احتياطي
FALLBACK_CONTENT = {
    "chat": [
        "🔥 **سؤال للنقاش بصراحة:**\nلو خيروك بين السفر لدولة أحلامك بدون مال، أو البقاء في بلدك مع 50 ألف دولار.. ماذا تختار ولماذا؟ 🤔👇",
        "💬 **سؤال للشباب والبنات:**\nما هي الصفة التي إذا رأيتها في شخص تبتعد عنه فوراً مهما كان قريباً منك؟ شاركونا بالتعليقات 👇",
        "⚡ **تحدي الصراحة:**\nاكتب أول حرف من اسم شخص تتمنى رؤيته الآن، واللي بعدك يخمن الاسم! 👇"
    ],
    "booh": [
        "🖤 **همسة المساء:**\n\"ثم يرضيك الله كأنك لم تحزن يوماً، ويعوضك كأنك لم تفقد شيئاً.. فقط ثق بالله.\"\n\n✨ شارك المنشور مع من تحب.",
        "🖤 **بوح:**\n\"بعض الأشخاص مثل الكتب، قد يكون العنوان جذاباً ولكن المحتوى لا يستحق القراءة.. انتقوا علاقاتكم بوعي.\""
    ],
    "puzzle": [
        "🧠 **لغز للأذكياء فقط (90% يخطئون فيه):**\nشيء يمشي بلا رجلين، ويبكي بلا عينين، وإذا لمسته مات.. ما هو؟ 🤔\n\nاكتب إجابتك في قروب الدردشة أو التعليقات!",
        "🕵️‍♂️ **تحدي سرعة البديهة:**\nما هو الرقم الذي إذا ضربته في نفسه، وأضفت إليه 5، أصبح الناتج 30؟"
    ]
}

# متغير لحفظ اسم النموذج المكتشف لعدم تكرار البحث في كل مرة
ACTIVE_MODEL = None

def get_working_model():
    """الاتصال بجوجل لاكتشاف أحدث نموذج فعال ومجاني تلقائياً لتجنب خطأ 404 للأبد"""
    global ACTIVE_MODEL
    if ACTIVE_MODEL:
        return ACTIVE_MODEL
        
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={GEMINI_API_KEY}"
    try:
        req = urllib.request.Request(list_url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            models = data.get('models', [])
            
            # البحث عن نماذج flash الأحدث أولاً لأنها الأسرع والأعلى في الحصة المجانية
            for m in models:
                name = m.get('name', '')
                methods = m.get('supportedGenerationMethods', [])
                if 'generateContent' in methods and 'flash' in name and 'legacy' not in name:
                    ACTIVE_MODEL = name
                    print(f"✅ تم اكتشاف وتفعيل النموذج الذكي تلقائياً: {ACTIVE_MODEL}")
                    return ACTIVE_MODEL
                    
            # إذا لم يجد flash، يختار أي نموذج gemini متاح يدعم توليد النصوص
            for m in models:
                name = m.get('name', '')
                methods = m.get('supportedGenerationMethods', [])
                if 'generateContent' in methods and 'gemini' in name:
                    ACTIVE_MODEL = name
                    print(f"✅ تم اكتشاف وتفعيل النموذج البديل: {ACTIVE_MODEL}")
                    return ACTIVE_MODEL
                    
    except urllib.error.HTTPError as e:
        err_body = e.read().decode('utf-8')
        print(f"❌ فشل جلب قائمة النماذج من جوجل ({e.code}): {err_body}")
    except Exception as e:
        print(f"❌ خطأ أثناء البحث عن النماذج: {e}")
        
    # في حال فشل الجلب التلقائي، نستخدم أحدث إصدار معروف
    return "models/gemini-2.5-flash"

def generate_ai_post(category):
    """توليد منشور جديد تلقائياً عبر Gemini API"""
    if not GEMINI_API_KEY:
        print("⚠️ لم يتم العثور على مفتاح GEMINI_API_KEY في إعدادات GitHub Secrets!")
        return random.choice(FALLBACK_CONTENT[category])
    
    prompts = {
        "chat": "اكتب سؤالاً تفاعلياً قصيراً ومثيراً للجدل والنقاش الاجتماعي ليتم طرحه في مجموعة دردشة عربية على تليجرام بحيث يحفز الجميع على الرد في التعليقات. استخدم الإيموجي ولا تكتب مقدمات.",
        "booh": "اكتب اقتباساً أدبياً عميقاً ومؤثراً جداً من سطرين عن الحياة أو الحنين أو القوة النفسية بأسلوب راقٍ مع إيموجي مناسب بدون مقدمات.",
        "puzzle": "اكتب لغزاً ذكياً وقصيراً وممتعاً يتطلب التفكير، بدون كتابة الجواب، واطلب من القراء كتابة الحل في التعليقات. بدون مقدمات."
    }
    
    model_name = get_working_model()
    # ملاحظة: model_name يأتي جاهزاً بصيغة "models/gemini-..."
    url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={GEMINI_API_KEY}"
    data = {"contents": [{"parts": [{"text": prompts[category]}]}]}
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=15) as response:
            res = json.loads(response.read().decode('utf-8'))
            ai_text = res['candidates'][0]['content']['parts'][0]['text'].strip()
            print(f"🤖 تم توليد النص بالذكاء الاصطناعي لقسم [{category}] بنجاح!")
            return ai_text
    except urllib.error.HTTPError as e:
        err_details = e.read().decode('utf-8')
        print(f"⚠️ خطأ من سيرفر جوجل ({e.code}): {err_details}")
        return random.choice(FALLBACK_CONTENT[category])
    except Exception as e:
        print(f"⚠️ خطأ عام في الذكاء الاصطناعي: {e}")
        return random.choice(FALLBACK_CONTENT[category])

def send_telegram_post(chat_id, text):
    """إرسال المنشور إلى تليجرام"""
    if not BOT_TOKEN:
        print("❌ خطأ: لم يتم العثور على توكن البوت (BOT_TOKEN)!")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text + "\n\n━━━━━━━━━━━━━━\n👇 **تصفح شبكتنا واحصل على هداياك:**",
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
        "reply_markup": NETWORK_BUTTONS
    }
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(payload).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"✅ تم النشر بنجاح في {chat_id}")
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        print(f"❌ خطأ تليجرام في {chat_id}: {error_msg}")
    except Exception as e:
        print(f"❌ خطأ أثناء النشر في {chat_id}: {e}")

if __name__ == "__main__":
    print("🚀 بدء تشغيل سكريبت النشر الآلي...")
    for category, channel_id in CHANNELS.items():
        if channel_id: 
            post_text = generate_ai_post(category)
            send_telegram_post(channel_id, post_text)
    print("🏁 انتهت عملية النشر بنجاح.")
