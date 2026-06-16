# ampower_whatsapp_bots_flow/menu.py

import frappe
from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.utils import get_optin

def get_menu_text(customer_name):
    return (
        f"👋 Welcome back, *{customer_name}*!\n\n"
        "📋 *Main Menu*\n\n"
        "Reply with a number:\n\n"
        "1️⃣  Create New Ticket\n"
        "2️⃣  Get Ticket Status\n\n"
        "─────────────────\n"
        "Reply *STOP* to unsubscribe"
    )


def handle_menu(doc):
    """Keyword: MENU, HELP, OPTIONS, 0"""
    phone = doc.get("from")
    optin = get_optin(phone)

    if not optin:
        return "Please send *START* to register first."

    return get_menu_text(optin.customer_name)


def handle_menu_selection(doc):
    """
    Keyword: 1, 2
    Routes user to correct flow from main menu
    """
    phone = doc.get("from")
    message = doc.message.strip()
    optin = get_optin(phone)

    if not optin:
        return "Please send *START* to register first."

    if message == "1":
        # Start ticket creation flow
        frappe.cache().set_value(
            f"wa_ticket_{phone}",
            {"step": "awaiting_type"},
            expires_in_sec=600
        )
        return (
            "🎫 *Create New Ticket*\n\n"
            "Please select ticket type:\n\n"
            "1️⃣  Problem\n"
            "2️⃣  Query\n\n"
            "Reply with *1* or *2*"
        )

    elif message == "2":
        from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.ticket_status import handle_status_entry
        return handle_status_entry(phone)

    else:
        return get_menu_text(optin.customer_name)