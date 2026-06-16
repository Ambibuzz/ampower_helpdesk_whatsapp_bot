# ampower_whatsapp_bots_flow/ticket_create.py

import frappe
from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.utils import get_optin

TICKET_TYPES = {"1": "Problem", "2": "Query"}


def handle_ticket_flow(doc):
    """
    Handles multi-step ticket creation:
    Step 1: Type selection (1/2)
    Step 2: Description
    → Creates HD Ticket in Frappe Helpdesk
    """
    phone = doc.get("from")
    message = doc.message.strip()

    optin = get_optin(phone)
    if not optin:
        return None

    state = frappe.cache().get_value(f"wa_ticket_{phone}")
    if not state:
        return None  # Not in ticket flow

    step = state.get("step")

    # Step 1: Ticket type
    if step == "awaiting_type":
        if message not in ("1", "2"):
            return (
                "❌ Invalid selection. Please reply:\n\n"
                "1️⃣  Problem\n"
                "2️⃣  Query"
            )

        state["ticket_type"] = TICKET_TYPES[message]
        state["step"] = "awaiting_description"
        frappe.cache().set_value(f"wa_ticket_{phone}", state, expires_in_sec=600)

        return (
            f"✅ Type: *{TICKET_TYPES[message]}*\n\n"
            "📝 Please describe your issue in detail:"
        )

    # Step 2: Description → Create ticket
    elif step == "awaiting_description":
        if len(message) < 10:
            return "❌ Description too short. Please provide more detail:"

        frappe.cache().delete_value(f"wa_ticket_{phone}")

        try:
            original_user = frappe.session.user

            try:
                frappe.set_user("Administrator")

                ticket = _create_hd_ticket(
                    customer_name=optin.company,
                    email=optin.email,
                    phone=phone,
                    ticket_type=state.get("ticket_type"),
                    description=message
                )

            finally:
                frappe.set_user(original_user)

            return (
                f"✅ *Ticket Created Successfully!*\n\n"
                f"🎫 Ticket ID: *{ticket}*\n"
                f"📌 Type: {state.get('ticket_type')}\n"
                f"📋 Description: {message[:80]}{'...' if len(message) > 80 else ''}\n\n"
                f"Our team is reviewing your request.\n"
                f"Reply *2* to check ticket status anytime.\n"
                f"Reply *MENU* to go back."
            )

        except Exception as e:
            frappe.log_error("HD Ticket Creation Error", str(e))
            return (
                "❌ Failed to create ticket. Please try again.\n"
                "Reply *1* to retry or *MENU* to go back."
            )

    return None


def _create_hd_ticket(customer_name, email, phone, ticket_type, description):
    """
    Create ticket in Frappe Helpdesk (HD Ticket DocType)
    """
    ticket = frappe.get_doc({
        "doctype": "HD Ticket",
        "subject": f"{ticket_type}: {description[:60]}",
        "description": description,
        "ticket_type": ticket_type,
        "raised_by": email or phone,
        "customer": customer_name,
        "via_customer_portal": 0,
        "source": "WhatsApp",
        "status": "Open"
    })
    ticket.insert(ignore_permissions=True)
    frappe.db.commit()
    return ticket.name