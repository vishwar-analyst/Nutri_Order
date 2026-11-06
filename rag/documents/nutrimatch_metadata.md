# NutriMatch Retrieval Metadata

Recommended Chroma document metadata: `source`, `kind`, `food_name`, `food_category`, `health_goal`, `dietary_type`, `ingredients`, `allergens`, `cuisine`, `meal_type`, `nutrition_status`, `serving_size`. Keep values scalar/string compatible with Chroma metadata. For a live menu row, use the food ID as a separate stable field and keep current availability/price authoritative in SQLite. Current generic Markdown loading attaches source and kind only; metadata labels inside documents are text until a future ingestion parser extracts them.

Do not put user profiles, allergies, health selections, age, height, or weight into the persistent vector index. Never include API keys in documents. Keep source attribution and estimate/verification status with each retrieved nutrition statement.
