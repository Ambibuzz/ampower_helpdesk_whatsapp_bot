# Catch-all script:
# ampower_whatsapp_bots_flow/catch_all.py

import frappe
from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.opt_in import handle_onboarding, get_optin
from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.ticket_create import handle_ticket_flow
from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.ticket_status import handle_status_flow

def handle_catch_all(doc):
    phone = doc.get("from")
    message = doc.message.strip()

    # Try ticket creation flow first
    result = handle_ticket_flow(doc)
    if result:
        return result

    # Try ticket status flow
    result = handle_status_flow(doc)
    if result:
        return result

    # Try onboarding flow
    result = handle_onboarding(doc)
    if result:
        return result
    
     # 4. No active state — handle menu selection
    optin = get_optin(phone)
    if optin and message in ("1", "2"):
        from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.menu import handle_menu_selection
        return handle_menu_selection(doc)

    # Default fallback
    return (
        "Sorry, I didn't understand that. 🤔\n\n"
        "Reply *MENU* to see available options\n"
        "Reply *START* to register"
    )