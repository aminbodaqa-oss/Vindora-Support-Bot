# database.py
import sqlite3
from datetime import datetime
from config import DATABASE_NAME


FAQ_DATA = [

    # =========================
    # CUSTOMER - العملاء (16)
    # =========================

    (
        "customer",
        "إزاي أقدر أعمل حساب على Vindora؟",
        "تقدر تعمل حساب جديد بسهولة عن طريق إدخال بياناتك الأساسية، زي البريد الإلكتروني ورقم الهاتف وكلمة المرور، وبعدها تقدر تستخدم حسابك للتسوق.",
        "انشاء حساب، تسجيل، حساب جديد، اعمل اكونت، اسجل ازاي"
    ),
    (
        "customer",
        "هل لازم أعمل حساب عشان أطلب منتج؟",
        "إنشاء حساب بيساعدك تتابع طلباتك وتدير بياناتك بسهولة، وتقدر تعرف تفاصيل حسابك وطلباتك من خلال المنصة.",
        "لازم اسجل، الطلب بدون حساب، اشتري من غير حساب، هل التسجيل اجباري"
    ),
    (
        "customer",
        "نسيت كلمة المرور، أعمل إيه؟",
        "استخدم خيار نسيت كلمة المرور في صفحة تسجيل الدخول، واتبع الخطوات الموضحة لاستعادة حسابك.",
        "نسيت الباسورد، استرجاع كلمة السر، اعادة تعيين كلمة المرور، مش فاكر كلمة المرور"
    ),
    (
        "customer",
        "هل أقدر أعدل بيانات حسابي؟",
        "تقدر تراجع بيانات حسابك وتحدّث المعلومات المتاحة من خلال إعدادات الحساب.",
        "تعديل الحساب، تغيير البيانات، تحديث بياناتي، اغير رقم الهاتف"
    ),

    (
        "customer",
        "إزاي أطلب منتج من Vindora؟",
        "اختار المنتج اللي عايزه، وادخل على صفحة تفاصيله، وبعدها اضغط على أضف للسلة واتبع خطوات إتمام الطلب.",
        "اطلب ازاي، طريقة الطلب، اشتري منتج، اضيف للسلة، اعمل اوردر"
    ),
    (
        "customer",
        "إزاي أعرف تفاصيل المنتج؟",
        "كل منتج بيكون ليه صفحة خاصة بتعرض الصور والتفاصيل والسعر والمعلومات المتاحة عنه قبل ما تطلب.",
        "مواصفات المنتج، تفاصيل السلعة، سعر المنتج، صور المنتج"
    ),
    (
        "customer",
        "هل أقدر أطلب أكتر من منتج؟",
        "تقدر تضيف المنتجات المتاحة للسلة وتراجع محتوياتها قبل إتمام الطلب.",
        "اكتر من منتج، منتجات متعددة، اضيف منتجات للسلة، اطلب حاجات كتير"
    ),
    (
        "customer",
        "إزاي أتابع طلبي؟",
        "تقدر تتابع حالة طلبك من خلال حسابك على Vindora، حسب التحديثات المتاحة للطلب.",
        "متابعة الاوردر، حالة الطلب، طلبي وصل لفين، تتبع الطلب"
    ),

    (
        "customer",
        "إيه طرق الدفع المتاحة؟",
        "طرق الدفع المتاحة بتظهرلك أثناء إتمام الطلب، وبتختلف حسب الخيارات المتوفرة على المنصة.",
        "الدفع ازاي، طرق السداد، كاش، دفع اونلاين، ادفع ازاي"
    ),
    (
        "customer",
        "هل فيه مصاريف شحن؟",
        "تكلفة الشحن بتتحدد حسب عنوان التوصيل والمنتج، وبتظهرلك تفاصيلها قبل تأكيد الطلب.",
        "سعر الشحن، مصاريف التوصيل، الشحن بكام، التوصيل مجاني"
    ),
    (
        "customer",
        "الطلب بيوصل خلال قد إيه؟",
        "مدة التوصيل بتختلف حسب المنطقة وتوافر المنتج وشركة الشحن، وبيتم توضيح التفاصيل المتاحة أثناء الطلب.",
        "مدة التوصيل، الشحن بياخد وقت قد ايه، امتى الطلب يوصل، ميعاد الاستلام"
    ),
    (
        "customer",
        "هل أقدر أغير عنوان التوصيل؟",
        "لو محتاج تغيّر عنوان التوصيل، تواصل مع الدعم في أسرع وقت، وهنساعدك حسب حالة الطلب.",
        "تغيير العنوان، تعديل عنوان الشحن، غيرت مكاني، عنوان التوصيل غلط"
    ),

    (
        "customer",
        "هل أقدر أستبدل أو أرجع المنتج؟",
        "سياسة الاستبدال والاسترجاع بتختلف حسب حالة المنتج وشروط البائع. تواصل مع الدعم لمعرفة الإجراءات المناسبة لطلبك.",
        "استرجاع، استبدال، ارجع المنتج، عايز ابدل، سياسة المرتجعات"
    ),
    (
        "customer",
        "وصلني منتج فيه مشكلة، أعمل إيه؟",
        "تواصل مع فريق الدعم ووضّح المشكلة، ويفضل إرفاق صور للمنتج عشان نقدر نساعدك بشكل أفضل.",
        "المنتج تالف، المنتج بايظ، فيه عيب، مشكلة في المنتج، وصلني غلط"
    ),
    (
        "customer",
        "إزاي أتواصل مع خدمة العملاء؟",
        "تقدر تتواصل مع فريق الدعم من خلال صفحة تواصل مع الدعم الموجودة في Vindora.",
        "خدمة العملاء، رقم الدعم، اكلم الدعم، التواصل مع الشركة"
    ),
    (
        "customer",
        "إزاي أقدم شكوى أو استفسار؟",
        "تقدر تبعت استفسارك أو شكواك لفريق الدعم، وهيتم مراجعتها ومساعدتك في أقرب وقت ممكن.",
        "تقديم شكوى، عندي شكوى، استفسار، ابلغ عن مشكلة"
    ),

    # =========================
    # SUPPLIER - الموردين (11)
    # =========================

    (
        "supplier",
        "إيه هي Vindora؟",
        "Vindora منصة للتسويق الإلكتروني بتعمل على ربط الموردين بالمسوقين والعملاء، وبتوفر بيئة لتنظيم عرض المنتجات والتعاون على تسويقها وفقًا لنظام المنصة.",
        "ما هي فيندورا، تعريف فيندورا، المنصة بتعمل ايه، طبيعة عمل vindora"
    ),
    (
        "supplier",
        "إزاي أبدأ كمورد؟",
        "ابدأ بالتواصل مع فريق Vindora من خلال قناة التواصل الرسمية، وقدّم بياناتك وبيانات منتجاتك، وبعدها راجع شروط التعاون والإجراءات المطلوبة قبل اعتمادها.",
        "التسجيل كمورد، انضم كمورد، ابيع منتجاتي، اضافة مورد، ابدأ التعاون"
    ),
    (
        "supplier",
        "إيه المنتجات اللي أقدر أضيفها؟",
        "المنتجات المناسبة هي المنتجات التي يمكن اعتمادها وفقًا لسياسات Vindora ومتطلبات الجودة والبيانات والتسعير. الأفضل تقديم وصف واضح وصور دقيقة وتفاصيل الكميات المتاحة لكل منتج.",
        "المنتجات المسموحة، اضيف ايه، انواع المنتجات، شروط قبول المنتجات"
    ),
    (
        "supplier",
        "هل لازم أوفّر صور وتفاصيل للمنتجات؟",
        "نعم، تجهيز صور واضحة ووصف صحيح وسعر محدث وبيانات دقيقة يساعد على عرض المنتج بصورة أفضل، ويساعد المسوق على تقديم معلومات صحيحة للعملاء.",
        "صور المنتجات، وصف المنتج، بيانات المنتج، تفاصيل واسعار المنتجات"
    ),
    (
        "supplier",
        "مين المسؤول عن الشحن والتوصيل؟",
        "مسؤولية الشحن وطريقة استلام المنتجات وتسليمها بتتحدد حسب اتفاق التعاون وإجراءات تنفيذ الطلبات المعتمدة مع Vindora. لازم تتأكد من التفاصيل قبل بدء استقبال الطلبات.",
        "الشحن على مين، مين بيوصل، التوصيل مسؤولية مين، شركة الشحن"
    ),
    (
        "supplier",
        "إمتى هستلم مستحقاتي المالية؟",
        "مواعيد صرف المستحقات وطريقة احتسابها بتعتمد على الاتفاق والسياسة المالية المعتمدة. راجع المواعيد وشروط التسوية مع فريق Vindora قبل تفعيل التعاون.",
        "ميعاد الفلوس، استلام المستحقات، تحويل المستحقات، فلوسي هتوصل امتى"
    ),
    (
        "supplier",
        "هل فيه عمولة على المنتجات؟",
        "أي عمولة أو تكلفة تخص المنصة أو المسوق لازم تكون واضحة ومتفق عليها قبل اعتماد المنتج. اسأل الفريق عن طريقة الحساب والقيمة التي تخص كل منتج أو اتفاق.",
        "عمولة المورد، نسبة المنصة، تكلفة التسويق، عمولة المسوق، خصم من السعر"
    ),
    (
        "supplier",
        "أعمل إيه لو المنتج خلص من المخزون؟",
        "حدّث حالة التوافر في النظام أو أبلغ الفريق بالطريقة المعتمدة في Vindora بأسرع وقت، حتى لا يستمر عرض المنتج على أنه متاح وهو غير متوفر.",
        "نفذ المخزون، المنتج خلص، الكمية خلصت، تحديث المخزون، غير متوفر"
    ),
    (
        "supplier",
        "مين بيتعامل مع المرتجعات والمنتجات المعيبة؟",
        "الإجراءات والمسؤوليات الخاصة بالمرتجعات والمنتجات المعيبة لازم تكون موضحة في اتفاق التعاون وسياسة المرتجعات المعتمدة، بما يشمل طريقة الإبلاغ والفحص والتسوية عند الحاجة.",
        "المرتجعات، منتج معيوب، المنتج التالف، مين يتحمل المرتجع"
    ),
    (
        "supplier",
        "هل أقدر أغيّر سعر المنتج أو بياناته؟",
        "تقدر تطلب تحديث السعر أو البيانات من خلال الآلية المعتمدة. تأكد من اعتماد التغييرات وتحديثها قبل استمرار التسويق بالسعر أو التفاصيل الجديدة.",
        "تعديل السعر، تغيير سعر المنتج، تحديث البيانات، اغير وصف المنتج"
    ),
    (
        "supplier",
        "أعمل إيه لو عندي مشكلة في طلب أو مستحقات؟",
        "تواصل مع فريق Vindora من خلال قناة الدعم الرسمية، ووضّح المشكلة مع رقم الطلب أو بيانات التعامل اللازمة لمراجعتها. تجنب إرسال بياناتك المالية الحساسة في مجموعات عامة.",
        "مشكلة في الطلب، مستحقاتي ناقصة، مشكلة فلوس، شكوى مورد، تأخير المستحقات"
    ),

    # =========================
    # MARKETER - المسوقين (10)
    # =========================

    (
        "marketer",
        "إيه هي Vindora؟",
        "Vindora منصة للتسويق الإلكتروني بتتيح للمسوقين التعرف على المنتجات المتاحة وتسويقها للعملاء، مع احتساب العمولات وفقًا لنظام المنصة وشروطها.",
        "ما هي فيندورا، تعريف المنصة، فيندورا بتعمل ايه، طبيعة الشغل"
    ),
    (
        "marketer",
        "هل التسجيل كمسوق مجاني؟",
        "التسجيل كمسوق مجاني، ومش مطلوب منك دفع رسوم تسجيل للانضمام. استخدم رابط التسجيل الرسمي: https://bit.ly/4zwPg03",
        "التسجيل ببلاش، في رسوم، اشتراك، فلوس للتسجيل، ادفع كام"
    ),
    (
        "marketer",
        "هل لازم أشتري منتجات أو أخزّن بضاعة؟",
        "لا، مش مطلوب منك شراء كميات أو تخزين المنتجات عندك عشان تبدأ التسويق. دورك الأساسي هو التسويق للمنتجات المتاحة وفقًا لنظام Vindora.",
        "اشتري بضاعة، اخزن منتجات، لازم رأس مال، شراء مخزون، عندي منتجات"
    ),
    (
        "marketer",
        "إزاي أكسب من التسويق؟",
        "بتختار المنتج المناسب، وبتسوّق له، ولما يتحقق طلب ناجح ومستوفٍ لشروط الاستحقاق، بتستحق عمولة ثابتة قدرها 40 جنيه عن الطلب.",
        "طريقة الربح، اكسب فلوس ازاي، اجيب عمولة، ارباح المسوق، ازاي ابيع"
    ),
    (
        "marketer",
        "العمولة بتكون كام؟",
        "عمولتك ثابتة 40 جنيه عن كل طلب ناجح ومستوفٍ لشروط الاستحقاق في Vindora.",
        "العمولة كام، باخد كام، 40 جنيه، نسبة المسوق، عمولة الطلب"
    ),
    (
        "marketer",
        "إمتى بستحق العمولة؟",
        "استحقاق العمولة بيكون عن الطلب الناجح والمستوفي لشروط الاستحقاق. أما مواعيد الصرف وإجراءات التسوية فبتكون حسب السياسات المعتمدة في Vindora.",
        "امتى اخد فلوسي، صرف العمولة، استحقاق الارباح، ميعاد العمولة"
    ),
    (
        "marketer",
        "هل فيه وقت محدد لازم أشتغل فيه؟",
        "تقدر تنظم وقتك في التسويق بما يناسب ظروفك، مع ضرورة الالتزام بسياسات المنصة وأي متطلبات مرتبطة بالمنتجات والطلبات.",
        "مواعيد الشغل، ساعات العمل، دوام، لازم اشتغل كل يوم، وقت محدد"
    ),
    (
        "marketer",
        "أجيب صور المنتجات وتفاصيلها منين؟",
        "استخدم الصور والتفاصيل والأسعار والعمولات المنشورة من خلال Vindora أو القنوات الرسمية المخصصة للمسوقين. تجنب تعديل معلومات المنتج بشكل ممكن يضلل العميل.",
        "صور المنتجات، اسعار المنتجات، تفاصيل المنتج، جروب التشغيل، محتوى التسويق"
    ),
    (
        "marketer",
        "هل أقدر أسوّق لأكتر من منتج؟",
        "تقدر تختار المنتجات المتاحة والمناسبة لجمهورك، مع مراجعة تفاصيل كل منتج والالتزام بالشروط والتعليمات الخاصة بتسويقه.",
        "منتجات كتير، اكتر من منتج، اسوق لمنتجات مختلفة، اختار المنتجات"
    ),
    (
        "marketer",
        "أعمل إيه لو عندي مشكلة أو استفسار؟",
        "تواصل مع فريق دعم Vindora من خلال قناة التواصل الرسمية المعتمدة. وضّح المشكلة وارفق رقم الطلب أو التفاصيل اللازمة للمساعدة، من غير مشاركة بيانات حساسة علنًا.",
        "الدعم، مشكلة في الحساب، استفسار مسوق، اكلم مين، خدمة المسوقين"
    ),

    # أسئلة تشغيلية مؤكدة للمسوقين
    (
        "marketer",
        "سجلت كمسوق، أعمل إيه بعد كده؟",
        "بعد ما تسجل حسابك كمسوق، لازم تتواصل مع دعم Vindora علشان يتم تفعيل حساب المسوق. التسجيل وحده مش معناه إن الحساب اتفعل تلقائيًا.",
        "تفعيل حساب المسوق، الحساب لسه مش شغال، سجلت ومفيش تفعيل، تفعيل المسوقين"
    ),
    (
        "marketer",
        "فين رابط التسجيل كمسوق؟",
        "تقدر تسجل كمسوق من خلال الرابط الرسمي: https://bit.ly/4zwPg03 وبعد التسجيل تواصل مع الدعم لتفعيل الحساب.",
        "لينك التسجيل، رابط المسوقين، اسجل فين، تسجيل مسوق"
    ),
]


def get_connection():
    conn = sqlite3.connect(DATABASE_NAME, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                audience TEXT DEFAULT 'general',
                created_at TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audience TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                keywords TEXT DEFAULT '',
                active INTEGER DEFAULT 1,
                created_at TEXT
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS unanswered (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                audience TEXT DEFAULT 'general',
                question TEXT NOT NULL,
                created_at TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_faq_audience
            ON faqs(audience, active)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_unanswered_status
            ON unanswered(status)
        """)

        conn.commit()

    seed_faqs()


def seed_faqs():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        for audience, question, answer, keywords in FAQ_DATA:
            exists = conn.execute(
                """
                SELECT id FROM faqs
                WHERE audience = ? AND question = ?
                LIMIT 1
                """,
                (audience, question)
            ).fetchone()

            if not exists:
                conn.execute(
                    """
                    INSERT INTO faqs
                    (audience, question, answer, keywords, active, created_at)
                    VALUES (?, ?, ?, ?, 1, ?)
                    """,
                    (audience, question, answer, keywords, now)
                )

        conn.commit()


def save_user(user_id, username, first_name):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, username, first_name, created_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name
            """,
            (user_id, username or "", first_name or "", now)
        )
        conn.commit()


def set_user_audience(user_id, audience):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET audience = ? WHERE user_id = ?",
            (audience, user_id)
        )
        conn.commit()


def get_user_audience(user_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT audience FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

    return row["audience"] if row else "general"


def get_faqs(audience=None, active_only=True):
    query = "SELECT * FROM faqs WHERE 1=1"
    params = []

    if audience and audience != "general":
        query += " AND audience IN (?, 'general')"
        params.append(audience)

    if active_only:
        query += " AND active = 1"

    query += " ORDER BY id DESC"

    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return [dict(row) for row in rows]


def add_faq(audience, question, answer, keywords=""):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO faqs
            (audience, question, answer, keywords, active, created_at)
            VALUES (?, ?, ?, ?, 1, ?)
            """,
            (audience, question, answer, keywords, now)
        )
        conn.commit()
        return cursor.lastrowid


def toggle_faq(faq_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT active FROM faqs WHERE id = ?",
            (faq_id,)
        ).fetchone()

        if not row:
            return None

        new_status = 0 if row["active"] else 1

        conn.execute(
            "UPDATE faqs SET active = ? WHERE id = ?",
            (new_status, faq_id)
        )
        conn.commit()

    return new_status


def save_unanswered(user_id, audience, question):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO unanswered (user_id, audience, question, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, audience, question, now)
        )
        conn.commit()


def get_pending_questions(limit=10):
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM unanswered
            WHERE status = 'pending'
            ORDER BY id ASC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()

    return [dict(row) for row in rows]


def close_unanswered(question_id, status="reviewed"):
    with get_connection() as conn:
        conn.execute(
            "UPDATE unanswered SET status = ? WHERE id = ?",
            (status, question_id)
        )
        conn.commit()


def get_faq_by_id(faq_id):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM faqs WHERE id = ?",
            (faq_id,)
        ).fetchone()

    return dict(row) if row else None


def get_statistics():
    with get_connection() as conn:
        users = conn.execute(
            "SELECT COUNT(*) AS total FROM users"
        ).fetchone()["total"]

        faqs = conn.execute(
            "SELECT COUNT(*) AS total FROM faqs WHERE active = 1"
        ).fetchone()["total"]

        pending = conn.execute(
            "SELECT COUNT(*) AS total FROM unanswered WHERE status = 'pending'"
        ).fetchone()["total"]

        total_questions = conn.execute(
            "SELECT COUNT(*) AS total FROM unanswered"
        ).fetchone()["total"]

        audience_rows = conn.execute(
            """
            SELECT audience, COUNT(*) AS total
            FROM users
            GROUP BY audience
            """
        ).fetchall()

    return {
        "users": users,
        "faqs": faqs,
        "pending": pending,
        "total_questions": total_questions,
        "audiences": {
            row["audience"]: row["total"]
            for row in audience_rows
        }
    }
