# Dietary Preference Matching

Use the live menu `food_type` and ingredient fields as recorded facts, but expose unknown recipe details. Vegetarian, non-vegetarian, egg-based, vegan, and pescatarian labels should not be inferred solely from cuisine or dish name. Current menu dietary labels may be incomplete; strict patterns without adequate ingredient information go to a verification list.

Vegan suitability requires checking dairy, ghee, butter, yogurt, honey, egg, meat/fish ingredients, and preparation handling. Eggetarian means egg may be included but meat and fish should not pass. Pescatarian accepts fish/seafood or confirmed vegetarian choices, not meat/poultry. For vegetarian requests, exclude menu rows marked non-vegetarian or with known egg/meat/fish ingredients.

Cuisine preferences and meal type are matched only against recorded database values. The demo menu is labeled Tamil Nadu cuisine by known project context; other cuisines are not claimed unless recorded. Meal availability reflects listed meal type; actual live stock is not currently tracked.
