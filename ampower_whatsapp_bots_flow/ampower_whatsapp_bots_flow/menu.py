# ampower_whatsapp_bots_flow/menu.py

import frappe
from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.utils import get_optin

# Canonical menu actions — the single source of truth for both the main menu
# and the help/fallback, so they never drift apart. Each: (number, icon, name,
# one-line description).
MENU_OPTIONS = (
    ("1️⃣", "🛠️", "New Problem", "report an issue"),
    ("2️⃣", "❓", "New Query", "ask a question"),
    ("3️⃣", "📋", "Ticket Status / Search", "view or look up your tickets"),
)


def get_menu_text(customer_name):
    lines = [
        f"👋 Welcome back, *{customer_name}*!",
        "",
        "📋 *Main Menu*",
        "",
        "Type a number:",
        "",
    ]
    for number, icon, name, _desc in MENU_OPTIONS:
        lines.append(f"{number}  {icon}  {name}")
    lines += [
        "",
        "─────────────────",
        "💡 Type *SEARCH* or *STATUS* anytime to look up a ticket.",
        "Type *EXIT* to cancel and return here anytime.",
        "Type *STOP* to unsubscribe.",
    ]
    return "\n".join(lines)


def get_help_text(customer_name=None):
    """Friendly 'here's what you can do' reply.

    Used as the fallback for unrecognised messages — proactively listing the
    same actions as the main menu (kept in sync via MENU_OPTIONS).
    """
    greeting = f"Hi *{customer_name}*! 👋" if customer_name else "👋"
    lines = [f"{greeting} How can I help you today?", ""]
    for number, icon, name, desc in MENU_OPTIONS:
        lines.append(f"{number}  {icon}  *{name}* — {desc}")
    lines += [
        "",
        "Type a number, or *MENU* for the full menu.",
        "Type *EXIT* to cancel anytime.",
    ]
    return "\n".join(lines)


# Short, reusable footer reminding users they can bail out of any flow. EXIT is
# a keyword that works everywhere; appending this keeps the prompts consistent.
EXIT_HINT = "_Type *EXIT* to cancel._"


# Menu replies — number or plain-word phrasing — mapped to the action they trigger.
MENU_NEW_PROBLEM = {"1", "new problem", "problem"}
MENU_NEW_QUERY = {"2", "new query", "query"}
MENU_STATUS = {"3", "status", "ticket status"}

# Word shortcuts that start a ticket from anywhere, like SEARCH. Numbers are
# excluded — a bare "1" typed idle is ambiguous and stays scoped to the menu.
GLOBAL_NEW_PROBLEM = {"new problem", "problem"}
GLOBAL_NEW_QUERY = {"new query", "query"}


def global_ticket_type(message):
    """Return 'Problem'/'Query' if the message is a global ticket shortcut, else None."""
    choice = message.strip().lower()
    if choice in GLOBAL_NEW_PROBLEM:
        return "Problem"
    if choice in GLOBAL_NEW_QUERY:
        return "Query"
    return None


def _menu_context_key(phone):
    return f"wa_menu_{phone}"


def arm_menu_context(phone):
    """Mark that the main menu was just shown to this phone.

    Menu shortcuts (1/2/3 and their word forms) are only honoured while this
    marker is set — i.e. as a direct reply to the menu. This keeps them from
    behaving like global keywords: a stray "1" or "problem" with no menu on
    screen falls through to the default handler instead of silently acting.
    """
    frappe.cache().set_value(_menu_context_key(phone), 1, expires_in_sec=600)


def has_menu_context(phone):
    """True if the menu was recently shown and is awaiting a selection."""
    return bool(frappe.cache().get_value(_menu_context_key(phone)))


def clear_menu_context(phone):
    frappe.cache().delete_value(_menu_context_key(phone))


# Every per-phone conversational-state cache key this app sets. Keep this list
# in sync when adding a new flow so clear_pending_flows() stays exhaustive.
FLOW_STATE_KEYS = ("wa_ticket", "wa_status", "wa_onboard", "wa_unsub")


def clear_pending_flows(phone):
    """Cancel every in-progress conversational flow for this phone.

    Top-level entry points (MENU, START, STOP, SEARCH, and any configured
    keyword) wipe stale awaiting state, otherwise the next reply gets consumed
    by a flow the user already left.

    Includes the unsubscribe confirmation: handle_stop() calls this *before*
    setting wa_unsub_, so its own confirmation survives, while every other entry
    point cancels a dangling one (a stray YES can't then unsubscribe the user).
    """
    for key in FLOW_STATE_KEYS:
        frappe.cache().delete_value(f"{key}_{phone}")
    # handle_menu re-arms this right after, so the menu path is unaffected.
    clear_menu_context(phone)


def handle_menu(doc):
    """Keyword: MENU, OPTIONS, EXIT"""
    phone = doc.get("from")

    # EXIT/MENU always cancels whatever was in progress — including a half-done
    # onboarding for a not-yet-registered user — so it never dead-ends.
    clear_pending_flows(phone)

    optin = get_optin(phone)
    if not optin:
        return "Type *START* to register first."

    arm_menu_context(phone)
    return get_menu_text(optin.customer_name)


def handle_menu_selection(doc):
    """
    Routes a main-menu reply to the right flow. Accepts both the number and the
    plain-word phrasing (e.g. "1" or "new problem").
    """
    phone = doc.get("from")
    choice = doc.message.strip().lower()
    optin = get_optin(phone)

    if not optin:
        return "Type *START* to register first."

    from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.ticket_create import handle_ticket_entry

    # A valid selection consumes the menu context so the same reply can't re-fire.
    if choice in MENU_NEW_PROBLEM:
        clear_menu_context(phone)
        return handle_ticket_entry(phone, ticket_type="Problem")

    if choice in MENU_NEW_QUERY:
        clear_menu_context(phone)
        return handle_ticket_entry(phone, ticket_type="Query")

    if choice in MENU_STATUS:
        clear_menu_context(phone)
        from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.ticket_status import handle_status_entry
        return handle_status_entry(phone)

    # Unrecognised — re-show the menu, keep the context armed.
    arm_menu_context(phone)
    return get_menu_text(optin.customer_name)


MENU_CHOICES = MENU_NEW_PROBLEM | MENU_NEW_QUERY | MENU_STATUS


def is_menu_choice(message):
    """True if `message` is a recognised main-menu selection (number or words)."""
    return message.strip().lower() in MENU_CHOICES
