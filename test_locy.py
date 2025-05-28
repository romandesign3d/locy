import unittest
from locy import Locy

class TestLocy(unittest.TestCase):
    def setUp(self):
        self.lc = Locy(translations_dir="./translations_test", default_lang="en")

    def test_basic_translation(self):
        lang = "ru"
        value1 = "данные"
        value2 = 42
        msg = self.lc(locals(), lang, "Get value {value1}, and {value2} apples.")
        self.assertIn("данные", msg)
        self.assertIn("42", msg)

    def test_alias_language_code(self):
        lang = "rus"
        value1 = "foo"
        value2 = "bar"
        msg = self.lc(locals(), lang, "Words: {value1}, {value2}.")
        self.assertIn("foo", msg)
        self.assertIn("bar", msg)

    def test_nonprintable_removal(self):
        lang = "es"
        value = "clean"
        template = "Text with\x07nonprintable {value}."
        msg = self.lc(locals(), lang, template)
        self.assertNotIn("\x07", msg)
        self.assertIn("clean", msg)

    def test_nested_braces_error(self):
        lang = "de"
        value = "bad"
        template = "Nested {error {value}} case"
        msg = self.lc(locals(), lang, template)
        self.assertIn("locy error", msg)

    def test_unmatched_braces_error(self):
        lang = "de"
        value = "oops"
        template = "Missed closing {value"
        msg = self.lc(locals(), lang, template)
        self.assertIn("locy error", msg)

    def test_double_curly_braces(self):
        lang = "fr"
        value = "abc"
        template = "Double {{curly}} braces {value}"
        msg = self.lc(locals(), lang, template)
        self.assertIn("locy error", msg)

    def test_missing_variable(self):
        lang = "en"
        a = 123
        msg = self.lc(locals(), lang, "Missing variable {b}")
        self.assertIn("locy error", msg)

    def test_invalid_variable_name(self):
        lang = "en"
        a1 = 123
        # Variable name starts with number is not valid
        msg = self.lc({"1a": 100}, lang, "Test {1a}")
        self.assertIn("locy error", msg)

    def test_too_long_template(self):
        lang = "en"
        v = "test"
        template = "a" * 1200 + " {v}"
        msg = self.lc(locals(), lang, template)
        self.assertTrue(len(msg) < 1020)  # + some length for "test" inserted

    def test_placeholder_varcount_mismatch(self):
        # Simulate manual change in translation (less/more placeholders)
        lang = "de"
        value1 = "eins"
        value2 = "zwei"
        # Patch internal dictionary directly for test
        self.lc.cache[lang] = {"Text {}, {}.": "Text {}, {}, EXTRA {}."}
        msg = self.lc(locals(), lang, "Text {value1}, {value2}.")
        self.assertIn("locy error", msg)

    def test_async_call(self):
        import asyncio
        async def run_async():
            lang = "es"
            value1 = "uno"
            value2 = "dos"
            msg = await self.lc.acall(locals(), lang, "Números {value1}, {value2}.")
            self.assertIn("uno", msg)
            self.assertIn("dos", msg)
        asyncio.run(run_async())

if __name__ == "__main__":
    unittest.main()
