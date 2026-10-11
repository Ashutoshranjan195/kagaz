import unittest
from unittest.mock import patch, MagicMock
from src.utils import validate_hunt, contains_forbidden, safe_filename


class TestUtils(unittest.TestCase):
    def test_contains_forbidden(self):
        self.assertTrue(contains_forbidden("touch the flower"))
        self.assertTrue(contains_forbidden("Taste this berry"))
        self.assertTrue(contains_forbidden("CHHOONA is bad"))
        self.assertFalse(contains_forbidden("look at the tree"))
        self.assertFalse(contains_forbidden("no forbidden words here"))

    def test_safe_filename(self):
        self.assertEqual(safe_filename("Hello World"), "hello_world")
        self.assertEqual(safe_filename("Test-File_123"), "test-file_123")
        self.assertEqual(safe_filename("Special!@#Chars"), "specialchars")
        self.assertEqual(safe_filename("lower_case"), "lower_case")

    def test_validate_hunt_happy_path(self):
        hunt = {
            "title": "Test Hunt",
            "intro": "Find things outside",
            "items": [
                {
                    "id": 1, "emoji": "🌿", "text_en": "Find a leaf",
                    "text_hi": "Patta dhoondo", "hint": "Look under a tree",
                    "type": "spot",
                }
            ],
            "bonus_challenge": "Find a bird nest",
            "parent_note": "Stay safe",
        }
        validate_hunt(hunt, 1)

    def test_validate_hunt_rejects_forbidden_words(self):
        hunt = {
            "title": "Test Hunt",
            "intro": "Find things outside",
            "items": [
                {
                    "id": 1, "emoji": "🌿", "text_en": "Find a leaf",
                    "text_hi": "Patta dhoondo", "hint": "Touch the insect",
                    "type": "spot",
                }
            ],
            "bonus_challenge": "Find a bird nest",
            "parent_note": "Stay safe",
        }
        with self.assertRaises(ValueError):
            validate_hunt(hunt, 1)

    def test_validate_hunt_rejects_wrong_count(self):
        hunt = {
            "title": "Test Hunt",
            "intro": "Find things outside",
            "items": [
                {
                    "id": 1, "emoji": "🌿", "text_en": "Find a leaf",
                    "text_hi": "Patta dhoondo", "hint": "Look under a tree",
                    "type": "spot",
                }
            ],
            "bonus_challenge": "Find a bird nest",
            "parent_note": "Stay safe",
        }
        with self.assertRaises(ValueError):
            validate_hunt(hunt, 5)

    def test_validate_hunt_rejects_bad_type(self):
        hunt = {
            "title": "Test Hunt",
            "intro": "Find things outside",
            "items": [
                {
                    "id": 1, "emoji": "🌿", "text_en": "Find a leaf",
                    "text_hi": "Patta dhoondo", "hint": "Look under a tree",
                    "type": "invalid_type",
                }
            ],
            "bonus_challenge": "Find a bird nest",
            "parent_note": "Stay safe",
        }
        with self.assertRaises(ValueError):
            validate_hunt(hunt, 1)

    def test_validate_hunt_rejects_not_dict(self):
        with self.assertRaises(ValueError):
            validate_hunt("not a dict", 1)

    def test_validate_hunt_rejects_missing_keys(self):
        hunt = {
            "title": "Test Hunt",
            "intro": "Find things outside",
            "items": [
                {
                    "id": 1, "emoji": "🌿", "text_en": "Find a leaf",
                    "text_hi": "Patta dhoondo",
                    # missing hint and type
                }
            ],
            "bonus_challenge": "Find a bird nest",
            "parent_note": "Stay safe",
        }
        with self.assertRaises(ValueError):
            validate_hunt(hunt, 1)
