# admin.py
import telebot
from telebot import types

from config import ADMIN_IDS
from database import (
    add_faq,
    get_pending_questions,
    close_unanswered,
    get_faqs,
    toggle_faq,
    get_statistics,
)

admin_states = {}


def is_admin(user_id):
    return user_id in ADMIN_IDS


def admin_home_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "➕ إضافة سؤال",
            callback_data="admin:add"
        ),
        types.InlineKeyboardButton(
            "📥 الأسئلة غير المجابة",
            callback_data="admin:pending"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📚 إدارة الأسئلة",
            callback_data="admin:faqs"
        ),
        types.InlineKeyboardButton(
            "📊 الإحصائيات",
            callback_data="admin:stats"
        )
    )

    return keyboard


def audience_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    keyboard.add(
        types.InlineKeyboardButton(
            "🛍 العملاء",
            callback_data="admin:audience:customer"
        ),
        types.InlineKeyboardButton(
            "📦 الموردين",
            callback_data="admin:audience:supplier"
        )
    )

    keyboard.add(
        types.InlineKeyboardButton(
            "📢 المسوقين",
            callback_data="admin:audience:marketer"
        )
    )

    return keyboard


def back_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            "⬅️ لوحة الإدارة",
            callback_data="admin:home"
        )
    )
    return keyboard


def register_admin(bot):

    # =========================
    # أمر لوحة الإدارة
    # =========================

    @bot.message_handler(commands=["admin"])
    def open_admin(message):
        if not is_admin(message.from_user.id):
            return

        admin_states.pop(message.from_user.id, None)

        bot.send_message(
            message.chat.id,
            "⚙️ **لوحة إدارة Vindora Assistant**\n\n"
            "اختار العملية اللي عايز تنفذها:",
            parse_mode="Markdown",
            reply_markup=admin_home_keyboard()
        )

    # =========================
    # إلغاء العملية الحالية
    # =========================

    @bot.message_handler(commands=["cancel"])
    def cancel_admin_action(message):
        user_id = message.from_user.id

        if not is_admin(user_id):
            return

        admin_states.pop(user_id, None)

        bot.send_message(
            message.chat.id,
            "تم إلغاء العملية الحالية.",
            reply_markup=admin_home_keyboard()
        )

    # =========================
    # استقبال رسائل خطوات الإضافة
    # =========================

    @bot.message_handler(
        func=lambda message: (
            is_admin(message.from_user.id)
            and message.from_user.id in admin_states
            and bool(message.text)
            and not message.text.startswith("/")
        ),
        content_types=["text"]
    )
    def handle_admin_state(message):
        user_id = message.from_user.id
        state = admin_states.get(user_id)

        if not state:
            return

        step = state.get("step")
        value = message.text.strip()

        if step == "question":
            if len(value) < 3:
                bot.send_message(
                    message.chat.id,
                    "السؤال قصير جدًا. ابعت السؤال بشكل أوضح."
                )
                return

            state["question"] = value
            state["step"] = "answer"

            bot.send_message(
                message.chat.id,
                "✍️ ابعت إجابة السؤال:"
            )
            return

        if step == "answer":
            if len(value) < 2:
                bot.send_message(
                    message.chat.id,
                    "الإجابة قصيرة جدًا. ابعت إجابة واضحة."
                )
                return

            state["answer"] = value
            state["step"] = "keywords"

            bot.send_message(
                message.chat.id,
                "🔎 ابعت الكلمات المفتاحية أو المرادفات، "
                "وافصل بينهم بفاصلة.\n\n"
                "مثال:\n"
                "العمولة كام، باخد كام، الأرباح\n\n"
                "لو مش محتاج كلمات مفتاحية ابعت: -"
            )
            return

        if step == "keywords":
            keywords = "" if value == "-" else value

            try:
                faq_id = add_faq(
                    audience=state["audience"],
                    question=state["question"],
                    answer=state["answer"],
                    keywords=keywords
                )
            except Exception as error:
                admin_states.pop(user_id, None)

                bot.send_message(
                    message.chat.id,
                    f"حصل خطأ أثناء حفظ السؤال:\n{error}"
                )
                return

            admin_states.pop(user_id, None)

            bot.send_message(
                message.chat.id,
                "✅ تمت إضافة السؤال بنجاح.\n\n"
                f"رقم السؤال: {faq_id}\n"
                f"القسم: {state['audience']}\n"
                f"السؤال: {state['question']}",
                reply_markup=admin_home_keyboard()
            )

    # =========================
    # جميع أزرار الإدارة
    # =========================

    @bot.callback_query_handler(
        func=lambda call: (
            call.data.startswith("admin:")
            or call.data.startswith("faq:")
            or call.data.startswith("pending:")
        )
    )
    def handle_admin_callback(call):
        user_id = call.from_user.id

        if not is_admin(user_id):
            bot.answer_callback_query(
                call.id,
                "غير مسموح لك باستخدام لوحة الإدارة.",
                show_alert=True
            )
            return

        data = call.data

        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass

        # العودة للرئيسية
        if data == "admin:home":
            admin_states.pop(user_id, None)

            bot.edit_message_text(
                "⚙️ **لوحة إدارة Vindora Assistant**\n\n"
                "اختار العملية اللي عايز تنفذها:",
                call.message.chat.id,
                call.message.message_id,
                parse_mode="Markdown",
                reply_markup=admin_home_keyboard()
            )
            return

        # بدء إضافة سؤال
        if data == "admin:add":
            admin_states[user_id] = {
                "step": "audience"
            }

            bot.send_message(
                call.message.chat.id,
                "اختار القسم اللي هتضيف فيه السؤال:",
                reply_markup=audience_keyboard()
            )
            return

        # اختيار قسم السؤال الجديد
        if data.startswith("admin:audience:"):
            audience = data.split(":")[2]

            if audience not in ("customer", "supplier", "marketer"):
                return

            admin_states[user_id] = {
                "step": "question",
                "audience": audience
            }

            bot.send_message(
                call.message.chat.id,
                "✍️ ابعت السؤال الجديد:"
            )
            return

        # الأسئلة غير المجابة
        if data == "admin:pending":
            pending = get_pending_questions(limit=10)

            if not pending:
                bot.send_message(
                    call.message.chat.id,
                    "✅ مفيش أسئلة معلقة للمراجعة.",
                    reply_markup=back_keyboard()
                )
                return

            for item in pending:
                keyboard = types.InlineKeyboardMarkup(row_width=2)

                keyboard.add(
                    types.InlineKeyboardButton(
                        "✔️ تمت المراجعة",
                        callback_data=f"pending:done:{item['id']}"
                    ),
                    types.InlineKeyboardButton(
                        "🗑 تجاهل",
                        callback_data=f"pending:ignore:{item['id']}"
                    )
                )

                bot.send_message(
                    call.message.chat.id,
                    f"🆔 السؤال رقم: {item['id']}\n"
                    f"👤 القسم: {item['audience']}\n"
                    f"💬 السؤال:\n{item['question']}\n"
                    f"📅 التاريخ: {item['created_at']}",
                    reply_markup=keyboard
                )

            bot.send_message(
                call.message.chat.id,
                "انتهى عرض الأسئلة المعلقة.",
                reply_markup=back_keyboard()
            )
            return

        # إغلاق سؤال غير مجاب
        if data.startswith("pending:done:"):
            question_id = int(data.split(":")[2])
            close_unanswered(question_id, "reviewed")

            bot.edit_message_text(
                "✅ تم وضع السؤال كمُراجع.",
                call.message.chat.id,
                call.message.message_id
            )
            return

        # تجاهل سؤال غير مجاب
        if data.startswith("pending:ignore:"):
            question_id = int(data.split(":")[2])
            close_unanswered(question_id, "ignored")

            bot.edit_message_text(
                "🗑 تم تجاهل السؤال.",
                call.message.chat.id,
                call.message.message_id
            )
            return

        # عرض الأسئلة
        if data == "admin:faqs":
            faqs = get_faqs(active_only=False)

            if not faqs:
                bot.send_message(
                    call.message.chat.id,
                    "لا توجد أسئلة في قاعدة البيانات.",
                    reply_markup=back_keyboard()
                )
                return

            for faq in faqs[:20]:
                status = "🟢 مفعل" if faq["active"] else "🔴 معطل"

                keyboard = types.InlineKeyboardMarkup()
                keyboard.add(
                    types.InlineKeyboardButton(
                        "تفعيل / تعطيل",
                        callback_data=f"faq:toggle:{faq['id']}"
                    )
                )

                bot.send_message(
                    call.message.chat.id,
                    f"رقم: {faq['id']}\n"
                    f"القسم: {faq['audience']}\n"
                    f"الحالة: {status}\n\n"
                    f"السؤال:\n{faq['question']}\n\n"
                    f"الإجابة:\n{faq['answer'][:700]}",
                    reply_markup=keyboard
                )

            bot.send_message(
                call.message.chat.id,
                "دي أول 20 نتيجة من الأسئلة المسجلة.",
                reply_markup=back_keyboard()
            )
            return

        # تفعيل أو تعطيل سؤال
        if data.startswith("faq:toggle:"):
            faq_id = int(data.split(":")[2])
            new_status = toggle_faq(faq_id)

            if new_status is None:
                bot.send_message(
                    call.message.chat.id,
                    "السؤال ده مش موجود."
                )
                return

            status_text = "تم تفعيل السؤال." if new_status else "تم تعطيل السؤال."

            bot.edit_message_text(
                f"✅ {status_text}",
                call.message.chat.id,
                call.message.message_id
            )
            return

        # الإحصائيات
        if data == "admin:stats":
            stats = get_statistics()
            audiences = stats["audiences"]

            text = (
                "📊 **إحصائيات البوت**\n\n"
                f"👥 إجمالي المستخدمين: {stats['users']}\n"
                f"📚 الأسئلة المفعلة: {stats['faqs']}\n"
                f"❓ الأسئلة غير المجابة المعلقة: {stats['pending']}\n"
                f"📝 إجمالي الأسئلة غير المجابة: {stats['total_questions']}\n\n"
                "توزيع المستخدمين:\n"
                f"🛍 العملاء: {audiences.get('customer', 0)}\n"
                f"📦 الموردين: {audiences.get('supplier', 0)}\n"
                f"📢 المسوقين: {audiences.get('marketer', 0)}"
            )

            bot.send_message(
                call.message.chat.id,
                text,
                parse_mode="Markdown",
                reply_markup=back_keyboard()
            )
            return
