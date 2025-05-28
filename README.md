# Locy

**Rapid, robust, human-friendly localization for Python MVPs and production!**

Locy lets you instantly localize all your app’s user-facing text, without inventing keys, drowning in boilerplate, or breaking your codebase.  
Just use your real text as keys, enjoy automatic draft translations (with Google Translate), and never lose your Python string formatting superpowers.

---

## Features

- **Real-string keys:**  
  No need to invent gettext keys or YAML monstrosities. Just write your text as-is, and Locy handles everything.
- **f-string compatible:**  
  Use `{variables}` as in f-strings — Locy supports all familiar Python string formatting, keeps variable order, and auto-fills values.
- **Automatic translation & instant dictionary building:**  
  Never copy-paste into Google Translate again — the first time you call a message, Locy adds it to the language dictionary and translates it. Later, translators can improve the machine draft in a single JSON.
- **Safe and robust:**  
  All common errors (bad braces, missing variables, too long strings, unknown language codes, manual dictionary mistakes) are handled gracefully — Locy never crashes your program.
- **Flexible language codes:**  
  Supports both 2- and 3-letter codes: `en`, `eng`, `ua`, `uk`, `ukr`, `ru`, `rus`, `de`, `deu`, etc. No more confusion!
- **Invisible/Unicode control character protection:**  
  Removes hidden, bidirectional, and potentially dangerous unicode/control symbols from your templates.
- **Checks for manual translation errors:**  
  When loading a translation, Locy checks for mismatched braces, wrong number of placeholders, and other common issues after hand-editing the dictionary.
- **Async support:**  
  Use in async code (`await lc.acall(...)`) out-of-the-box.
- **Ready for CI/CD:**  
  Comes with complete test suite — see `test_locy.py`.

---

## Installation
```bash
pip install googletrans==4.0.0-rc1
```
Clone this repo and use the files directly, or pip-install after PyPI release.

## Usage Example
```python
from locy import Locy


lc = Locy(translations_dir="./translations", default_lang="ru")
lang = "en"
value1 = "данные"
value2 = 42

message = lc(locals(), lang, "Получено значение {value1}, еще значение {value2}!")
print(message)  # "Value data received, value 42!" (auto translation, variables inserted)
```
## Async usage
```python
import asyncio
lc = Locy(translations_dir="./translations", default_lang="ru")
async def main():
    lang = "en"
    foo = "тест"
    bar = 17
    msg = await lc.acall(locals(), lang, "Асинхронно: {foo}, число: {bar}")
    print(msg)
asyncio.run(main())
```

## Language Codes (with aliases)
- You can use either 2-letter (en, ru, uk, de, etc.) or 3-letter codes (eng, rus, ukr, deu, etc.).
- All codes are auto-mapped: for example, ua or ukr are both treated as Ukrainian.

## How Locy prevents errors
- Invisible unicode symbols (zero-width space, RLM, LRM, etc.) are removed automatically.
- All braces {} are checked: nested, unbalanced, or double curly braces like {{/}} produce a clear error, not a crash.
- Manual translation edits protected: If you add/remove braces by mistake in a translation file, Locy warns you and shows a message, instead of breaking your app.
- Variable count is checked: If the translation has a different number of {} than variables, you'll see an error.
- Unknown languages: Any unrecognized code is mapped via lang_aliases.py, and if that fails, a readable error is returned — your app keeps running.

## How translation keys and variables work
- When you call:
```python
lc(locals(), lang, "Hello {user}, balance: {amount} USD.")
```
- Locy removes variable names before sending the string to Google Translate or looking up in the dictionary:
```python
"Hello {}, balance: {} USD."
```
- The translated result is stored with empty {} placeholders, and actual values are inserted at runtime, preserving order.

## Tests
- Run all tests:
```bash
python -m unittest test_locy.py
```
- The test suite checks all core scenarios: translation, variable matching, language aliases, brace errors, hidden symbols, async mode, and manual translation file mistakes.

## Contributing

PRs and issues are welcome!
If you want to support a new feature, check/add tests in test_locy.py.