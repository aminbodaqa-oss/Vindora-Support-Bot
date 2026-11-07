# answer_engine.py
import re
import unicodedata
from rapidfuzz import fuzz

from config import ANSWER_THRESHOLD
from database import get_faqs


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
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # إزالة الرموز وعلامات الترقيم
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def score_text(query, candidate):
    query = normalize_arabic(query)
    candidate = normalize_arabic(candidate)

    if not query or not candidate:
        return 0

    return max(
        fuzz.ratio(query, candidate),
        fuzz.token_set_ratio(query, candidate),
        fuzz.partial_ratio(query, candidate),
    )


def find_best_answer(question, audience):
    faqs = get_faqs(audience)

    best_faq = None
    best_score = 0

    normalized_question = normalize_arabic(question)

    for faq in faqs:
        candidates = [faq["question"]]

        keywords = faq.get("keywords", "")
        if keywords:
            candidates.extend(
                item.strip()
                for item in re.split(r"[,،;\n]", keywords)
                if item.strip()
            )

        current_score = max(
            score_text(normalized_question, candidate)
            for candidate in candidates
        )

        if current_score > best_score:
            best_score = current_score
            best_faq = faq

    if best_faq and best_score >= ANSWER_THRESHOLD:
        best_faq["match_score"] = round(best_score, 1)
        return best_faq

    return None
