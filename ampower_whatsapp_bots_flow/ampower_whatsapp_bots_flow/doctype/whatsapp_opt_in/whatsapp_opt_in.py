# Copyright (c) 2026, Ambibuzz Technologies LLP and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from ampower_whatsapp_bots_flow.ampower_whatsapp_bots_flow.utils import send_message


class WhatsAppOptin(Document):
	def on_update(self):
		on_optin_update(self)

def on_optin_update(doc):
	# Detect transition from Pending → Opted In
	if doc.has_value_changed("consent_status"):
		if doc.consent_status == "Opted In" and doc.is_active:
			send_message(
				to=doc.phone_number,
				message=(
					f"✅ *Account Activated!*\n\n"
					f"Welcome, *{doc.customer_name}*! 🎉\n\n"
					f"You can now use Ambibuzz WhatsApp Support.\n\n"
					f"Reply *MENU* to get started."
				)
			)