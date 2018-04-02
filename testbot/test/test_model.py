import unittest

from testbot.model import Package, Test, Question


class TestPackage(unittest.TestCase):
    def test_empty_args(self):
        package = Package()
        empty_package = {
            "name": None,
            "description": "",
            "short_description": "",
            "price": 0.0,
            "tests": list()
        }
        self.assertEqual(dict(package), empty_package)

        for key, value in empty_package.items():
            with self.subTest(key=key):
                self.assertEqual(package[key], empty_package[key])

        for key, value in empty_package.items():
            with self.subTest(attr=key):
                self.assertEqual(package.__getattr__(key), empty_package[key])

    def test_exceptions(self):
        package = Package()
        with self.subTest(func="__getattr__"):
            self.assertRaises(KeyError, package.__getattr__, "wrong_attr")
        with self.subTest(func="__getitem__"):
            self.assertRaises(KeyError, package.__getitem__, "wrong_attr")
        with self.subTest(func="__setitem__"):
            self.assertRaises(KeyError, package.__setitem__, "wrong_attr", "value")


class TestTest(unittest.TestCase):
    def test_empty_args(self):
        test = Test()
        empty_test = {
            "name": None,
            "price": 0.0,
            "current_question": None,
            "description": "",
            "is_exam": False,
            "questions": list()
        }
        self.assertEqual(dict(test), empty_test)


class TestQuestion(unittest.TestCase):
    def test_empty_args(self):
        question = Question()
        empty_question = {
            "answer": None,
            "answer_variants": list(),
            "img_url": None,
            "points": 1,
            "text": None
        }
        self.assertEqual(dict(question), empty_question)


if __name__ == "__main__":
    unittest.main()
