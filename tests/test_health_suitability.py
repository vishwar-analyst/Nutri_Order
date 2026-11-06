import unittest

from rag.chatbot import _load_documents, answer_question
from rag.health_suitability import build_health_analysis, identify_conditions, load_current_menu


class HealthSuitabilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = _load_documents()
        cls.foods = load_current_menu()

    def test_detects_multiple_separate_conditions(self):
        conditions = identify_conditions("Is idli suitable for diabetes and high blood pressure?")
        self.assertIn("Diabetes", conditions)
        self.assertIn("High Blood Pressure", conditions)

    def test_ragi_dosa_uses_qualified_knowledge_estimates(self):
        result = answer_question("Is ragi dosa suitable for high blood sugar?")
        analysis = result["health_analysis"]
        self.assertEqual(analysis["food_name"], "Ragi Dosa")
        self.assertEqual(analysis["nutrition"]["carbohydrates"], "28–45")
        self.assertEqual(analysis["nutrition"]["sodium"], None)
        self.assertEqual(analysis["nutrition"]["status"], "illustrative_estimate_not_verified")
        self.assertEqual(analysis["health_assessments"][0]["status"], "portion_control")

    def test_blood_pressure_does_not_infer_sodium_or_treatment(self):
        result = build_health_analysis("Is curd rice good for high BP?", self.foods, documents=self.documents)
        analysis = result
        self.assertIsNone(analysis["nutrition"]["sodium"])
        self.assertEqual(analysis["health_assessments"][0]["status"], "preparation_matters")
        self.assertIn("not measured", analysis["health_assessments"][0]["summary"])

    def test_lower_sodium_question_reports_measurement_gap(self):
        result = answer_question("Which Tamil Nadu foods are lower in sodium?")
        analysis = result["health_analysis"]
        self.assertEqual(analysis["health_assessments"][0]["condition"], "Low-Sodium Diet")
        self.assertIsNone(analysis["nutrition"]["sodium"])
        self.assertEqual(analysis["alternatives"], [])

    def test_unknown_food_keeps_nutrition_missing(self):
        analysis = build_health_analysis("Is grilled chicken a good high-protein choice?", self.foods, documents=self.documents)
        self.assertIsNone(analysis["nutrition"]["protein"])
        self.assertEqual(analysis["nutrition"]["status"], "not available")

    def test_allergy_question_requires_staff_confirmation_and_no_alternatives(self):
        analysis = build_health_analysis("Is lemon rice safe for peanut allergy?", self.foods, documents=self.documents)
        self.assertEqual(analysis["health_assessments"][0]["status"], "check_ingredients")
        self.assertEqual(analysis["alternatives"], [])
        self.assertTrue(any("restaurant" in warning.lower() for warning in analysis["warnings"]))

    def test_non_health_question_keeps_existing_chat_flow(self):
        result = answer_question("What does fibre do?")
        self.assertNotIn("health_analysis", result)
        self.assertIn("answer", result)

    def test_compare_question_returns_actual_menu_items(self):
        result = answer_question("Compare idli and dosa for diabetes considerations")
        analysis = result["health_analysis"]
        names = [item["name"] for item in analysis["comparison_items"]]
        self.assertTrue(any("idli" in name.lower() for name in names))
        self.assertTrue(any("dosa" in name.lower() for name in names))


if __name__ == "__main__":
    unittest.main()
