# ampower_helpdesk_whatsapp_bot/ticket_create.py

import frappe

from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot import hd_client
from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.utils import get_optin

TICKET_TYPES = {"1": "Problem", "2": "Query"}

# Valid ticket types, keyed by the canonical label used on the HD Ticket.
VALID_TICKET_TYPES = ("Problem", "Query")


def handle_ticket_entry(phone, ticket_type=None):
    """
    Start the create-ticket flow. If `ticket_type` is supplied (e.g. the user
    chose "New Problem"/"New Query"), skip the type-selection step and go
    straight to the description. If omitted, fall back to asking for the type.
    """
    from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.menu import (
        EXIT_HINT,
        clear_pending_flows,
    )
    clear_pending_flows(phone)

    if ticket_type in VALID_TICKET_TYPES:
        frappe.cache().set_value(
            f"wa_ticket_{phone}",
            {"step": "awaiting_description", "ticket_type": ticket_type},
            expires_in_sec=600,
        )
        return (
            f"🎫 *New {ticket_type}*\n\n"
            "📝 Please describe your issue in detail:\n\n"
            f"{EXIT_HINT}"
        )

    # No type chosen yet — ask for it.
    frappe.cache().set_value(
        f"wa_ticket_{phone}",
        {"step": "awaiting_type"},
        expires_in_sec=600,
    )
    return (
        "🎫 *Create New Ticket*\n\n"
        "What would you like to raise?\n\n"
        "1️⃣  New Problem\n"
        "2️⃣  New Query\n\n"
        "Type *1* or *2*\n\n"
        f"{EXIT_HINT}"
    )


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

    from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.menu import EXIT_HINT

    # Step 1: Ticket type
    if step == "awaiting_type":
        if message not in ("1", "2"):
            return (
                "❌ Invalid selection. Please reply:\n\n"
                "1️⃣  New Problem\n"
                "2️⃣  New Query\n\n"
                f"{EXIT_HINT}"
            )

        state["ticket_type"] = TICKET_TYPES[message]
        state["step"] = "awaiting_description"
        frappe.cache().set_value(f"wa_ticket_{phone}", state, expires_in_sec=600)

        return (
            f"🎫 *New {TICKET_TYPES[message]}*\n\n"
            "📝 Please describe your issue in detail:\n\n"
            f"{EXIT_HINT}"
        )

    # Step 2: Description → create the ticket
    elif step == "awaiting_description":
        if len(message) < 10:
            return (
                "❌ Description too short. Please provide more detail:\n\n"
                f"{EXIT_HINT}"
            )

        state["description"] = message
        return _finalize_ticket(phone, state, optin)

    return None


def _finalize_ticket(phone, state, optin):
    """Create the HD Ticket and report back."""
    frappe.cache().delete_value(f"wa_ticket_{phone}")

    description = state.get("description", "")

    try:
        original_user = frappe.session.user
        try:
            frappe.set_user("Administrator")
            ticket = _create_hd_ticket(
                customer_name=optin.company,
                email=optin.email,
                phone=phone,
                ticket_type=state.get("ticket_type"),
                description=description,
            )
        finally:
            frappe.set_user(original_user)
    except Exception as e:
        frappe.log_error("HD Ticket Creation Error", str(e))
        return (
            "❌ Failed to create ticket. Please try again.\n"
            "Type *MENU* to start over."
        )

    url = hd_client.ticket_url(ticket)
    link_block = f"🔗 *Open in Helpdesk:*\n{url}\n\n" if url else ""

    return (
        f"✅ *Ticket Created Successfully!*\n\n"
        f"🎫 Ticket ID: *{ticket}*\n"
        f"📌 Type: {state.get('ticket_type')}\n"
        f"📋 Description: {description[:80]}{'...' if len(description) > 80 else ''}\n\n"
        f"{link_block}"
        f"Our team is reviewing your request.\n"
        f"Type *STATUS* to check your tickets, or *MENU* for the menu."
    )


def _create_hd_ticket(customer_name, email, phone, ticket_type, description):
    """
    Create ticket on the remote Helpdesk (HD Ticket) via Ampower Bot Configuration API
    """
    ticket = hd_client.create_ticket({
        "subject": f"{ticket_type}: {description[:60]}",
        "description": description,
        "ticket_type": ticket_type,
        "raised_by": email or phone,
        "customer": customer_name,
        "via_customer_portal": 0,
        "source": "WhatsApp",
        "status": "Open"
    })
    return ticket["name"]
