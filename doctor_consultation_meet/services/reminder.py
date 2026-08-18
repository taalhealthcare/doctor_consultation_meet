# Copyright (c) 2026, TAAL+ Healthcare and contributors
"""Thirty-minute appointment reminders.

TWO SOURCES, ONE JOB:

  1. Doctor Consultation (Online)
       Covers both direct bookings and telecaller bookings, because a
       telecaller Online booking creates a Doctor Consultation record.
       Message carries the Google Meet link.

  2. Consultation Lead (In-Clinic only)
       No Doctor Consultation exists for these, so they are reminded here.
       Message carries the clinic address.

The booking confirmation is NOT sent from this file. That is handled by
services/whatsapp_meta.py for Online, and by the Consultation Lead itself for
In-Clinic. This file only ever sends reminders.

LATE-BOOKING RULE: if a booking is made when the 30-minute window has already
opened (e.g. a slot 20 minutes away), no reminder is sent. The patient just
received a confirmation; a reminder seconds later would be noise.
"""

import frappe
from frappe import _
from frappe.utils import add_to_date, get_datetime, now_datetime, nowdate

from doctor_consultation_meet.doctor_consultation_meet.doctype.consultation_lead.consultation_lead_notification import (
	DC_FIELD_CANDIDATES,
	get_doctor_name,
	resolve_field,
	send_template,
)

# ----------------------------------------------------------------------
# Tuning. Change this one number, nothing else.
#
# The cron interval in hooks.py MUST be shorter than this, or a reminder can
# be skipped entirely. With 30 below, hooks.py runs at "*/10 * * * *".
# ----------------------------------------------------------------------
REMINDER_MINUTES = 30

# Meta template names. Must match Business Manager character-for-character.
TEMPLATE_ONLINE = "appointment_reminder_online"
TEMPLATE_CLINIC = "appointment_reminder_clinic"


# ======================================================================
# Cron entry point  -  hooks.py: "*/10 * * * *"
# ======================================================================
def send_appointment_reminders():
	now = now_datetime()

	try:
		remind_online_consultations(now)
	except Exception:
		frappe.log_error(
			title="Reminder sweep failed: Doctor Consultation",
			message=frappe.get_traceback(),
		)

	try:
		remind_clinic_leads(now)
	except Exception:
		frappe.log_error(
			title="Reminder sweep failed: In-Clinic leads", message=frappe.get_traceback()
		)

	frappe.db.commit()


# ======================================================================
# 1. Online — Doctor Consultation
# ======================================================================
def remind_online_consultations(now):
	meta = frappe.get_meta("Doctor Consultation")

	date_field = resolve_field(meta, DC_FIELD_CANDIDATES["date"])
	time_field = resolve_field(meta, DC_FIELD_CANDIDATES["time"])
	mobile_field = resolve_field(meta, DC_FIELD_CANDIDATES["mobile"])
	name_field = resolve_field(meta, DC_FIELD_CANDIDATES["patient_name"])
	doctor_field = resolve_field(meta, DC_FIELD_CANDIDATES["doctor"])

	if not (date_field and mobile_field):
		frappe.log_error(
			title="Reminder: Doctor Consultation fields not resolved",
			message=(
				"Could not find a date or mobile field on Doctor Consultation.\n"
				"Update DC_FIELD_CANDIDATES in consultation_lead_notification.py.\n"
				f"date={date_field} time={time_field} mobile={mobile_field}"
			),
		)
		return

	fields = ["name", "creation", "g_meet", date_field, mobile_field]
	for extra in (time_field, name_field, doctor_field):
		if extra and extra not in fields:
			fields.append(extra)

	filters = {date_field: (">=", nowdate())}
	if meta.has_field("reminder_sent"):
		filters["reminder_sent"] = 0

	rows = frappe.get_all(
		"Doctor Consultation", filters=filters, fields=fields, limit_page_length=0
	)

	for row in rows:
		appointment_at = combine(row.get(date_field), row.get(time_field) if time_field else None)
		if not appointment_at:
			# Unparseable time. Skip quietly rather than stopping the sweep.
			continue
		if not is_due(appointment_at, row.get("creation"), now):
			continue

		# Mark first, send second. A crash costs one reminder, never a duplicate.
		frappe.db.set_value(
			"Doctor Consultation",
			row.name,
			{"reminder_sent": 1, "reminder_sent_on": now_datetime()},
			update_modified=False,
		)
		frappe.db.commit()

		send_template(
			mobile_no=row.get(mobile_field),
			region="National",
			template_name=TEMPLATE_ONLINE,
			params=[
				row.get(name_field) if name_field else "",
				get_doctor_name(row.get(doctor_field)) if doctor_field else "",
				frappe.format(row.get(date_field), {"fieldtype": "Date"}),
				frappe.format(row.get(time_field), {"fieldtype": "Time"}) if time_field else "",
				row.get("g_meet") or _("link shared by email"),
			],
		)


# ======================================================================
# 2. In-Clinic — Consultation Lead
# ======================================================================
def remind_clinic_leads(now):
	rows = frappe.get_all(
		"Consultation Lead",
		filters={
			"lead_status": "Appointment Booked",
			"consultation_mode": "In-Clinic",
			"reminder_sent": 0,
			"appointment_date": (">=", nowdate()),
		},
		fields=[
			"name",
			"creation",
			"patient_name",
			"mobile_no",
			"region",
			"appointment_date",
			"appointment_time",
			"doctor_assigned",
			"clinic_location",
		],
		limit_page_length=0,
	)

	for row in rows:
		appointment_at = combine(row.appointment_date, row.appointment_time)
		if not is_due(appointment_at, row.creation, now):
			continue

		frappe.db.set_value(
			"Consultation Lead",
			row.name,
			{"reminder_sent": 1, "reminder_sent_on": now_datetime()},
			update_modified=False,
		)
		frappe.db.commit()

		send_template(
			mobile_no=row.mobile_no,
			region=row.region,
			template_name=TEMPLATE_CLINIC,
			params=[
				row.patient_name,
				get_doctor_name(row.doctor_assigned),
				frappe.format(row.appointment_date, {"fieldtype": "Date"}),
				frappe.format(row.appointment_time, {"fieldtype": "Time"}),
				(row.clinic_location or "").replace("\n", ", "),
			],
		)


# ======================================================================
# Shared timing logic
# ======================================================================
def combine(appointment_date, appointment_time):
	"""Build a datetime, tolerating every time format in this codebase.

	Doctor Consultation may store time as a range string like
	"01:30 PM - 02:00 PM". Consultation Lead uses a proper Time field. Both
	must work, and a bad value must never take the whole cron down.
	"""
	if not appointment_date:
		return None

	start = parse_start_time(appointment_time)
	if not start:
		return None

	try:
		return get_datetime(f"{appointment_date} {start}")
	except Exception:
		return None


def parse_start_time(value):
	"""Return an HH:MM:SS string, or None if it cannot be understood."""
	if value in (None, ""):
		return None

	# Native Time fields arrive as timedelta or time objects.
	if hasattr(value, "seconds") and not isinstance(value, str):
		total = int(value.seconds)
		return f"{total // 3600:02d}:{(total % 3600) // 60:02d}:{total % 60:02d}"
	if hasattr(value, "hour") and not isinstance(value, str):
		return f"{value.hour:02d}:{value.minute:02d}:{value.second:02d}"

	text = str(value).strip()

	# "01:30 PM - 02:00 PM" -> take the start of the range.
	for separator in (" - ", " to ", "-", "\u2013"):
		if separator in text:
			text = text.split(separator)[0].strip()
			break

	# Already 24-hour.
	try:
		return str(get_datetime(f"2000-01-01 {text}").time())
	except Exception:
		pass

	# 12-hour with meridiem.
	from datetime import datetime as _dt

	for fmt in ("%I:%M %p", "%I:%M%p", "%I.%M %p", "%H:%M", "%H:%M:%S"):
		try:
			return _dt.strptime(text.upper().replace(".", ":"), fmt).strftime("%H:%M:%S")
		except Exception:
			continue

	return None


def is_due(appointment_at, created_at, now):
	"""True only when the reminder should genuinely go out now."""
	if not appointment_at:
		return False

	# Already started or finished.
	if appointment_at <= now:
		return False

	window_opens = add_to_date(appointment_at, minutes=-REMINDER_MINUTES)

	# Too early.
	if now < window_opens:
		return False

	# LATE BOOKING: the record was created after the window had already opened,
	# so the confirmation message effectively was the reminder.
	if created_at and get_datetime(created_at) >= window_opens:
		return False

	return True