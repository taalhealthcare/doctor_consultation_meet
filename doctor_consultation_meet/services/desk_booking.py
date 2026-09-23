"""Manual Desk bookings: copy the Offline fields onto the real fields.

Runs on before_insert, ahead of doctor_routing.assign_doctor. After this
function has run, the record looks exactly like a website booking, so the
doctor routing, the Meet job, the three emails and both WhatsApps all work
without a single change.

Website bookings have entry_mode Online and skip this file entirely. So do the
records created before entry_mode existed, where the value is empty.

FIELDS THIS READS, all created in the Doctor Consultation DocType:
    entry_mode                  Select   Online / Offline
    offline_speciality          Select   website wording
    offline_appointment_date    Date
    offline_appointment_time    Select   "04:00 PM - 04:30 PM" style
    created_by_user             Link     User, read only
"""

import frappe
from frappe import _
from frappe.utils import getdate

# Website wording on the left, the existing book_specialist Select option on
# the right. book_specialist rejects any value not in its own option list, so
# this mapping is what keeps the save from failing.
SPECIALITY_TO_BOOK_SPECIALIST = {
	"Mental Health": "Mental Health",
	"HIV Care (ART)": "HIV Treatment",
	"PrEP & PEP Support": "PrEP/PEP",
	"STI & STD Care": "STI/STD",
	"Men's Health (Sexual & Reproductive)": "Men's Health",
	"Women's Health (Sexual & Reproductive Gynaecology)": "Woman's Health",
}


def apply_desk_booking(doc, method=None):
	"""before_insert on Doctor Consultation. First of the two handlers."""

	# Empty or Online means a website booking, handled exactly as before.
	if (doc.get("entry_mode") or "Online") != "Offline":
		return

	missing = []
	if not doc.get("offline_speciality"):
		missing.append(_("Speciality"))
	if not doc.get("offline_appointment_date"):
		missing.append(_("Appointment Date"))
	if not doc.get("offline_appointment_time"):
		missing.append(_("Appointment Time"))

	if missing:
		frappe.throw(
			_("Please fill these Offline Booking fields: {0}").format(", ".join(missing)),
			title=_("Offline Booking Incomplete"),
		)

	speciality = doc.offline_speciality
	mapped = SPECIALITY_TO_BOOK_SPECIALIST.get(speciality)

	if not mapped:
		frappe.throw(
			_("No mapping for the speciality {0}. Please tell the admin team.").format(speciality),
			title=_("Speciality Not Mapped"),
		)

	doc.book_specialist = mapped

	# appointment_date and time are Data fields on this DocType, so write them
	# in the same shape the website already produces. The time option uses a
	# plain hyphen, which is what build_event_payload() splits on.
	doc.appointment_date = str(getdate(doc.offline_appointment_date))
	doc.time = doc.offline_appointment_time

	# The consultation itself is still a Google Meet call, so the Meet job runs.
	if not doc.get("mode_of_consultation"):
		doc.mode_of_consultation = "Online"

	doc.created_by_user = frappe.session.user