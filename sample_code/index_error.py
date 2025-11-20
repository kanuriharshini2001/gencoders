# sample_code/index_error.py

def get_first_and_last(data_list):
    
    # 1. LOGIC BUG (IndexError)
    # This will crash if the list is empty
    first_item = data_list[0]
    
    # 2. LOGIC BUG (IndexError)
    # This will crash if the list has fewer than 2 items
    second_item = data_list[1]

    print(f"First: {first_item}, Second: {second_item}")

# Example usage
# This call will cause the code to crash
get_first_and_last([])