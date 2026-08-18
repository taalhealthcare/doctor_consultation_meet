# Copyright (c) 2026, TAAL+ Healthcare and contributors
"""Booking confirmations for Consultation Lead.

DIVISION OF LABOUR — this is the important bit:

  ONLINE     -> a "Doctor Consultation" record is created. Your existing
                after_insert hook takes over and does Meet + patient email +
                doctor email + admin email + WhatsApp. We do NOT duplicate any
                of that. We only read the result back onto the lead.

  IN-CLINIC  -> no Doctor Consultation, no Meet, no Google Calendar call.
                This module sends the confirmation email and WhatsApp itself,
                using the clinic address instead of a link.

That split means there is exactly one owner of every message. Nothing is sent
twice, and the proven Online path is untouched.
"""

import json

import frappe
from frappe import _
from frappe.utils import now_datetime

SETTINGS_DOCTYPE = "Doctor Consultation Meet Settings"

EMAIL_TEMPLATE_CLINIC = "Consultation Confirmation - Clinic"

# ----------------------------------------------------------------------
# FIELD MAPPING — the ONE place to edit if a fieldname differs.
#
# Run this to see the real fieldnames on your Doctor Consultation DocType:
#   bench --site erp.taalhealthcare.com console
#   >>> [f.fieldname for f in frappe.get_meta("Doctor Consultation").fields]
#
# Each entry is a list of candidates tried in order. The first one that
# actually exists on the DocType wins, so a wrong guess is skipped, never
# crashed on.
# ----------------------------------------------------------------------
DC_FIELD_CANDIDATES = {
	# --- CONFIRMED from services/whatsapp_meta.py ---
	"patient_name": ["patient_name"],
	"email_to": ["email_to"],
	"date": ["appointment_date"],
	"time": ["time"],
	"doctor_name": ["doctor_name"],
	"doctor_mobile": ["doctor_mobile"],
	"specialist": ["book_specialist"],
	# --- STILL GUESSED: confirm with the console command in the guide ---
	"mobile": ["patient_mobile", "mobile_no", "mobile", "phone", "contact_number"],
	"mode": ["mode_of_consultation"],  # CONFIRMED from services/utils.py
	"notes": ["notes", "remarks", "description", "chief_complaint"],
}

# Your services/utils.py does:
#     is_online_consultation(doc) -> normalize_mode(doc.mode_of_consultation) == "online"
# so the stored value only has to normalise to "online". If mode_of_consultation is a
# Select, resolve_online_value() below picks the real option instead of guessing.
ONLINE_MODE_VALUE = "Online"


# ----------------------------------------------------------------------
# DOCTOR NOTIFICATION FOR IN-CLINIC BOOKINGS
#
# Online bookings already notify the doctor: they create a Doctor Consultation
# and your safe_send_doctor_whatsapp() fires. In-Clinic bookings do not, so
# this is the only gap.
#
# TWO WAYS TO FILL IT - pick one by editing the constant below.
#
# CONFIRMED: your existing doctor template takes 6 parameters and the 6th IS
# the Google Meet link, so it CANNOT be reused for an In-Clinic booking.
# A new 5-parameter template is required. See WHATSAPP_META_TEMPLATES.md.
#
# Set to None to switch doctor notification off entirely.
# ----------------------------------------------------------------------
DOCTOR_TEMPLATE_CLINIC = "appointment_notify_doctor_clinic"

# Fieldnames to try when looking up the doctor's WhatsApp number.
PRACTITIONER_MOBILE_FIELDS = ("mobile_phone", "mobile_no", "phone", "office_phone")


# ======================================================================
# Entry point
# ======================================================================
def send_booking_confirmation(lead, force=False):
	"""Called once a Patient Appointment exists, and by the Resend button."""
	if lead.consultation_mode == "Online":
		dispatch_online(lead, force=force)
	else:
		dispatch_in_clinic(lead, force=force)


# ======================================================================
# ONLINE — hand off to the existing Meet pipeline
# ======================================================================
def dispatch_online(lead, force=False):
	if lead.doctor_consultation_ref and not force:
		lead.db_set(
			"notification_remarks",
			_("Handled by Doctor Consultation {0}.").format(lead.doctor_consultation_ref),
			update_modified=False,
		)
		return

	if not lead.email_id:
		lead.db_set(
			"notification_remarks",
			_("Cannot start the Online consultation without an email address."),
			update_modified=False,
		)
		return

	# Resend on an existing consultation should re-queue, not create a second one.
	if lead.doctor_consultation_ref and force:
		requeue_meet(lead)
		return

	try:
		consultation_name = create_doctor_consultation(lead)

		lead.db_set("doctor_consultation_ref", consultation_name, update_modified=False)
		lead.db_set("meet_status", "Queued", update_modified=False)
		lead.db_set(
			"notification_remarks",
			_(
				"Doctor Consultation {0} created. The Meet link, emails and WhatsApp are "
				"being generated in the background."
			).format(consultation_name),
			update_modified=False,
		)

	except Exception:
		frappe.log_error(
			title="Consultation Lead: Doctor Consultation creation failed",
			message=frappe.get_traceback(),
		)
		lead.db_set(
			"notification_remarks",
			_("Could not start the online consultation. Admin has been notified."),
			update_modified=False,
		)


def requeue_meet(lead):
	"""Reuse the retry entry point that already exists in your app."""
	from doctor_consultation_meet.services.consultation_meet import retry_generate_meet

	retry_generate_meet(lead.doctor_consultation_ref)
	lead.db_set("meet_status", "Queued", update_modified=False)
	lead.db_set(
		"notification_remarks",
		_("Meet generation re-queued for {0}.").format(lead.doctor_consultation_ref),
		update_modified=False,
	)


def create_doctor_consultation(lead):
	"""Build a Doctor Consultation from the lead, setting only fields that exist."""
	meta = frappe.get_meta("Doctor Consultation")
	doc = frappe.new_doc("Doctor Consultation")

	values = {
		"patient_name": lead.patient_name,
		"email_to": lead.email_id,
		"mobile": lead.mobile_no,
		"date": lead.appointment_date,
		"time": format_time_for_dc(meta, lead.appointment_time),
		# doctor_name is a display string on Doctor Consultation, not a Link,
		# so write the practitioner's name rather than its record ID.
		"doctor_name": get_doctor_name(lead.doctor_assigned),
		"doctor_mobile": get_practitioner_mobile(lead.doctor_assigned),
		"specialist": lead.chief_concern,
		"mode": ONLINE_MODE_VALUE,
		"notes": build_notes(lead),
	}

	for key, value in values.items():
		if value in (None, ""):
			continue
		fieldname = resolve_field(meta, DC_FIELD_CANDIDATES.get(key, []))
		if not fieldname:
			continue
		if key == "mode":
			value = resolve_online_value(meta, fieldname)
		set_if_valid(doc, meta, fieldname, value)

	# Origin markers, created as Custom Fields by lead_setup.py.
	# These make it obvious at a glance that a telecaller made this booking.
	if meta.has_field("consultation_lead_ref"):
		doc.consultation_lead_ref = lead.name
	if meta.has_field("booking_source"):
		doc.booking_source = "Telecaller"
	if meta.has_field("booked_by"):
		doc.booked_by = lead.telecaller

	doc.flags.ignore_mandatory = True
	doc.insert(ignore_permissions=True)
	return doc.name


def resolve_online_value(meta, fieldname):
	"""Return the exact value that mode_of_consultation should hold for Online.

	If the field is a Select, pick the real option whose text contains "online",
	so we never write a value Frappe would reject. Otherwise fall back to the
	plain string, which normalize_mode() lower-cases anyway.
	"""
	df = meta.get_field(fieldname)
	if df and df.fieldtype == "Select" and df.options:
		for option in df.options.split("\n"):
			if "online" in option.strip().lower():
				return option.strip()
	return ONLINE_MODE_VALUE


def set_if_valid(doc, meta, fieldname, value):
	"""Set a field, but never write a value a Select would reject.

	Frappe throws on an out-of-list Select value, and that would abort the whole
	booking. A skipped optional field is far better than a failed appointment.
	"""
	df = meta.get_field(fieldname)
	if df and df.fieldtype == "Select" and df.options:
		allowed = [o.strip() for o in df.options.split("\n")]
		if str(value).strip() not in allowed:
			return
	doc.set(fieldname, value)


def format_time_for_dc(meta, appointment_time):
	"""Match whatever format the Doctor Consultation time field expects.

	If it is a real Time field, pass the value straight through. If it is Data
	or Select, your existing records may store a range string such as
	"01:30 PM - 02:00 PM", so we write the start time in the same 12-hour shape.
	"""
	if not appointment_time:
		return None

	fieldname = resolve_field(meta, DC_FIELD_CANDIDATES["time"])
	if not fieldname:
		return None

	df = meta.get_field(fieldname)
	if df and df.fieldtype == "Time":
		return appointment_time

	return frappe.format(appointment_time, {"fieldtype": "Time"})


def resolve_field(meta, candidates):
	for fieldname in candidates:
		if meta.has_field(fieldname):
			return fieldname
	return None


def build_notes(lead):
	parts = [_("Booked from Consultation Lead {0}").format(lead.name)]
	if lead.chief_concern:
		parts.insert(0, _("Concern: {0}").format(lead.chief_concern))
	if lead.remarks:
		parts.insert(0, lead.remarks)
	return "\n".join(parts)


def sync_from_doctor_consultation(doc, method=None):
	"""Hooked on Doctor Consultation. Pulls the Meet result back to the lead."""
	lead_name = frappe.db.get_value(
		"Consultation Lead", {"doctor_consultation_ref": doc.name}, "name"
	)
	if not lead_name:
		return

	updates = {}
	meet_link = doc.get("g_meet")
	status = doc.get("meet_generation_status")

	if meet_link:
		updates["meet_link"] = meet_link
		# The existing pipeline sends email + WhatsApp in the same job as the link.
		updates["email_sent"] = 1
		updates["email_sent_on"] = now_datetime()
		updates["whatsapp_sent"] = 1
		updates["whatsapp_sent_on"] = now_datetime()
		updates["notification_remarks"] = _("Meet link created. Email and WhatsApp sent.")

	if status:
		updates["meet_status"] = status
		if status == "Failed":
			updates["notification_remarks"] = _(
				"Meet link could not be created. Press Resend Confirmation or contact admin."
			)

	if updates:
		frappe.db.set_value("Consultation Lead", lead_name, updates, update_modified=False)


# ======================================================================
# IN-CLINIC — owned entirely here
# ======================================================================
def dispatch_in_clinic(lead, force=False):
	remarks = []

	if not lead.clinic_location:
		address = get_default_clinic_address()
		if address:
			lead.db_set("clinic_location", address, update_modified=False)
			lead.clinic_location = address

	if not lead.email_sent or force:
		ok, note = send_clinic_email(lead)
		if ok:
			lead.db_set("email_sent", 1, update_modified=False)
			lead.db_set("email_sent_on", now_datetime(), update_modified=False)
		remarks.append(note)

	if not lead.whatsapp_sent or force:
		ok, note = send_whatsapp_template(
			lead,
			template_name="appointment_confirm_clinic",
			params=[
				lead.patient_name,
				get_doctor_name(lead.doctor_assigned),
				frappe.format(lead.appointment_date, {"fieldtype": "Date"}),
				frappe.format(lead.appointment_time, {"fieldtype": "Time"}),
				(lead.clinic_location or "").replace("\n", ", "),
			],
		)
		if ok:
			lead.db_set("whatsapp_sent", 1, update_modified=False)
			lead.db_set("whatsapp_sent_on", now_datetime(), update_modified=False)
		remarks.append(note)

	if (not lead.doctor_notified or force) and DOCTOR_TEMPLATE_CLINIC:
		ok, note = notify_doctor_for_clinic(lead)
		if ok:
			lead.db_set("doctor_notified", 1, update_modified=False)
			lead.db_set("doctor_notified_on", now_datetime(), update_modified=False)
		remarks.append(note)

	lead.db_set("notification_remarks", "\n".join(filter(None, remarks)), update_modified=False)


def notify_doctor_for_clinic(lead):
	"""Tell the doctor an In-Clinic patient has been booked with them.

	Deliberately fires at booking time, not 30 minutes before, to match what
	your Online pipeline already does for doctors.
	"""
	if not lead.doctor_assigned:
		return False, _("No doctor assigned, so the doctor was not notified.")

	mobile = get_practitioner_mobile(lead.doctor_assigned)
	if not mobile:
		return False, _("No mobile number on the doctor's record.")

	return send_template(
		mobile_no=mobile,
		region="National",
		template_name=DOCTOR_TEMPLATE_CLINIC,
		# Parameter order deliberately mirrors your existing doctor template
		# (doctor, date, time, patient, specialist) so the doctor sees a
		# familiar layout. Only the meet link is dropped.
		params=[
			get_doctor_name(lead.doctor_assigned),
			frappe.format(lead.appointment_date, {"fieldtype": "Date"}),
			frappe.format(lead.appointment_time, {"fieldtype": "Time"}),
			lead.patient_name,
			lead.chief_concern or _("General Consultation"),
		],
	)


def get_practitioner_mobile(practitioner):
	meta = frappe.get_meta("Healthcare Practitioner")
	for fieldname in PRACTITIONER_MOBILE_FIELDS:
		if not meta.has_field(fieldname):
			continue
		value = frappe.db.get_value("Healthcare Practitioner", practitioner, fieldname)
		if value:
			return value

	# Fall back to the linked User account.
	user_id = frappe.db.get_value("Healthcare Practitioner", practitioner, "user_id")
	if user_id:
		return frappe.db.get_value("User", user_id, "mobile_no")

	return None


def send_clinic_email(lead):
	if not lead.email_id:
		return False, _("No email address on the lead, so no email was sent.")

	context = build_context(lead)

	try:
		if frappe.db.exists("Email Template", EMAIL_TEMPLATE_CLINIC):
			template = frappe.get_doc("Email Template", EMAIL_TEMPLATE_CLINIC)
			subject = frappe.render_template(template.subject, context)
			message = frappe.render_template(
				template.response_html or template.response, context
			)
		else:
			subject = _("Your clinic appointment is confirmed - {0}").format(
				context["appointment_date"]
			)
			message = fallback_clinic_html(context)

		frappe.sendmail(
			recipients=[lead.email_id],
			subject=subject,
			message=message,
			reference_doctype="Consultation Lead",
			reference_name=lead.name,
			now=True,
		)
		return True, _("Email sent to {0}.").format(lead.email_id)

	except Exception:
		frappe.log_error(
			title="Consultation Lead: clinic email failed", message=frappe.get_traceback()
		)
		return False, _("Email could not be sent. Admin has been notified.")


def fallback_clinic_html(c):
	address = (c["clinic_location"] or "").replace("\n", "<br>")
	return f"""
		<p>Dear {c['patient_name']},</p>
		<p>Your <b>in-clinic consultation</b> is confirmed.</p>
		<table cellpadding="6" style="border-collapse:collapse">
			<tr><td><b>Doctor</b></td><td>{c['doctor_name']}</td></tr>
			<tr><td><b>Date</b></td><td>{c['appointment_date']}</td></tr>
			<tr><td><b>Time</b></td><td>{c['appointment_time']}</td></tr>
			<tr><td><b>Mode</b></td><td>In-Clinic (OPD)</td></tr>
		</table>
		<p><b>Please visit us at:</b><br>{address}</p>
		<p>Kindly arrive ten minutes early and carry any previous reports.</p>
		<p>Warm regards,<br>TAAL+ Healthcare</p>
	"""


# ======================================================================
# WhatsApp via Meta Cloud API
# ======================================================================
def send_whatsapp_template(lead, template_name, params, language="en"):
	"""Convenience wrapper for a Consultation Lead."""
	return send_template(
		mobile_no=lead.mobile_no,
		region=lead.region,
		template_name=template_name,
		params=params,
		language=language,
	)


def send_template(mobile_no, region, template_name, params, language="en"):
	"""Meta forbids free-form business-initiated messages, so this is template-only.

	Kept generic (no doc argument) so both Consultation Lead and Doctor
	Consultation reminders can call it.
	"""
	if not mobile_no:
		return False, _("No mobile number, so no WhatsApp was sent.")

	if not frappe.db.exists("DocType", SETTINGS_DOCTYPE):
		return False, _("WhatsApp settings not found.")

	settings = frappe.get_single(SETTINGS_DOCTYPE)

	# VERIFY these two fieldnames against your settings DocType.
	try:
		access_token = settings.get_password("access_token", raise_exception=False)
	except Exception:
		access_token = settings.get("access_token")

	phone_number_id = settings.get("phone_number_id")

	if not (access_token and phone_number_id):
		return False, _("WhatsApp credentials are not configured.")

	to_number = "91" + str(mobile_no) if region != "International" else str(mobile_no)

	payload = {
		"messaging_product": "whatsapp",
		"to": to_number,
		"type": "template",
		"template": {
			"name": template_name,
			"language": {"code": language},
			"components": [
				{
					"type": "body",
					"parameters": [{"type": "text", "text": str(p or "")} for p in params],
				}
			],
		},
	}

	try:
		import requests

		response = requests.post(
			f"https://graph.facebook.com/v20.0/{phone_number_id}/messages",
			headers={
				"Authorization": f"Bearer {access_token}",
				"Content-Type": "application/json",
			},
			data=json.dumps(payload),
			timeout=15,
		)

		if response.status_code in (200, 201):
			return True, _("WhatsApp sent to {0}.").format(mobile_no)

		frappe.log_error(
			title="Consultation Lead: WhatsApp send failed",
			message=f"{response.status_code}\n{response.text}\n{json.dumps(payload)}",
		)
		return False, _("WhatsApp could not be sent. Admin has been notified.")

	except Exception:
		frappe.log_error(
			title="Consultation Lead: WhatsApp exception", message=frappe.get_traceback()
		)
		return False, _("WhatsApp could not be sent. Admin has been notified.")


# ======================================================================
# Shared helpers
# ======================================================================
def get_default_clinic_address():
	if not frappe.db.exists("DocType", SETTINGS_DOCTYPE):
		return None
	# VERIFY: add this field to your settings DocType if it does not exist.
	return frappe.db.get_single_value(SETTINGS_DOCTYPE, "clinic_address")


def get_doctor_name(practitioner):
	if not practitioner:
		return ""
	return (
		frappe.db.get_value("Healthcare Practitioner", practitioner, "practitioner_name")
		or practitioner
	)


def build_context(lead):
	return {
		"patient_name": lead.patient_name,
		"doctor_name": get_doctor_name(lead.doctor_assigned),
		"appointment_date": frappe.format(lead.appointment_date, {"fieldtype": "Date"}),
		"appointment_time": frappe.format(lead.appointment_time, {"fieldtype": "Time"}),
		"consultation_mode": lead.consultation_mode,
		"meet_link": lead.meet_link,
		"clinic_location": lead.clinic_location,
		"chief_concern": lead.chief_concern,
	}