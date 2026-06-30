# ampower_helpdesk_whatsapp_bot/ticket_status.py

import frappe

from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot import hd_client
from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.utils import get_optin

STATUS_EMOJI = {
    "Open": "🟡",
    "Replied": "🔵",
    "Resolved": "🟢",
    "Closed": "⚫",
    "On Hold": "🟠",
}


def handle_status_entry(phone):
    """
    Unified entry for both STATUS and SEARCH: show the latest 5 tickets and let
    the user reply with a number (open from list), a Ticket ID, or SUBJECT to
    search by title.
    """
    from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.menu import clear_pending_flows
    clear_pending_flows(phone)

    optin = get_optin(phone)
    tickets = _get_recent_tickets(phone)

    frappe.cache().set_value(
        f"wa_status_{phone}",
        {"step": "awaiting_selection", "tickets": [t["name"] for t in tickets]},
        expires_in_sec=600
    )

    if not tickets:
        return (
            "📭 No tickets found for your account.\n\n"
            "Type a *Ticket ID* to look one up, or *SUBJECT* to search by title.\n"
            "Type *MENU* to create a new ticket, or *EXIT* to cancel."
        )

    heading = "🏢 *Recent Company Tickets*" if _has_company_access(optin) else "📋 *Your Recent Tickets*"
    lines = [heading, ""]
    for i, ticket in enumerate(tickets, 1):
        emoji = STATUS_EMOJI.get(ticket["status"], "⚪")
        status_line = f"{emoji} {ticket['status']}"
        if ticket.get("ticket_type"):
            status_line += f" · {ticket['ticket_type']}"
        lines.append(f"{i}️⃣  Ticket *{ticket['name']}*")
        lines.append(status_line)
        lines.append(f"📅 {frappe.format(ticket['creation'], {'fieldtype': 'Date'})}")
        url = hd_client.ticket_url(ticket["name"])
        if url:
            lines.append(url)
        lines.append("")

    lines.append("─────────────────")
    lines.append("How to continue:")
    lines.append(f"• {_pick_a_number(len(tickets))} to open a ticket from the list above")
    lines.append("• Type a full *Ticket ID* (e.g. 0092) to look up any ticket")
    lines.append("• Type *SUBJECT* to search by title")
    lines.append("• Type *EXIT* to cancel")

    return "\n".join(lines)


# SEARCH and STATUS are the same flow now.
handle_search_entry = handle_status_entry


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

    # At the list: a number opens a ticket, SUBJECT starts a title search, and
    # anything else is treated as a Ticket ID lookup.
    if step == "awaiting_selection":

        # SUBJECT → ask for the title, search on the next message.
        if message.upper() == "SUBJECT":
            from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.menu import EXIT_HINT
            state["step"] = "awaiting_title"
            frappe.cache().set_value(f"wa_status_{phone}", state, expires_in_sec=600)
            return (
                "🔍 Type a few words from the ticket's *subject / title*:\n\n"
                f"{EXIT_HINT}"
            )

        # A short number matching a list position (1..N) opens that ticket.
        # Ticket IDs are themselves numeric (e.g. 0092), so we ONLY treat input
        # as a list pick when it lands in the small 1..N range; anything else —
        # including a longer number — is looked up as a Ticket ID.
        tickets = state.get("tickets", [])
        list_pick = _as_list_position(message, len(tickets))
        if list_pick is not None:
            frappe.cache().delete_value(f"wa_status_{phone}")
            return _get_ticket_detail(tickets[list_pick], phone)

        # Otherwise treat it as a Ticket ID lookup.
        frappe.cache().delete_value(f"wa_status_{phone}")
        return _get_ticket_detail(message, phone)

    # Search by title / subject
    elif step == "awaiting_title":
        return _handle_title_search(message, phone, state)

    return None


def _pick_a_number(count):
    """Plain-language instruction for picking from a numbered list.

    Avoids dev shorthand like "1 to 3" that non-technical users misread. Spells
    out the choices for short lists and uses clear phrasing for longer ones.
    """
    if count <= 1:
        return "Reply *1*"
    if count == 2:
        return "Reply *1* or *2*"
    options = ", ".join(f"*{i}*" for i in range(1, count))
    return f"Reply with the ticket number ({options} or *{count}*)"


def _as_list_position(message, count):
    """Return the 0-based index if `message` is a plain list pick (1..count).

    Ticket IDs are numeric and zero-padded (e.g. 0092), so we accept only a bare
    1..count with no leading zeros — that can't collide with a real Ticket ID.
    Returns None when it isn't a list pick.
    """
    text = message.strip()
    if not text.isdigit() or (len(text) > 1 and text[0] == "0"):
        return None
    n = int(text)
    if 1 <= n <= count:
        return n - 1
    return None


def _handle_title_search(term, phone, state):
    """Search the user's (or company's) tickets by subject and show top matches."""
    from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.menu import EXIT_HINT

    term = term.strip()
    if len(term) < 3:
        return (
            "Please type at least *3 characters* of the subject to search.\n\n"
            f"{EXIT_HINT}"
        )

    optin = get_optin(phone)
    matches = _search_tickets_by_subject(optin, term)

    if not matches:
        # Stay in title-search mode so the user can simply try different words.
        return (
            f"😕 No tickets found matching *{term}*.\n\n"
            "Try different words.\n\n"
            f"{EXIT_HINT}"
        )

    # Reuse the existing numbered-selection machinery.
    state["step"] = "awaiting_selection"
    state["tickets"] = [t["name"] for t in matches]
    frappe.cache().set_value(f"wa_status_{phone}", state, expires_in_sec=600)

    lines = [f"🔍 *Top matches for* “{term}”", ""]
    for i, ticket in enumerate(matches, 1):
        emoji = STATUS_EMOJI.get(ticket["status"], "⚪")
        lines.append(f"{i}️⃣  Ticket *{ticket['name']}*")
        lines.append(f"{emoji} {ticket['status']} · {ticket['subject']}")
        lines.append("")

    lines.append("─────────────────")
    lines.append(f"{_pick_a_number(len(matches))} to open a ticket, or *EXIT* to cancel.")
    return "\n".join(lines)


def _search_tickets_by_subject(optin, term):
    """Top 5 tickets whose subject matches `term`, scoped to what the user may see."""
    filters = _ticket_scope_filters(optin)
    filters["subject"] = ["like", f"%{term}%"]
    return hd_client.get_tickets(
        filters=filters,
        fields=["name", "subject", "status", "ticket_type", "creation"],
        order_by="creation desc",
        limit=5,
    )


def _get_ticket_detail(ticket_id, phone):
    """Fetch and display ticket detail — enforces ownership"""
    optin = get_optin(phone)

    ticket = hd_client.get_ticket(ticket_id)
    if not ticket:
        return (
            f"❌ Ticket *{ticket_id}* not found.\n\n"
            "Please check the ID and try again.\n"
            "Type *STATUS* to view your tickets, or *EXIT* to cancel."
        )

    # Security: validate access.
    #  - Own ticket: raised_by matches the person's email or phone.
    #  - Company access: the ticket belongs to the person's linked company.
    is_own = ticket["raised_by"] in [optin.email, phone]
    is_company = _has_company_access(optin) and ticket.get("customer") == optin.company

    if not (is_own or is_company):
        frappe.log_error(
            "WhatsApp Unauthorized Ticket Access",
            f"Phone: {phone} tried to access {ticket_id}"
        )
        return (
            "🔒 *Unauthorized Access*\n\n"
            "You are only authorized to check the "
            "status of your own tickets.\n\n"
            "Type *EXIT* to cancel."
        )

    emoji = STATUS_EMOJI.get(ticket["status"], "⚪")
    url = hd_client.ticket_url(ticket["name"])
    type_line = f"🏷️ Type: {ticket['ticket_type']}\n" if ticket.get("ticket_type") else ""
    link_block = f"🔗 *Open in Helpdesk:*\n{url}\n\n" if url else ""

    return (
        f"🎫 *Ticket Details*\n\n"
        f"📌 ID: *{ticket['name']}*\n"
        f"📋 Subject: {ticket['subject']}\n"
        f"{type_line}"
        f"{emoji} Status: *{ticket['status']}*\n"
        f"📅 Created: {frappe.format(ticket['creation'], {'fieldtype': 'Date'})}\n"
        f"🕐 Updated: {frappe.format(ticket['modified'], {'fieldtype': 'Date'})}\n\n"
        f"{link_block}"
        f"─────────────────\n"
        f"Type *STATUS* for your tickets, or *MENU* for the menu."
    )


def _has_company_access(optin):
    """True when this person may view all tickets for their company.

    The checkbox alone isn't enough — a linked company is required (the doctype
    enforces this on save, but we re-check defensively here).
    """
    return bool(optin.get("can_view_company_tickets") and optin.get("company"))


def _ticket_scope_filters(optin):
    """Filters that scope HD Tickets to what this person is allowed to see.

    Company-level access  -> all tickets for the linked HD Customer.
    Otherwise             -> only tickets the person raised.
    """
    if _has_company_access(optin):
        return {"customer": optin.company}
    return {"raised_by": optin.email}


def _get_recent_tickets(phone):
    """Get last 5 tickets this person is allowed to see"""
    optin = get_optin(phone)
    if not optin:
        return []

    return hd_client.get_tickets(
        filters=_ticket_scope_filters(optin),
        fields=["name", "subject", "status", "ticket_type", "creation"],
        order_by="creation desc",
        limit=5
    )