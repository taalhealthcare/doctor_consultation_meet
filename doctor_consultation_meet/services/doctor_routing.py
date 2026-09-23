"""Assign the doctor from the speciality the patient picked.

WHY before_insert:
The Meet job runs on after_insert. Doing this first means the Google Meet
invite, all three emails and both WhatsApps already carry the right doctor.
Nothing downstream needs to change.

WHY practitioner IDs and not names:
Names differ between the booking form and the Healthcare Practitioner records
("Dr. Pujari" vs "Dr. Sanjay Pujari"). The ID never changes. The name, mobile
and email are read live from the record, so correcting a doctor's number in
Healthcare Practitioner is enough. No code edit, no deploy.
"""

import re

import frappe
from frappe import _

# ----------------------------------------------------------------------
# Speciality to Healthcare Practitioner.
#
# Keys cover BOTH the website wording and the DocType Select options, because
# the two do not match today. Matching ignores case, spaces and punctuation,
# so "PrEP & PEP Support", "PrEP/PEP" and "prep pep" all land on the same row.
#
# To change a doctor, change the HLC-PRAC id here. That is the only edit.
# ----------------------------------------------------------------------
SPECIALITY_DOCTOR = {
	# Mental Health
	"mentalhealth": "HLC-PRAC-2026-00004",  # Dr. Rahul Bagale

	# HIV Care (ART)
	"hivcareart": "HLC-PRAC-2026-00003",  # Dr. Sanjay Pujari
	"hivtreatment": "HLC-PRAC-2026-00003",
	"hivcare": "HLC-PRAC-2026-00003",
	"art": "HLC-PRAC-2026-00003",

	# PrEP & PEP Support
	"preppepsupport": "HLC-PRAC-2024-00005",  # Dr. Smita Mahindrakar
	"preppep": "HLC-PRAC-2024-00005",

	# STI & STD Care
	"stistdcare": "HLC-PRAC-2026-00006",  # Dr. Kanchan Pawar
	"stistd": "HLC-PRAC-2026-00006",

	# Men's Health (Sexual & Reproductive)
	"menshealthsexualreproductive": "HLC-PRAC-2026-00002",  # Dr. Apparao Kale
	"menshealth": "HLC-PRAC-2026-00002",

	# Women's Health (Sexual & Reproductive Gynaecology)
	"womenshealthsexualreproductivegynaecology": "HLC-PRAC-2026-00005",  # Dr. Manisha Gujrathi
	"womenshealthsexualreproductive": "HLC-PRAC-2026-00005",
	"womenshealth": "HLC-PRAC-2026-00005",
	"womanshealth": "HLC-PRAC-2026-00005",
}

# Used when the speciality is blank or has no row above, so behaviour for
# Lab testing, Sexual Wellness, LGBTQ Health and Global Services is unchanged.
DEFAULT_DOCTOR = "HLC-PRAC-2024-00005"  # Dr. Smita Mahindrakar

# Practitioner fieldnames tried in order, first non-empty wins.
EMAIL_FIELDS = ("custom_email", "email_id")
MOBILE_FIELDS = ("mobile_phone", "residence_phone")


def normalise(value):
	"""Lowercase and drop everything that is not a letter or a digit."""
	return re.sub(r"[^a-z0-9]", "", (value or "").lower())


def get_practitioner_for_speciality(speciality):
	"""Return the practitioner id for this speciality, or the default."""
	return SPECIALITY_DOCTOR.get(normalise(speciality)) or DEFAULT_DOCTOR


def first_value(row, fieldnames):
	for fieldname in fieldnames:
		value = row.get(fieldname)
		if value:
			return value
	return None


def sanitize_mobile(number):
	"""Store the doctor's number the way the WhatsApp step expects it."""
	digits = "".join(ch for ch in str(number or "") if ch.isdigit())
	if len(digits) == 11 and digits.startswith("0"):
		digits = digits[1:]
	if len(digits) == 10:
		digits = "91" + digits
	return digits


def assign_doctor(doc, method=None):
	"""before_insert on Doctor Consultation.

	Never raises. A booking must always be saved, even if the practitioner
	record is missing, in which case the DocType defaults stay as they are.
	"""
	try:
		# A telecaller booking already carries its own doctor. Leave it alone.
		if doc.get("consultation_lead_ref") or doc.get("booking_source") == "Telecaller":
			return

		practitioner_id = get_practitioner_for_speciality(doc.get("book_specialist"))

		row = frappe.db.get_value(
			"Healthcare Practitioner",
			practitioner_id,
			["name", "practitioner_name", "custom_email", "email_id", "mobile_phone", "residence_phone", "status"],
			as_dict=True,
		)

		if not row:
			frappe.log_error(
				title="Doctor routing: practitioner not found",
				message=f"Speciality: {doc.get('book_specialist')}\nLooked for: {practitioner_id}",
			)
			return

		if row.get("status") and row.get("status") != "Active":
			frappe.log_error(
				title="Doctor routing: practitioner is not Active",
				message=f"Speciality: {doc.get('book_specialist')}\nPractitioner: {practitioner_id}",
			)

		email = first_value(row, EMAIL_FIELDS)
		mobile = sanitize_mobile(first_value(row, MOBILE_FIELDS))

		doc.doctor_name = row.get("practitioner_name") or doc.doctor_name
		if email:
			doc.doctor_email = email
		if mobile:
			doc.doctor_mobile = mobile

		# Origin marker, only if the custom field exists on the DocType.
		if frappe.get_meta("Doctor Consultation").has_field("assigned_practitioner"):
			doc.assigned_practitioner = row.get("name")

	except Exception:
		frappe.log_error(
			title="Doctor routing failed",
			message=frappe.get_traceback(),
		)


@frappe.whitelist()
def preview_routing():
	"""Check the mapping from the UI without creating a booking.

	Run from System Console:
	    from doctor_consultation_meet.services.doctor_routing import preview_routing
	    print(preview_routing())
	"""
	specialities = [
		"Mental Health",
		"HIV Care (ART)",
		"PrEP & PEP Support",
		"STI & STD Care",
		"Men's Health (Sexual & Reproductive)",
		"Women's Health (Sexual & Reproductive Gynaecology)",
		"HIV Treatment",
		"STI/STD",
		"Men's Health",
		"Woman's Health",
		"ART",
		"PrEP/PEP",
		"Lab testing",
		"Sexual Wellness",
		"LGBTQ Health",
		"Global Services",
	]

	lines = []
	for speciality in specialities:
		practitioner_id = get_practitioner_for_speciality(speciality)
		row = frappe.db.get_value(
			"Healthcare Practitioner",
			practitioner_id,
			["practitioner_name", "custom_email", "email_id", "mobile_phone", "residence_phone"],
			as_dict=True,
		) or {}
		mapped = "mapped" if normalise(speciality) in SPECIALITY_DOCTOR else "default"
		lines.append(
			f"{speciality} -> {row.get('practitioner_name') or practitioner_id} "
			f"| {first_value(row, EMAIL_FIELDS)} "
			f"| {sanitize_mobile(first_value(row, MOBILE_FIELDS))} ({mapped})"
		)

	return "\n".join(lines)


# ----------------------------------------------------------------------
# Used by the Client Script and by the Reassign Doctor button
# ----------------------------------------------------------------------
@frappe.whitelist()
def get_doctor_for_speciality(speciality):
	"""Return the doctor this speciality points at, for the form to display."""
	practitioner_id = get_practitioner_for_speciality(speciality)

	row = frappe.db.get_value(
		"Healthcare Practitioner",
		practitioner_id,
		["practitioner_name", "custom_email", "email_id", "mobile_phone", "residence_phone"],
		as_dict=True,
	)
	if not row:
		return None

	return {
		"practitioner": practitioner_id,
		"doctor_name": row.get("practitioner_name") or "",
		"doctor_email": first_value(row, EMAIL_FIELDS) or "",
		"doctor_mobile": sanitize_mobile(first_value(row, MOBILE_FIELDS)) or "",
	}


@frappe.whitelist()
def reassign_doctor(consultation_name):
	"""Move a saved booking to the doctor its speciality now points at.

	Deliberately manual. The Meet link and the emails already name the old
	doctor, so this tells the new doctor and the patient, rather than changing
	the fields quietly and leaving everyone with different details.
	"""
	from doctor_consultation_meet.services.notifications import send_doctor_email_notification
	from doctor_consultation_meet.services.whatsapp_meta import safe_send_doctor_whatsapp

	doc = frappe.get_doc("Doctor Consultation", consultation_name)
	doc.check_permission("write")

	target = get_doctor_for_speciality(doc.book_specialist)
	if not target:
		frappe.throw(_("No doctor found for this speciality."))

	if target["doctor_name"] == doc.doctor_name:
		return _("Already assigned to {0}.").format(doc.doctor_name)

	previous = doc.doctor_name

	frappe.db.set_value(
		"Doctor Consultation",
		doc.name,
		{
			"doctor_name": target["doctor_name"],
			"doctor_email": target["doctor_email"],
			"doctor_mobile": target["doctor_mobile"],
		},
		update_modified=True,
	)
	frappe.db.commit()

	doc.reload()

	if doc.g_meet:
		send_doctor_email_notification(doc, doc.g_meet)
		safe_send_doctor_whatsapp(doc, doc.g_meet)
		notify_patient_of_change(doc, previous)

	frappe.db.commit()

	return _("Moved from {0} to {1}. The new doctor and the patient have been told.").format(
		previous, target["doctor_name"]
	)


def notify_patient_of_change(doc, previous_doctor):
	"""Send the patient the usual confirmation, with a line about the change.

	Email only. A WhatsApp would need its own approved Meta template.
	"""
	from doctor_consultation_meet.services.notifications import build_patient_notification_message

	if not doc.email_to:
		return

	try:
		subject, message = build_patient_notification_message(doc, doc.g_meet)

		note = (
			'<div style="margin:0 0 18px 0;padding:14px 18px;background-color:#FAF6EF;'
			'border-left:3px solid #BD9148;font-family:Arial,Helvetica,sans-serif;'
			'font-size:14px;line-height:21px;color:#2B2B2B;">'
			+ frappe.utils.escape_html(
				"Your consultation is now with {0}, in place of {1}. "
				"The date, the time and the meeting link stay the same.".format(
					doc.doctor_name or "", previous_doctor or ""
				)
			)
			+ "</div>"
		)

		marker = '<td align="center" style="padding:28px 12px;">'
		if marker in message:
			message = message.replace(marker, marker + note, 1)
		else:
			message = note + message

		frappe.sendmail(
			recipients=[doc.email_to],
			subject=_("Update: your consultation is now with {0}").format(doc.doctor_name),
			message=message,
			now=True,
		)

	except Exception:
		frappe.log_error(
			title="Reassign: patient email failed",
			message=frappe.get_traceback(),
		)