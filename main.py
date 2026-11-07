# main.py
import logging
import time

import telebot
from telebot import types
from dotenv import load_dotenv

load_dotenv()

from config import BOT_TOKEN, ADMIN_IDS
from database import (
    init_db,
    save_user,
    set_user_audience,
    get_user_audience,
    save_unanswered,
)
from gemini_engine import ask_vindora, clear_session
from admin import register_admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN غير مضبوط. أضفه في متغيرات البيئة أو ملف .env.")

bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


def audience_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        types.InlineKeyboardButton("🛍 أنا عميل", callback_data="audience:customer"),
        types.InlineKeyboardButton("📦 أنا مورد", callback_data="audience:supplier"),
        types.InlineKeyboardButton("📢 أنا مسوق", callback_data="audience:marketer"),
    )
    return keyboard


def send_welcome(chat_id, first_name=""):
    name = first_name.strip() if first_name else "صديقنا"
    bot.send_message(
        chat_id,
        f"أهلًا بيك يا {name} في مساعد Vindora الذكي.\n\n"
        "تقدر تسألني بطريقتك العادية عن التسجيل والطلبات والتسويق والتعامل مع الموردين.\n\n"
        "اختار القسم المناسب ليك:",
        reply_markup=audience_keyboard()
    )


def send_long_message(chat_id, text, reply_to_message_id=None):
    # Telegram message limit is 4096 characters.
    text = text or ""
    chunks = [text[i:i + 4000] for i in range(0, len(text), 4000)] or [""]
    for index, chunk in enumerate(chunks):
        bot.send_message(
            chat_id,
            chunk,
            reply_to_message_id=reply_to_message_id if index == 0 else None
        )


# تسجيل لوحة الإدارة قبل معالجات المستخدمين.
register_admin(bot)


@bot.message_handler(commands=["start"])
def start_command(message):
    user = message.from_user
    save_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )
    clear_session(user.id)
    send_welcome(message.chat.id, user.first_name or "")


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "اسألني عن خدمات Vindora حسب نوع حسابك:\n"
        "🛍 العملاء والطلبات.\n"
        "📦 الموردين والمنتجات.\n"
        "📢 المسوقين والتسجيل والعمولات.\n\n"
        "الأوامر:\n/category تغيير القسم\n/reset بدء محادثة جديدة"
    )


@bot.message_handler(commands=["category"])
def category_command(message):
    bot.send_message(
        message.chat.id,
        "اختار القسم اللي عايز تسأل عنه:",
        reply_markup=audience_keyboard()
    )


@bot.message_handler(commands=["reset"])
def reset_command(message):
    clear_session(message.from_user.id)
    bot.send_message(message.chat.id, "بدأنا محادثة جديدة. اسألني عن Vindora.")


@bot.message_handler(commands=["myid"])
def my_id_command(message):
    bot.reply_to(message, f"Telegram ID الخاص بيك:\n{message.from_user.id}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("audience:"))
def select_audience(call):
    user_id = call.from_user.id
    audience = call.data.split(":", 1)[1]

    if audience not in ("customer", "supplier", "marketer"):
        bot.answer_callback_query(call.id, "اختيار غير صحيح.", show_alert=True)
        return

    set_user_audience(user_id, audience)
    clear_session(user_id)

    names = {
        "customer": "العملاء",
        "supplier": "الموردين",
        "marketer": "المسوقين",
    }
    bot.answer_callback_query(call.id, "تم اختيار القسم.")
    confirmation = (
        f"✅ تم اختيار قسم {names[audience]}.\n\n"
        "اكتب سؤالك دلوقتي، وهحاول أساعدك."
    )
    try:
        bot.edit_message_text(
            confirmation,
            call.message.chat.id,
            call.message.message_id
        )
    except Exception:
        bot.send_message(call.message.chat.id, confirmation)


@bot.message_handler(
    func=lambda message: bool(message.text) and not message.text.startswith("/"),
    content_types=["text"]
)
def receive_question(message):
    user_id = message.from_user.id
    question = message.text.strip()
    if not question:
        return

    # حفظ المستخدم حتى لو كان أدمن ويختبر البوت.
    save_user(
        user_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name
    )

    audience = get_user_audience(user_id)
    if audience not in ("customer", "supplier", "marketer"):
        bot.send_message(
            message.chat.id,
            "علشان أجاوبك بدقة، اختار الأول أنت عميل ولا مورد ولا مسوق:",
            reply_markup=audience_keyboard()
        )
        return

    try:
        bot.send_chat_action(message.chat.id, "typing")
        answer = ask_vindora(
            question=question,
            audience=audience,
            user_id=user_id
        )

        if answer:
            send_long_message(message.chat.id, answer, message.message_id)
            logger.info(
                "Gemini answered user=%s audience=%s",
                user_id, audience
            )
            return

        save_unanswered(
            user_id=user_id,
            audience=audience,
            question=question
        )
        bot.send_message(
            message.chat.id,
            "مش معايا معلومة مؤكدة أجاوبك بيها دلوقتي، ومش هخمن عليك.\n\n"
            "سجلت سؤالك علشان فريق Vindora يراجعه. "
            "ولو استفسارك متعلق بطلب أو حساب، تقدر تتواصل مع الدعم."
        )

    except Exception:
        logger.exception("Gemini request failed for user=%s", user_id)
        bot.send_message(
            message.chat.id,
            "حصل عطل مؤقت وأنا بحاول أجهز الإجابة. جرّب تاني بعد شوية.\n"
            "لو المشكلة مستمرة، تواصل مع دعم Vindora."
        )


if __name__ == "__main__":
    init_db()
    logger.info("Vindora Gemini Assistant is starting...")
    print("Vindora Gemini Assistant is running...")
    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )
