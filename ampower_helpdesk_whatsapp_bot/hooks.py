app_name = "ampower_helpdesk_whatsapp_bot"
app_title = "Ampower Helpdesk WhatsApp Bot"
app_publisher = "Ambibuzz Technologies LLP"
app_description = "ampower_helpdesk_whatsapp_bot"
app_email = "ithead@ambibuzz.com"
app_license = "mit"


# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "ampower_helpdesk_whatsapp_bot",
# 		"logo": "/assets/ampower_helpdesk_whatsapp_bot/logo.png",
# 		"title": "Ampower Helpdesk WhatsApp Bot",
# 		"route": "/ampower_helpdesk_whatsapp_bot",
# 		"has_permission": "ampower_helpdesk_whatsapp_bot.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/ampower_helpdesk_whatsapp_bot/css/ampower_helpdesk_whatsapp_bot.css"
# app_include_js = "/assets/ampower_helpdesk_whatsapp_bot/js/ampower_helpdesk_whatsapp_bot.js"

# include js, css files in header of web template
# web_include_css = "/assets/ampower_helpdesk_whatsapp_bot/css/ampower_helpdesk_whatsapp_bot.css"
# web_include_js = "/assets/ampower_helpdesk_whatsapp_bot/js/ampower_helpdesk_whatsapp_bot.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "ampower_helpdesk_whatsapp_bot/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "ampower_helpdesk_whatsapp_bot/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "ampower_helpdesk_whatsapp_bot.utils.jinja_methods",
# 	"filters": "ampower_helpdesk_whatsapp_bot.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "ampower_helpdesk_whatsapp_bot.install.before_install"
# after_install = "ampower_helpdesk_whatsapp_bot.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "ampower_helpdesk_whatsapp_bot.uninstall.before_uninstall"
# after_uninstall = "ampower_helpdesk_whatsapp_bot.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "ampower_helpdesk_whatsapp_bot.utils.before_app_install"
# after_app_install = "ampower_helpdesk_whatsapp_bot.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "ampower_helpdesk_whatsapp_bot.utils.before_app_uninstall"
# after_app_uninstall = "ampower_helpdesk_whatsapp_bot.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "ampower_helpdesk_whatsapp_bot.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"ampower_helpdesk_whatsapp_bot.tasks.all"
# 	],
# 	"daily": [
# 		"ampower_helpdesk_whatsapp_bot.tasks.daily"
# 	],
# 	"hourly": [
# 		"ampower_helpdesk_whatsapp_bot.tasks.hourly"
# 	],
# 	"weekly": [
# 		"ampower_helpdesk_whatsapp_bot.tasks.weekly"
# 	],
# 	"monthly": [
# 		"ampower_helpdesk_whatsapp_bot.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "ampower_helpdesk_whatsapp_bot.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "ampower_helpdesk_whatsapp_bot.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "ampower_helpdesk_whatsapp_bot.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["ampower_helpdesk_whatsapp_bot.utils.before_request"]
# after_request = ["ampower_helpdesk_whatsapp_bot.utils.after_request"]

# Job Events
# ----------
# before_job = ["ampower_helpdesk_whatsapp_bot.utils.before_job"]
# after_job = ["ampower_helpdesk_whatsapp_bot.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"ampower_helpdesk_whatsapp_bot.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []



fixtures = [
    {
        "doctype": "WhatsApp Keyword Reply",
        "filters": [["enabled", "=", 1]]
    }
]