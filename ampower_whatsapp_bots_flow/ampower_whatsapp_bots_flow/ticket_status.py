# ampower_whatsapp_bots_flow/ticket_status.py

import frappe
from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.utils import get_optin

STATUS_EMOJI = {
    "Open": "🟡",
    "Replied": "🔵",
    "Resolved": "🟢",
    "Closed": "⚫",
    "On Hold": "🟠",
}


def handle_status_entry(phone):
    """Called from menu when user selects option 2"""
    tickets = _get_recent_tickets(phone)

    if not tickets:
        return (
            "📭 No tickets found for your account.\n\n"
            "Reply *1* to create a new ticket.\n"
            "Reply *MENU* to go back."
        )

    # Store state for search flow
    frappe.cache().set_value(
        f"wa_status_{phone}",
        {"step": "awaiting_selection", "tickets": [t.name for t in tickets]},
        expires_in_sec=600
    )

    lines = ["📋 *Your Recent Tickets*\n"]
    for i, ticket in enumerate(tickets, 1):
        emoji = STATUS_EMOJI.get(ticket.status, "⚪")
        lines.append(f"{i}️⃣  *{ticket.name}*")
        lines.append(f"    {emoji} {ticket.status} | {ticket.ticket_type}")
        lines.append(f"    📅 {frappe.format(ticket.creation, {'fieldtype': 'Date'})}")
        lines.append("")

    lines.append("─────────────────")
    lines.append("Reply ticket *number* to view details")
    lines.append("Reply *0* to search by Ticket ID")
    lines.append("Reply *MENU* to go back")

    return "\n".join(lines)


def handle_status_flow(doc):
    """
    Handles ticket status selection and search
    """
    phone = doc.get("from")
    message = doc.message.strip()
    optin = get_optin(phone)

    if not optin:
        return None

    state = frappe.cache().get_value(f"wa_status_{phone}")
    if not state:
        return None

    step = state.get("step")

    # User selected a ticket number from list or chose to search
    if step == "awaiting_selection":

        # Search by ID
        if message == "0":
            state["step"] = "awaiting_ticket_id"
            frappe.cache().set_value(f"wa_status_{phone}", state, expires_in_sec=600)
            return "🔍 Please enter the *Ticket ID* (e.g. HDT-2026-00042):"

        # Selected number from list
        tickets = state.get("tickets", [])
        try:
            idx = int(message) - 1
            if 0 <= idx < len(tickets):
                ticket_id = tickets[idx]
                frappe.cache().delete_value(f"wa_status_{phone}")
                return _get_ticket_detail(ticket_id, phone)
        except ValueError:
            pass

        return (
            "❌ Invalid selection.\n"
            "Reply with a ticket number from the list, "
            "or *0* to search by ID."
        )

    # Search by ticket ID
    elif step == "awaiting_ticket_id":
        frappe.cache().delete_value(f"wa_status_{phone}")
        ticket_id = message.upper().strip()
        return _get_ticket_detail(ticket_id, phone)

    return None


def _get_ticket_detail(ticket_id, phone):
    """Fetch and display ticket detail — enforces ownership"""
    optin = get_optin(phone)

    # Check ticket exists
    if not frappe.db.exists("HD Ticket", ticket_id):
        return (
            f"❌ Ticket *{ticket_id}* not found.\n\n"
            "Please check the ID and try again.\n"
            "Reply *2* to view your tickets."
        )

    ticket = frappe.get_doc("HD Ticket", ticket_id)

    # Security: validate ownership
    # Match by email or raised_by phone
    if ticket.raised_by not in [optin.email, phone]:
        frappe.log_error(
            "WhatsApp Unauthorized Ticket Access",
            f"Phone: {phone} tried to access {ticket_id}"
        )
        return (
            "🔒 *Unauthorized Access*\n\n"
            "You are only authorized to check the "
            "status of your own tickets."
        )

    emoji = STATUS_EMOJI.get(ticket.status, "⚪")

    return (
        f"🎫 *Ticket Details*\n\n"
        f"📌 ID: *{ticket.name}*\n"
        f"📋 Subject: {ticket.subject}\n"
        f"🏷️  Type: {ticket.ticket_type}\n"
        f"{emoji} Status: *{ticket.status}*\n"
        f"📅 Created: {frappe.format(ticket.creation, {'fieldtype': 'Date'})}\n"
        f"🕐 Updated: {frappe.format(ticket.modified, {'fieldtype': 'Date'})}\n\n"
        f"─────────────────\n"
        f"Reply *MENU* to go back."
    )


def _get_recent_tickets(phone):
    """Get last 5 tickets for this phone number"""
    optin = get_optin(phone)
    if not optin:
        return []

    return frappe.get_all(
        "HD Ticket",
        filters={
            "raised_by": optin.email
        },
        fields=["name", "subject", "status", "ticket_type", "creation"],
        order_by="creation desc",
        limit=5
    )