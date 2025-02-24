

def update_CRM_phone(DB, lead_id, dealer_id, crm_new_lead_id, phone):

    phone_url = f"{PWA_CRM_API_URL}/lead/{crm_new_lead_id}?user_id={dealer_id}&new_phone={phone}"


    headers=create_token()
    r = requests.put(phone_url, headers=headers)
    return r.status_code






def update_Chat_Phone(message, lead_id):
    query = "Update leads SET phone_number= %s WHERE id = %s"
    data = (message, lead_id)
    conn_DBC = DB.connexion(
        PWA_DB_HOST_V12CHAT_WRITE,
        PWA_DB_USERNAME_V12CHAT_WRITE,
        PWA_DB_PASSWORD_V12CHAT_WRITE,
        PWA_DB_DATABASE_V12CHAT_WRITE,
    )
    res_update = DB.updateQuery(conn_DBC, query, data)