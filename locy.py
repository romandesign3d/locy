import os
import json
import re
from pathlib import Path
from googletrans import Translator
import asyncio
import unicodedata

from lang_aliases import LANG_ALIASES
MAX_LEN = 1000

class Locy:
    def __init__(self, translations_dir="./translations", default_lang="ru"):
        self.translations_dir = Path(translations_dir)
        self.translations_dir.mkdir(parents=True, exist_ok=True)
        self.default_lang = self.resolve_lang(default_lang)
        self.translator = Translator()
        self.cache = {}

    def __call__(self, variables, lang, template):
        lang = self.resolve_lang(lang)
        # 0. Limit maximum string length
        if len(template) > MAX_LEN:
            template = template[:MAX_LEN]

        # 1. Remove non-printable and potentially harmful characters
        cleaned, removed = self.clean_nonprintable(template)
        if removed:
            template = cleaned

        # 2. Check braces pairing and for nested/double curly braces
        ok, err = self.check_braces(template)
        if not ok:
            return f"[locy error: {err}]"

        # 3. Check all variables in braces exist and are valid
        ok, err = self.check_variables_exist(template, variables)
        if not ok:
            return f"[locy error: {err}] String: {template}"
        
        stripped_template, var_names = self.strip_template_vars(template)

        # 4. Translation logic
        if lang == self.default_lang:
            translated_template = stripped_template
        else:
            translations = self.cache.get(lang)
            if translations is None:
                translations = self._load_translations(lang)
                self.cache[lang] = translations
            if stripped_template in translations:
                translated_template = translations[stripped_template]
            else:
                translated_template = self.translate(stripped_template, self.default_lang, lang)
                # Always store as string!
                if not isinstance(translated_template, str):
                    translated_template = f"[locy error: Unexpected non-string translation: {str(translated_template)}]"
                translations[stripped_template] = translated_template
                self._save_translations(lang, translations)

        # Fill values by order of variable names
        num_placeholders = self.count_placeholders(translated_template)
        if num_placeholders != len(var_names):
            return (f"[locy error: Mismatch between variable count ({len(var_names)}) "
                    f"and placeholders in translation ({num_placeholders})] "
                    f"Template: {translated_template}")

        return self.fill_template(translated_template, var_names, variables)

    async def acall(self, variables, lang, template):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, self.__call__, variables, lang, template
        )

    def resolve_lang(self, code):
        return LANG_ALIASES.get(code.lower(), code.lower())

    def translate(self, text, src_lang, dst_lang):
        try:
            result = self.translator.translate(text, src=src_lang, dest=dst_lang).text
        except Exception as e:
            result = f"[locy error: {str(e)}]"
        return result

    def _load_translations(self, lang):
        translation_file = self.translations_dir / f"{self.default_lang}_{lang}.json"
        if translation_file.exists():
            with open(translation_file, encoding="utf-8") as f:
                return json.load(f)
        else:
            return {}

    def _save_translations(self, lang, translations):
        translation_file = self.translations_dir / f"{self.default_lang}_{lang}.json"
        # Ensure only string values are saved!
        for k, v in translations.items():
            if not isinstance(v, str):
                translations[k] = f"[locy error: non-string value {type(v)}]"
        with open(translation_file, "w", encoding="utf-8") as f:
            json.dump(translations, f, ensure_ascii=False, indent=4)

    def clean_nonprintable(self, text):
        # Remove control characters and invisible Unicode formatting symbols except for \n, \r, \t
        cleaned = []
        removed = []
        for c in text:
            code = ord(c)
            if code < 32 and code not in (9, 10, 13):
                removed.append(c)
                continue
            if unicodedata.category(c) in ("Cf",) and c not in {'\n', '\r', '\t'}:
                removed.append(c)
                continue
            cleaned.append(c)
        return ''.join(cleaned), ''.join(removed)

    def check_braces(self, text):
        depth = 0
        for idx, char in enumerate(text):
            if char == '{':
                if depth > 0:
                    return False, f"Nested braces detected at position {idx} in: {text}"
                depth += 1
            elif char == '}':
                if depth == 0:
                    return False, f"Unmatched closing brace at position {idx} in: {text}"
                depth -= 1
        if depth > 0:
            return False, f"Unmatched opening brace in: {text}"
        if "{{" in text or "}}" in text:
            return False, f"Double curly braces not allowed in: {text}"
        return True, ""
    
    def check_variables_exist(self, template, variables):
        # Check that all variables inside curly braces exist and are valid Python identifiers
        pattern = re.compile(r'{(\w+)}')
        vars_in_template = set(pattern.findall(template))
        vars_in_locals = set(variables.keys())
        missing = vars_in_template - vars_in_locals
        if missing:
            return False, f"Missing variables: {', '.join(missing)}"
        bad_names = [v for v in vars_in_template if not v.isidentifier()]
        if bad_names:
            return False, f"Invalid variable names: {', '.join(bad_names)}"
        return True, ""
    
    def strip_template_vars(self, template):
        """
        Replace {var} with {} and return stripped template and list of variable names in order of appearance.
        """
        var_pattern = re.compile(r'{(\w+)}')
        var_names = var_pattern.findall(template)
        stripped = var_pattern.sub("{}", template)
        return stripped, var_names
    
    def count_placeholders(self, template):
        # Check count of {} 
        return len(re.findall(r'\{\}', template))
    
    def fill_template(self, template, var_names, variables):
        """
        Substitute variables into template by order using the list of variable names.
        """
        try:
            values = [variables[name] for name in var_names]
            return template.format(*values)
        except KeyError as e:
            return f"[locy error: Missing variable {e}]"
