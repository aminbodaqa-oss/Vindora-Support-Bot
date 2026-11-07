
import telebot
from telebot import types

from config import ADMIN_IDS

from database import (
    get_unanswered,
    answer_unanswered,
    ignore_unanswered,
    get_stats,
    get_all_faqs,
    delete_faq
)


# ==========================================
# إعدادات الإدارة
# ==========================================

admin_states = {}


def is_admin(user_id):
    """التحقق من صلاحية الأدمن."""
    return int(user_id) in ADMIN_IDS


def admin_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "الأسئلة المعلقة",
            callback_data="admin_pending"
        ),
        types.InlineKeyboardButton(
            "إحصائيات البوت",
            callback_data="admin_stats"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "الأسئلة الشائعة",
            callback_data="admin_faqs"
        )
    )

    return keyboard


# ==========================================
# تسجيل أوامر الإدارة
# ==========================================

def register_admin(bot):

    @bot.message_handler(commands=["admin"])
    def admin_panel(message):

        if not is_admin(message.from_user.id):
            return

        admin_states.pop(message.from_user.id, None)

        bot.send_message(
            message.chat.id,
            "لوحة إدارة بوت Vindora\n\n"
            "أهلاً بك في لوحة التحكم.\n"
            "اختر القسم المطلوب:",
            reply_markup=admin_keyboard()
        )

    # ======================================
    # عرض الأسئلة المعلقة
    # ======================================

    @bot.message_handler(commands=["unanswered"])
    def unanswered_command(message):

        if not is_admin(message.from_user.id):
            return

        show_pending(message.chat.id, bot)

    def show_pending(chat_id, bot):

        questions = get_unanswered(
            status="pending",
            limit=20
        )

        if not questions:
            bot.send_message(
                chat_id,
                "لا توجد أسئلة معلقة حالياً."
            )
            return

        bot.send_message(
            chat_id,
            f"الأسئلة المعلقة: {len(questions)}"
        )

        for item in questions:

            text = (
                f"رقم السؤال: #{item['id']}\n"
                f"المستخدم: {item['first_name'] if 'first_name' in item.keys() else item['username'] or item['user_id']}\n"
                f"نوع الحساب: {item['audience'] or 'غير محدد'}\n\n"
                f"السؤال:\n{item['question']}"
            )

            keyboard = types.InlineKeyboardMarkup()

            keyboard.row(
                types.InlineKeyboardButton(
                    "إضافة إجابة",
                    callback_data=f"admin_answer_{item['id']}"
                ),
                types.InlineKeyboardButton(
                    "تجاهل",
                    callback_data=f"admin_ignore_{item['id']}"
                )
            )

            bot.send_message(
                chat_id,
                text,
                reply_markup=keyboard
            )

    # ======================================
    # التعامل مع أزرار لوحة الإدارة
    # ======================================

    @bot.callback_query_handler(
        func=lambda call: call.data.startswith("admin_")
    )
    def admin_callbacks(call):

        user_id = call.from_user.id

        if not is_admin(user_id):
            bot.answer_callback_query(
                call.id,
                "غير مسموح لك باستخدام لوحة الإدارة.",
                show_alert=True
            )
            return

        data = call.data

        if data == "admin_pending":

            bot.answer_callback_query(call.id)
            show_pending(call.message.chat.id, bot)

        elif data == "admin_stats":

            bot.answer_callback_query(call.id)

            stats = get_stats()

            text = (
                "إحصائيات بوت Vindora\n\n"
                f"إجمالي المستخدمين: {stats['users']}\n"
                f"العملاء: {stats['customers']}\n"
                f"المسوقين: {stats['marketers']}\n"
                f"الموردين: {stats['suppliers']}\n\n"
                f"الأسئلة المعلقة: {stats['unanswered']}\n"
                f"الأسئلة الشائعة: {stats['faqs']}"
            )

            bot.send_message(
                call.message.chat.id,
                text,
                reply_markup=admin_keyboard()
            )

        elif data == "admin_faqs":

            bot.answer_callback_query(call.id)

            faqs = get_all_faqs()

            if not faqs:
                bot.send_message(
                    call.message.chat.id,
                    "لا توجد أسئلة شائعة حتى الآن."
                )
                return

            bot.send_message(
                call.message.chat.id,
                f"عدد الأسئلة الشائعة: {len(faqs)}"
            )

            for faq in faqs[:30]:

                text = (
                    f"السؤال رقم #{faq['id']}\n\n"
                    f"السؤال:\n{faq['question']}\n\n"
                    f"الإجابة:\n{faq['answer']}"
                )

                keyboard = types.InlineKeyboardMarkup()

                keyboard.add(
                    types.InlineKeyboardButton(
                        "حذف السؤال",
                        callback_data=f"admin_deletefaq_{faq['id']}"
                    )
                )

                bot.send_message(
                    call.message.chat.id,
                    text,
                    reply_markup=keyboard
                )

        elif data.startswith("admin_answer_"):

            question_id = int(data.split("_")[-1])

            admin_states[user_id] = {
                "action": "answer",
                "question_id": question_id
            }

            bot.answer_callback_query(call.id)

            bot.send_message(
                call.message.chat.id,
                f"اكتب الإجابة الخاصة بالسؤال #{question_id}.\n\n"
                "سيتم اعتمادها وإضافتها تلقائياً للأسئلة الشائعة.\n\n"
                "للإلغاء اكتب /cancel"
            )

        elif data.startswith("admin_ignore_"):

            question_id = int(data.split("_")[-1])

            success = ignore_unanswered(question_id)

            bot.answer_callback_query(
                call.id,
                "تم تجاهل السؤال." if success else "تعذر تنفيذ العملية."
            )

            if success:
                try:
                    bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=None
                    )
                except Exception:
                    pass

        elif data.startswith("admin_deletefaq_"):

            faq_id = int(data.split("_")[-1])

            success = delete_faq(faq_id)

            bot.answer_callback_query(
                call.id,
                "تم حذف السؤال." if success else "السؤال غير موجود."
            )

            if success:
                try:
                    bot.edit_message_reply_markup(
                        call.message.chat.id,
                        call.message.message_id,
                        reply_markup=None
                    )
                except Exception:
                    pass

    # ======================================
    # استقبال إجابة الأدمن
    # ======================================

    @bot.message_handler(
        func=lambda message: (
            message.from_user is not None
            and message.from_user.id in admin_states
        ),
        content_types=["text"]
    )
    def receive_admin_answer(message):

        user_id = message.from_user.id

        if not is_admin(user_id):
            admin_states.pop(user_id, None)
            return

        if message.text.strip() == "/cancel":

            admin_states.pop(user_id, None)

            bot.reply_to(
                message,
                "تم إلغاء العملية."
            )
            return

        state = admin_states.get(user_id)

        if not state or state["action"] != "answer":
            return

        answer = message.text.strip()

        if len(answer) < 3:

            bot.reply_to(
                message,
                "الإجابة قصيرة جداً. اكتب إجابة واضحة."
            )
            return

        success = answer_unanswered(
            state["question_id"],
            answer
        )

        admin_states.pop(user_id, None)

        if success:

            bot.reply_to(
                message,
                "تم اعتماد الإجابة بنجاح.\n\n"
                "تمت إضافتها إلى قاعدة الأسئلة الشائعة، "
                "وسيتمكن Gemini من استخدامها في الإجابات القادمة."
            )

        else:

            bot.reply_to(
                message,
                "تعذر اعتماد الإجابة. ربما تم حذف السؤال."
            )

    print("Vindora admin system loaded successfully.")
              
