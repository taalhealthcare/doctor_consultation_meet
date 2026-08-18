# Copyright (c) 2026, TAAL+ Healthcare and contributors
"""One-time (and safely repeatable) setup for the Consultation Lead module.

Runs on every `bench migrate` via the after_migrate hook. Every function here
checks before it writes, so running it ten times changes nothing.
"""

import frappe

CHIEF_CONCERNS = [
	"PEP",
	"PrEP",
	"Erectile Dysfunction",
	"Premature Ejaculation",
	"Low Libido",
	"STI / STD Concern",
	"HIV Consultation",
	"Sexual Wellness",
	"Infertility",
	"Hair Loss",
	"Weight Management",
	"General Consultation",
	"Medicine Refill",
	"Other",
]

DROP_REASONS = [
	"Not Reachable",
	"Wrong Number",
	"Price Concern",
	"Consulting Elsewhere",
	"Just Enquiring",
	"Language Barrier",
	"Location Not Serviceable",
	"Duplicate Enquiry",
	"Not Interested",
	"Other",
]

TIME_SLOTS = [
	("10:00 AM - 12:00 PM", "10:00:00", "12:00:00"),
	("12:00 PM - 02:00 PM", "12:00:00", "14:00:00"),
	("02:00 PM - 04:00 PM", "14:00:00", "16:00:00"),
	("04:00 PM - 06:00 PM", "16:00:00", "18:00:00"),
	("06:00 PM - 08:00 PM", "18:00:00", "20:00:00"),
	("Any Time", None, None),
]

LEAD_SOURCES = [
	"Interakt",
	"WhatsApp",
	"Website",
	"Google Ads",
	"Meta Ads",
	"Instagram",
	"Referral",
	"Walk-in",
	"Incoming Call",
]

INDIAN_STATES = [
	"Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa",
	"Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala",
	"Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya", "Mizoram", "Nagaland",
	"Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
	"Uttar Pradesh", "Uttarakhand", "West Bengal",
	"Andaman and Nicobar Islands", "Chandigarh",
	"Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
	"Ladakh", "Lakshadweep", "Puducherry",
]

ROLES = ["Telecaller", "Consultation Manager"]

LEAD_DOCTYPES = [
	"Consultation Lead",
	"Chief Concern",
	"Lead Drop Reason",
	"Consultation Time Slot",
	"Consultation State",
]


def setup_consultation_lead_masters():
	"""Entry point called from hooks.after_migrate."""
	create_roles()
	create_custom_fields_on_doctor_consultation()
	seed_email_templates()
	seed_simple("Chief Concern", "concern_name", CHIEF_CONCERNS)
	seed_simple("Lead Drop Reason", "reason", DROP_REASONS)
	seed_time_slots()
	seed_states()
	seed_lead_sources()
	apply_permissions()
	frappe.db.commit()


def seed_simple(doctype, fieldname, values):
	for value in values:
		if frappe.db.exists(doctype, value):
			continue
		doc = frappe.new_doc(doctype)
		doc.set(fieldname, value)
		doc.insert(ignore_permissions=True)


def seed_time_slots():
	for name, from_time, to_time in TIME_SLOTS:
		if frappe.db.exists("Consultation Time Slot", name):
			continue
		doc = frappe.new_doc("Consultation Time Slot")
		doc.slot_name = name
		doc.from_time = from_time
		doc.to_time = to_time
		doc.insert(ignore_permissions=True)


def seed_states():
	if not frappe.db.exists("Country", "India"):
		return

	for state in INDIAN_STATES:
		if frappe.db.exists("Consultation State", state):
			continue
		doc = frappe.new_doc("Consultation State")
		doc.state_name = state
		doc.country = "India"
		doc.insert(ignore_permissions=True)


def seed_lead_sources():
	if not frappe.db.exists("DocType", "Lead Source"):
		return

	for source in LEAD_SOURCES:
		if frappe.db.exists("Lead Source", source):
			continue
		doc = frappe.new_doc("Lead Source")
		doc.source_name = source
		doc.insert(ignore_permissions=True)


def create_roles():
	for role in ROLES:
		if frappe.db.exists("Role", role):
			continue
		doc = frappe.new_doc("Role")
		doc.role_name = role
		doc.desk_access = 1
		doc.insert(ignore_permissions=True)


def apply_permissions():
	"""Telecaller can work the funnel. Manager can also delete and amend masters."""
	from frappe.permissions import add_permission, update_permission_property

	for doctype in LEAD_DOCTYPES:
		if not frappe.db.exists("DocType", doctype):
			continue

		for role in ROLES:
			add_permission(doctype, role, 0)

			for ptype in ("read", "write", "create", "report", "export", "email", "share", "print"):
				update_permission_property(doctype, role, 0, ptype, 1)

			if role == "Consultation Manager":
				update_permission_property(doctype, role, 0, "delete", 1)


# ----------------------------------------------------------------------
# Email templates — admin-editable wording, no code change needed
# ----------------------------------------------------------------------
EMAIL_TEMPLATES = [
	{
		"name": "Consultation Confirmation - Online",
		"subject": "Your online consultation is confirmed - {{ appointment_date }}",
		"response_html": """
<p>Dear {{ patient_name }},</p>
<p>Your <b>online video consultation</b> is confirmed.</p>
<table cellpadding="6" style="border-collapse:collapse">
  <tr><td><b>Doctor</b></td><td>{{ doctor_name }}</td></tr>
  <tr><td><b>Date</b></td><td>{{ appointment_date }}</td></tr>
  <tr><td><b>Time</b></td><td>{{ appointment_time }}</td></tr>
  <tr><td><b>Mode</b></td><td>Online (Google Meet)</td></tr>
</table>
{% if meet_link %}
<p><b>Join your consultation here:</b><br>
<a href="{{ meet_link }}">{{ meet_link }}</a></p>
{% else %}
<p>Your video link will be sent to you shortly before the appointment.</p>
{% endif %}
<p>Please join two minutes early from a quiet place with a stable internet connection.</p>
<p>Warm regards,<br>TAAL+ Healthcare</p>
""",
	},
	{
		"name": "Consultation Confirmation - Clinic",
		"subject": "Your clinic appointment is confirmed - {{ appointment_date }}",
		"response_html": """
<p>Dear {{ patient_name }},</p>
<p>Your <b>in-clinic consultation</b> is confirmed.</p>
<table cellpadding="6" style="border-collapse:collapse">
  <tr><td><b>Doctor</b></td><td>{{ doctor_name }}</td></tr>
  <tr><td><b>Date</b></td><td>{{ appointment_date }}</td></tr>
  <tr><td><b>Time</b></td><td>{{ appointment_time }}</td></tr>
  <tr><td><b>Mode</b></td><td>In-Clinic (OPD)</td></tr>
</table>
{% if clinic_location %}
<p><b>Please visit us at:</b><br>{{ clinic_location | replace("\n", "<br>") }}</p>
{% endif %}
<p>Kindly arrive ten minutes early and carry any previous prescriptions or reports.</p>
<p>Warm regards,<br>TAAL+ Healthcare</p>
""",
	},
]


def seed_email_templates():
	if not frappe.db.exists("DocType", "Email Template"):
		return

	for template in EMAIL_TEMPLATES:
		if frappe.db.exists("Email Template", template["name"]):
			continue

		doc = frappe.new_doc("Email Template")
		doc.name = template["name"]
		doc.subject = template["subject"]
		doc.use_html = 1
		doc.response_html = template["response_html"]
		doc.insert(ignore_permissions=True)


# ----------------------------------------------------------------------
# Back-reference on Doctor Consultation, so the Meet result finds its lead
# ----------------------------------------------------------------------
def create_custom_fields_on_doctor_consultation():
	if not frappe.db.exists("DocType", "Doctor Consultation"):
		return

	from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

	create_custom_fields(
		{
			"Doctor Consultation": [
				# --- Origin markers: make a telecaller booking obvious at a glance ---
				{
					"fieldname": "booking_source",
					"label": "Booking Source",
					"fieldtype": "Select",
					"options": "\nDirect\nTelecaller",
					"read_only": 1,
					"in_list_view": 1,
					"in_standard_filter": 1,
					"insert_after": "patient_name",
					"description": "Telecaller means this came from a Consultation Lead.",
				},
				{
					"fieldname": "consultation_lead_ref",
					"label": "Consultation Lead",
					"fieldtype": "Link",
					"options": "Consultation Lead",
					"read_only": 1,
					"no_copy": 1,
					"insert_after": "booking_source",
					"depends_on": "eval:doc.booking_source == 'Telecaller'",
					"description": "The telecaller lead this booking came from.",
				},
				{
					"fieldname": "booked_by",
					"label": "Booked By",
					"fieldtype": "Link",
					"options": "User",
					"read_only": 1,
					"no_copy": 1,
					"insert_after": "consultation_lead_ref",
					"depends_on": "eval:doc.booking_source == 'Telecaller'",
				},
				# --- Reminder tracking, used by services/reminder.py ---
				{
					"fieldname": "reminder_sent",
					"label": "30-Minute Reminder Sent",
					"fieldtype": "Check",
					"default": "0",
					"read_only": 1,
					"no_copy": 1,
					"insert_after": "booked_by",
				},
				{
					"fieldname": "reminder_sent_on",
					"label": "Reminder Sent On",
					"fieldtype": "Datetime",
					"read_only": 1,
					"no_copy": 1,
					"depends_on": "doc.reminder_sent",
					"insert_after": "reminder_sent",
				},
			]
		},
		ignore_validate=True,
	)