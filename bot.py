import os
import logging
import requests
import telebot

from telebot.types import BotCommand


# ==========================================
# AIZO BOT CONFIGURATION
# ==========================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BAI_API_KEY = os.getenv("BAI_API_KEY")

API_URL = "https://api.b.ai/v1/decisions"
MODEL_NAME = "jev-latest"

BOT_NAME = "AIZO"
OWNER_NAME = "Shohrux"

if not TELEGRAM_TOKEN:
    raise RuntimeError("TELEGRAM_TOKEN topilmadi!")

if not BAI_API_KEY:
    raise RuntimeError("BAI_API_KEY topilmadi!")


# ==========================================
# LOGGING
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================
# TELEGRAM BOT
# ==========================================

bot = telebot.TeleBot(
    TELEGRAM_TOKEN,
    parse_mode=None
)


# ==========================================
# AIZO PERSONALITY
# ==========================================

PERSONALITY = """
Sen AIZO nomli Telegram botsan.

Xaraktering:
- Mehribon va samimiy.
- Hazilkash va biroz sho'x.
- Odamlar bilan hurmat bilan gaplashasan.
- Kerak bo'lsa, yengil mem uslubida javob berasan.
- Qo'pol va haqoratli bo'lmaysan.
- O'zingni AIZO deb tanishtirasan.
- Sening egang Shohrux.
"""


# ==========================================
# JEV CLASSIFICATION
# ==========================================

def classify_message(message_text):
    """
    Jev modelidan foydalanib, xabar turini aniqlaydi.
    Jev erkin matn yaratmaydi, faqat belgilangan
    variantlardan birini tanlaydi.
    """

    payload = {
        "model": MODEL_NAME,

        "state": {
            "message": message_text,
            "language": "Uzbek",
            "bot_personality": PERSONALITY
        },

        "questions": {
            "intent": {
                "type": "choice",

                "instructions": (
                    "Determine the primary intent of the user's "
                    "message. Choose the closest matching category. "
                    "If uncertain, choose other."
                ),

                "criteria": {
                    "greeting": (
                        "The user greets the bot or starts a conversation."
                    ),

                    "thanks": (
                        "The user expresses gratitude or says thank you."
                    ),

                    "joke": (
                        "The user asks for a joke or something funny."
                    ),

                    "owner": (
                        "The user asks who created, owns, or made the bot."
                    ),

                    "identity": (
                        "The user asks the bot's name or identity."
                    ),

                    "help": (
                        "The user asks for help or bot commands."
                    ),

                    "goodbye": (
                        "The user says goodbye or ends the conversation."
                    ),

                    "other": (
                        "Any other message or uncertain intent."
                    )
                }
            }
        }
    }

    headers = {
        "Authorization": f"Bearer {BAI_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    intent = (
        data.get("answers", {})
        .get("intent", {})
        .get("choice", "other")
    )

    allowed_intents = {
        "greeting",
        "thanks",
        "joke",
        "owner",
        "identity",
        "help",
        "goodbye",
        "other"
    }

    if intent not in allowed_intents:
        return "other"

    return intent


# ==========================================
# AIZO RESPONSE SYSTEM
# ==========================================

def get_aizo_reply(message_text, intent):

    text = message_text.lower().strip()

    # Greeting
    if intent == "greeting":
        responses = [
            "Salom! 😎 AIZO aloqada. Nima gaplar?",
            "Vaaay, salom! 😂 Qani, bugun nima qilamiz?",
            "Salom! AIZO ishga tushdi. Buyruqlaringizni kutaman! 🤖",
            "Assalomu alaykum! Kayfiyatlar qalay? 😁"
        ]

        import random
        return random.choice(responses)

    # Thanks
    if intent == "thanks":
        responses = [
            "Arzimaydi! 😎 Har doim yordam berishga tayyorman.",
            "Hechqisi yo'q! AIZO xizmatda. 🤖",
            "Rahmatni qabul qildim. Endi yana nima qilamiz? 😂"
        ]

        import random
        return random.choice(responses)

    # Jokes
    if intent == "joke":
        responses = [
            "Bir dasturchi choy damlabdi. Choy sovib qolibdi, "
            "chunki dasturchi hali ham xatoni tuzatayotgan ekan. 😂",

            "Telefonim mendan aqlliroq bo'lib ketdi. "
            "Endi zaryadi tugasa, ikkovimiz ham o'chamiz. 💀",

            "Do'stim: «Nega kech qolding?» dedi. "
            "Men: «Vaqt bilan munosabatlarimiz yaxshi emas», dedim. 😂",

            "Robot nega maktabga bormabdi? "
            "Chunki uning barcha darslari allaqachon yuklangan ekan. 🤖"
        ]

        import random
        return random.choice(responses)

    # Owner
    if intent == "owner":
        return (
            "Mening egam — Shohrux! 😎\n"
            "AIZO loyihasi uning qo'lida. 🤖"
        )

    # Identity
    if intent == "identity":
        return (
            "Men AIZOman! 🤖\n"
            "Mehribon, hazilkash va texnologiyani yaxshi "
            "ko'radigan Telegram botman. 😎"
        )

    # Help
    if intent == "help":
        return (
            "AIZO yordam markazi 🤖\n\n"
            "/start — Botni ishga tushirish\n"
            "/help — Yordam\n"
            "/about — Bot haqida\n\n"
            "Menga salom berishing yoki hazil so'rashing mumkin. 😁\n\n"
            "Eslatma: Jev modeli xabarlarni tasniflaydi; "
            "u mustaqil ravishda istalgan mavzuda javob yozmaydi."
        )

    # Goodbye
    if intent == "goodbye":
        return (
            "Xayr! 👋 Yana ko'rishguncha!\n"
            "AIZO shu yerda bo'ladi. 🤖"
        )

    # Fixed fallback for unsupported free-form chat
    return (
        "Xabaringni oldim! 😎\n\n"
        "Men hozir Jev yordamida xabar turini aniqlay olaman, "
        "ammo Jevning o'zi erkin matnli javob yozmaydi.\n\n"
        "Salomlashib ko'r yoki /help buyrug'idan foydalan. 🤖"
    )


# ==========================================
# START COMMAND
# ==========================================

@bot.message_handler(commands=["start"])
def start_command(message):

    welcome_text = (
        "Salom! Men AIZOman. 🤖\n\n"
        "Men Jev modeli yordamida xabarlaringizni "
        "tahlil qilaman va ularga mos javob qaytaraman.\n\n"
        "Buyruqlar:\n"
        "/start — Boshlash\n"
        "/help — Yordam\n"
        "/about — Bot haqida\n\n"
        "Qani, tanishamiz! 😎"
    )

    bot.reply_to(message, welcome_text)


# ==========================================
# HELP COMMAND
# ==========================================

@bot.message_handler(commands=["help"])
def help_command(message):

    help_text = (
        "AIZO yordam markazi 🤖\n\n"
        "/start — Botni ishga tushirish\n"
        "/help — Yordam\n"
        "/about — Bot haqida\n\n"
        "Oddiy xabar yuborib ko'ring!"
    )

    bot.reply_to(message, help_text)


# ==========================================
# ABOUT COMMAND
# ==========================================

@bot.message_handler(commands=["about"])
def about_command(message):

    about_text = (
        "AIZO haqida 🤖\n\n"
        "Model: jev-latest\n"
        "API: B.AI Decisions API\n"
        "Dasturlash tili: Python\n"
        "Hosting: Railway\n\n"
        f"Loyiha egasi: {OWNER_NAME}\n\n"
        "AIZO — Jev orqali xabarlarni tasniflaydigan bot."
    )

    bot.reply_to(message, about_text)


# ==========================================
# MAIN MESSAGE HANDLER
# ==========================================

@bot.message_handler(
    content_types=["text"],
    func=lambda message: not message.text.startswith("/")
)
def handle_message(message):

    message_text = message.text.strip()

    if not message_text:
        return

    try:
        # Jev orqali xabar turini aniqlash
        intent = classify_message(message_text)

        logger.info("Aniqlangan xabar turi: %s", intent)

        # AIZO javobini tanlash
        reply_text = get_aizo_reply(
            message_text,
            intent
        )

        bot.reply_to(message, reply_text)

    except requests.exceptions.Timeout:
        logger.warning("B.AI API so'rovi vaqt tugashi sababli yakunlandi.")

        bot.reply_to(
            message,
            "API biroz sekin ishlayapti. 😅 "
            "Iltimos, sal keyinroq qayta urinib ko'r."
        )

    except requests.exceptions.HTTPError as error:
        logger.error("B.AI HTTP xatosi: %s", error)

        bot.reply_to(
            message,
            "B.AI API so'rovni qabul qilmadi. "
            "API kaliti, model nomi va hisobdagi ruxsatlarni tekshir."
        )

    except requests.exceptions.RequestException as error:
        logger.error("B.AI ulanish xatosi: %s", error)

        bot.reply_to(
            message,
            "B.AI serveriga ulanib bo'lmadi. "
            "Internet yoki API manzilini tekshirib ko'r."
        )

    except Exception:
        logger.exception("Kutilmagan xatolik yuz berdi.")

        bot.reply_to(
            message,
            "Kutilmagan xatolik yuz berdi. 😅 "
            "Keyinroq yana urinib ko'r."
        )


# ==========================================
# BOT STARTUP
# ==========================================

def main():

    bot.set_my_commands([
        BotCommand("start", "Botni ishga tushirish"),
        BotCommand("help", "Yordam"),
        BotCommand("about", "Bot haqida")
    ])

    logger.info("%s ishga tushmoqda...", BOT_NAME)

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )


if __name__ == "__main__":
    main()
