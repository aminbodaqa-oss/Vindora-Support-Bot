
import logging
import telebot
from telebot import types

from config import BOT_TOKEN

from database import (
    init_db,
    save_user,
    set_user_audience,
    get_user_audience,
    save_unanswered
)

from gemini_engine import (
    ask_vindora,
    clear_session
)

from admin import register_admin


# ==========================================
# إعداد التسجيل والأخطاء
# ==========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("VindoraBot")


# ==========================================
# إعداد البوت
# ==========================================

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing from environment.")

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML",
    threaded=True
)


# ==========================================
# واجهة اختيار نوع المستخدم
# ==========================================

def audience_keyboard():

    keyboard = types.InlineKeyboardMarkup(row_width=1)

    keyboard.add(
        types.InlineKeyboardButton(
            "🛍️ أنا عميل",
            callback_data="audience_customer"
        ),
        types.InlineKeyboardButton(
            "📦 أنا مورد",
            callback_data="audience_supplier"
        ),
        types.InlineKeyboardButton(
            "💼 أنا مسوق",
            callback_data="audience_marketer"
        )
    )

    return keyboard


def main_keyboard():

    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )

    keyboard.row("❓ المساعدة", "🔄 محادثة جديدة")
    keyboard.row("👤 تغيير نوع الحساب")

    return keyboard


# ==========================================
# رسالة البداية
# ==========================================

@bot.message_handler(commands=["start"])
def start(message):

    user = message.from_user

    save_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )

    text = (
        "أهلاً بيك في مساعد Vindora الذكي!\n\n"
        "أنا هنا علشان أساعدك في كل ما يخص المنصة، "
        "سواء كنت عميل أو مورد أو مسوق.\n\n"
        "اختار نوع حسابك علشان أقدر أساعدك بشكل أفضل."
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=audience_keyboard()
    )


# ==========================================
# اختيار نوع الحساب
# ==========================================

@bot.callback_query_handler(
    func=lambda call: call.data.startswith("audience_")
)
def choose_audience(call):

    user_id = call.from_user.id

    audience = call.data.replace(
        "audience_",
        "",
        1
    )

    allowed = [
        "customer",
        "supplier",
        "marketer"
    ]

    if audience not in allowed:
        bot.answer_callback_query(
            call.id,
            "اختيار غير صحيح."
        )
        return

    set_user_audience(
        user_id,
        audience
    )

    audience_names = {
        "customer": "العميل",
        "supplier": "المورد",
        "marketer": "المسوق"
    }

    bot.answer_callback_query(
        call.id,
        "تم حفظ اختيارك."
    )

    try:
        bot.edit_message_text(
            "تم تحديد نوع حسابك: "
            + audience_names[audience]
            + "\n\nتقدر دلوقتي تسألني عن أي حاجة تخص Vindora."
            ,
            call.message.chat.id,
            call.message.message_id
        )
    except Exception:
        pass

    bot.send_message(
        call.message.chat.id,
        "اكتب سؤالك هنا، وأنا هساعدك.",
        reply_markup=main_keyboard()
    )


# ==========================================
# المساعدة
# ==========================================

@bot.message_handler(commands=["help"])
def help_command(message):

    text = (
        "مساعد Vindora الذكي\n\n"
        "تقدر تسألني عن:\n"
        "• التسجيل في المنصة.\n"
        "• نظام التسويق والعمولات.\n"
        "• إضافة المنتجات للموردين.\n"
        "• التسوق وطلب المنتجات.\n"
        "• استخدام المنصة.\n\n"
        "اكتب سؤالك بطريقتك العادية."
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_keyboard()
    )


# ==========================================
# تغيير نوع الحساب
# ==========================================

@bot.message_handler(
    func=lambda message: message.text == "👤 تغيير نوع الحساب"
)
def change_audience(message):

    bot.send_message(
        message.chat.id,
        "اختار نوع الحساب الجديد:",
        reply_markup=audience_keyboard()
    )


# ==========================================
# بدء محادثة جديدة
# ==========================================

@bot.message_handler(
    func=lambda message: message.text == "🔄 محادثة جديدة"
)
def new_conversation(message):

    clear_session(message.from_user.id)

    bot.reply_to(
        message,
        "بدأنا محادثة جديدة.\n"
        "اتفضل اسألني عن أي حاجة تخص Vindora."
    )


# ==========================================
# زر المساعدة
# ==========================================

@bot.message_handler(
    func=lambda message: message.text == "❓ المساعدة"
)
def help_button(message):

    help_command(message)


# ==========================================
# استقبال الأسئلة والرد عليها
# ==========================================

@bot.message_handler(
    content_types=["text"],
    func=lambda message: True
)
def handle_question(message):

    user = message.from_user
    question = (message.text or "").strip()

    if not question:
        return

    # تجاهل الأوامر التي لا تخص هذا المعالج.
    if question.startswith("/"):
        return

    # حفظ المستخدم.
    save_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name
    )

    # معرفة نوع المستخدم.
    audience = get_user_audience(user.id)

    if audience == "unknown":
        bot.send_message(
            message.chat.id,
            "قبل ما نبدأ، اختار نوع حسابك:",
            reply_markup=audience_keyboard()
        )
        return

    # مؤشر انتظار.
    waiting = bot.send_message(
        message.chat.id,
        "ثواني، براجع سؤالك..."
    )

    try:

        answer = ask_vindora(
            user_id=user.id,
            question=question,
            audience=audience
        )

        if answer:

            bot.send_message(
                message.chat.id,
                answer,
                reply_markup=main_keyboard()
            )

        else:

            save_unanswered(
                user_id=user.id,
                username=user.username,
                audience=audience,
                question=question
            )

            bot.send_message(
                message.chat.id,
                "مش متأكد من إجابة سؤالك، ومش هديك معلومة غير مؤكدة.\n\n"
                "سجلت سؤالك علشان فريق Vindora يراجعه "
                "ويضيف الإجابة المعتمدة.\n\n"
                "تقدر تسألني عن موضوع تاني."
            )

    except Exception:

        logger.exception(
            "Error while answering user %s",
            user.id
        )

        bot.send_message(
            message.chat.id,
            "حصل عطل مؤقت أثناء معالجة سؤالك.\n"
            "جرب تاني بعد شوية."
        )

    finally:

        try:
            bot.delete_message(
                message.chat.id,
                waiting.message_id
            )
        except Exception:
            pass


# ==========================================
# تشغيل البوت
# ==========================================

def main():

    logger.info("Initializing Vindora database...")

    init_db()

    logger.info("Registering admin commands...")

    register_admin(bot)

    logger.info("Vindora Support Bot is starting...")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=30
    )


if __name__ == "__main__":

    try:
        main()

    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")

    except Exception:
        logger.exception("Fatal bot error.")
