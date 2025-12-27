from test import print_even_numbers
print_even_numbers(10)

added_line = "print('This is a new line added to demo.py')"
with open(__file__, 'a') as f:
    f.write('\n' + added_line + '\n')   