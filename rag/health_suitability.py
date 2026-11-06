"""Deterministic, conservative food-health suitability response builder.

This module organizes available menu facts; it does not diagnose or prescribe.
Missing nutrition data remains null and every menu estimate retains its recorded status.
"""

from __future__ import annotations

import re
from typing import Any

DISCLAIMER = "General nutrition information only—not medical advice or a treatment plan. Confirm recipes and allergies with the restaurant; follow your healthcare professional's guidance."

CONDITIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Low Blood Pressure", ("low blood pressure", "low bp", "hypotension")),
    ("High Blood Pressure", ("high blood pressure", "high bp", "hypertension")),
    ("High Blood Sugar", ("high blood sugar", "elevated blood sugar")),
    ("Diabetes", ("diabetes", "diabetic")),
    ("Prediabetes", ("prediabetes", "pre diabetes")),
    ("General Blood Sugar Management", ("blood sugar", "glucose management", "blood glucose")),
    ("Heart Disease", ("heart disease", "heart health", "cardiac")),
    ("High Cholesterol", ("high cholesterol", "cholesterol")),
    ("High Triglycerides", ("high triglycerides", "triglycerides")),
    ("Weight Loss", ("weight loss", "lose weight", "fat loss")),
    ("Weight Gain", ("weight gain", "gain weight")),
    ("Weight Maintenance", ("weight maintenance", "maintain weight")),
    ("Muscle Building", ("muscle building", "build muscle", "muscle gain")),
    ("Kidney Health", ("kidney health", "kidney disease", "renal")),
    ("Digestive Health", ("digestive health", "digestion", "digestive")),
    ("Low-Sodium Diet", ("low sodium", "low-sodium", "lower sodium", "lower in sodium", "less sodium", "sodium restriction", "less salt")),
    ("High-Protein Diet", ("high protein", "high-protein", "protein-rich")),
    ("High-Fibre Diet", ("high fibre", "high-fibre", "high fiber", "high-fiber")),
    ("Allergy / Ingredient Restriction", ("allergy", "allergic", "allergen", "intolerance", "intolerant", "gluten-free", "gluten free", "nut-free", "nut free", "dairy-free", "dairy free")),
    ("Dietary Preference", ("vegan", "vegetarian", "non-vegetarian", "non vegetarian")),
)

# Canonical KB names for foods that may not be available in the live menu.
FOOD_ALIASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("ragi dosa", ("ragi dosa", "finger millet dosa")),
    ("plain dosa", ("plain dosa", "dosa", "dosai")),
    ("idli", ("idli", "idlis")),
    ("ven pongal", ("ven pongal", "pongal")),
    ("uthappam", ("uthappam", "uttapam")),
    ("idiyappam", ("idiyappam", "string hopper")),
    ("appam", ("appam")),
    ("chapati", ("chapati", "chapathi", "roti")),
    ("sambar rice", ("sambar rice", "sambar sadam")),
    ("curd rice", ("curd rice", "yogurt rice", "thayir sadam")),
    ("lemon rice", ("lemon rice", "elumichai sadam")),
    ("vegetable meals", ("vegetable meals", "veg meals", "banana leaf meals", "thali")),
    ("keerai rice", ("keerai rice", "spinach rice")),
    ("rasam rice", ("rasam rice", "rasam sadam")),
    ("chicken biryani", ("chicken biryani", "biryani")),
    ("fish curry with rice", ("fish curry", "fish curry with rice")),
    ("egg omelette", ("omelette", "omelet")),
    ("egg curry with rice", ("egg curry", "egg curry with rice")),
    ("sundal", ("sundal", "chickpea sundal")),
    ("sprouts salad", ("sprouts salad", "sprout salad")),
    ("fruit salad", ("fruit salad",)),
    ("banana", ("banana",)),
    ("grilled chicken", ("grilled chicken",)),
)

NUTRIENT_FIELDS = {
    "calories": "calories",
    "protein": "protein",
    "carbohydrates": "carbs",
    "fat": "fat",
    "fiber": None,
    "sodium": None,
}


def _contains_phrase(text: str, phrase: str) -> bool:
    return bool(re.search(rf"(?<![a-z0-9]){re.escape(phrase.lower())}(?![a-z0-9])", text.lower()))


def identify_conditions(question: str) -> list[str]:
    text = question.lower().replace("_", " ")
    found = []
    for condition, aliases in CONDITIONS:
        if any(_contains_phrase(text, alias) for alias in aliases):
            found.append(condition)
    # Prefer specific metabolic labels over their broad "blood sugar" parent.
    specific = {"Diabetes", "Prediabetes", "High Blood Sugar"}
    if len(specific.intersection(found)) and "General Blood Sugar Management" in found:
        found.remove("General Blood Sugar Management")
    return found


def _food_from_question(question: str, foods: list[dict[str, Any]]) -> tuple[str | None, dict[str, Any] | None]:
    text = question.lower()
    # Exact active menu names first, longest name wins (e.g. idli with sambar).
    for item in sorted(foods, key=lambda row: len(str(row.get("name") or "")), reverse=True):
        name = str(item.get("name") or "").strip()
        if name and _contains_phrase(text, name):
            return name, item

    aliases = [
        (text.find(alias), alias, canonical)
        for canonical, values in FOOD_ALIASES
        for alias in values
        if _contains_phrase(text, alias)
    ]
    for _, alias, canonical in sorted(aliases, key=lambda match: (match[0], -len(match[1]))):
        # Match only an explicitly named menu item or an unambiguous canonical
        # dish; never substitute a fried/creamy preparation for a different one.
        menu_match = next(
            (item for item in foods if _menu_matches_canonical(str(item.get("name") or ""), canonical)),
            None,
        )
        return (str(menu_match.get("name")), menu_match) if menu_match else (canonical.title(), None)
    return None, None


def _menu_matches_canonical(menu_name: str, canonical: str) -> bool:
    name = menu_name.lower()
    if canonical == "plain dosa":
        return (
            _contains_phrase(name, "dosa")
            and not any(_contains_phrase(name, variant) for variant in ("ragi dosa", "ghee roast", "masala dosa", "paper dosa"))
        )
    if canonical == "idli":
        return _contains_phrase(name, "idli")
    if canonical == "ven pongal":
        return _contains_phrase(name, "pongal")
    if canonical == "vegetable meals":
        return "meals" in name or "thali" in name
    if canonical == "chicken biryani":
        return "biryani" in name and "chicken" in name
    if canonical == "fish curry with rice":
        return "fish" in name and "curry" in name
    if canonical == "egg omelette":
        return "omelette" in name or "omelet" in name
    if canonical == "egg curry with rice":
        return "egg" in name and "curry" in name
    return _contains_phrase(name, canonical)


def identify_health_question(question: str) -> bool:
    return bool(identify_conditions(question))


def _number(item: dict[str, Any] | None, key: str) -> int | float | None:
    if not item:
        return None
    value = item.get(key)
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _nutrition_value(item: dict[str, Any] | None, key: str) -> int | float | str | None:
    if not item or item.get(key) is None:
        return None
    value = item[key]
    try:
        number = float(value)
        return int(number) if number.is_integer() else number
    except (TypeError, ValueError):
        return str(value)


def _knowledge_food_record(food_name: str | None, documents: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Extract explicit illustrative ranges from a matching retrieved KB entry."""
    if not food_name:
        return None
    text = "\n".join(
        document.get("page_content", "")
        for document in documents
        if document.get("metadata", {}).get("kind") == "knowledge"
    )
    sections = re.split(r"(?=^### )", text, flags=re.MULTILINE)
    for section in sections:
        heading = re.match(r"^### (.+)$", section, flags=re.MULTILINE)
        if not heading or heading.group(1).strip().lower() != food_name.lower().strip():
            continue
        serving = re.search(r"\*\*Serving and estimates:\*\*\s*(.*?):\s*\*\*", section, flags=re.IGNORECASE)
        patterns = {
            "calories": r"([0-9]+(?:\.[0-9]+)?\s*(?:[–-]\s*[0-9]+(?:\.[0-9]+)?)?)\s*kcal",
            "protein": r"protein\s+([0-9]+(?:\.[0-9]+)?\s*(?:[–-]\s*[0-9]+(?:\.[0-9]+)?)?)\s*g",
            "carbs": r"carbohydrate\s+([0-9]+(?:\.[0-9]+)?\s*(?:[–-]\s*[0-9]+(?:\.[0-9]+)?)?)\s*g",
            "fat": r"fat\s+([0-9]+(?:\.[0-9]+)?\s*(?:[–-]\s*[0-9]+(?:\.[0-9]+)?)?)\s*g",
            "fiber": r"fibre\s+([0-9]+(?:\.[0-9]+)?\s*(?:[–-]\s*[0-9]+(?:\.[0-9]+)?)?)\s*g",
        }
        values = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, section, flags=re.IGNORECASE)
            values[key] = re.sub(r"\s+", "", match.group(1)) if match else None
        if not serving and not any(values.values()):
            return None
        return {
            "name": heading.group(1).strip().title(),
            "serving_size": serving.group(1).strip() if serving else None,
            **values,
            "nutrition_status": "illustrative_estimate_not_verified",
            "ingredients": "",
        }
    return None


def _status(condition: str, item: dict[str, Any] | None) -> tuple[str, str, list[str], list[str]]:
    carbs = _nutrition_value(item, "carbs")
    calories = _nutrition_value(item, "calories")
    protein = _nutrition_value(item, "protein")
    fat = _nutrition_value(item, "fat")
    is_knowledge_estimate = bool(item and item.get("nutrition_status") == "illustrative_estimate_not_verified")
    source_label = "The curated guide provides an illustrative estimate" if is_knowledge_estimate else "The menu lists an estimate"
    if condition == "Allergy / Ingredient Restriction":
        return (
            "check_ingredients",
            "Ingredient lists and kitchen cross-contact are incomplete, so allergy safety cannot be established here.",
            ["A listed ingredient is not a complete allergen or cross-contact statement."],
            ["Confirm every ingredient and preparation surface directly with restaurant staff; do not rely on this analysis to establish safety."],
        )
    if condition == "Dietary Preference":
        return (
            "check_ingredients",
            "A dietary label cannot be confirmed from the dish name alone; recipes may include dairy, ghee, egg, or shared equipment.",
            ["The available ingredient list may be incomplete."],
            ["Confirm the exact recipe and cooking method with the restaurant."],
        )
    if condition in {"Low Blood Pressure"}:
        return (
            "limited_information",
            "This food is not a treatment for low blood pressure, and its sodium content is not available.",
            ["A food's suitability cannot be determined from its name alone."],
            ["Hydration can be relevant for some causes, but fluid needs vary; do not change salt or fluid intake based on this result."],
        )
    if condition in {"High Blood Pressure", "Low-Sodium Diet"}:
        return (
            "preparation_matters",
            "Sodium is not measured in the available menu data, so a lower-sodium claim cannot be made.",
            ["Salt, seasoning, sauces, and portion size can vary by preparation."],
            ["Ask the restaurant whether less salt is possible; follow any clinician-provided sodium limits."],
        )
    if condition in {"Diabetes", "Prediabetes", "High Blood Sugar", "General Blood Sugar Management"}:
        if carbs is None:
            return (
                "limited_information",
                "Carbohydrate information is not available for this menu serving.",
                ["Recipe and portion size affect total carbohydrate and blood-glucose response."],
                ["Confirm serving and ingredients; follow your individualized care plan."],
            )
        return (
            "portion_control",
            f"{source_label} for this serving, but it does not predict an individual's blood-glucose response.",
            [f"Listed carbohydrates: {carbs} g per serving ({item.get('nutrition_status', 'status not recorded')})."],
            ["Check the serving size and total meal carbohydrates, including sides and drinks.", "Ragi, millet, brown rice, and traditional foods can still contribute carbohydrate."],
        )
    if condition in {"Heart Disease", "High Cholesterol", "High Triglycerides"}:
        if fat is None:
            return (
                "limited_information",
                "Available data is not enough to assess this dish for heart-related dietary needs.",
                ["Sodium, saturated fat, and trans fat are not recorded."],
                ["Preparation oil, frying, and portion size may matter; seek individualized clinical advice."],
            )
        return (
            "preparation_matters",
            f"{source_label} for total fat; saturated fat, trans fat, and sodium are unavailable.",
            [f"Listed total fat: {fat} g per serving ({item.get('nutrition_status', 'status not recorded')}).", "Cooking method and recipe may change the result."],
            ["Ask about oil, ghee, frying, and salt; do not treat this estimate as a heart-health rating."],
        )
    if condition in {"Weight Loss", "Weight Maintenance", "Weight Gain", "Muscle Building"}:
        if calories is None and protein is None:
            return (
                "limited_information",
                "Energy and protein information is unavailable for this serving, so a meaningful comparison cannot be made.",
                ["Portion size and recipe are not confirmed."],
                ["Choose according to your preferences and seek professional help for individualized goals."],
            )
        relevant = []
        if calories is not None:
            relevant.append(f"Listed energy: {calories} kcal per menu serving.")
        if protein is not None:
            relevant.append(f"Listed protein: {protein} g per menu serving.")
        return (
            "portion_control",
            "This is a menu-data comparison only, not a personalized weight or muscle-building recommendation.",
            relevant,
            ["Actual serving and preparation may differ; consider the overall meal and your individualized needs."],
        )
    if condition == "High-Protein Diet":
        if protein is None:
            return ("limited_information", "Protein data is not available for this menu item.", [], ["Ask the restaurant for a verified recipe-specific value."])
        return ("limited_information", "The menu's protein value may be an estimate and does not establish that the meal meets a personal protein target.", [f"Listed protein: {protein} g per menu serving."], ["Use an individualized target from a qualified professional if you have one."])
    if condition == "High-Fibre Diet":
        return ("limited_information", "Fibre is not recorded for this menu item.", [], ["Ask whether whole grains, legumes, or vegetables are included; do not infer a fibre amount."])
    if condition == "Kidney Health":
        return ("seek_professional_advice", "Kidney-related food needs depend on the person's condition, lab results, and care plan.", ["Sodium and other kidney-relevant nutrients are not fully available."], ["Consult your nephrologist or renal dietitian before using a food recommendation."])
    return ("limited_information", "The available information is not sufficient for an individualized assessment.", [], ["Check recipe details and seek qualified professional advice for medical decisions."])


def _allergy_warnings(question: str, item: dict[str, Any] | None) -> tuple[list[str], list[str]]:
    if not item:
        return [], ["Ingredients and cross-contact are not confirmed; contact the restaurant before ordering if allergies are relevant."]
    ingredients = str(item.get("ingredients") or "").lower()
    known_allergens = {
        "wheat/gluten": ("wheat", "gluten", "flour"),
        "dairy": ("milk", "yogurt", "curd", "ghee", "butter", "cream"),
        "egg": ("egg",),
        "fish": ("fish",),
        "peanut": ("peanut",),
        "tree nuts": ("cashew", "almond", "pistachio", "walnut"),
        "soy": ("soy",),
        "sesame": ("sesame",),
    }
    present = [label for label, terms in known_allergens.items() if any(term in ingredients for term in terms)]
    warnings = ["Menu ingredient lists may be incomplete; cross-contact is not recorded. Confirm with the restaurant."]
    allergy_mentioned = any(word in question.lower() for word in ("allerg", "intoleran", "celiac", "coeliac"))
    if allergy_mentioned:
        warnings.insert(0, "Do not rely on this analysis to establish allergy safety; ask restaurant staff about every ingredient and cross-contact.")
    return present, warnings


def _alternatives(foods: list[dict[str, Any]], selected: dict[str, Any] | None, conditions: list[str]) -> list[dict[str, Any]]:
    candidates = [food for food in foods if not selected or food.get("id") != selected.get("id")]
    if not candidates:
        return []

    reason_prefix = "Menu comparison only; this is not a medically verified alternative. "
    ranked: list[tuple[float, dict[str, Any], str]] = []
    condition_set = set(conditions)
    if condition_set.intersection({
        "Allergy / Ingredient Restriction", "Dietary Preference", "High Blood Pressure",
        "Low-Sodium Diet", "Low Blood Pressure", "Heart Disease", "High Cholesterol",
        "High Triglycerides", "Kidney Health",
    }):
        return []
    if condition_set.intersection({"Diabetes", "Prediabetes", "High Blood Sugar", "General Blood Sugar Management"}):
        available = [food for food in candidates if _number(food, "carbs") is not None]
        ranked = [(float(_number(food, "carbs") or 0), food, "Listed carbohydrate estimate is lower than other available choices; verify the recipe and portion.") for food in available]
    elif condition_set.intersection({"Weight Loss", "Weight Maintenance"}):
        available = [food for food in candidates if _number(food, "calories") is not None]
        ranked = [(float(_number(food, "calories") or 0), food, "Listed energy estimate can support a menu comparison; it is not a weight-loss promise.") for food in available]
    elif condition_set.intersection({"Weight Gain", "Muscle Building", "High-Protein Diet"}):
        available = [food for food in candidates if _number(food, "protein") is not None]
        ranked = [(-float(_number(food, "protein") or 0), food, "Listed protein estimate is available for comparison; match it to your needs with professional guidance.") for food in available]
    elif condition_set.intersection({"High-Fibre Diet"}):
        # Fibre is unavailable for the current schema; do not rank using a proxy.
        ranked = []
    else:
        ranked = [(float(index), food, "Another item in the current menu; ingredients and health suitability require separate confirmation.") for index, food in enumerate(candidates)]

    ranked.sort(key=lambda result: result[0])
    result = []
    for _, food, reason in ranked[:3]:
        result.append({
            "food_id": food.get("id"),
            "name": food.get("name"),
            "image_url": food.get("image_url"),
            "category": food.get("category"),
            "price": food.get("price"),
            "nutrition": {
                "calories": food.get("calories"),
                "protein": food.get("protein"),
                "carbohydrates": food.get("carbs"),
                "fat": food.get("fat"),
                "fiber": None,
                "sodium": None,
                "status": food.get("nutrition_status") or "not recorded",
            },
            "reason": reason_prefix + reason,
        })
    return result


def _comparison_items(question: str, foods: list[dict[str, Any]]) -> list[dict[str, Any]]:
    text = question.lower()
    if not any(term in text for term in ("compare", "comparison", "versus", " vs ", "between")):
        return []
    found = []
    for food in foods:
        name = str(food.get("name") or "")
        matched = False
        for canonical, aliases in FOOD_ALIASES:
            if canonical == "plain dosa":
                matched = _contains_phrase(text, "dosa") and _contains_phrase(name, "dosa")
            else:
                matched = any(_contains_phrase(text, alias) and _menu_matches_canonical(name, canonical) for alias in aliases)
            if matched:
                break
        if matched:
            found.append({
                "food_id": food.get("id"),
                "name": name,
                "image_url": food.get("image_url"),
                "price": food.get("price"),
                "nutrition": {
                    "calories": food.get("calories"),
                    "protein": food.get("protein"),
                    "carbohydrates": food.get("carbs"),
                    "fat": food.get("fat"),
                    "fiber": None,
                    "sodium": None,
                    "status": food.get("nutrition_status") or "not recorded",
                },
            })
    return found[:4]


def validate_health_response(payload: dict[str, Any]) -> dict[str, Any]:
    """Validate API shape without adding a Pydantic runtime dependency."""
    required = {"response_type", "food_name", "serving_size", "health_assessments", "nutrition", "ingredients", "allergens", "alternatives", "warnings", "sources", "disclaimer"}
    if not isinstance(payload, dict) or not required.issubset(payload):
        raise ValueError("Invalid health analysis response shape")
    if payload["response_type"] != "health_suitability" or not isinstance(payload["health_assessments"], list):
        raise ValueError("Invalid health analysis response type")
    allowed_status = {"generally_suitable", "portion_control", "preparation_matters", "check_ingredients", "limited_information", "seek_professional_advice"}
    for assessment in payload["health_assessments"]:
        if not isinstance(assessment, dict) or assessment.get("status") not in allowed_status:
            raise ValueError("Invalid health assessment status")
        if not all(isinstance(assessment.get(key), list) for key in ("reason", "considerations")):
            raise ValueError("Invalid health assessment lists")
    if not isinstance(payload["nutrition"], dict) or any(value is not None and not isinstance(value, (int, float, str)) for value in payload["nutrition"].values()):
        raise ValueError("Invalid nutrition values")
    return payload


def build_health_analysis(question: str, foods: list[dict[str, Any]], sources: list[dict[str, str]] | None = None, documents: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    conditions = identify_conditions(question)
    if not conditions:
        return None

    food_name, selected = _food_from_question(question, foods)
    pending_catalog_item = bool(selected and selected.get("catalog_status") == "reference_pending_restaurant_confirmation")
    knowledge_item = _knowledge_food_record(food_name, documents or []) if not selected or pending_catalog_item else None
    nutrition_item = (selected if selected and not pending_catalog_item else None) or knowledge_item
    assessments = []
    for condition in conditions:
        status, summary, reason, considerations = _status(condition, nutrition_item)
        assessments.append({
            "condition": condition,
            "status": status,
            "summary": summary,
            "reason": reason,
            "considerations": considerations,
        })

    nutrition_status = nutrition_item.get("nutrition_status") if nutrition_item else None
    if nutrition_status in (None, "", "unavailable"):
        nutrition_status = "not available"
    nutrition = {
        "calories": _nutrition_value(nutrition_item, "calories"),
        "protein": _nutrition_value(nutrition_item, "protein"),
        "carbohydrates": _nutrition_value(nutrition_item, "carbs"),
        "fat": _nutrition_value(nutrition_item, "fat"),
        "fiber": _nutrition_value(nutrition_item, "fiber"),
        "sodium": None,
        "status": nutrition_status,
    }
    allergens, warnings = _allergy_warnings(question, selected if not pending_catalog_item else None)
    if selected and not pending_catalog_item and selected.get("nutrition_status") not in {"verified", "lab_verified"}:
        warnings.append("Nutrition figures are menu estimates, not verified measurements.")
    if pending_catalog_item:
        warnings.append("This dish is in the Tamil food reference catalog but has not been confirmed as a currently offered restaurant item.")
    if (not selected or pending_catalog_item) and knowledge_item:
        warnings.append("These are broad illustrative knowledge-base estimates, not verified measurements for the current restaurant recipe.")
    elif not selected or pending_catalog_item:
        warnings.append("This food is not matched to a current menu item; menu nutrition and serving size are not available.")

    payload = {
        "response_type": "health_suitability",
        "food_name": food_name,
        "food_category": selected.get("category") if selected else None,
        "cuisine": selected.get("cuisine") if selected else ("Tamil Nadu" if knowledge_item else None),
        "tamil_name": selected.get("tamil_name") if selected else None,
        "serving_size": knowledge_item.get("serving_size") if knowledge_item else selected.get("serving_size") if selected else None,
        "image_url": selected.get("image_url") if selected and not pending_catalog_item and selected.get("image_verified") == 1 else None,
        "price": selected.get("price") if selected and not pending_catalog_item else None,
        "health_assessments": assessments,
        "nutrition": nutrition,
        "ingredients": [part.strip() for part in re.split(r"[,;]", str(selected.get("ingredients") or "")) if part.strip()] if selected else [],
        "preparation_method": (selected.get("preparation_method") or selected.get("cooking_method")) if selected else None,
        "dietary_type": selected.get("food_type") if selected else None,
        "availability_status": selected.get("availability_status") if selected else None,
        "catalog_status": selected.get("catalog_status") if selected else None,
        "allergens": allergens,
        "alternatives": _alternatives(foods, selected, conditions),
        "comparison_items": _comparison_items(question, foods),
        "warnings": warnings,
        "sources": sources or [],
        "disclaimer": DISCLAIMER,
    }
    return validate_health_response(payload)


def build_food_information(question: str, foods: list[dict[str, Any]], sources: list[dict[str, str]] | None = None) -> dict[str, Any] | None:
    """Return a structured food card for a named live or pending catalog entry."""
    if identify_conditions(question):
        return None
    name, food = _food_from_question(question, foods)
    if not food:
        return None
    pending = food.get("catalog_status") == "reference_pending_restaurant_confirmation"
    ingredients_text = str(food.get("ingredients") or "")
    allergens, warnings = _allergy_warnings(question, food if not pending else None)
    if pending:
        warnings = [
            "Traditional dish reference only; this item is not confirmed as currently offered by the restaurant.",
            "Ingredient examples and preparation are common recipe references, not this restaurant's confirmed recipe.",
            "Price, exact image, nutrition, allergens, and availability are not confirmed.",
        ]
    elif food.get("allergens_verified") != 1:
        warnings.append("Restaurant allergen and cross-contact status has not been verified.")
    nutrition_status = food.get("nutrition_status") or "not recorded"
    if nutrition_status == "unavailable":
        nutrition_status = "not available"
    return {
        "response_type": "food_information",
        "food_name": name,
        "food_category": food.get("category"),
        "cuisine": food.get("cuisine") or ("Tamil Nadu" if pending else None),
        "tamil_name": food.get("tamil_name"),
        "serving_size": food.get("serving_size"),
        "image_url": food.get("image_url") if not pending and food.get("image_verified") == 1 else None,
        "image_verified": bool(food.get("image_verified")),
        "price": food.get("price") if not pending else None,
        "availability_status": food.get("availability_status"),
        "catalog_status": food.get("catalog_status"),
        "restaurant_name": food.get("restaurant_name") or "NutriOrder AI",
        "nutrition": {
            "calories": food.get("calories"),
            "protein": food.get("protein"),
            "carbohydrates": food.get("carbs"),
            "fat": food.get("fat"),
            "fiber": food.get("fiber"),
            "sodium": food.get("sodium"),
            "status": nutrition_status,
            "source": food.get("nutrition_source"),
        },
        "ingredients": [part.strip() for part in re.split(r"[,;]", ingredients_text) if part.strip()],
        "preparation_method": food.get("preparation_method") or food.get("cooking_method"),
        "dietary_type": food.get("food_type"),
        "allergens": allergens,
        "warnings": warnings,
        "alternatives": [],
        "health_assessments": [],
        "sources": sources or [],
        "disclaimer": "General food information only. Confirm the restaurant's current recipe, availability, and allergy cross-contact with staff.",
    }


def load_current_menu() -> list[dict[str, Any]]:
    try:
        from backend.database import get_db_connection
    except ImportError:
        from database import get_db_connection

    connection = get_db_connection()
    try:
        rows = connection.execute(
            """SELECT id, name, price, calories, category, description, image_url,
                     ingredients, food_type, meal_type, protein, carbs, fat, nutrition_status,
                     fiber, sodium, serving_size, allergens, cooking_method, cuisine,
                     availability_status, dietary_verified, allergens_verified,
                     food_slug, tamil_name, preparation_method, nutrition_source,
                     nutrition_confidence, restaurant_name, catalog_status, image_verified
               FROM foods ORDER BY name"""
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()
