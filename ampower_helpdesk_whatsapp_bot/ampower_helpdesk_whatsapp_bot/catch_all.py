# Catch-all script:
# ampower_helpdesk_whatsapp_bot/catch_all.py

import frappe

from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.opt_in import (
    handle_onboarding,
    handle_unsubscribe_flow,
)
from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.ticket_create import handle_ticket_flow
from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.ticket_status import handle_status_flow
from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.utils import get_optin


def _matches_configured_keyword(message, account):
    """
    Return True if the message matches any enabled, non-wildcard keyword in the
    WhatsApp Keyword Reply doctype.

    This is dynamic on purpose: whatever keywords are configured there (now or in
    future) count. The `*` catch-all rule is excluded — it matches everything and
    is the rule that routes here, so it is not a real "keyword" for this purpose.
    """
    try:
        from frappe_whatsapp_chatbot.chatbot.keyword_matcher import KeywordMatcher

        matcher = KeywordMatcher(account)
        # Drop the wildcard rule so it doesn't match every message.
        matcher.rules = [r for r in matcher.rules if (r.keywords or "").strip() != "*"]
        return matcher.match(message) is not None
    except Exception as e:
        frappe.log_error(f"_matches_configured_keyword error: {str(e)}")
        return False


def handle_catch_all(doc):
    phone = doc.get("from")
    message = doc.message.strip()

    # Handle a pending unsubscribe confirmation first
    result = handle_unsubscribe_flow(doc)
    if result:
        return result

    # Any configured keyword cancels an in-progress flow before the awaiting
    # handlers run, so a stray keyword isn't swallowed by a flow the user left.
    # Dynamic: driven by the WhatsApp Keyword Reply doctype.
    if _matches_configured_keyword(message, doc.get("whatsapp_account")):
        from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.menu import clear_pending_flows
        clear_pending_flows(phone)

    # Universal SEARCH / STATUS — identical behaviour, work from anywhere: show
    # the recent tickets and the lookup options. Pre-empt active flows.
    if message.strip().lower() in ("search", "status", "ticket status") and get_optin(phone):
        from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.ticket_status import handle_status_entry
        return handle_status_entry(phone)

    result = handle_ticket_flow(doc)
    if result:
        return result

    result = handle_status_flow(doc)
    if result:
        return result

    result = handle_onboarding(doc)
    if result:
        return result

    # No active flow: handle a menu selection, but only if the menu was just
    # shown (armed context) — otherwise a stray "1"/"problem" falls to default.
    from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.menu import (
        global_ticket_type,
        handle_menu_selection,
        has_menu_context,
        is_menu_choice,
    )
    optin = get_optin(phone)
    if optin and is_menu_choice(message) and has_menu_context(phone):
        return handle_menu_selection(doc)

    # Word shortcuts work from anywhere when idle. They run after the flow
    # handlers so an active flow consumes the word as input first.
    if optin:
        ticket_type = global_ticket_type(message)
        if ticket_type:
            from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.ticket_create import (
                handle_ticket_entry,
            )
            return handle_ticket_entry(phone, ticket_type=ticket_type)

    # Proactive fallback: registered users get a guided list of what they can
    # type (and we re-arm the menu context so a follow-up 1/2/3 works); everyone
    # else is pointed at START.
    if optin:
        from ampower_helpdesk_whatsapp_bot.ampower_helpdesk_whatsapp_bot.menu import (
            arm_menu_context,
            get_help_text,
        )
        arm_menu_context(phone)
        return get_help_text(optin.customer_name)

    return (
        "👋 Welcome to *Ambibuzz Support*!\n\n"
        "Type *START* to register and get help."
    )