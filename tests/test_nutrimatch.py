import unittest
from unittest.mock import patch

from backend.app import app
from backend.nutrimatch_service import recommend, validate_profile


class NutriMatchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()

    def food(self, **overrides):
        base = {
            "id": 1,
            "name": "Test dish",
            "price": 80,
            "calories": 320,
            "protein": 18,
            "carbs": 40,
            "fat": 7,
            "fiber": None,
            "sodium": None,
            "rating": 4.5,
            "category": "Breakfast",
            "description": "A Tamil breakfast",
            "image_url": None,
            "ingredients": "Rice, lentils",
            "allergens": None,
            "food_type": "vegetarian",
            "meal_type": "Breakfast",
            "nutrition_status": "estimated",
            "serving_size": None,
            "cuisine": "Tamil Nadu",
            "availability_status": None,
            "dietary_verified": None,
            "allergens_verified": None,
        }
        base.update(overrides)
        return base

    def profile(self, **overrides):
        data = {"dietary_preference": "no_preference", "budget": "no_limit"}
        data.update(overrides)
        return validate_profile(data)

    def test_primary_and_secondary_goal_and_fixed_scoring(self):
        profile = self.profile(goal="weight_loss", secondary_goals=["high_protein"], cuisine_preferences=["tamil_nadu"])
        result = recommend(profile, [self.food()])
        item = result["best_matches"][0]
        self.assertEqual(item["match_percentage"], 73)
        self.assertEqual(result["score_weights"]["goal"], 30)

    def test_price_budget_filters_menu_items(self):
        result = recommend(self.profile(budget="under_50"), [self.food()])
        self.assertEqual(result["best_matches"], [])

    def test_known_allergen_conflicts_are_hard_excluded(self):
        result = recommend(
            self.profile(allergies=["dairy"]),
            [self.food(ingredients="Rice, curd"), self.food(id=2, ingredients="Rice, lentils", allergens_verified=1)],
        )
        self.assertEqual([item["id"] for item in result["best_matches"]], [2])
        self.assertEqual(result["requiring_verification"], [])

    def test_selected_allergy_requires_verified_declaration(self):
        unknown = self.food(id=1, allergens_verified=None)
        verified = self.food(id=2, allergens_verified=1, allergens="", ingredients="Rice, lentils")
        result = recommend(self.profile(allergies=["peanuts"]), [unknown, verified])
        self.assertEqual([item["id"] for item in result["best_matches"]], [2])
        self.assertEqual([item["id"] for item in result["requiring_verification"]], [1])

    def test_vegan_with_unverified_recipe_is_not_recommended(self):
        result = recommend(self.profile(dietary_preference="vegan"), [self.food()])
        self.assertEqual(result["best_matches"], [])
        self.assertEqual(result["requiring_verification"][0]["id"], 1)

    def test_eggetarian_does_not_pass_chicken_with_egg(self):
        result = recommend(
            self.profile(dietary_preference="eggetarian"),
            [self.food(food_type="non-vegetarian", ingredients="Egg, chicken")],
        )
        self.assertEqual(result["best_matches"], [])
        self.assertEqual(result["requiring_verification"], [])

    def test_non_vegetarian_preference_excludes_vegetarian_items(self):
        result = recommend(self.profile(dietary_preference="non_vegetarian"), [self.food()])
        self.assertEqual(result["best_matches"], [])

    def test_plural_nut_ingredient_is_a_hard_conflict(self):
        result = recommend(
            self.profile(allergies=["tree_nuts"]),
            [self.food(ingredients="Rice, cashews")],
        )
        self.assertEqual(result["requiring_verification"], [])
        self.assertEqual(result["best_matches"], [])

    def test_multiple_allergies_and_unknown_conflicts(self):
        result = recommend(
            self.profile(allergies=["dairy", "tree_nuts"]),
            [self.food(id=1, ingredients="Rice, curd"), self.food(id=2, ingredients="Rice, cashews"), self.food(id=3, allergens_verified=1)],
        )
        self.assertEqual([item["id"] for item in result["best_matches"]], [3])
        self.assertEqual({item["id"] for item in result["requiring_verification"]}, set())

    def test_no_matching_filters_returns_empty_without_fake_food(self):
        result = recommend(
            self.profile(dietary_preference="vegetarian", budget="under_50"),
            [self.food(food_type="non-vegetarian", price=120)],
        )
        self.assertEqual(result["best_matches"], [])
        self.assertEqual(result["alternative_choices"], [])
        self.assertEqual(result["requiring_verification"], [])

    def test_unavailable_food_is_not_recommended(self):
        result = recommend(self.profile(), [self.food(availability_status="unavailable")])
        self.assertEqual(result["best_matches"], [])

    def test_empty_profile_works_and_does_not_store_health_data(self):
        response = self.client.post("/api/nutrimatch/recommendations", json={})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.get_json()["profile_saved"])

    def test_dairy_allergy_vegan_flow_does_not_recommend_unknown_recipe(self):
        result = recommend(
            self.profile(dietary_preference="vegan", allergies=["dairy"]),
            [self.food(ingredients=None, dietary_verified=1), self.food(id=2, ingredients="Rice, ghee")],
        )
        self.assertEqual(result["best_matches"], [])
        self.assertTrue(result["requiring_verification"])
        self.assertEqual(len(result["requiring_verification"]), 1)

    def test_rag_failure_keeps_deterministic_recommendations_available(self):
        profile = self.profile(goal="high_protein")
        with patch("rag.chatbot._load_documents", side_effect=RuntimeError("retrieval down")):
            result = recommend(profile, [self.food()])
        self.assertTrue(result["best_matches"])
        self.assertEqual(result["rag_guidance"], [])

    def test_missing_sodium_gets_no_assumed_nutrition_advantage(self):
        result = recommend(self.profile(nutrition_preferences=["less_salt"]), [self.food()])
        item = result["best_matches"][0]
        self.assertEqual(item["nutrition"]["sodium"], None)
        self.assertEqual(item["match_components"]["nutrition"], 0.5)

    def test_allergy_selection_does_not_store_or_echo_personal_profile(self):
        result = recommend(self.profile(allergies=["peanuts"]), [self.food()])
        self.assertFalse(result["profile_saved"])
        self.assertNotIn("profile", result)

    def test_invalid_budget_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_profile({"budget": "free_food"})

    def test_api_profile_recommendations_and_detail(self):
        profile_response = self.client.post("/api/nutrimatch/profile", json={"goal": "weight_loss"})
        self.assertEqual(profile_response.status_code, 200)
        self.assertFalse(profile_response.get_json()["profile_saved"])

        recommendations = self.client.post("/api/nutrimatch/recommendations", json={"goal": "weight_loss"})
        self.assertEqual(recommendations.status_code, 200)
        self.assertIn("score_weights", recommendations.get_json())

        foods = self.client.get("/api/nutrimatch/foods").get_json()
        self.assertTrue(foods)
        detail = self.client.get(f"/api/nutrimatch/foods/{foods[0]['id']}")
        self.assertEqual(detail.status_code, 200)

    def test_api_rejects_invalid_profile(self):
        response = self.client.post("/api/nutrimatch/recommendations", json={"budget": "free"})
        self.assertEqual(response.status_code, 400)

    def test_chat_uses_request_preferences(self):
        response = self.client.post("/api/nutrimatch/chat", json={"message": "Suggest a high protein breakfast", "preferences": {"dietary_preference": "vegetarian"}})
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertFalse(payload["profile_saved"])
        self.assertTrue(payload["answer"])


if __name__ == "__main__":
    unittest.main()
