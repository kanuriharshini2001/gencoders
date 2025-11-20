def add_numbers(a, b):
    return a + b

def main():
    x = 10
    y = 5
    result = add_numbers(x, y)
    print("The result is: " + result)  # Bug: mixing int & string

if __name__ == "__main__":
    main()
