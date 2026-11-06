import unittest

from backend.app import app
from backend.nutrimatch_service import load_menu, recommend, validate_profile
from backend.seed import seed_data
from rag.chatbot import _load_documents, answer_question


class TamilCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        seed_data()
        cls.client = app.test_client()
        cls.menu = load_menu()

    def test_requested_catalog_dishes_exist_in_one_database(self):
        names = {food["name"] for food in self.menu}
        expected = {"Ragi Dosa", "Kambu Dosa", "Thinai Dosa", "Kollu Rasam", "Kambu Koozh", "Neer Mor", "Tamil Nadu Style Fish Curry", "Egg Dosa"}
        self.assertTrue(expected.issubset(names))
        self.assertGreaterEqual(len(self.menu), 65)

    def test_catalog_only_foods_have_no_fake_prices_nutrition_or_images(self):
        dish = next(food for food in self.menu if food["name"] == "Kambu Koozh")
        self.assertIsNone(dish["price"])
        self.assertIsNone(dish["calories"])
        self.assertIsNone(dish["image_url"])
        self.assertEqual(dish["availability_status"], "pending_confirmation")
        self.assertEqual(dish["catalog_status"], "reference_pending_restaurant_confirmation")

    def test_live_food_api_matches_recommendation_database(self):
        foods = self.client.get("/api/foods").get_json()
        api_dish = next(food for food in foods if food["name"] == "Ragi Dosa")
        match_menu = next(food for food in self.menu if food["name"] == "Ragi Dosa")
        self.assertEqual(api_dish["id"], match_menu["id"])
        self.assertEqual(api_dish["tamil_name"], "கேழ்வரகு தோசை")
        result = recommend(validate_profile({}), self.menu)
        self.assertNotIn(api_dish["id"], result["eligible_menu_ids"])
        self.assertTrue(any(food["id"] == api_dish["id"] for food in result["requiring_verification"]))

    def test_food_detail_and_categories_api(self):
        dish = next(food for food in self.menu if food["name"] == "Kambu Koozh")
        detail = self.client.get(f"/api/foods/{dish['id']}").get_json()
        self.assertEqual(detail["food"]["food_slug"], dish["food_slug"])
        categories = self.client.get("/api/foods/categories").get_json()["categories"]
        self.assertIn("Traditional Breakfast", categories)
        self.assertIn("Traditional Drinks", categories)

    def test_rag_loads_new_foods_from_database_without_reseed_index(self):
        docs = _load_documents()
        self.assertTrue(any(doc["metadata"].get("food_name") == "Kambu Koozh" for doc in docs))
        result = answer_question("What is Kambu Koozh?")
        info = result.get("food_information")
        self.assertIsNotNone(info)
        self.assertEqual(info["food_name"], "Kambu Koozh")
        self.assertIsNone(info["price"])
        self.assertIsNone(info["nutrition"]["calories"])
        self.assertEqual(info["catalog_status"], "reference_pending_restaurant_confirmation")

    def test_unknown_exact_dish_photo_uses_no_unrelated_url(self):
        dishes = [food for food in self.menu if food["catalog_status"] == "reference_pending_restaurant_confirmation"]
        self.assertTrue(dishes)
        self.assertTrue(all(food["image_url"] is None for food in dishes))

    def test_only_verified_photos_are_returned_to_chat(self):
        result = answer_question("What is Ragi Dosa?")
        self.assertIsNone(result["food_information"]["image_url"])

    def test_nutribot_alias_returns_same_structured_food(self):
        response = self.client.post("/api/nutribot/chat", json={"message": "What is Kambu Koozh?"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["food_information"]["food_name"], "Kambu Koozh")

    def test_old_health_and_menu_routes_still_work(self):
        self.assertEqual(self.client.get("/api/foods/healthy").status_code, 200)
        self.assertTrue(self.client.get("/api/foods").get_json())


if __name__ == "__main__":
    unittest.main()
