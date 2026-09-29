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

import re

import frappe
from frappe import _
from frappe.utils import add_to_date, get_datetime, getdate, now_datetime

SETTINGS_DOCTYPE = "Doctor Consultation Meet Settings"

EMAIL_TEMPLATE_CLINIC = "Consultation Confirmation - Clinic"

# All four new Meta templates were approved as English (US).
TEMPLATE_LANGUAGE = "en_US"

# ----------------------------------------------------------------------
# FIELD MAPPING — the ONE place to edit if a fieldname differs.
#
# To see the real fieldnames: Customize Form > Doctor Consultation.
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
	# --- STILL GUESSED (optional field, skipped safely if missing) ---
	"mobile": ["mobile_number"],  # CONFIRMED from services/whatsapp_meta.py
	"doctor": ["doctor_name"],  # used by services/reminder.py
	"mode": ["mode_of_consultation"],  # CONFIRMED from services/utils.py
	"notes": ["notes", "remarks", "description", "chief_complaint"],
}

# Your services/utils.py does:
#     is_online_consultation(doc) -> normalize_mode(doc.mode_of_consultation) == "online"
# so the stored value only has to normalise to "online". If mode_of_consultation is a
# Select, resolve_online_value() below picks the real option instead of guessing.
ONLINE_MODE_VALUE = "Online"

# Chief Concern (telecaller wording) -> book_specialist option on Doctor
# Consultation. book_specialist is a Select, so any concern not listed here is
# left blank and the existing emails fall back to "Doctor Consultation".
CONCERN_TO_BOOK_SPECIALIST = {
	"PEP": "PrEP/PEP",
	"PrEP": "PrEP/PEP",
	"STI / STD Concern": "STI/STD",
	"HIV Consultation": "HIV Treatment",
	"Erectile Dysfunction": "Men's Health",
	"Premature Ejaculation": "Men's Health",
}


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
		"specialist": CONCERN_TO_BOOK_SPECIALIST.get(lead.chief_concern),
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
	"""Write the time in the same shape the website uses.

	On this site appointment_date and time are Data fields, and website
	bookings store time as "04:00 PM - 04:30 PM". build_event_payload() splits
	on the hyphen, and the existing emails and WhatsApps print this text as is,
	so a telecaller booking must look exactly the same.
	"""
	if not appointment_time:
		return None

	fieldname = resolve_field(meta, DC_FIELD_CANDIDATES["time"])
	if not fieldname:
		return None

	df = meta.get_field(fieldname)
	if df and df.fieldtype == "Time":
		return appointment_time

	start = to_datetime_today(appointment_time)
	if not start:
		return str(appointment_time)

	duration = 30
	if frappe.db.exists("DocType", SETTINGS_DOCTYPE):
		duration = (
			frappe.db.get_single_value(SETTINGS_DOCTYPE, "default_event_duration_minutes") or 30
		)
	end = add_to_date(start, minutes=int(duration), as_datetime=True)
	return f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"


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
				fmt_date(lead.appointment_date),
				fmt_time(lead.appointment_time),
				address_for_whatsapp(lead.clinic_location),
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
		# The template already says "Hello Dr. {{1}}", so drop any "Dr" prefix.
		params=[
			strip_dr_prefix(get_doctor_name(lead.doctor_assigned)),
			fmt_date(lead.appointment_date),
			fmt_time(lead.appointment_time),
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
	map_line = (
		f'<p><a href="{c["clinic_map_link"]}">Open location in Google Maps</a></p>'
		if c.get("clinic_map_link")
		else ""
	)
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
		{map_line}
		<p>Kindly arrive ten minutes early and carry any previous reports.</p>
		<p>Warm regards,<br>TAAL+ Healthcare</p>
	"""


# ======================================================================
# WhatsApp via Meta Cloud API
# ======================================================================
def send_whatsapp_template(lead, template_name, params, language=TEMPLATE_LANGUAGE):
	"""Convenience wrapper for a Consultation Lead."""
	return send_template(
		mobile_no=lead.mobile_no,
		region=lead.region,
		template_name=template_name,
		params=params,
		language=language,
	)


def send_template(mobile_no, region, template_name, params, language=TEMPLATE_LANGUAGE):
	"""Send one approved Meta template. Never raises.

	Uses the app's own send_template_message() from services/whatsapp_meta.py,
	so it reads the same credentials as the working Online flow
	(whatsapp_phone_number_id, whatsapp_access_token) and cleans the number
	the same way (a 10-digit number gets 91 in front).

	International numbers are passed as typed, so they must include the
	country code.

	Returns (ok, plain-language note for the lead).
	"""
	if not mobile_no:
		return False, _("No mobile number, so no WhatsApp was sent.")

	from doctor_consultation_meet.services.whatsapp_meta import send_template_message

	number = "".join(ch for ch in str(mobile_no) if ch.isdigit())
	if region == "International" and len(number) == 10:
		# A 10-digit foreign number without country code would wrongly get 91.
		frappe.log_error(
			title="Consultation Lead: WhatsApp send failed",
			message=f"International number without country code: {mobile_no}\nTemplate: {template_name}",
		)
		return False, _("International number needs the country code. WhatsApp not sent.")

	clean_params = [clean_param(p) for p in params]

	try:
		send_template_message(
			to_number=number,
			template_name=template_name,
			template_language=language,
			body_parameters=clean_params,
		)
		return True, _("WhatsApp sent to {0}.").format(mobile_no)

	except Exception:
		frappe.log_error(
			title="Consultation Lead: WhatsApp send failed",
			message=(
				f"Template: {template_name} ({language})\nTo: {number}\n"
				f"Params: {clean_params}\n\n{frappe.get_traceback()}"
			),
		)
		return False, _("WhatsApp could not be sent. Admin has been notified.")


def clean_param(value):
	"""Meta rejects a parameter with a newline, a tab, or 4+ spaces in a row,
	and an empty one. Make every value safe."""
	text = re.sub(r"\s+", " ", str(value or "")).strip()
	return text or "-"


# ======================================================================
# Shared helpers
# ======================================================================
def get_default_clinic_address():
	if not frappe.db.exists("DocType", SETTINGS_DOCTYPE):
		return None
	return frappe.db.get_single_value(SETTINGS_DOCTYPE, "clinic_address")


def get_clinic_map_link():
	if not frappe.db.exists("DocType", SETTINGS_DOCTYPE):
		return None
	return frappe.db.get_single_value(SETTINGS_DOCTYPE, "clinic_map_link")


def address_for_whatsapp(address):
	"""One line, commas instead of line breaks, map link at the end if set."""
	parts = [p.strip().strip(",") for p in (address or "").splitlines() if p.strip()]
	text = ", ".join(parts)
	link = get_clinic_map_link()
	if link:
		text = f"{text}. Map: {link}" if text else link
	return text


def strip_dr_prefix(name):
	"""'Dr Smita Mahindrakar' or 'Dr. Sanjay Pujari' -> 'Smita Mahindrakar'."""
	return re.sub(r"^\s*dr\.?\s+", "", name or "", flags=re.IGNORECASE).strip()


def fmt_date(value):
	"""2026-09-30 -> 'September 30, 2026' (matches the template samples)."""
	if not value:
		return ""
	try:
		d = getdate(value)
		return f"{d.strftime('%B')} {d.day}, {d.year}"
	except Exception:
		return str(value)


def fmt_time(value):
	"""13:00:00 or '01:00 PM - 01:30 PM' -> '1:00 PM'."""
	start = to_datetime_today(value)
	if not start:
		return str(value or "")
	return start.strftime("%I:%M %p").lstrip("0")


def to_datetime_today(value):
	"""Any time format used in this app -> a datetime (date part unused)."""
	# Lazy import: reminder.py imports this module at load time.
	from doctor_consultation_meet.services.reminder import parse_start_time

	start = parse_start_time(value)
	if not start:
		return None
	try:
		return get_datetime(f"2000-01-01 {start}")
	except Exception:
		return None


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
		"appointment_date": fmt_date(lead.appointment_date),
		"appointment_time": fmt_time(lead.appointment_time),
		"consultation_mode": lead.consultation_mode,
		"meet_link": lead.meet_link,
		"clinic_location": lead.clinic_location,
		"clinic_map_link": get_clinic_map_link(),
		"chief_concern": lead.chief_concern,
	}