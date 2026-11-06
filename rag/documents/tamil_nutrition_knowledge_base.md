# NutriOrder AI — Tamil Nadu Food and Nutrition Knowledge Base

**Document type:** Curated general-information reference for restaurant recommendations  
**Scope:** Tamil Nadu cuisine, menu navigation, approximate nutrition, and safe conversational guidance  
**Important:** This document is not a clinical nutrition database. Recipe, serving size, oil, salt, ingredient brands, and cooking method change nutrition substantially. Values below are broad, illustrative estimates for the stated serving only; they are not laboratory analysis, verified NutriOrder menu data, or a substitute for an item's recipe card. Confirm ingredients and current preparation with the restaurant before making an allergy or medical-diet decision.

## Retrieval and metadata guide

Each food entry is intended to be a self-contained retrieval unit. Keep its food name, serving size, estimates, preparation, dietary type, and suitability caveat together when chunking. Suggested metadata fields for an indexed record:

- `food_name`: canonical name, for example `Ragi dosa`.
- `food_category`: breakfast, rice dish, meal, side, snack, beverage, or dessert.
- `health_goal`: general, weight_management, blood_glucose_awareness, heart_health, sodium_awareness, or none_assigned. These are retrieval topics, not a medical endorsement.
- `dietary_type`: vegetarian, vegan_if_recipe_confirmed, egg, or non_vegetarian.
- `meal_type`: breakfast, lunch, dinner, snack, or any.
- `ingredients`: known recipe ingredients; use `recipe varies` if not confirmed.
- `allergens`: known allergens or `unknown—confirm with restaurant`; never infer allergen absence.
- `serving_size`: the exact household or gram estimate used for the nutrition range.
- `nutrition_status`: `illustrative_estimate_not_verified` unless measured and approved for the exact recipe.
- `source`: `NutriOrder curated general food reference`.

The current NutriOrder RAG loader reads Markdown and TXT files from `rag/documents/`, then chunks text and assigns source/kind metadata. The metadata labels above are included in each record as text so the current lexical retriever can search them. A future ingestion pipeline may extract them as native vector-store metadata. Do not replace these estimates with verified menu values unless the recipe and serving have actually been measured.

## 1. Introduction to NutriOrder AI

NutriOrder AI helps customers explore Tamil Nadu restaurant food and find options that may fit preferences, goals, and ingredient constraints. A chatbot can explain common ingredients, compare menu descriptions, and suggest questions to ask restaurant staff. It should use the live menu as the authority for availability, price, ingredients, and any verified nutrition facts. This general reference provides context only; it must not override a restaurant's current recipe or a customer's clinician-provided plan.

A “potentially suitable” description is a prompt for an informed choice, not a guarantee. A food's name alone cannot establish its exact ingredients, carbohydrate amount, sodium, allergen status, glycemic response, or suitability for an individual.

## 2. Tamil Nadu restaurant food categories

- **Steamed breakfast foods:** idli, idiyappam, and some forms of puttu. Steaming generally uses less added cooking fat than pan-frying, but accompaniments and portions still matter.
- **Griddle and fermented foods:** dosa, ragi dosa, and uthappam. Oil, batter composition, fermentation, toppings, and size vary.
- **Porridge and one-pot dishes:** pongal, sambar rice, and rasam rice. Tempering, ghee, rice-to-pulse ratio, and serving size can change nutrition.
- **Rice varieties:** curd rice, lemon rice, keerai rice, and other seasoned rice. Oil, salt, nuts, dairy, and rice portion vary.
- **Meals and curries:** vegetable meals, fish curry, chicken biryani, egg curry, and side dishes. Meal composition and restaurant recipes are especially variable.
- **Snacks and fresh sides:** sundal, sprouts, fruit salad, and salads. Added salt, coconut, dressing, chutney, sugar, and food handling matter.
- **Breads and steamed rice noodles:** chapati, appam, and idiyappam, typically paired with curries or gravies that determine much of the complete meal's nutrition.

## 3–4. Traditional Tamil Nadu food database: ingredients and preparation

Nutrition estimates below apply to the stated serving and recipe assumptions. They are intentionally shown as ranges, not exact values. “Carbohydrate” is total carbohydrate; fibre is included within that total. Ranges are approximate common-recipe estimates and may not add mathematically at their endpoints because recipes differ. Dietary labels describe common versions only; verify the actual recipe.

### Idli
- **Metadata:** `food_name=idli`; `food_category=steamed_breakfast`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=breakfast`; `allergens=possible urad dal cross-contact; recipe-specific confirmation required`.
- **Serving and estimates:** 2 medium idlis (about 100–120 g), without chutney/sambar: **130–180 kcal; protein 4–6 g; carbohydrate 26–34 g; fat 1–3 g; fibre 2–4 g**. Illustrative, not verified.
- **Common ingredients and preparation:** fermented rice and urad-dal batter, steamed in moulds. Batter ratio and size vary. Common accompaniments include sambar and coconut or tomato chutney; these are not included in the estimate.
- **Considerations:** steaming usually avoids substantial cooking oil. Idli is still a rice-and-lentil carbohydrate food; count the serving and accompaniments according to personal needs. Not inherently suitable for every blood-glucose plan.

### Plain dosa
- **Metadata:** `food_name=plain dosa`; `food_category=griddle_breakfast`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=breakfast`.
- **Serving and estimates:** 1 medium plain dosa (about 100–130 g, prepared with a modest amount of oil): **170–260 kcal; protein 4–7 g; carbohydrate 28–40 g; fat 4–10 g; fibre 1–3 g**. Illustrative, not verified.
- **Common ingredients and preparation:** fermented rice-and-urad-dal batter spread thin on a hot griddle; oil or ghee may be used. Masala filling and sides are excluded.
- **Considerations:** large, crisp, ghee-roast, or oil-heavy dosas can contain considerably more energy and fat. Ask whether batter or toppings contain an ingredient of concern.

### Ragi dosa
- **Metadata:** `food_name=ragi dosa`; `food_category=griddle_breakfast`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=breakfast`.
- **Serving and estimates:** 1 medium dosa (about 120–150 g, recipe may include rice or lentil batter): **170–280 kcal; protein 4–8 g; carbohydrate 28–45 g; fat 4–11 g; fibre 3–7 g**. Illustrative, not verified.
- **Common ingredients and preparation:** finger-millet flour or batter, often mixed with rice/urad batter, water, spices, and sometimes onion; cooked on a griddle with oil.
- **Considerations:** ragi contributes fibre, but ragi dosa is not automatically low-carbohydrate or diabetes-friendly. Flour proportions, size, oil, and sides matter.

### Ven pongal
- **Metadata:** `food_name=ven pongal`; `food_category=rice_pulse_dish`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=breakfast`.
- **Serving and estimates:** 1 bowl (about 250 g), recipe with rice, moong dal and moderate tempering: **300–450 kcal; protein 8–13 g; carbohydrate 45–65 g; fat 8–18 g; fibre 3–7 g**. Illustrative, not verified.
- **Common ingredients and preparation:** rice and split moong dal cooked soft with pepper, cumin, ginger, curry leaves, and tempering that may use ghee, oil, cashews, and salt.
- **Considerations:** ghee and cashews can raise fat and energy; portion and rice-to-dal ratio vary. Ask about ghee, cashew, and salt when relevant.

### Uthappam
- **Metadata:** `food_name=uthappam`; `food_category=griddle_breakfast`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=breakfast`.
- **Serving and estimates:** 1 medium vegetable uthappam (about 160–200 g): **220–360 kcal; protein 6–10 g; carbohydrate 35–55 g; fat 5–14 g; fibre 3–7 g**. Illustrative, not verified.
- **Common ingredients and preparation:** fermented rice-and-urad batter cooked thicker than dosa, often topped with onion, tomato, green chilli, or other vegetables; griddle oil varies.
- **Considerations:** vegetable topping does not remove the batter's carbohydrate. Size, oil, and chutney/sambar can change the total.

### Idiyappam
- **Metadata:** `food_name=idiyappam`; `food_category=steamed_breakfast`; `health_goal=general`; `dietary_type=vegan_if_recipe_confirmed`; `meal_type=breakfast`.
- **Serving and estimates:** 2 nests (about 150–180 g), plain: **190–300 kcal; protein 3–6 g; carbohydrate 42–65 g; fat 1–5 g; fibre 1–3 g**. Illustrative, not verified.
- **Common ingredients and preparation:** rice flour, water, and salt formed into fine strands and steamed. Coconut milk, sweetened coconut, or curry served alongside is excluded.
- **Considerations:** usually rice-flour based and carbohydrate-rich. Confirm flour, salt, and accompaniments.

### Appam
- **Metadata:** `food_name=appam`; `food_category=fermented_breakfast`; `health_goal=general`; `dietary_type=vegan_if_recipe_confirmed`; `meal_type=breakfast`.
- **Serving and estimates:** 2 medium appams (about 160–200 g), plain: **220–340 kcal; protein 4–7 g; carbohydrate 45–65 g; fat 2–8 g; fibre 1–4 g**. Illustrative, not verified.
- **Common ingredients and preparation:** fermented rice batter, sometimes with coconut milk or a small amount of sugar, cooked in a rounded pan. Stew or curry is excluded.
- **Considerations:** recipe sweetness, coconut milk, size, and side dish affect energy and fat. Ask about dairy or coconut ingredients if relevant.

### Chapati
- **Metadata:** `food_name=chapati`; `food_category=flatbread`; `health_goal=general`; `dietary_type=vegan_if_recipe_confirmed`; `meal_type=any`.
- **Serving and estimates:** 2 medium chapatis (about 100–120 g total), without ghee or curry: **200–300 kcal; protein 6–10 g; carbohydrate 36–52 g; fat 3–8 g; fibre 4–8 g**. Illustrative, not verified.
- **Common ingredients and preparation:** whole-wheat flour, water, and sometimes salt; rolled and cooked on a hot griddle. Added oil/ghee is recipe-dependent.
- **Considerations:** contains wheat/gluten. Size, flour type, added fat, and curry portions matter; not appropriate for a person who must avoid wheat/gluten unless a safe alternative is confirmed.

### Sambar rice
- **Metadata:** `food_name=sambar rice`; `food_category=rice_dish`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=lunch`.
- **Serving and estimates:** 1 bowl (about 300 g), rice cooked with lentil-and-vegetable sambar: **300–470 kcal; protein 8–14 g; carbohydrate 50–75 g; fat 4–13 g; fibre 5–10 g**. Illustrative, not verified.
- **Common ingredients and preparation:** rice, toor dal, mixed vegetables, tamarind, sambar spices, and tempering with oil; salt varies.
- **Considerations:** includes both rice and lentils; carbohydrate, sodium, and oil depend on recipe and bowl size. Extra vegetables or dal do not make a large rice serving carbohydrate-free.

### Curd rice
- **Metadata:** `food_name=curd rice`; `food_category=rice_dish`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=lunch`.
- **Serving and estimates:** 1 bowl (about 250 g), rice mixed with plain curd and modest tempering: **250–400 kcal; protein 6–11 g; carbohydrate 40–62 g; fat 5–14 g; fibre 1–3 g**. Illustrative, not verified.
- **Common ingredients and preparation:** cooked rice, yogurt/curd, and optional milk, mustard, curry leaves, ginger, chilli, and oil; sometimes garnished with pomegranate or cucumber.
- **Considerations:** contains dairy and rice. Curd type, rice portion, tempering, and added milk alter values. Do not assume it is low in carbohydrate or suitable for lactose intolerance.

### Lemon rice
- **Metadata:** `food_name=lemon rice`; `food_category=seasoned_rice`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=lunch`.
- **Serving and estimates:** 1 bowl (about 250 g): **300–470 kcal; protein 5–9 g; carbohydrate 48–72 g; fat 8–20 g; fibre 2–6 g**. Illustrative, not verified.
- **Common ingredients and preparation:** cooked rice tossed with lemon juice, turmeric, mustard seeds, curry leaves, chilli, oil, and sometimes peanuts or cashews.
- **Considerations:** nuts may be present; confirm allergen handling. Oil, salt, nuts, and rice portion are variable. Lemon flavour does not make the dish low-sodium.

### Vegetable meals (Tamil-style thali)
- **Metadata:** `food_name=vegetable meals`; `food_category=complete_meal`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=lunch`.
- **Serving and estimates:** 1 restaurant plate with about 1 cup cooked rice, 2–3 vegetable/dal sides, rasam or sambar, and a small curd portion: **550–900 kcal; protein 14–28 g; carbohydrate 85–140 g; fat 12–32 g; fibre 10–20 g**. Illustrative, not verified; actual plate can be outside this range.
- **Common ingredients and preparation:** rice, vegetables, dal, sambar/rasam, poriyal, kootu, pickle, papad, and sometimes curd or dessert; coconut, oil, ghee, and salt use vary by kitchen.
- **Considerations:** ask what sides are included and whether rice, pickle, papad, or dessert can be adjusted. A vegetarian meal can still be high in sodium, carbohydrate, or saturated fat depending on preparation and portions.

### Keerai rice
- **Metadata:** `food_name=keerai rice`; `food_category=seasoned_rice`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=lunch`.
- **Serving and estimates:** 1 bowl (about 250–300 g), rice mixed with greens: **280–450 kcal; protein 6–12 g; carbohydrate 45–70 g; fat 6–17 g; fibre 4–9 g**. Illustrative, not verified.
- **Common ingredients and preparation:** cooked rice, spinach or other local greens, spices, onion, and tempering; recipe may add dal, coconut, sesame, or ghee.
- **Considerations:** greens contribute micronutrients and fibre, but do not determine the rice portion or sodium. “Keerai” refers to different greens; ask which one and how it is cooked.

### Rasam rice
- **Metadata:** `food_name=rasam rice`; `food_category=rice_dish`; `health_goal=general`; `dietary_type=vegetarian`; `meal_type=lunch_or_dinner`.
- **Serving and estimates:** 1 bowl (about 300 g), rice with rasam: **250–420 kcal; protein 5–10 g; carbohydrate 48–75 g; fat 3–12 g; fibre 2–6 g**. Illustrative, not verified.
- **Common ingredients and preparation:** cooked rice with thin tamarind/tomato broth, spices, and tempering; salt and added fat vary.
- **Considerations:** rasam's light broth does not make the complete rice serving low in carbohydrate. Ask about salt and portion size when sodium or carbohydrate is a concern.

### Chicken biryani
- **Metadata:** `food_name=chicken biryani`; `food_category=rice_main`; `health_goal=general`; `dietary_type=non_vegetarian`; `meal_type=lunch_or_dinner`.
- **Serving and estimates:** 1 restaurant plate (about 350–450 g, including one average chicken portion): **550–900 kcal; protein 25–45 g; carbohydrate 65–115 g; fat 18–40 g; fibre 2–7 g**. Illustrative, not verified.
- **Common ingredients and preparation:** rice, chicken, onion, yogurt or other marinade, spices, oil/ghee, herbs, and salt; recipe can include nuts, fried onions, or colouring.
- **Considerations:** portion, skin, oil/ghee, cut of chicken, and accompaniments vary widely. Ask about nuts, dairy marinade, sodium, and preparation if relevant. Do not describe biryani as a guaranteed weight-loss or heart-healthy choice.

### Fish curry with rice
- **Metadata:** `food_name=fish curry with rice`; `food_category=rice_and_curry`; `health_goal=general`; `dietary_type=non_vegetarian`; `meal_type=lunch_or_dinner`.
- **Serving and estimates:** 1 meal with about 1 cup cooked rice (150–180 g) and one fish portion with curry (about 100–140 g fish): **400–700 kcal; protein 22–40 g; carbohydrate 48–80 g; fat 8–28 g; fibre 2–7 g**. Illustrative, not verified.
- **Common ingredients and preparation:** fish, tamarind or tomato, spices, curry leaves, and oil; some regional recipes use coconut or coconut milk. Rice estimate is included.
- **Considerations:** fish type, edible portion, frying, gravy, coconut, and salt affect values. Contains fish; avoid if fish allergy is present. Verify cross-contact and exact fish species.

### Egg omelette
- **Metadata:** `food_name=egg omelette`; `food_category=egg_side`; `health_goal=general`; `dietary_type=egg`; `meal_type=any`.
- **Serving and estimates:** 2-egg omelette (about 110–140 g, modest oil, no bread): **180–300 kcal; protein 12–16 g; carbohydrate 1–5 g; fat 13–23 g; fibre 0–1 g**. Illustrative, not verified.
- **Common ingredients and preparation:** eggs, onion, chilli, herbs, salt, and oil; cheese or extra oil may be added.
- **Considerations:** contains egg. Cooking fat, cheese, and salt change the profile. A side of bread or rice is not included.

### Egg curry with rice
- **Metadata:** `food_name=egg curry with rice`; `food_category=rice_and_curry`; `health_goal=general`; `dietary_type=egg`; `meal_type=lunch_or_dinner`.
- **Serving and estimates:** meal with 2 eggs, about 1 cup cooked rice, and curry gravy: **450–750 kcal; protein 18–28 g; carbohydrate 55–90 g; fat 14–35 g; fibre 3–9 g**. Illustrative, not verified.
- **Common ingredients and preparation:** boiled eggs, onion/tomato or coconut-based gravy, spices, oil, and salt; rice is included.
- **Considerations:** egg, gravy base, and oil vary. Ask whether the curry contains dairy, nuts, or coconut if a restriction applies; these are recipe-dependent.

### Sundal
- **Metadata:** `food_name=sundal`; `food_category=snack`; `health_goal=general`; `dietary_type=vegan_if_recipe_confirmed`; `meal_type=snack`.
- **Serving and estimates:** 1 cup (about 150 g) cooked chickpea or legume sundal with modest tempering: **180–320 kcal; protein 8–15 g; carbohydrate 28–48 g; fat 3–12 g; fibre 7–14 g**. Illustrative, not verified.
- **Common ingredients and preparation:** boiled chickpeas, peas, or another legume, with mustard, curry leaves, chilli, and sometimes coconut; salt and oil vary.
- **Considerations:** legumes provide protein and fibre but also carbohydrate. Legume type, cup size, coconut, and salt matter. Confirm which legume is used for allergy or intolerance concerns.

### Sprouts salad
- **Metadata:** `food_name=sprouts salad`; `food_category=snack_or_side`; `health_goal=general`; `dietary_type=vegan_if_recipe_confirmed`; `meal_type=snack_or_any`.
- **Serving and estimates:** 1 bowl (about 180–220 g), mixed sprouts and raw vegetables, without creamy dressing: **120–260 kcal; protein 8–16 g; carbohydrate 18–38 g; fat 1–9 g; fibre 6–13 g**. Illustrative, not verified.
- **Common ingredients and preparation:** mung or other sprouts, onion, tomato, cucumber, lemon, herbs, and spices; dressing, peanuts, or sev may be added. Preparation may use raw or cooked sprouts.
- **Considerations:** ask whether sprouts are cooked and what dressing/toppings are included. Raw sprouts can carry food-safety risk; people at higher risk from foodborne illness should seek safer preparation advice from a qualified professional and restaurant.

### Fruit salad
- **Metadata:** `food_name=fruit salad`; `food_category=snack_or_dessert`; `health_goal=general`; `dietary_type=vegan_if_recipe_confirmed`; `meal_type=snack`.
- **Serving and estimates:** 1 cup (about 150–200 g) mixed fresh fruit, no syrup, cream, or ice cream: **80–180 kcal; protein 1–3 g; carbohydrate 20–42 g; fat 0–2 g; fibre 3–8 g**. Illustrative, not verified.
- **Common ingredients and preparation:** chopped seasonal fruit; restaurant versions may add syrup, honey, sugar, cream, yogurt, nuts, or ice cream.
- **Considerations:** fruit type and portion affect carbohydrate. Ask about toppings, added sweeteners, and shared utensils if a restriction applies. “Natural” does not mean unlimited for every meal plan.

## 5. Using nutrition information responsibly

Calories and macronutrients depend on the exact ingredient weights and cooked yield. Restaurant portions may differ substantially from the serving described above. Oil and ghee add energy; coconut, nuts, dairy, and meat change fat and protein; rice, flour, and other grains contribute most of the carbohydrate in many dishes. Salt affects sodium but is not represented by calories or the macronutrients shown here. Fibre estimates are particularly sensitive to grain refinement, vegetable quantity, and portion size.

Use the live NutriOrder menu's nutrition fields only when explicitly marked verified for that specific serving. If no verified value exists, say it is unavailable or use the clearly labelled illustrative range with its serving caveat. Do not turn an estimate into an exact number or rank dishes using unverified values as if they were measured.

## 6. Weight-loss food considerations

Weight management is individual and depends on overall eating pattern, health, activity, and other factors. The chatbot may offer neutral portion-aware ideas, not a prescription or a promise of weight loss. Customers may consider a smaller rice or bread portion, a vegetable-rich side, a steamed option, or a preparation with less added oil if the restaurant can confirm it. Ask about fullness, preferences, and the actual menu; do not shame, moralize, or assume a person's body-size goal. Do not label a food “weight-loss food” solely because it is steamed, vegetarian, or described as healthy.

## 7. Weight-gain food considerations

Weight gain goals may require individualized energy and protein planning. The chatbot can identify menu options that include energy- and protein-containing ingredients—such as meals with dal, egg, fish, chicken, dairy, or legumes—when these align with the customer's preferences and restrictions. It must not prescribe quantities, supplements, or a clinical plan. Suggest a qualified dietitian or healthcare professional for unintentional weight change, undernutrition concerns, or medically directed weight goals. Confirm recipe and portion before making comparisons.

## 8. Diabetes and blood-glucose considerations

Do not call a dish “diabetes-safe,” “sugar-free,” or guaranteed to control blood glucose. Rice, rice flour, wheat, millet, fruit, and legumes all contribute carbohydrate; the amount and response vary by recipe, portion, medication, and individual. Neutral assistance may include identifying the grain or starch, pointing out portion uncertainty, and asking whether the customer follows a clinician-provided meal plan. Some people may prefer pairing a starch portion with protein- or fibre-containing foods, but do not present this as treatment or a universal rule. Encourage customers to follow their healthcare professional's individualized advice. Do not advise changes to insulin, medication, or glucose monitoring.

## 9. Heart-health considerations

The chatbot may help customers ask about cooking fat, saturated fat sources, portion size, vegetables, and sodium, but it must not promise a heart benefit or prescribe a heart diet. Preparation matters: deep-frying, generous ghee, creamy gravies, and processed additions can change a dish considerably. Offer comparisons only when ingredients and portions are known. Refer disease-specific questions, including cholesterol or heart-failure restrictions, to the customer's clinician or qualified dietitian.

## 10. High blood pressure and sodium awareness

Salt, pickles, papad, seasoning mixes, sauces, and restaurant gravies can contribute sodium; this database has no measured sodium values. Do not call a dish “low sodium” unless the exact recipe and serving have verified sodium data. The chatbot can suggest asking whether less salt or a sauce/gravy on the side is possible, while noting that the kitchen may not be able to guarantee a specific amount. Do not recommend potassium-rich foods or salt substitutes as a treatment: they can be unsafe for some people, including those with kidney conditions or particular medicines. Follow clinician-provided sodium or fluid limits.

## 11. Low blood pressure considerations

Low blood pressure has different causes and is not automatically treated with extra salt or a particular food. The chatbot must not advise increasing salt, fluids, caffeine, or medication without clinical direction. For dizziness, fainting, severe weakness, confusion, chest pain, or difficulty breathing, encourage urgent medical help according to local emergency services. For non-urgent recurring symptoms, suggest a healthcare professional. Food suggestions should be ordinary menu information only, not treatment.

## 12. Vegetarian and non-vegetarian recommendations

- **Vegetarian:** common examples include idli, dosa, pongal, uthappam, sambar rice, curd rice, lemon rice, vegetable meals, keerai rice, rasam rice, sundal, and fruit salad. Recipes can contain dairy, ghee, honey, or animal-derived ingredients, and shared equipment may be used. Verify if strict vegetarian or vegan status matters.
- **Vegan:** do not assume a dish is vegan from its name. Confirm ghee, butter, curd, milk, cream, honey, and cooking surfaces. Plain rice-based items may still be prepared with ghee or shared utensils.
- **Egg:** omelette and egg curry contain egg. Confirm whether a sauce or side contains other restricted ingredients.
- **Non-vegetarian:** chicken biryani, fish curry, and some egg dishes are examples. Confirm the meat/fish type, preparation, stock or marinade, and shared equipment. Fish and shellfish are distinct allergens; never infer one from the other.

## 13. Food allergies and dietary restrictions

Allergen safety requires the restaurant's direct confirmation. The current menu/database may not include a complete ingredient or cross-contact record. Ask the customer which allergen or restriction applies, then clearly disclose if ingredients or kitchen handling are unknown. Do not claim “allergen-free,” “safe,” or “no cross-contamination” without a reliable restaurant process and item-specific confirmation. If the restaurant cannot confirm safety, advise the customer not to rely on the chatbot's estimate and to contact staff directly.

Potentially relevant ingredients in common dishes include wheat/gluten (chapati and some batters), dairy (curd rice, ghee, yogurt marinades, creamy sides), egg, fish, peanuts or tree nuts (some lemon rice, pongal, biryani, chutneys), sesame, soy, and legumes. This list is illustrative, not exhaustive; recipes and cross-contact vary. Also confirm vegetarian/vegan needs, religious restrictions, intolerances, and texture requirements. Do not equate an intolerance with an allergy or give medical advice about reactions. For suspected severe allergic reaction, encourage immediate emergency care.

## 14. Breakfast, lunch, dinner, and snack navigation

- **Breakfast:** idli, dosa, ragi dosa, pongal, uthappam, idiyappam, appam, and chapati. Ask about portion, cooking fat, batter ingredients, and sides.
- **Lunch:** vegetable meals, sambar rice, curd rice, lemon rice, keerai rice, rasam rice, chicken biryani, fish curry with rice, and egg curry with rice. Ask what is included and clarify rice, gravy, salt, and oil.
- **Dinner:** any available grain, vegetable, pulse, egg, fish, or chicken dishes can be compared using the current menu; the chatbot must not assume a food is inherently better at a particular time. Check serving size and customer's clinical advice.
- **Snacks:** sundal, sprouts salad, and fruit salad. Ask about legume type, raw/cooked sprouts, toppings, dressing, salt, and added sugar.

## 15. Frequently asked customer questions

**Q: Which item has the fewest calories?**  
A: I can compare only items with nutrition values for the same verified serving. The values in this general guide are estimates and may not reflect this restaurant's portions. Would you like me to compare the live menu items with available nutrition data?

**Q: Is ragi dosa safe for diabetes?**  
A: I can't determine whether it is safe for you. Ragi dosa still contains carbohydrate, and the amount depends on batter, size, oil, and sides. Please follow your clinician's plan; I can help check the restaurant's ingredients or serving details.

**Q: Is curd rice good for high blood pressure?**  
A: I can't assess your individual diet, and we don't have verified sodium values for this serving. Ask the restaurant about salt and portion size, and follow any sodium guidance from your healthcare professional.

**Q: Which food is best for weight loss?**  
A: There isn't one best food for everyone. I can show portion and preparation details for available options and help you compare them without promising a weight-loss result.

**Q: Does the lemon rice contain peanuts?**  
A: Some recipes include peanuts, but I can't confirm this restaurant's recipe or cross-contact. Please ask the restaurant directly before ordering if peanuts are a concern.

**Q: Is the vegetable meals plate vegan?**  
A: Not necessarily. It may include curd, ghee, or other dairy ingredients. Please confirm each side and the cooking method with the restaurant.

**Q: Can you recommend food for low blood pressure?**  
A: I can describe menu ingredients, but food is not a substitute for evaluation or treatment. I can't recommend extra salt or a treatment plan. Please consult a healthcare professional, especially if symptoms recur.

**Q: How much protein is in this biryani?**  
A: I can provide an approximate range only if the serving size is stated. The amount varies with the rice-to-chicken ratio and portion; this guide's estimate is not a measurement of the restaurant's biryani.

## 16. Chatbot response guidelines

1. Retrieve current menu data first for availability, price, listed ingredients, and nutrition status. Clearly distinguish verified item data from this general reference.
2. Use the canonical dish name and mention the serving size associated with any estimate. Preserve units and the fact that values are approximate.
3. For health-goal requests, give cautious options and explain relevant uncertainty; never promise a health outcome or rank food as medically best.
4. Ask a concise follow-up when a relevant allergy, ingredient restriction, dietary type, serving size, or preference is missing. Do not interrogate the customer unnecessarily.
5. For allergies, disclose unknown ingredients and cross-contact plainly and direct the customer to restaurant staff. Never infer absence from an incomplete menu.
6. If evidence is missing or conflicting, say so and do not fill gaps with guesses. Do not invent ingredients, nutrition facts, portion sizes, menu availability, or preparation methods.
7. Use inclusive, non-judgmental language. Do not shame weight, food choices, culture, or health status.
8. Decline diagnosis, treatment, medication changes, and disease-specific diet prescriptions. Refer those decisions to a qualified healthcare professional.
9. Keep an answer concise: direct response, useful evidence, important caveat, and next step. Cite the item or reference source when available.
10. Use urgent-care language when the customer reports potentially serious symptoms or a severe allergic reaction; do not continue ordinary food recommendations as if it were routine.

## 17. Medical safety and nutrition disclaimer

This knowledge base provides general food and nutrition information for menu exploration only. It is not medical advice, diagnosis, treatment, or an individualized diet prescription. Nutrition values are estimates for representative serving assumptions and have not been verified for NutriOrder restaurant recipes. Recipes, portions, ingredients, allergens, and preparation can change without notice. Customers with diabetes, cardiovascular disease, blood-pressure concerns, kidney disease, food allergies, pregnancy-related dietary needs, or other medical conditions should use advice from a qualified healthcare professional and confirm ingredients directly with the restaurant. In a medical emergency, contact local emergency services.
