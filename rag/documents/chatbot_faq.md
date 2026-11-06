# NutriMatch and NutriBot FAQ

**Are NutriMatch scores medical suitability scores?** No. They are preference-match percentages from fixed weights; allergy and strict dietary filters are applied first. A score does not guarantee safety or health benefit.

**Are nutrition values verified?** Not necessarily. Existing seeded menu values are marked estimated. Missing fibre, sodium, serving size, allergens, or stock are shown unavailable/not recorded. Do not infer zero.

**Does selecting an allergy guarantee safety?** No. Known conflicts are excluded; dishes with unknown ingredient/cross-contact details require direct confirmation from restaurant staff. Unverified items are not recommended alternatives.

**Are health preferences stored?** No. The current profile/recommendation/chat requests are processed in memory for the request/session and are not written to a user profile or recommendation history.

**Does the chatbot use Gemini?** Existing NutriBot can use Gemini when configured, but deterministic NutriMatch ranking does not depend on external AI. It uses current menu data and optional retrieved knowledge for context. Without configured credentials, recommendations still work using local rules.

**Can NutriMatch tell me what to eat for diabetes, blood pressure, kidney disease, or heart disease?** It provides general menu facts only. It cannot assess an individual's medical needs. Follow a qualified healthcare professional's advice.
