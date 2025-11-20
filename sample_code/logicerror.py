# sample_code/logic_error.py

def get_total_price(item_price, tax_rate):
    
    # This is a logic error
    # The parameter is 'tax_rate', but the code uses 'tax'
    total = item_price + (item_price * tax) 
    
    return total

# Example usage
print(get_total_price(100, 0.05))