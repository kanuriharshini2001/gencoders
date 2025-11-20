def is_even(n):
    if n % 2 == 0:
        return True
    else:
        return False

def print_even_numbers(numbers):
    for n in numbers:
        if is_even(n) == True:
            print(n)
