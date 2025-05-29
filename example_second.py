# example_second.py
# Example: Using the global Locy instance in another module

from locy import lc

def second_mesage(lang, message):
    # Demonstrate usage in this module
    print(lc(locals(), lang, message))

    # Example with more variables
    val1 = "some val"
    val2 = "other val"
    msg = lc(locals(), lang, "some value {val1} and other value {val2}")
    return msg
