import os
import json
import random
import urllib.request

# سحب المفاتيح السرية من إعدادات GitHub بأمان
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# --- 1. إعدادات شبكتك (عدّل المعرفات والروابط هنا مرة واحدة فقط) ---
CHANNELS = {
    "chat": "@Sahran_Chat",      # معرف قروب الدردشة والتعارف
    "booh": "@Booh_Vip",         # معرف قناة البوح والاقتباسات
    "puzzle": "@IQ_Challenge0"   # معرف قناة الألغاز والتحديات
}

# الأزرار الثابتة (الليستة الشبكية) التي ستظهر أسفل كل منشور في كل المجموعات لجلب الناس لبوتاتك
NETWORK_BUTTONS = {
    "inline_keyboard": [
        [
            {"text": "🎁 بوت الهدايا والرشق المجاني", "url": "https://t.me/MyGift_Stars_bot"}
        ],
        [
            {"text": "💬 قروب دردشة وسهر", "url": "https://t.me/Sahran_Chat"},
            {"text": "🖤 همسات وبوح", "url": "https://t.me/Booh_Vip"} # <-- تم تصحيح الرابط هنا
        ],
        [
            {"text": "🧠 ألغاز وتحديات", "url": "https://t.me/IQ_Challenge0"},
            {"text": "🦅 حماية المجموعات مجاناً", "url": "https://t.me/shaheen_Pro_bot"}
        ]
    ]
}

# --- 2. محتوى احتياطي (يعمل تلقائياً إذا لم تضع مفتاح Gemini) ---
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

def generate_ai_post(category):
    """توليد منشور جديد تلقائياً عبر Gemini API المجاني لكي لا يتكرر المحتوى أبداً"""
    if not GEMINI_API_KEY:
        return random.choice(FALLBACK_CONTENT[category])
    
    prompts = {
        "chat": "اكتب سؤالاً تفاعلياً قصيراً ومثيراً للجدل والنقاش الاجتماعي ليتم طرحه في مجموعة دردشة عربية على تليجرام بحيث يحفز الجميع على الرد في التعليقات. استخدم الإيموجي ولا تكتب مقدمات.",
        "booh": "اكتب اقتباساً أدبياً عميقاً ومؤثراً جداً من سطرين عن الحياة أو الحنين أو القوة النفسية بأسلوب راقٍ مع إيموجي مناسب بدون مقدمات.",
        "puzzle": "اكتب لغزاً ذكياً وقصيراً وممتعاً يتطلب التفكير، بدون كتابة الجواب، واطلب من القراء كتابة الحل في التعليقات. بدون مقدمات."
    }
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    data = {"contents": [{"parts": [{"text": prompts[category]}]}]}
    
    try:
        req = urllib.request.Request(
            url, 
            data=json.dumps(data).encode('utf-8'), 
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res['candidates'][0]['content']['parts'][0]['text'].strip()
    except Exception as e:
        print(f"AI Fallback used: {e}")
        return random.choice(FALLBACK_CONTENT[category])

def send_telegram_post(chat_id, text):
    """إرسال المنشور مع الليستة الشبكية (الأزرار) إلى تليجرام"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text + "\n\n━━━━━━━━━━━━━━\n👇 **تصفح شبكتنا واحصل على هداياك:**",
        "parse_mode": "Markdown",
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
    except Exception as e:
        print(f"❌ خطأ أثناء النشر في {chat_id}: {e}")

if __name__ == "__main__":
    for category, channel_id in CHANNELS.items():
        if not channel_id.startswith("@Your"): 
            post_text = generate_ai_post(category)
            send_telegram_post(channel_id, post_text)
