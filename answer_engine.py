
# answer_engine.py
import re
from rapidfuzz import fuzz

from config import ANSWER_THRESHOLD
from database import get_faqs


STOP_WORDS = {
    "ازاي", "كيف", "ايه", "ما", "ماذا", "هل", "انا", "انت",
    "هو", "هي", "في", "من", "على", "عن", "الى", "او", "و",
    "ب", "ل", "عايز", "عاوزه", "محتاج", "محتاجه", "ممكن",
    "لو", "سمحت", "اعرف", "اعمل", "اقدر", "عندي", "عند",
    "ده", "دي", "دا", "كده", "طيب", "طب", "بكام", "كام",
}


def normalize_arabic(text):
    text = str(text or "").lower()

    # إزالة التشكيل والتطويل
    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    text = text.replace("ـ", "")

    # توحيد الحروف
    replacements = {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ى": "ي",
        "ؤ": "و",
        "ئ": "ي",
        "ة": "ه",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # إزالة الرموز وعلامات الترقيم
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def meaningful_tokens(text):
    return {
        token
        for token in normalize_arabic(text).split()
        if len(token) > 1 and token not in STOP_WORDS
    }


def score_text(query, candidate):
    query = normalize_arabic(query)
    candidate = normalize_arabic(candidate)

    if not query or not candidate:
        return 0

    # بدون partial_ratio لمنع المطابقات الوهمية
    return max(
        fuzz.ratio(query, candidate),
        fuzz.token_set_ratio(query, candidate),
    )


def find_best_answer(question, audience):
    normalized_question = normalize_arabic(question)
    question_tokens = meaningful_tokens(normalized_question)

    # رفض الرسائل القصيرة والعشوائية
    if len(question_tokens) < 2:
        return None

    faqs = get_faqs(audience)

    best_faq = None
    best_score = 0

    # حد أدنى أكثر صرامة
    threshold = max(75, int(ANSWER_THRESHOLD))

    for faq in faqs:
        candidates = [faq["question"]]

        keywords = faq.get("keywords", "")

        if keywords:
            candidates.extend(
                item.strip()
                for item in re.split(r"[,،;\n]", keywords)
                if item.strip()
            )

        for candidate in candidates:
            candidate_normalized = normalize_arabic(candidate)
            candidate_tokens = meaningful_tokens(candidate_normalized)

            if not candidate_tokens:
                continue

            exact_match = (
                normalized_question == candidate_normalized
            )

            common_tokens = question_tokens.intersection(
                candidate_tokens
            )

            # لازم يكون فيه كلمتان واضحتان مشتركتان
            if not exact_match and len(common_tokens) < 2:
                continue

            current_score = score_text(
                normalized_question,
                candidate
            )

            if current_score > best_score:
                best_score = current_score
                best_faq = faq

    if best_faq and best_score >= threshold:
        best_faq["match_score"] = round(best_score, 1)
        return best_faq

    return None
