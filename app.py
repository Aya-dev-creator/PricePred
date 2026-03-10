from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypedDict
import re

from flask import Flask, render_template, request


def ask_llm_for_price(category: str, brand: str, model: str, year: str, condition: str) -> float | None:
    if not brand and not model:
        return None

    try:
        from huggingface_hub import InferenceClient
        # Initialize client with provided key
        client = InferenceClient(api_key="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")
        
        prompt = (
            f"Tu es un expert en évaluation de prix au Maroc.\n"
            f"Estime le prix actuel raisonnable sur le marché de l'occasion en dirhams marocains (MAD) "
            f"pour cet article, en tenant compte de son âge et de son état.\n"
            f"- Catégorie : {category}\n"
            f"- Marque : {brand}\n"
            f"- Modèle : {model}\n"
            f"- Année : {year}\n"
            f"- État : {condition}\n\n"
            "Analyse l'objet et réponds UNIQUEMENT avec le prix final estimé sous forme d'un nombre entier, "
            "sans aucun autre texte explicatif, sans symboles, ni devises."
        )
        response = client.chat_completion(
            model="Qwen/Qwen2.5-72B-Instruct", 
            messages=[{"role": "user", "content": prompt}], 
            max_tokens=20,
        )
        content = response.choices[0].message.content.strip()
        
        # Clean up commas, spaces
        content = content.replace(" ", "").replace(",", "").replace(".", "")
        match = re.search(r'\d+', content)
        if match:
            price = float(match.group())
            if price > 10.0:
                return price
    except Exception as e:
        print(f"LLM Error: {e}")
    return None


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
                actions = request.form.getlist("form_action")
                action = actions[-1] if actions else "estimate"

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

                llm_price = ask_llm_for_price(
                    category=category_raw, 
                    brand=brand, 
                    model=model, 
                    year=year_raw, 
                    condition=state_text
                )

                if llm_price is not None:
                    rounded_price = round(llm_price / 10.0) * 10.0
                    
                    if selected_category == "car":
                        category_label = "Voiture"
                    elif selected_category == "phone":
                        category_label = "Téléphone"
                    elif selected_category == "computer":
                        category_label = "Ordinateur"
                    elif selected_category == "watch":
                        category_label = "Montre"
                    elif selected_category == "camera":
                        category_label = "Appareil photo"
                    else:
                        category_label = "Objet"
                        
                    prediction = {
                        "category": category_label,
                        "price": float(rounded_price),
                        "details": "",
                    } # type: ignore[typeddict-item]
                    prediction = prediction # Keep type checker happy for further assignments
                else:
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

