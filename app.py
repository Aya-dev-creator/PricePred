from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypedDict

from flask import Flask, render_template, request


class PredictionResult(TypedDict):
    category: str
    price: float
    details: str


Category = Literal["car", "phone", "computer", "watch", "camera", "other"]
LanguageCode = Literal["fr", "ar"]
ThemeCode = Literal["dark", "light"]


@dataclass
class ItemFeatures:
    category: Category
    age_years: float
    condition: int  # 1–5
    original_price: float


CATEGORY_BASE_PRICE: dict[Category, float] = {
    # Valeurs indicatives en dirhams (DH)
    "car": 250_000.0,
    "phone": 9_000.0,
    "computer": 15_000.0,
    "watch": 7_000.0,
    "camera": 12_000.0,
    "other": 3_000.0,
}


def _age_from_year(raw_year: str | None) -> float:
    if not raw_year:
        return 0.0
    try:
        year = int(raw_year)
    except ValueError:
        return 0.0

    current_year = datetime.now().year
    if year < 1980 or year > current_year + 1:
        return 0.0
    return max(0.0, float(current_year - year))


def _condition_from_text(raw_state: str | None) -> int:
    """Very rough mapping from free-text state to 1–5."""
    if not raw_state:
        return 3

    text = raw_state.lower()

    if any(word in text for word in ("neuf", "comme neuf", "parfait", "excellent")):
        return 5
    if any(word in text for word in ("bon", "bien")):
        return 4
    if any(word in text for word in ("moyen", "utilisé", "usage")):
        return 3
    if any(word in text for word in ("mauvais", "abîmé", "cassé", "fissuré")):
        return 2
    return 3


def estimate_price(features: ItemFeatures) -> PredictionResult:
    """Very simple heuristic-based 'model'."""
    age = max(features.age_years, 0.0)
    condition = max(1, min(features.condition, 5))
    original = max(features.original_price, 0.0)

    # Base depreciation by category
    if features.category == "car":
        # Cars: high first-year drop, then slower
        base_rate = 0.18
        yearly_factor = 0.12
    elif features.category == "phone":
        # Phones: fast depreciation
        base_rate = 0.25
        yearly_factor = 0.20
    else:
        # Other electronics / objects
        base_rate = 0.20
        yearly_factor = 0.15

    # Depreciation multiplier
    depreciation = min(0.9, base_rate + yearly_factor * age)
    remaining_ratio = max(0.05, 1.0 - depreciation)

    # Condition adjustment: 1 (très mauvais) → -40%, 5 (excellent) → +10%
    condition_adjust = -0.4 + (condition - 1) * (0.5 / 4)

    estimated = original * remaining_ratio * (1.0 + condition_adjust)
    estimated = max(10.0, estimated)

    # Round to nearest 10 for a more realistic price
    rounded_price = round(estimated / 10.0) * 10.0

    if features.category == "car":
        category_label = "Voiture"
    elif features.category == "phone":
        category_label = "Téléphone"
    elif features.category == "computer":
        category_label = "Ordinateur"
    elif features.category == "watch":
        category_label = "Montre"
    elif features.category == "camera":
        category_label = "Appareil photo"
    else:
        category_label = "Objet"

    return {
        "category": category_label,
        "price": float(rounded_price),
        "details": "",
    }


def create_app() -> Flask:
    app = Flask(__name__)

    @app.route("/", methods=["GET", "POST"])
    def index():
        prediction: PredictionResult | None = None
        error: str | None = None
        allowed_categories: tuple[Category, ...] = (
            "car",
            "phone",
            "computer",
            "watch",
            "camera",
            "other",
        )

        selected_category: Category = "car"
        lang: LanguageCode = "fr"
        theme: ThemeCode = "dark"

        if request.method == "POST":
            try:
                action = request.form.get("form_action", "estimate")

                lang_raw = (request.form.get("lang") or "fr").lower()
                if lang_raw in ("fr", "ar"):
                    lang = lang_raw  # type: ignore[assignment]

                theme_raw = (request.form.get("theme") or "dark").lower()
                if theme_raw in ("dark", "light"):
                    theme = theme_raw  # type: ignore[assignment]

                category_raw = request.form.get("category", "car")
                if category_raw not in allowed_categories:
                    category_raw = "car"
                selected_category = category_raw  # type: ignore[assignment]

                # If the user only wants to change category or preferences,
                # we stop here and re-render without computing a prediction.
                if action in ("change_category", "change_prefs"):
                    return render_template(
                        "index.html",
                        prediction=None,
                        error=None,
                        clear_form=True,
                        selected_category=selected_category,
                        lang=lang,
                        theme=theme,
                    )

                brand = (request.form.get("brand") or "").strip()
                model = (request.form.get("model") or "").strip()
                year_raw = (request.form.get("year") or "").strip()
                state_text = (request.form.get("state") or "").strip()

                age_years = _age_from_year(year_raw)
                condition = _condition_from_text(state_text)

                base_original = CATEGORY_BASE_PRICE[selected_category]
                original_price = base_original

                features = ItemFeatures(
                    category=selected_category,
                    age_years=age_years,
                    condition=condition,
                    original_price=original_price,
                )
                prediction = estimate_price(features)

                # Build a human-readable detail sentence
                detail_parts: list[str] = []
                if brand or model:
                    detail_parts.append(f"{brand} {model}".strip())
                if year_raw:
                    detail_parts.append(f"année {year_raw}")
                if state_text:
                    detail_parts.append(f"état : {state_text}")

                base_detail = " • ".join(part for part in detail_parts if part)
                if lang == "ar":
                    category_labels_ar: dict[Category, str] = {
                        "car": "سيارة",
                        "phone": "هاتف",
                        "computer": "حاسوب",
                        "watch": "ساعة",
                        "camera": "كاميرا",
                        "other": "غرض",
                    }
                    prediction["category"] = category_labels_ar[selected_category]
                    if base_detail:
                        prediction[
                            "details"
                        ] = f"{base_detail}. هذا السعر تقريبي ويعتمد على المعلومات التي أدخلتها، وليس تقييماً رسمياً."
                    else:
                        prediction[
                            "details"
                        ] = "هذا السعر تقريبي ويعتمد على المعلومات التي أدخلتها، وليس تقييماً رسمياً."
                else:
                    if base_detail:
                        prediction["details"] = (
                            f"{base_detail}. Estimation basée sur les informations fournies. "
                            "Ce n’est pas une évaluation professionnelle."
                        )
                    else:
                        prediction[
                            "details"
                        ] = "Estimation basée sur les informations fournies. Ce n’est pas une évaluation professionnelle."
            except ValueError:
                if lang == "ar":
                    error = "يرجى التحقق من القيم المُدخلة."
                else:
                    error = "Merci de vérifier les valeurs saisies."

        return render_template(
            "index.html",
            prediction=prediction,
            error=error,
            selected_category=selected_category,
            lang=lang,
            theme=theme,
            clear_form=False,
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)

