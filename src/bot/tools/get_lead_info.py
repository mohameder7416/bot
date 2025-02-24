from bot.utils.update_phone import update_Chat_Phone,update_CRM_phone

def get_lead_info(phone_number):
    """
    Takes a phone number as a string and returns it as an integer.
    
    Args:
        phone_number (str): A string containing a phone number
        
    Returns:
        int: The phone number converted to an integer
    """
    # Remove any non-digit characters from the phone number
    digits_only = ''.join(char for char in phone_number if char.isdigit())
    digits_only=int(digits_only)
    update_Chat_Phone(digits_only)
    update_CRM_phone(digits_only)
    # Convert to integer and return
    return digits_only