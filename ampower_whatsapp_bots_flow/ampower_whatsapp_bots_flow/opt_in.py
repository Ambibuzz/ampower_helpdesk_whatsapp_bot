# ampower_whatsapp_bots_flow/opt_in.py

import frappe

def handle_start(doc):
    """
    Keyword: START, HI, HELLO, HELP
    Entry point — check opt-in status and route accordingly
    """
    phone = doc.get("from")

    # START is a fresh entry point — cancel any flow the user was mid-way through.
    from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.menu import clear_pending_flows
    clear_pending_flows(phone)

    existing = frappe.db.get_value(
        "WhatsApp Opt-in",
        {"phone_number": phone},
        ["name", "customer_name", "consent_status", "is_active"],
        as_dict=True
    )

    if existing:
        if existing.consent_status == "Pending":
            return (
                "⏳ Your registration is pending admin approval.\n\n"
                "You'll be notified once your account is activated."
            )

        # Registered but not yet approved / deactivated by admin
        if not existing.is_active:
            return (
                "⚠️ Your account isn't active yet.\n\n"
                "Please contact your administrator to activate access."
            )

        # Previously unsubscribed → re-opt-in on START
        if existing.consent_status == "Opted Out":
            frappe.db.set_value(
                "WhatsApp Opt-in", existing.name,
                {"consent_status": "Opted In", "opt_out_date": None}
            )
            frappe.db.commit()

        from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.menu import (
            arm_menu_context,
            get_menu_text,
        )
        # Lands on the menu → arm context so 1/2/3 work as selections.
        arm_menu_context(phone)
        return get_menu_text(existing.customer_name)

    # New user — start onboarding
    frappe.cache().set_value(
        f"wa_onboard_{phone}",
        {"step": "awaiting_name"},
        expires_in_sec=600
    )

    from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.menu import EXIT_HINT
    return (
        "👋 Welcome to *Ambibuzz Support*!\n\n"
        "To get started, we need a few details.\n\n"
        "Please enter your *Full Name*:\n\n"
        f"{EXIT_HINT}"
    )


def handle_onboarding(doc):
    """
    Handles multi-step onboarding conversation:
    Step 1: Name
    Step 2: Company Name
    Step 3: Email
    → Creates WhatsApp Opt-in with Pending status
    """
    phone = doc.get("from")
    message = doc.message.strip()

    state = frappe.cache().get_value(f"wa_onboard_{phone}")
    if not state:
        return None  # Not in onboarding — let other rules handle

    step = state.get("step")
    from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.menu import EXIT_HINT

    if step == "awaiting_name":
        state["customer_name"] = message
        state["step"] = "awaiting_company_name"
        frappe.cache().set_value(f"wa_onboard_{phone}", state, expires_in_sec=600)
        return (
            f"Thanks, *{message}*! 👍\n\n"
            "Please enter your *Company Name*:\n\n"
            f"{EXIT_HINT}"
        )

    elif step == "awaiting_company_name":
        # Store whatever the customer typed verbatim.
        state["entered_company_name"] = message
        # Best-effort link to an HD Customer when the typed name matches one;
        # otherwise leave company empty and keep the raw text.
        state["company"] = frappe.db.get_value(
            "HD Customer", {"name": message}, "name"
        )
        state["step"] = "awaiting_email"
        frappe.cache().set_value(f"wa_onboard_{phone}", state, expires_in_sec=600)
        return (
            "Got it! Now please enter your *Official Email ID*:\n\n"
            f"{EXIT_HINT}"
        )

    elif step == "awaiting_email":
        if "@" not in message or "." not in message:
            return (
                "❌ Please enter a valid email address:\n\n"
                f"{EXIT_HINT}"
            )

        state["email"] = message
        frappe.cache().delete_value(f"wa_onboard_{phone}")

        # Create WhatsApp Opt-in as Pending
        try:
            optin_doc = frappe.get_doc({
                "doctype": "WhatsApp Opt-in",
                "phone_number": phone,
                "customer_name": state.get("customer_name"),
                "entered_company_name": state.get("entered_company_name"),
                "company": state.get("company"),
                "email": state.get("email"),
                "consent_status": "Pending",
                "consent_method": "Chatbot",
                "consent_date": frappe.utils.now(),
                "is_active": 0
            })
            optin_doc.insert(ignore_permissions=True)
            frappe.db.commit()

            return (
                "✅ *Registration Submitted Successfully!*\n\n"
                f"📋 Name: {state.get('customer_name')}\n"
                f"🏢 Company: {state.get('entered_company_name')}\n"
                f"📧 Email: {state.get('email')}\n\n"
                "Your account is pending admin approval.\n"
                "You'll receive a confirmation once activated. ⏳"
            )

        except Exception as e:
            frappe.log_error("WhatsApp Opt-in Creation Error", str(e))
            return "❌ Something went wrong. Please try again by sending START."

    return None


def handle_stop(doc):
    """Keyword: STOP, UNSUBSCRIBE"""
    phone = doc.get("from")

    # Cancel any in-progress flow before asking to unsubscribe. This clears any
    # prior wa_unsub_ too; the fresh confirmation set below is the only one left.
    from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.menu import clear_pending_flows
    clear_pending_flows(phone)

    optin = frappe.db.exists(
        "WhatsApp Opt-in",
        {"phone_number": phone, "consent_status": "Opted In"}
    )

    if not optin:
        return "You are not currently subscribed."

    # Ask for confirmation before opting out; the reply is handled by
    # handle_unsubscribe_flow.
    frappe.cache().set_value(
        f"wa_unsub_{phone}",
        {"step": "awaiting_confirmation"},
        expires_in_sec=600
    )

    from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.menu import EXIT_HINT
    return (
        "⚠️ *Confirm Unsubscribe*\n\n"
        "Are you sure you want to unsubscribe from Ambibuzz WhatsApp Support?\n\n"
        "Type *YES* to confirm.\n"
        "Type *NO* to stay subscribed.\n\n"
        f"{EXIT_HINT}"
    )


def handle_unsubscribe_flow(doc):
    """Handles the YES/NO confirmation after a STOP/UNSUBSCRIBE request."""
    phone = doc.get("from")
    message = doc.message.strip()

    state = frappe.cache().get_value(f"wa_unsub_{phone}")
    if not state:
        return None

    if message.upper() in ("YES", "Y"):
        frappe.cache().delete_value(f"wa_unsub_{phone}")
        optin = frappe.db.exists(
            "WhatsApp Opt-in",
            {"phone_number": phone, "consent_status": "Opted In"}
        )
        if not optin:
            return "You are not currently subscribed."

        # Unsubscribe = change the user's consent only; leave is_active (admin
        # approval flag) untouched so re-opting in via START is instant.
        frappe.db.set_value(
            "WhatsApp Opt-in", optin,
            {"consent_status": "Opted Out", "opt_out_date": frappe.utils.now()}
        )
        frappe.db.commit()

        return (
            "You've been unsubscribed. 👋\n\n"
            "Type *START* anytime to reactivate."
        )

    if message.upper() in ("NO", "N"):
        frappe.cache().delete_value(f"wa_unsub_{phone}")
        return (
            "👍 You're still subscribed.\n\n"
            "Type *MENU* for the menu."
        )

    from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.menu import EXIT_HINT
    return (
        "Please reply *YES* to unsubscribe or *NO* to stay subscribed.\n\n"
        f"{EXIT_HINT}"
    )
