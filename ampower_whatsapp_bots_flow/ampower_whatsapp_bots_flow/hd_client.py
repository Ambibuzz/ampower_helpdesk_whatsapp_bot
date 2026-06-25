# ampower_whatsapp_bots_flow/hd_client.py

"""
HTTP client for the remote Helpdesk site.

Instead of reaching HD Ticket data through the local Frappe ORM, we read the
remote site's URL and token from the `Ampower Bot Configuration` single DocType and talk
to its REST API. Scoped to HD Ticket: create (handle) and fetch.
"""

from urllib.parse import quote

import frappe
import requests


def _config():
    """Return (base_url, token) from the Ampower Bot Configuration single DocType."""
    cfg = frappe.get_cached_doc("Ampower Bot Configuration")
    token = cfg.get_password("api_token") if cfg.api_token else None
    if not cfg.api_url or not token:
        frappe.throw("Ampower Bot Configuration is missing an API URL or API Token.")
    return cfg.api_url.rstrip("/"), token


def _headers():
    _, token = _config()
    return {
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def ticket_url(name: str) -> str | None:
    """
    Build a link to a ticket in the remote Helpdesk portal, or None if the
    Helpdesk URL isn't configured. WhatsApp auto-links a bare URL in text.
    """
    cfg = frappe.get_cached_doc("Ampower Bot Configuration")
    if not cfg.api_url:
        return None
    base = cfg.api_url.rstrip("/")
    return f"{base}/helpdesk/tickets/{quote(str(name), safe='')}"


def create_ticket(ticket: dict) -> dict:
    """
    Create an HD Ticket on the remote Helpdesk.

    `ticket` is the field dict (the "doctype" key is added here).
    Returns the created ticket's data dict (including its `name`).
    """
    base, _ = _config()
    payload = {"doctype": "HD Ticket", **ticket}
    response = requests.post(
        f"{base}/api/resource/HD Ticket",
        headers=_headers(),
        data=frappe.as_json(payload),
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["data"]


def get_ticket(name: str) -> dict | None:
    """
    Fetch a single HD Ticket from the remote Helpdesk.
    Returns the data dict, or None if it does not exist (404).
    """
    base, _ = _config()
    response = requests.get(
        f"{base}/api/resource/HD Ticket/{quote(str(name), safe='')}",
        headers=_headers(),
        timeout=30,
    )
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()["data"]


def get_tickets(filters=None, fields=None, order_by=None, limit=None) -> list:
    """
    List HD Tickets from the remote Helpdesk. Mirrors frappe.get_all semantics.
    Returns a list of data dicts.
    """
    base, _ = _config()
    params = {}
    if filters:
        params["filters"] = frappe.as_json(filters)
    if fields:
        params["fields"] = frappe.as_json(fields)
    if order_by:
        params["order_by"] = order_by
    if limit:
        params["limit_page_length"] = limit
    response = requests.get(
        f"{base}/api/resource/HD Ticket",
        headers=_headers(),
        params=params,
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["data"]
