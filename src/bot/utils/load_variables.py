import os
import json 




# Function to load variables from JSON
def load_variables():
    variables_file = os.path.join(os.path.dirname(__file__), '..', 'variables', 'variables.json')
    if os.path.exists(variables_file):
        with open(variables_file, 'r') as f:
            return json.load(f)
    return {"lead_id": 1, "dealer_id": 1, "lead_crm_id": 1, "product_id": 1}




if __name__ == "__main__":
    variables = load_variables()
    dealer_id = variables["dealer_id"]
    print(dealer_id)