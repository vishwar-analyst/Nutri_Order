# Nutrition Data and Uncertainty

Report calories, protein, carbohydrate, fat, fibre, and sodium only when the exact field exists for the selected restaurant item. Missing values must be described as “not available,” never estimated from dish names in a personalized card. Menu records with `nutrition_status=estimated` are approximate menu values, not verified or laboratory measurements. The curated food reference gives broad recipe-based ranges for stated portions and must remain explicitly labeled `illustrative_estimate_not_verified`.

A nutrition comparison is meaningful only with serving context. Portion size, ingredients, cooking oil, ghee, salt, recipe, and side dishes change values. Total fat is not saturated or trans fat. Carbohydrate amounts do not predict an individual's glucose response. Sodium is not included in calories/macros and must not be inferred from taste or dish names. Fibre and sodium columns are currently nullable/unrecorded for the sample menu. Record serving size and source when restaurant-verified data becomes available.

Recommended record metadata: `food_name`, `serving_size`, `calories`, `protein`, `carbohydrates`, `fat`, `fiber`, `sodium`, `nutrition_status`, `source`, `updated_at`. Use null when unavailable and label all estimates.
