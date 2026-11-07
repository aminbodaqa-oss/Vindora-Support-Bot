# bot.py
import logging
import telebot
from telebot import types

from config import BOT_TOKEN, ADMIN_IDS
from database import (
    init_db,
    save_user,
    set_user_audience,
    get_user_audience,
    save_unanswered,
)
from answer_engine import find_best_answer
from admin import register_admin


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


if not BOT_TOKEN or BOT_TOKEN == "PUT_YOUR_BOT_TOKEN_HERE":
    raise ValueError(
        "من فضلك ضع توكن البوت في ملف config.py أو متغير BOT_TOKEN."
    )


bot = telebot.TeleBot(BOT_TOKEN, parse_mode=None)


def audience_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        types.InlineKeyboardButton(
            "🛍 أنا عميل",
            callback_data="audience:customer"
        ),
        types.InlineKeyboardButton(
            "📦 أنا مورد",
            callback_data="audience:supplier"
        ),
        types.InlineKeyboardButton(
            "📢 أنا مسوق",
            callback_data="audience:marketer"
        )
    )

    return keyboard


def send_welcome(chat_id, first_name=""):
    name = first_name.strip() if first_name else "صديقنا"

    bot.send_message(
        chat_id,
        f"أهلًا بيك يا {name} في مساعد Vindora.\n\n"
        "أنا هنا علشان أساعدك في معرفة معلومات عن المنصة "
        "والتسجيل والطلبات والتسويق والتعامل مع الموردين.\n\n"
        "اختار القسم المناسب ليك علشان أقدر أجاوبك بدقة:",
        reply_markup=audience_keyboard()
    )


# مهم: تسجيل الإدارة قبل معالج الرسائل العام
register_admin(bot)


# =========================
# أوامر المستخدم
# =========================

@bot.message_handler(commands=["start"])
def start_command(message):
    user = message.from_user

    save_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )

    send_welcome(
        message.chat.id,
        user.first_name or ""
    )


@bot.message_handler(commands=["help"])
def help_command(message):
    bot.send_message(
        message.chat.id,
        "تقدر تسألني عن:\n\n"
        "🛍 حسابات العملاء والطلبات والشحن والاستبدال.\n"
        "📦 التعاون مع الموردين وإضافة المنتجات والمستحقات.\n"
        "📢 التسجيل كمسوق والعمولات وطريقة العمل.\n\n"
        "اكتب سؤالك بشكل طبيعي، وأنا هحاول أوصل لأقرب إجابة."
    )


@bot.message_handler(commands=["category"])
def category_command(message):
    bot.send_message(
        message.chat.id,
        "اختار القسم اللي عايز تسأل عنه:",
        reply_markup=audience_keyboard()
    )


@bot.message_handler(commands=["myid"])
def my_id_command(message):
    bot.reply_to(
        message,
        f"Telegram ID الخاص بيك:\n`{message.from_user.id}`",
        parse_mode="Markdown"
    )


# =========================
# اختيار نوع المستخدم
# =========================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("audience:")
)
def select_audience(call):
    user_id = call.from_user.id
    audience = call.data.split(":")[1]

    if audience not in ("customer", "supplier", "marketer"):
        bot.answer_callback_query(
            call.id,
            "اختيار غير صحيح.",
            show_alert=True
        )
        return

    set_user_audience(user_id, audience)

    names = {
        "customer": "العملاء",
        "supplier": "الموردين",
        "marketer": "المسوقين"
    }

    bot.answer_callback_query(
        call.id,
        "تم اختيار القسم."
    )

    try:
        bot.edit_message_text(
            f"✅ تم اختيار قسم {names[audience]}.\n\n"
            "اكتب سؤالك دلوقتي، وأنا هساعدك.",
            call.message.chat.id,
            call.message.message_id
        )
    except Exception:
        bot.send_message(
            call.message.chat.id,
            f"✅ تم اختيار قسم {names[audience]}.\n\n"
            "اكتب سؤالك دلوقتي، وأنا هساعدك."
        )


# =========================
# استقبال أسئلة المستخدمين
# =========================

@bot.message_handler(
    func=lambda message: (
        bool(message.text)
        and not message.text.startswith("/")
        and message.from_user.id not in ADMIN_IDS
    ),
    content_types=["text"]
)
def receive_question(message):
    user_id = message.from_user.id
    question = message.text.strip()

    if not question:
        return

    audience = get_user_audience(user_id)

    if audience not in ("customer", "supplier", "marketer"):
        bot.send_message(
            message.chat.id,
            "علشان أقدر أجاوبك بشكل صحيح، اختار الأول أنت عميل ولا مورد ولا مسوق:",
            reply_markup=audience_keyboard()
        )
        return

    answer_data = find_best_answer(
        question=question,
        audience=audience
    )

    if answer_data:
        answer = answer_data["answer"]

        bot.send_message(
            message.chat.id,
            answer
        )

        logger.info(
            "Answered user=%s audience=%s faq_id=%s score=%s",
            user_id,
            audience,
            answer_data["id"],
            answer_data.get("match_score")
        )
        return

    # لو مفيش إجابة مناسبة، نسجل السؤال للمراجعة
    save_unanswered(
        user_id=user_id,
        audience=audience,
        question=question
    )

    bot.send_message(
        message.chat.id,
        "وصلني سؤالك، لكن مش لاقي إجابة مؤكدة ليه في قاعدة المعلومات الحالية.\n\n"
        "سجلت السؤال علشان فريق Vindora يراجعه ويضيف إجابته.\n\n"
        "تقدر تسألني عن موضوع تاني، أو تعيد صياغة سؤالك بشكل أوضح."
    )

    logger.info(
        "Unanswered user=%s audience=%s question=%s",
        user_id,
        audience,
        question
    )


# =========================
# تشغيل البوت
# =========================

if __name__ == "__main__":
    init_db()

    logger.info("Vindora Assistant is starting...")

    print("Vindora Assistant is running...")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
  )
