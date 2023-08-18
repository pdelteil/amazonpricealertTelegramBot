import re

def validate_input_string(input_string):
    pattern = r'^/add_item\s+([\w\s]+),\s*(.+)?$'
    match = re.match(pattern, input_string)

    if match:
        # Extract the parts
        item_name = match.group(1)
        item_text = match.group(2)
        item_url = match.group(3)

        # Process the extracted parts here
        print("Item Name:", item_name)
        print("Item Text:", item_text)
        print("Item URL:", item_url if item_url else "URL is missing")
    else:
        print("Invalid input format.")

# Example usage
input_str = "/add_item Nombre Texto, https://example.com"
validate_input_string(input_str)

