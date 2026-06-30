# Ampower Helpdesk Whatsapp Bot


A WhatsApp self-service bot for [Frappe Helpdesk](https://github.com/frappe/helpdesk). Customers register, raise tickets (Problem / Query), and look up ticket status - entirely over WhatsApp chat. Tickets are created and read on a **remote** Helpdesk site through its REST API, so this app does **not** require Helpdesk to be installed locally.

> A Frappe app by [Ambibuzz Technologies LLP](https://www.ambibuzz.com).

## What it does

For an end user, the entire support workflow happens in a WhatsApp thread:

- **Register** - a guided onboarding (Name → Company → Email) creates an opt-in record, pending admin approval.
- **Raise a ticket** - choose *Problem* or *Query*, describe the issue; an `HD Ticket` is created on the remote Helpdesk with `source = WhatsApp`.
- **Check status / search** - list the 5 most recent tickets, open one by number, look one up by Ticket ID, or search by subject.
- **Manage consent** - `STOP` to unsubscribe (with a YES/NO confirmation), `START` to re-subscribe instantly.

## Doctypes

### Ampower Bot Configuration (Single)

Holds the connection to the remote Helpdesk REST API.

| Field | Type | Notes |
| --- | --- | --- |
| `api_url` | Data (URL), required | Base URL of the remote Helpdesk, e.g. `https://helpdesk.example.com` |
| `api_token` | Password, required | Token in the form `api_key:api_secret` |

### WhatsApp Opt-in

One record per registered phone number. Autonamed `{phone_number}-{email}`.

| Field | Type | Notes |
| --- | --- | --- |
| `phone_number` | Data | The WhatsApp number (record key) |
| `customer_name` | Data | Name entered during onboarding |
| `email` | Data | Used as `raised_by` on tickets and for ownership checks |
| `entered_company_name` | Data | Raw company text the user typed |
| `company` | Link → `HD Customer` | Set only when the typed name matches an existing HD Customer |
| `can_view_company_tickets` | Check | Grants company-wide ticket visibility (requires a linked `company`) |
| `consent_status` | Select | `Pending` / `Opted In` / `Opted Out` |
| `consent_method` | Select | `Chatbot` / `Manual` / `Web Form` |
| `consent_date` / `opt_out_date` | Data | Timestamps |
| `is_active` | Check | Admin approval flag - the bot only serves users with `Opted In` **and** `is_active = 1` |

A user is "live" only when `consent_status = Opted In` **and** `is_active = 1`; onboarding leaves them `Pending` / inactive until an admin approves.
---

## Access control

When a user looks up tickets, what they can see is scoped

- **Company access** - when `can_view_company_tickets` is enabled *and* a `company` is linked, the user sees **all** tickets for their `Company`.
- **Otherwise** - only the tickets they raised (`raised_by` matches their email).

Individual ticket detail is additionally re-checked on open: access is granted only if the ticket was raised by the user (email or phone) or, with company access, belongs to their linked customer. Unauthorized attempts are logged via `frappe.log_error`.

## Installation

After installing, complete the setup in Frappe Desk:

1. **Ampower Bot Configuration** - set:
   - **API URL** - base URL of the remote Helpdesk (e.g. `https://helpdesk.example.com`)
   - **API Token** - `api_key:api_secret` for the Helpdesk REST API
3. **WhatsApp Keyword Reply** - the four routing rules ship as fixtures (`enabled = 1`). Confirm they loaded and are pointed at the correct WhatsApp account.

Onboarding registrations land as `Pending`; an admin approves them by setting `consent_status = Opted In` and `is_active = 1` on the **WhatsApp Opt-in** record.

## Dependencies

- [`frappe`](https://github.com/frappe/frappe) v15 - installed and managed by bench.
- `frappe_whatsapp_chatbot` - keyword matcher / message processor that dispatches to this app's handler scripts.
- A reachable **Frappe Helpdesk** site exposing the REST API (`HD Ticket`, `HD Customer`).

Python: [`requests`](https://pypi.org/project/requests/) for the remote REST calls.

## License

[MIT](license.txt) - © Ambibuzz Technologies LLP.
