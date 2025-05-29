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

## Example projects

Ready-to-run example files can be found in this repository:  
- [example_main.py](example_main.py) — entry point and Locy configuration  
- [example_second.py](example_second.py) — using `lc` in other modules

---

## Installation
```bash
pip install googletrans==4.0.0-rc1
```
Clone this repo and use the files directly, or pip-install after PyPI release.

## Usage Example

See ready-to-run usage in [example_main.py](example_main.py) and [example_second.py](example_second.py) in this repository.

The recommended way to use Locy is to configure it **once** at the entry point of your application (for example, in `main.py`) and then import and use the singleton instance `lc` in all other modules.  
Always call `configure()` before importing `lc` or any modules that depend on it!

- Note: Do not import lc or any modules that use it before you call configure(). Otherwise you will get an initialization error.

```python
from locy import configure

configure(translations_dir="./translations", default_lang="en")

from locy import lc

lang = "ru"
var = "hello"
message = lc(locals(), lang, "Your message: {var}")
print(message)
```

## Async usage

You can use Locy in async code with `await lc.acall(...)`.

See [example_main.py](example_main.py) for an async usage demo.

```python
import asyncio
from locy import configure

configure(translations_dir="./translations", default_lang="en")
from locy import lc

async def main():
    lang = "ru"
    foo = "async test"
    bar = 123
    msg = await lc.acall(locals(), lang, "Async example: {foo}, value: {bar}")
    print(msg)
asyncio.run(main())
```


---

## Using Locy in multiple files

Check out [example_main.py](example_main.py) and [example_second.py](example_second.py) for a real-world multi-file usage pattern.

- Configure Locy **once** at the start of your main module, *before* importing `lc` or any modules that will use it.
- In all other modules, simply `from locy import lc` and use it as shown in the examples.

**Note:**  
If you try to use `lc` before calling `configure()`, you'll get a helpful error message explaining that Locy needs to be configured first.


## Initialization order matters!

- Always configure Locy in your main file before using or importing `lc` elsewhere.
- All calls to `lc` will use the singleton instance you configured.
- If you forget to call `configure()` before using `lc`, Locy will show a clear error message instead of crashing your app.

See the provided example files for best practices.

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

## Best Practice

- Call `configure()` only once, as early as possible in your main entry file.
- Only after configuration, import `lc` in all files where you want to use it.
- If you want to use more than one configuration in a single app (rarely needed), create explicit Locy instances instead of using the singleton.

---

## Contributing

PRs and issues are welcome!
If you want to support a new feature, check/add tests in test_locy.py.