# ampower_whatsapp_bots_flow/opt_in.py

import frappe
from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.utils import send_message, get_optin

def handle_start(doc):
    """
    Keyword: START, HI, HELLO, HELP
    Entry point — check opt-in status and route accordingly
    """
    phone = doc.get("from")
    optin = get_optin(phone)

    if optin:
        # Already opted in → go to menu
        from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.menu import get_menu_text
        return get_menu_text(optin.customer_name)

    # Check if pending approval
    pending = frappe.db.get_value(
        "WhatsApp Opt-in",
        {"phone_number": phone, "consent_status": "Pending"},
        "name"
    )

    if pending:
        return (
            "⏳ Your registration is pending admin approval.\n\n"
            "You'll be notified once your account is activated."
        )

    # state = frappe.cache().get_value(f"wa_onboard_{phone}")
    # frappe.log_error(title=f"{phone} * : {state.get('step')} =>", message= f"msg : {state}")
    
    # New user — start onboarding
    # Store state so next message captures name
    frappe.cache().set_value(
        f"wa_onboard_{phone}", 
        {"step": "awaiting_name"}, 
        expires_in_sec=600
    )

    return (
        "👋 Welcome to *Ambibuzz Support*!\n\n"
        "To get started, we need a few details.\n\n"
        "Please enter your *Full Name*:"
    )


def handle_onboarding(doc):
    """
    Handles multi-step onboarding conversation:
    Step 1: Name
    Step 2: Department
    Step 3: Email
    → Creates WhatsApp Opt-in with Pending status
    """
    phone = doc.get("from")
    message = doc.message.strip()

    state = frappe.cache().get_value(f"wa_onboard_{phone}")
    # frappe.log_error(title=f"{phone} : {state.get('step')} =>", message= f"msg : {state}")
    if not state:
        return None  # Not in onboarding — let other rules handle

    step = state.get("step")
    frappe.log_error(title=f"{phone} : {step} =>",message= f"msg : {message}")
    if step == "awaiting_name":
        state["customer_name"] = message
        state["step"] = "awaiting_department"
        frappe.cache().set_value(f"wa_onboard_{phone}", state, expires_in_sec=600)
        return (
            f"Thanks, *{message}*! 👍\n\n"
            "Please enter your *Department*:"
        )

    elif step == "awaiting_department":
        state["department"] = message
        state["step"] = "awaiting_email"
        frappe.cache().set_value(f"wa_onboard_{phone}", state, expires_in_sec=600)
        return (
            "Got it! Now please enter your *Official Email ID*:"
        )

    elif step == "awaiting_email":
        # Basic email validation
        if "@" not in message or "." not in message:
            return "❌ Please enter a valid email address:"

        state["email"] = message
        frappe.cache().delete_value(f"wa_onboard_{phone}")

        # Create WhatsApp Opt-in as Pending
        try:
            optin_doc = frappe.get_doc({
                "doctype": "WhatsApp Opt-in",
                "phone_number": phone,
                "customer_name": state.get("customer_name"),
                "department": state.get("department"),
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
                f"🏢 Department: {state.get('department')}\n"
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

    optin = frappe.db.exists(
        "WhatsApp Opt-in",
        {"phone_number": phone, "consent_status": "Opted In"}
    )

    if optin:
        optin_doc = frappe.get_doc("WhatsApp Opt-in", optin)
        optin_doc.consent_status = "Opted Out"
        optin_doc.opt_out_date = frappe.utils.now()
        optin_doc.is_active = 0
        optin_doc.save(ignore_permissions=True)
        frappe.db.commit()

        return (
            "You've been unsubscribed. 👋\n\n"
            "Reply *START* anytime to reactivate."
        )

    return "You are not currently subscribed."