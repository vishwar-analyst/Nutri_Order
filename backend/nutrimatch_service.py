"""Deterministic NutriMatch ranking, validation, and menu safety filters.

Profiles are request-scoped and never persisted. Nutrition is reported only when
present in the restaurant database; missing data is not imputed.
"""

from __future__ import annotations

import re
from typing import Any

try:
    from backend.database import get_db_connection
except ImportError:
    from database import get_db_connection

GOALS = {
    "weight_loss", "weight_gain", "muscle_building", "weight_maintenance",
    "healthy_eating", "high_protein", "heart_healthy", "balanced_nutrition",
}
HEALTH_CONSIDERATIONS = {
    "diabetes", "high_blood_pressure", "low_blood_pressure", "heart_disease",
    "high_cholesterol", "thyroid_conditions", "other", "none", "prefer_not_to_say",
}
DIETARY_TYPES = {"vegetarian", "non_vegetarian", "eggetarian", "vegan", "pescatarian", "no_preference"}
CUISINES = {"tamil_nadu", "south_indian", "north_indian", "continental", "chinese", "all_cuisines"}
ALLERGIES = {"peanuts", "tree_nuts", "dairy", "egg", "fish", "shellfish", "soy", "gluten", "sesame", "other", "no_known_allergies"}
NUTRITION_PREFERENCES = {"low_calorie", "high_protein", "high_fibre", "lower_carbohydrate", "less_oil", "less_salt", "balanced_nutrition"}
TASTES = {"spicy", "mild", "sweet", "less_oily", "less_salty", "no_preference"}
MEALS = {"breakfast", "lunch", "evening_snacks", "dinner", "anytime"}
BUDGETS = {"under_50", "50_100", "100_200", "200_300", "above_300", "no_limit"}

OPTION_MAPS = {
    "secondary_goals": GOALS,
    "health_considerations": HEALTH_CONSIDERATIONS,
    "cuisine_preferences": CUISINES,
    "allergies": ALLERGIES,
    "nutrition_preferences": NUTRITION_PREFERENCES,
    "taste_preferences": TASTES,
    "meal_preferences": MEALS,
}

ALLERGEN_TERMS = {
    "peanuts": ("peanut", "groundnut"),
    "tree_nuts": ("cashew", "almond", "walnut", "pistachio", "hazelnut", "pecan"),
    "dairy": ("milk", "buttermilk", "curd", "yogurt", "yoghurt", "ghee", "butter", "cream", "paneer", "cheese", "whey"),
    "egg": ("egg",),
    "fish": ("fish",),
    "shellfish": ("shellfish", "prawn", "shrimp", "crab", "lobster", "crayfish"),
    "soy": ("soy", "soya", "tofu"),
    "gluten": ("wheat", "gluten", "maida", "semolina", "sooji", "barley", "rye"),
    "sesame": ("sesame", "til"),
}
ANIMAL_TERMS = ALLERGEN_TERMS["dairy"] + ALLERGEN_TERMS["egg"] + ALLERGEN_TERMS["fish"] + ALLERGEN_TERMS["shellfish"] + ("chicken", "mutton", "meat", "beef", "pork", "gelatin", "honey")
MEAT_TERMS = ("chicken", "mutton", "meat", "beef", "pork", "fish", "prawn", "shrimp", "crab", "lobster")


def _enum(value: Any, allowed: set[str], field: str, *, optional: bool = False) -> str | None:
    if value in (None, "") and optional:
        return None
    if not isinstance(value, str) or value not in allowed:
        raise ValueError(f"Invalid {field} selection.")
    return value


def _list(value: Any, allowed: set[str], field: str, *, limit: int = 20) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > limit:
        raise ValueError(f"{field} must be a list with no more than {limit} selections.")
    if any(not isinstance(item, str) or item not in allowed for item in value):
        raise ValueError(f"Invalid {field} selection.")
    return list(dict.fromkeys(value))


def validate_profile(data: Any) -> dict[str, Any]:
    if data is None:
        data = {}
    if not isinstance(data, dict):
        raise ValueError("Send profile preferences as a JSON object.")

    goal = _enum(data.get("goal"), GOALS, "primary goal", optional=True)
    normalized: dict[str, Any] = {"goal": goal}
    for key, allowed in OPTION_MAPS.items():
        normalized[key] = _list(data.get(key), allowed, key)

    normalized["dietary_preference"] = _enum(
        data.get("dietary_preference", "no_preference"), DIETARY_TYPES, "dietary preference"
    )
    normalized["budget"] = _enum(data.get("budget", "no_limit"), BUDGETS, "budget")

    other_allergies = data.get("other_allergies", "")
    if not isinstance(other_allergies, str) or len(other_allergies) > 160:
        raise ValueError("Other allergy details must be 160 characters or fewer.")
    normalized["other_allergies"] = other_allergies.strip()

    # Optional body measurements are deliberately not normalized, returned, or saved.
    allergies = normalized["allergies"]
    if "no_known_allergies" in allergies:
        normalized["allergies"] = []
        normalized["other_allergies"] = ""
    if "none" in normalized["health_considerations"] or "prefer_not_to_say" in normalized["health_considerations"]:
        normalized["health_considerations"] = [
            value for value in normalized["health_considerations"]
            if value not in {"none", "prefer_not_to_say"}
        ]
    if "all_cuisines" in normalized["cuisine_preferences"]:
        normalized["cuisine_preferences"] = ["all_cuisines"]
    if "no_preference" in normalized["taste_preferences"]:
        normalized["taste_preferences"] = ["no_preference"]
    if "anytime" in normalized["meal_preferences"]:
        normalized["meal_preferences"] = ["anytime"]
    return normalized


def load_menu() -> list[dict[str, Any]]:
    connection = get_db_connection()
    try:
        rows = connection.execute(
            """SELECT id, name, price, calories, rating, category, healthy,
                      description, image_url, ingredients, food_type, meal_type,
                      protein, carbs, fat, nutrition_status, fiber, sodium,
                      serving_size, allergens, cooking_method, cuisine,
                      availability_status, dietary_verified, allergens_verified,
                      food_slug, tamil_name, preparation_method, nutrition_source,
                      nutrition_confidence, restaurant_name, catalog_status, image_verified
               FROM foods ORDER BY id"""
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def _contains_any(text: str, terms: tuple[str, ...] | list[str]) -> bool:
    lowered = text.lower()
    return any(re.search(rf"(?<![a-z]){re.escape(term)}s?(?![a-z])", lowered) for term in terms)


def _allergy_conflicts(food: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    requested = [allergy for allergy in profile["allergies"] if allergy != "other"]
    ingredient_text = " ".join(str(food.get(field) or "") for field in ("name", "ingredients", "allergens"))
    conflicts = [
        allergy for allergy in requested
        if _contains_any(ingredient_text, ALLERGEN_TERMS.get(allergy, ()))
    ]
    # Some common names do not expose an ingredient (for example coconut
    # chutney may contain cashew cross-contact); require verification to decide.
    if "tree_nuts" in requested and "chutney" in ingredient_text.lower() and "cashew" not in ingredient_text.lower():
        conflicts.append("tree_nuts_uncertain")
    other_terms = [term.strip().lower() for term in re.split(r"[,;]", profile.get("other_allergies", "")) if term.strip()]
    conflicts.extend(term for term in other_terms if _contains_any(ingredient_text, (term,)))
    return list(dict.fromkeys(conflicts))


def _allergen_status(food: dict[str, Any]) -> str:
    return "restaurant verified" if food.get("allergens_verified") == 1 else "not verified; ask restaurant about ingredients and cross-contact"


def _diet_state(food: dict[str, Any], preference: str) -> tuple[str, str | None]:
    food_type = (food.get("food_type") or "").lower()
    ingredients = " ".join(str(food.get(field) or "") for field in ("name", "ingredients"))
    if preference == "no_preference":
        return "eligible", None
    if preference == "non_vegetarian":
        if food_type == "non-vegetarian":
            return "eligible", None
        if food_type == "vegetarian":
            return "excluded", "Does not match the non-vegetarian preference."
        return "verify", "Protein source is not recorded."
    if preference == "vegetarian":
        if food_type in {"non-vegetarian", "egg"} or _contains_any(ingredients, ("chicken", "mutton", "fish", "prawn", "egg")):
            return "excluded", "Does not match the vegetarian preference."
        if food_type != "vegetarian":
            return "verify", "Dietary type is not recorded."
        return "eligible", None
    if preference == "eggetarian":
        if food_type == "vegetarian" and not _contains_any(ingredients, MEAT_TERMS):
            return "eligible", None
        if _contains_any(ingredients, ("egg",)) and not _contains_any(ingredients, MEAT_TERMS):
            return "eligible", None
        if food_type == "non-vegetarian":
            return "excluded", "This menu item is not confirmed as egg-only."
        return "verify", "Ingredients and dietary type need confirmation."
    if preference == "pescatarian":
        if food_type == "vegetarian":
            return "eligible", None
        if _contains_any(ingredients, ("fish", "prawn", "shrimp", "crab", "lobster")) and not _contains_any(ingredients, ("chicken", "mutton", "beef", "pork")):
            return "eligible", None
        if food_type == "non-vegetarian":
            return "excluded", "This item is not identified as fish or vegetarian."
        return "verify", "Confirm the protein source with restaurant staff."
    if preference == "vegan":
        if not food.get("ingredients"):
            return "verify", "Ingredients are not recorded, so vegan suitability cannot be confirmed."
        if _contains_any(ingredients, ANIMAL_TERMS):
            return "excluded", "A listed ingredient appears inconsistent with vegan preference."
        if food.get("dietary_verified") != 1:
            return "verify", "Vegan recipe and kitchen handling are not verified."
        return "eligible", None
    return "eligible", None


def _budget_bounds(budget: str) -> tuple[float, float] | None:
    return {
        "under_50": (0, 50),
        "50_100": (50, 100),
        "100_200": (100, 200),
        "200_300": (200, 300),
        "above_300": (300, float("inf")),
    }.get(budget)


def _within_budget(price: float, budget: str) -> bool:
    bounds = _budget_bounds(budget)
    if not bounds:
        return True
    lower, upper = bounds
    if budget == "above_300":
        return price > lower
    if budget == "200_300":
        return lower <= price <= upper
    return lower <= price < upper


def _matches_meal(food: dict[str, Any], meals: list[str]) -> bool:
    if not meals or "anytime" in meals:
        return True
    meal = str(food.get("meal_type") or "").lower()
    aliases = {
        "breakfast": ("breakfast",),
        "lunch": ("lunch",),
        "evening_snacks": ("snack",),
        "dinner": ("dinner",),
    }
    return any(term in meal for selected in meals for term in aliases.get(selected, (selected,)))


def _cuisine_match(food: dict[str, Any], cuisines: list[str]) -> tuple[str, float]:
    selected = [cuisine for cuisine in cuisines if cuisine != "all_cuisines"]
    if not selected:
        return "eligible", 0.5
    cuisine = str(food.get("cuisine") or "").lower().replace(" ", "_")
    if not cuisine:
        return "verify", 0.5
    aliases = {"tamil_nadu": {"tamil_nadu", "tamil"}, "south_indian": {"tamil_nadu", "south_indian"}}
    if any(cuisine in aliases.get(item, {item}) for item in selected):
        return "eligible", 1.0
    return "excluded", 0.0


def _numeric(food: dict[str, Any], field: str) -> float | None:
    try:
        value = food.get(field)
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _goal_score(food: dict[str, Any], goal: str | None) -> tuple[float, str]:
    if not goal:
        return 0.5, "No primary goal selected; goal match is neutral."
    calories = _numeric(food, "calories")
    protein = _numeric(food, "protein")
    carbs = _numeric(food, "carbs")
    if goal == "weight_loss":
        score = 0.5 if calories is None else (1 if calories <= 350 else 0.65 if calories <= 550 else 0.3)
    elif goal == "weight_gain":
        score = 0.5 if calories is None else (1 if calories >= 500 else 0.65 if calories >= 350 else 0.3)
    elif goal in {"muscle_building", "high_protein"}:
        score = 0.5 if protein is None else (1 if protein >= 25 else 0.65 if protein >= 15 else 0.3)
    elif goal == "heart_healthy":
        score = 0.5  # Saturated fat and sodium are not recorded for current items.
    elif goal in {"healthy_eating", "balanced_nutrition", "weight_maintenance"}:
        score = 0.5 if calories is None or protein is None else 0.75
        if carbs is not None and protein is not None:
            score = 0.75
    else:
        score = 0.5
    if goal == "heart_healthy":
        reason = "Heart-related nutrition match is neutral because sodium and saturated-fat measurements are unavailable."
    elif goal in {"muscle_building", "high_protein"} and protein is None:
        reason = "Protein match is neutral because protein is not listed."
    elif goal in {"weight_loss", "weight_gain"} and calories is None:
        reason = "Energy match is neutral because calories are not listed."
    else:
        reason = f"Primary goal: {goal.replace('_', ' ')}; ranking uses listed nutrients only."
    return score, reason


def _nutrition_score(food: dict[str, Any], preferences: list[str]) -> tuple[float, list[str]]:
    if not preferences:
        return 0.5, ["No nutrition preference selected; nutrition match is neutral."]
    scores = []
    reasons = []
    fields = {
        "low_calorie": ("calories", lambda v: 1 if v <= 350 else 0.65 if v <= 500 else 0.3, "calories"),
        "high_protein": ("protein", lambda v: 1 if v >= 25 else 0.65 if v >= 15 else 0.3, "protein"),
        "high_fibre": ("fiber", lambda v: 1 if v >= 8 else 0.65 if v >= 4 else 0.3, "fibre"),
        "lower_carbohydrate": ("carbs", lambda v: 1 if v <= 35 else 0.65 if v <= 60 else 0.3, "carbohydrates"),
        "less_oil": (None, None, "cooking oil"),
        "less_salt": ("sodium", lambda v: 1 if v <= 500 else 0.5, "sodium"),
        "balanced_nutrition": (None, None, "balanced nutrition"),
    }
    for preference in preferences:
        field, scorer, label = fields[preference]
        value = _numeric(food, field) if field else None
        if scorer is None or value is None:
            scores.append(0.5)
            reasons.append(f"{label.title()} data is not available; no advantage was assumed.")
        else:
            scores.append(scorer(value))
            reasons.append(f"{label.title()} uses the current menu's {food.get('nutrition_status') or 'unverified'} value.")
    return sum(scores) / len(scores), reasons


def _taste_score(food: dict[str, Any], tastes: list[str]) -> tuple[float, str]:
    active = [taste for taste in tastes if taste != "no_preference"]
    if not active:
        return 0.5, "Taste preference is neutral."
    description = " ".join(str(food.get(field) or "") for field in ("name", "description", "ingredients")).lower()
    keywords = {
        "spicy": ("spicy", "chilli", "pepper", "masala"),
        "mild": ("mild", "plain", "curd"),
        "sweet": ("sweet", "sugar", "kesari"),
        "less_oily": (),
        "less_salty": (),
    }
    values = [1.0 if keywords[taste] and any(word in description for word in keywords[taste]) else 0.5 for taste in active]
    return sum(values) / len(values), "Taste match is based only on words in the menu description; ask about preparation."


def _score_food(food: dict[str, Any], profile: dict[str, Any], cuisine_score: float) -> tuple[int, dict[str, float], list[str]]:
    goal_score, goal_reason = _goal_score(food, profile.get("goal"))
    nutrition_score, nutrition_reasons = _nutrition_score(food, profile["nutrition_preferences"])
    taste_score, taste_reason = _taste_score(food, profile["taste_preferences"])
    budget_score = 1.0 if profile["budget"] != "no_limit" else 0.5
    meal_score = 1.0 if profile["meal_preferences"] and "anytime" not in profile["meal_preferences"] else 0.5
    components = {
        "goal": round(goal_score, 2),
        "nutrition": round(nutrition_score, 2),
        "cuisine": round(cuisine_score, 2),
        "taste": round(taste_score, 2),
        "budget": round(budget_score, 2),
        "meal": round(meal_score, 2),
    }
    score = int(100 * (
        0.30 * goal_score + 0.25 * nutrition_score + 0.15 * cuisine_score
        + 0.10 * taste_score + 0.10 * budget_score + 0.10 * meal_score
    ) + 0.5)
    return score, components, [goal_reason, *nutrition_reasons, taste_reason]


def _food_card(food: dict[str, Any], score: int, components: dict[str, float], reasons: list[str]) -> dict[str, Any]:
    ingredients = [part.strip() for part in str(food.get("ingredients") or "").split(",") if part.strip()]
    allergens = [part.strip() for part in str(food.get("allergens") or "").split(",") if part.strip()]
    return {
        "id": food["id"],
        "food_id": food.get("food_slug") or str(food["id"]),
        "food_slug": food.get("food_slug"),
        "name": food["name"],
        "tamil_name": food.get("tamil_name"),
        "description": food.get("description"),
        "image_url": food.get("image_url") if str(food.get("image_url") or "").startswith("/images/") else None,
        "category": food.get("category"),
        "cuisine": food.get("cuisine"),
        "restaurant_name": food.get("restaurant_name") or "NutriOrder AI",
        "price": food.get("price"),
        "availability": food.get("availability_status") or "Listed in menu; live stock is not tracked",
        "food_type": food.get("food_type"),
        "meal_type": food.get("meal_type"),
        "ingredients": ingredients,
        "allergens": allergens,
        "allergen_status": _allergen_status(food),
        "serving_size": food.get("serving_size"),
        "preparation_method": food.get("preparation_method") or food.get("cooking_method"),
        "nutrition_source": food.get("nutrition_source"),
        "nutrition_confidence": food.get("nutrition_confidence"),
        "catalog_status": food.get("catalog_status"),
        "image_verified": bool(food.get("image_verified")),
        "nutrition": {
            "calories": food.get("calories"),
            "protein": food.get("protein"),
            "carbohydrates": food.get("carbs"),
            "fat": food.get("fat"),
            "fiber": food.get("fiber"),
            "sodium": food.get("sodium"),
            "status": food.get("nutrition_status") or "not recorded",
        },
        "match_percentage": score,
        "match_components": components,
        "match_explanation": reasons,
        "health_notice": "General menu matching only. Nutrition may be estimated; this is not medical advice or a guarantee of suitability.",
    }


def recommend(profile: dict[str, Any], foods: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    items = foods if foods is not None else load_menu()
    allergy_selected = bool(profile["allergies"] or profile.get("other_allergies"))
    budget_bounds = _budget_bounds(profile["budget"])
    cuisine_preferences = profile["cuisine_preferences"]
    candidates: list[tuple[int, dict[str, Any], dict[str, float], list[str]]] = []
    verification: list[dict[str, Any]] = []
    excluded = 0

    for food in items:
        if food.get("catalog_status") != "reference_pending_restaurant_confirmation" and not food.get("cuisine"):
            # The known project seed menu is Tamil Nadu cuisine; no other
            # cuisine classification is inferred for later manually added rows.
            if str(food.get("category") or "") in {"Breakfast", "Lunch", "Dinner", "Traditional Meals", "Biryani", "Non-Vegetarian", "Snacks", "Beverages", "Desserts"}:
                food = {**food, "cuisine": "Tamil Nadu"}
        if str(food.get("catalog_status") or "").lower() == "reference_pending_restaurant_confirmation" or str(food.get("availability_status") or "").lower() == "pending_confirmation":
            if profile["allergies"] or profile.get("other_allergies"):
                reason = "Traditional dish reference only; recipe and allergy/cross-contact status are not confirmed."
            else:
                reason = "Traditional dish reference only; restaurant recipe, price, exact image, and availability are not confirmed."
            verification.append({"id": food["id"], "name": food["name"], "image_url": food.get("image_url") if str(food.get("image_url") or "").startswith("/images/") else None, "price": food.get("price"), "reason": reason})
            continue
        if str(food.get("availability_status") or "").lower() in {"unavailable", "out_of_stock", "disabled"}:
            excluded += 1
            continue
        try:
            price = float(food.get("price"))
        except (TypeError, ValueError):
            excluded += 1
            continue
        if budget_bounds and not _within_budget(price, profile["budget"]):
            excluded += 1
            continue
        if not _matches_meal(food, profile["meal_preferences"]):
            excluded += 1
            continue

        conflicts = _allergy_conflicts(food, profile)
        if conflicts:
            excluded += 1
            continue

        if allergy_selected and food.get("allergens_verified") != 1:
            verification.append({"id": food["id"], "name": food["name"], "image_url": food.get("image_url") if str(food.get("image_url") or "").startswith("/images/") else None, "price": price, "reason": "Allergen declaration and cross-contact have not been verified by the restaurant."})
            continue

        diet_state, diet_reason = _diet_state(food, profile["dietary_preference"])
        if diet_state == "excluded":
            excluded += 1
            continue
        if diet_state == "verify":
            verification.append({"id": food["id"], "name": food["name"], "image_url": food.get("image_url") if str(food.get("image_url") or "").startswith("/images/") else None, "price": price, "reason": diet_reason or "Dietary details need confirmation."})
            continue

        cuisine_state, cuisine_score = _cuisine_match(food, cuisine_preferences)
        if cuisine_state == "excluded":
            excluded += 1
            continue
        if cuisine_state == "verify":
            verification.append({"id": food["id"], "name": food["name"], "image_url": food.get("image_url") if str(food.get("image_url") or "").startswith("/images/") else None, "price": price, "reason": "Cuisine is not recorded for this menu item."})
            continue

        score, components, reasons = _score_food(food, profile, cuisine_score)
        candidates.append((score, food, components, reasons))

    candidates.sort(key=lambda result: (result[0], float(result[1].get("rating") or 0)), reverse=True)
    cards = [_food_card(food, score, parts, reasons) for score, food, parts, reasons in candidates]
    best = cards[:3]
    alternatives = cards[3:8]

    rag_sources: list[str] = []
    rag_guidance: list[dict[str, str]] = []
    if cards:
        try:
            from rag.chatbot import _lexical_retrieve, _load_documents, retrieve_context

            # Only public menu dish names are embedded/retrieved. Do not send
            # user goals, medical selections, allergy names, or measurements.
            query = "NutriOrder food and nutrition reference: " + ", ".join(card["name"] for card in cards[:3])
            corpus = _load_documents()
            docs = retrieve_context(query, corpus)
            # User preference terms are matched locally only and are never sent
            # to external embedding services.
            local_terms = [profile.get("goal") or "", *profile.get("secondary_goals", []), *profile.get("nutrition_preferences", []), *profile.get("health_considerations", [])]
            docs.extend(_lexical_retrieve(" ".join(local_terms), corpus, limit=3))
            unique_docs = []
            seen_docs = set()
            for document in docs:
                identity = (document.get("metadata", {}).get("source"), document.get("page_content"))
                if identity not in seen_docs:
                    seen_docs.add(identity)
                    unique_docs.append(document)
            for document in unique_docs:
                source = str(document.get("metadata", {}).get("source", "NutriOrder knowledge base"))
                if source not in rag_sources:
                    rag_sources.append(source)
                if document.get("metadata", {}).get("kind") == "knowledge" and len(rag_guidance) < 3:
                    excerpt = re.sub(r"\s+", " ", str(document.get("page_content", ""))).strip()
                    if excerpt:
                        rag_guidance.append({"source": source, "excerpt": excerpt[:360] + ("…" if len(excerpt) > 360 else "")})
        except Exception:
            rag_sources = []

    health_notes = []
    for concern in profile["health_considerations"]:
        health_notes.append(f"{concern.replace('_', ' ').title()} selected: menu matching does not assess medical suitability; consult your healthcare professional for disease-specific choices.")
    if allergy_selected:
        health_notes.append("Allergy selections are active: foods without restaurant-verified allergen declarations were not recommended. Confirm ingredients and cross-contact directly with staff.")
    return {
        "success": True,
        "recommendation_method": "deterministic weighted menu match; hard filters applied before scoring",
        "score_weights": {"goal": 30, "nutrition": 25, "cuisine": 15, "taste": 10, "budget": 10, "meal": 10},
        "best_matches": best,
        "alternative_choices": alternatives,
        "requiring_verification": verification[:12],
        "filtered_count": excluded,
        "menu_count": len(items),
        "eligible_menu_ids": sorted(food.get("id") for _, food, _, _ in candidates if food.get("id") is not None),
        "rag_sources": rag_sources,
        "rag_guidance": rag_guidance,
        "health_notices": health_notes,
        "disclaimer": "NutriMatch provides general menu personalization, not medical advice. Nutrition values may be estimates. Confirm ingredients and allergen cross-contact with the restaurant; follow qualified professional advice for medical dietary needs.",
        "profile_saved": False,
    }


def chat_reply(message: str, profile_data: Any) -> dict[str, Any]:
    if not isinstance(message, str) or not message.strip() or len(message.strip()) > 500:
        raise ValueError("Enter a message of 1–500 characters.")
    profile = validate_profile(profile_data)
    text = message.lower()
    if "weight loss" in text or "lose weight" in text:
        profile["goal"] = "weight_loss"
    elif "weight gain" in text:
        profile["goal"] = "weight_gain"
    if "high protein" in text or "protein-rich" in text:
        profile["nutrition_preferences"] = list(dict.fromkeys(profile["nutrition_preferences"] + ["high_protein"]))
    if "vegetarian" in text and "non-vegetarian" not in text:
        profile["dietary_preference"] = "vegetarian"
    result = recommend(profile)
    if result["best_matches"]:
        names = ", ".join(item["name"] for item in result["best_matches"][:3])
        answer = f"Based on the current menu and the preferences available in this session, you could explore: {names}. These are menu matches, not medical recommendations."
    elif result["requiring_verification"]:
        answer = "I found menu items that need ingredient or dietary verification before I can suggest them. Please confirm details with restaurant staff."
    else:
        answer = "I couldn't find menu items matching those restrictions. You can adjust the questionnaire or ask the restaurant about current options."
    return {
        "success": True,
        "answer": answer,
        "recommendations": result,
        "sources": result.get("rag_sources", []),
        "mode": "deterministic_menu_rag_context" if result.get("rag_sources") else "deterministic_menu_only",
        "profile_saved": False,
    }