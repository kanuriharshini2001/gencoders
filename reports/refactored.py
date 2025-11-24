def calculate_total(price, tax):
    """Calculates the total price including tax."""
    total = price + (price * tax)
    return total

print(calculate_total(100, 0.05))