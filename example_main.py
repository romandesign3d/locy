# example_main.py
# Example: Proper initialization and usage of Locy across multiple files

from locy import configure

# 1. Configure Locy ONCE at application startup (before any usage or imports)
configure(translations_dir="./translations", default_lang="en")

# 2. Import the global Locy instance after configuration
from locy import lc

# 3. Import functions from other modules that will use Locy
from example_second import second_mesage

lang = "ru"
var = "gooooooooggg"

# Example usage in main
message = lc(locals(), lang, "Your message {var}")
print(message)

# Example usage in another module
returned_msg = second_mesage(lang, "second message")
print(returned_msg)
