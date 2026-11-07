
import sqlite3
import os
from datetime import datetime, timezone

from config import DATABASE_NAME


# ==========================================
# إعدادات قاعدة البيانات
# ==========================================

DB_PATH = DATABASE_NAME or "vindora_bot.db"


def get_connection():
    """إنشاء اتصال بقاعدة البيانات."""
    folder = os.path.dirname(DB_PATH)

    if folder:
        os.makedirs(folder, exist_ok=True)

    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def now():
    return datetime.now(timezone.utc).isoformat()


# ==========================================
# إنشاء الجداول
# ==========================================

def init_db():
    """إنشاء جداول قاعدة البيانات عند تشغيل البوت."""

    with get_connection() as conn:

        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                audience TEXT DEFAULT 'unknown',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS faqs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                audience TEXT DEFAULT 'all',
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS unanswered (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                audience TEXT,
                question TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                admin_answer TEXT,
                created_at TEXT NOT NULL,
                answered_at TEXT
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_faqs_audience
            ON faqs(audience, active)
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_unanswered_status
            ON unanswered(status)
        """)

        conn.commit()


# ==========================================
# إدارة المستخدمين
# ==========================================

def save_user(user_id, username=None, first_name=None):
    """حفظ المستخدم أو تحديث بياناته."""

    timestamp = now()

    with get_connection() as conn:
        conn.execute("""
            INSERT INTO users (
                user_id, username, first_name,
                audience, created_at, updated_at
            )
            VALUES (?, ?, ?, 'unknown', ?, ?)

            ON CONFLICT(user_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                updated_at = excluded.updated_at
        """, (
            user_id,
            username,
            first_name,
            timestamp,
            timestamp
        ))

        conn.commit()


def set_user_audience(user_id, audience):
    """تحديد نوع المستخدم: عميل أو مورد أو مسوق."""

    allowed = ["customer", "supplier", "marketer"]

    if audience not in allowed:
        return False

    with get_connection() as conn:
        conn.execute("""
            UPDATE users
            SET audience = ?, updated_at = ?
            WHERE user_id = ?
        """, (audience, now(), user_id))

        conn.commit()

    return True


def get_user_audience(user_id):
    """الحصول على نوع المستخدم."""

    with get_connection() as conn:
        row = conn.execute("""
            SELECT audience
            FROM users
            WHERE user_id = ?
        """, (user_id,)).fetchone()

    return row["audience"] if row else "unknown"


def get_user(user_id):
    """الحصول على بيانات مستخدم."""

    with get_connection() as conn:
        row = conn.execute("""
            SELECT *
            FROM users
            WHERE user_id = ?
        """, (user_id,)).fetchone()

    return dict(row) if row else None


# ==========================================
# الأسئلة الشائعة FAQ
# ==========================================

def add_faq(question, answer, audience="all"):
    """إضافة سؤال شائع."""

    if not question or not answer:
        return False

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO faqs (
                audience, question, answer, active, created_at
            )
            VALUES (?, ?, ?, 1, ?)
        """, (audience, question, answer, now()))

        conn.commit()
        return cursor.lastrowid


def get_faqs(audience="unknown"):
    """
    إرجاع الأسئلة الشائعة المناسبة للمستخدم.
    تُستخدم بواسطة Gemini.
    """

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT question, answer, audience
            FROM faqs
            WHERE active = 1
            AND audience IN (?, 'all')
            ORDER BY id DESC
        """, (audience,)).fetchall()

    return [
        {
            "question": row["question"],
            "answer": row["answer"],
            "audience": row["audience"]
        }
        for row in rows
    ]


def delete_faq(faq_id):
    """حذف سؤال شائع."""

    with get_connection() as conn:
        cursor = conn.execute("""
            DELETE FROM faqs
            WHERE id = ?
        """, (faq_id,))

        conn.commit()
        return cursor.rowcount > 0


def get_all_faqs():
    """الحصول على جميع الأسئلة الشائعة."""

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM faqs
            ORDER BY id DESC
        """).fetchall()

    return [dict(row) for row in rows]


# ==========================================
# الأسئلة التي لم يعرف البوت إجابتها
# ==========================================

def save_unanswered(user_id, question, username=None, audience=None):
    """حفظ سؤال لم يتمكن البوت من الإجابة عنه."""

    if not question:
        return None

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO unanswered (
                user_id,
                username,
                audience,
                question,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, 'pending', ?)
        """, (
            user_id,
            username,
            audience,
            question,
            now()
        ))

        conn.commit()
        return cursor.lastrowid


def get_unanswered(status="pending", limit=50):
    """الحصول على الأسئلة التي تحتاج مراجعة الأدمن."""

    with get_connection() as conn:
        rows = conn.execute("""
            SELECT *
            FROM unanswered
            WHERE status = ?
            ORDER BY id DESC
            LIMIT ?
        """, (status, limit)).fetchall()

    return [dict(row) for row in rows]


def answer_unanswered(question_id, answer):
    """
    اعتماد إجابة سؤال غير مجاب عليه،
    وإضافتها تلقائياً إلى الأسئلة الشائعة.
    """

    if not answer:
        return False

    with get_connection() as conn:

        row = conn.execute("""
            SELECT *
            FROM unanswered
            WHERE id = ?
        """, (question_id,)).fetchone()

        if not row:
            return False

        conn.execute("""
            UPDATE unanswered
            SET status = 'answered',
                admin_answer = ?,
                answered_at = ?
            WHERE id = ?
        """, (answer, now(), question_id))

        conn.execute("""
            INSERT INTO faqs (
                audience,
                question,
                answer,
                active,
                created_at
            )
            VALUES (?, ?, ?, 1, ?)
        """, (
            row["audience"] or "all",
            row["question"],
            answer,
            now()
        ))

        conn.commit()

    return True


def ignore_unanswered(question_id):
    """تجاهل سؤال غير مجاب عليه."""

    with get_connection() as conn:
        cursor = conn.execute("""
            UPDATE unanswered
            SET status = 'ignored'
            WHERE id = ?
        """, (question_id,))

        conn.commit()
        return cursor.rowcount > 0


# ==========================================
# إحصائيات البوت
# ==========================================

def get_stats():
    """إحصائيات عامة عن البوت."""

    with get_connection() as conn:

        users = conn.execute("""
            SELECT COUNT(*) AS total
            FROM users
        """).fetchone()["total"]

        customers = conn.execute("""
            SELECT COUNT(*) AS total
            FROM users
            WHERE audience = 'customer'
        """).fetchone()["total"]

        suppliers = conn.execute("""
            SELECT COUNT(*) AS total
            FROM users
            WHERE audience = 'supplier'
        """).fetchone()["total"]

        marketers = conn.execute("""
            SELECT COUNT(*) AS total
            FROM users
            WHERE audience = 'marketer'
        """).fetchone()["total"]

        unanswered = conn.execute("""
            SELECT COUNT(*) AS total
            FROM unanswered
            WHERE status = 'pending'
        """).fetchone()["total"]

        faqs = conn.execute("""
            SELECT COUNT(*) AS total
            FROM faqs
            WHERE active = 1
        """).fetchone()["total"]

    return {
        "users": users,
        "customers": customers,
        "suppliers": suppliers,
        "marketers": marketers,
        "unanswered": unanswered,
        "faqs": faqs
    }


# ==========================================
# اختبار تهيئة قاعدة البيانات
# ==========================================

if __name__ == "__main__":
    init_db()
    print("Vindora database initialized successfully.")
  
