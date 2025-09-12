# This script generates a lookup table for Persian numbers in word form
# and prints it in a format that can be directly used in Python code.

import os
from persian_tools.digits import convert_to_word

# Define the range for your lookup table
MAX_NUMBER = 1000

# Generate the lookup table
lookup_table = {}
for i in range(1, MAX_NUMBER + 1):
    # Get the word form of the number using the library
    word_form = convert_to_word(i)

    # Apply string replacement to fix "یکصد" and "یکهزار"
    # This ensures that numbers like 1358 ("یکهزار و سیصد و پنجاه و هشت") are corrected
    # to "هزار و سیصد و پنجاه و هشت"
    word_form = word_form.replace("یکصد", "صد")
    word_form = word_form.replace("یک هزار", "هزار")

    lookup_table[i] = word_form

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(script_dir, "lut.txt")

# Write the dictionary to a file in a format suitable for Python code
with open(output_file, "w", encoding="utf-8") as f:
    f.write("PERSIAN_NUMBERS_AS_WORDS = {\n")
    for key, value in lookup_table.items():
        f.write(f'    {key}: "{value}",\n')
    f.write("}\n")

print(f"Lookup table written to {output_file} with {len(lookup_table)} entries.")
