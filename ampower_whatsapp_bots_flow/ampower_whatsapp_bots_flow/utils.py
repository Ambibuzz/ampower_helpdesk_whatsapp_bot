# ampower_whatsapp_bots_flow/utils.py

import frappe

def send_message(to, message):
    """Send WhatsApp message using WhatsApp Message DocType"""
    try:
        # Get default WhatsApp account
        whatsapp_account = frappe.db.get_value(
            "WhatsApp Account",
            {"is_default_outgoing": 1},
            "name"
        )

        msg_doc = frappe.get_doc({
            "doctype": "WhatsApp Message",
            "to": to,
            "message": message,
            "content_type": "text",
            "whatsapp_account": whatsapp_account
        })
        msg_doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return True

    except Exception as e:
        frappe.log_error(
            title="WhatsApp Send Error",
            message=f"To: {to}\nError: {str(e)}"
        )
        return False


def get_optin(phone):
    """Return opt-in doc dict if user is opted in, else None"""
    return frappe.db.get_value(
        "WhatsApp Opt-in",
        {"phone_number": phone, "consent_status": "Opted In", "is_active": 1},
        ["name", "customer_name", "email", "department", "company"],
        as_dict=True
    )


def is_opted_in(phone):
    """Quick boolean check"""
    return bool(get_optin(phone))