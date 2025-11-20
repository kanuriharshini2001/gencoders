def get_first_and_last(data_list):
    """
    Retrieves and prints the first and second elements of a list.

    If the list is too short, missing elements are treated as None.
    """
    first_item = None
    second_item = None

    if data_list:
        first_item = data_list[0]
        
        if len(data_list) > 1:
            second_item = data_list[1]

    print(f"First: {first_item}, Second: {second_item}")

# Example usage
get_first_and_last([])