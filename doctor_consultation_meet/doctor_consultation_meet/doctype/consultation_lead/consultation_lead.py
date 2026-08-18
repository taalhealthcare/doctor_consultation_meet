# Copyright (c) 2026, TAAL+ Healthcare and contributors
# For license information, please see license.txt

import re

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_days, cint, getdate, nowdate

BOOKED_STATUSES = ("Appointment Booked", "Consultation Done")


class ConsultationLead(Document):
	# ------------------------------------------------------------------
	# Lifecycle
	# ------------------------------------------------------------------
	def validate(self):
		self.clean_numbers()
		self.sync_dob_and_age()
		self.set_previous_lead()

	def on_update(self):
		self.create_appointment()
		self.create_follow_up_todo()

	# ------------------------------------------------------------------
	# Data hygiene
	# ------------------------------------------------------------------
	def clean_numbers(self):
		"""Telecallers paste numbers in every possible format. Store one format."""
		self.mobile_no = normalise_mobile(self.mobile_no)
		self.alt_mobile_no = normalise_mobile(self.alt_mobile_no)

		if self.region == "National" and self.mobile_no and len(self.mobile_no) != 10:
			frappe.msgprint(
				_("Contact Number does not look like a 10 digit Indian mobile number. Please re-check."),
				indicator="orange",
				alert=True,
			)

	def sync_dob_and_age(self):
		"""DOB is the source of truth. Age is only a fallback."""
		if self.dob:
			dob = getdate(self.dob)
			today = getdate(nowdate())
			if dob > today:
				frappe.throw(_("Date of Birth cannot be in the future."))
			years = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
			self.age = years
		elif cint(self.age) and cint(self.age) > 120:
			frappe.throw(_("Please enter a valid age."))

	def set_previous_lead(self):
		"""Link, don't block. A repeat caller is useful information, not an error."""
		if not self.mobile_no:
			return

		previous = frappe.db.get_value(
			"Consultation Lead",
			{"mobile_no": self.mobile_no, "name": ("!=", self.name or "")},
			["name", "lead_status", "lead_date"],
			order_by="creation desc",
			as_dict=True,
		)

		if not previous:
			self.duplicate_of = None
			return

		self.duplicate_of = previous.name

		if self.is_new():
			frappe.msgprint(
				_("This number already called on {0}. Earlier lead {1} is at status <b>{2}</b>.").format(
					frappe.format(previous.lead_date, {"fieldtype": "Date"}),
					frappe.utils.get_link_to_form("Consultation Lead", previous.name),
					previous.lead_status,
				),
				title=_("Repeat Caller"),
				indicator="orange",
			)

	# ------------------------------------------------------------------
	# Conversion
	# ------------------------------------------------------------------
	def create_appointment(self):
		"""Create Patient + Patient Appointment once the lead is booked.

		Wrapped so that a failure here never stops a telecaller from saving
		the lead. Capturing the enquiry always wins over automation.
		"""
		if self.lead_status not in BOOKED_STATUSES:
			return
		if self.patient_appointment:
			return
		if not (self.appointment_date and self.appointment_time and self.doctor_assigned):
			return

		try:
			patient = self.get_or_create_patient()

			appointment = frappe.new_doc("Patient Appointment")
			appointment.patient = patient
			appointment.practitioner = self.doctor_assigned
			appointment.appointment_date = self.appointment_date
			appointment.appointment_time = self.appointment_time
			appointment.status = "Scheduled"
			appointment.notes = self.build_appointment_notes()

			department = frappe.db.get_value(
				"Healthcare Practitioner", self.doctor_assigned, "department"
			)
			if department:
				appointment.department = department

			appointment.flags.ignore_mandatory = True
			appointment.insert(ignore_permissions=True)

			self.db_set("patient", patient, update_modified=False)
			self.db_set("patient_appointment", appointment.name, update_modified=False)

			frappe.msgprint(
				_("Appointment {0} created.").format(
					frappe.utils.get_link_to_form("Patient Appointment", appointment.name)
				),
				indicator="green",
				alert=True,
			)

			self.send_confirmation()

		except Exception:
			frappe.log_error(
				title="Consultation Lead: appointment creation failed",
				message=frappe.get_traceback(),
			)
			frappe.msgprint(
				_(
					"The lead has been saved, but the appointment could not be created automatically. "
					"Please inform the admin team."
				),
				title=_("Appointment Not Created"),
				indicator="red",
			)

	def get_or_create_patient(self):
		"""Find the patient by mobile number, otherwise create one."""
		existing = frappe.db.get_value("Patient", {"mobile": self.mobile_no}, "name")
		if existing:
			return existing

		patient = frappe.new_doc("Patient")
		patient.first_name = self.patient_name
		patient.mobile = self.mobile_no
		patient.phone = self.alt_mobile_no

		if self.gender and frappe.db.exists("Gender", self.gender):
			patient.sex = self.gender
		if self.dob:
			patient.dob = self.dob

		patient.flags.ignore_mandatory = True
		patient.insert(ignore_permissions=True)
		return patient.name

	def send_confirmation(self):
		"""Online hands off to the existing Meet pipeline. In-Clinic is sent here."""
		from doctor_consultation_meet.doctor_consultation_meet.doctype.consultation_lead.consultation_lead_notification import (
			send_booking_confirmation,
		)

		try:
			send_booking_confirmation(self)
		except Exception:
			frappe.log_error(
				title="Consultation Lead: confirmation dispatch failed",
				message=frappe.get_traceback(),
			)

	def build_appointment_notes(self):
		parts = []
		if self.consultation_mode:
			parts.append(_("Mode: {0}").format(self.consultation_mode))
		if self.chief_concern:
			parts.append(_("Concern: {0}").format(self.chief_concern))
		if self.remarks:
			parts.append(self.remarks)
		parts.append(_("Booked from lead {0}").format(self.name))
		return "\n".join(parts)

	# ------------------------------------------------------------------
	# Follow-up
	# ------------------------------------------------------------------
	def create_follow_up_todo(self):
		"""One open ToDo per lead, so nothing is forgotten."""
		if not self.follow_up_date or self.lead_status not in ("Follow-up", "Contacted", "Interested"):
			return

		existing = frappe.db.exists(
			"ToDo",
			{
				"reference_type": "Consultation Lead",
				"reference_name": self.name,
				"status": "Open",
			},
		)
		if existing:
			frappe.db.set_value("ToDo", existing, "date", self.follow_up_date)
			return

		todo = frappe.new_doc("ToDo")
		todo.allocated_to = self.telecaller
		todo.date = self.follow_up_date
		todo.priority = "Medium"
		todo.reference_type = "Consultation Lead"
		todo.reference_name = self.name
		todo.description = _("Follow up with {0} ({1}) - {2}").format(
			self.patient_name, self.mobile_no, self.chief_concern or ""
		)
		todo.insert(ignore_permissions=True)


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def normalise_mobile(number):
	"""Strip spaces, dashes, brackets and a leading +91 / 0."""
	if not number:
		return number

	digits = re.sub(r"[^\d+]", "", str(number))
	digits = digits.lstrip("+")

	if len(digits) == 12 and digits.startswith("91"):
		digits = digits[2:]
	elif len(digits) == 11 and digits.startswith("0"):
		digits = digits[1:]

	return digits


@frappe.whitelist()
def lookup_by_mobile(mobile_no):
	"""Called from the form as soon as the telecaller types a number.

	Returns the last known details so they never re-type a repeat caller.
	"""
	mobile_no = normalise_mobile(mobile_no)
	if not mobile_no or len(mobile_no) < 8:
		return {}

	lead = frappe.db.get_value(
		"Consultation Lead",
		{"mobile_no": mobile_no},
		[
			"name",
			"patient_name",
			"gender",
			"dob",
			"age",
			"lead_status",
			"lead_date",
			"chief_concern",
			"state",
			"city",
			"region",
		],
		order_by="creation desc",
		as_dict=True,
	)

	if lead:
		lead["found_in"] = "lead"
		return lead

	patient = frappe.db.get_value(
		"Patient", {"mobile": mobile_no}, ["name", "patient_name", "sex", "dob"], as_dict=True
	)
	if patient:
		return {
			"found_in": "patient",
			"name": patient.name,
			"patient_name": patient.patient_name,
			"gender": patient.sex,
			"dob": patient.dob,
		}

	return {}


@frappe.whitelist()
def get_my_counts():
	"""Small numbers shown on the telecaller's form, so they can see their day."""
	user = frappe.session.user
	today = nowdate()

	return {
		"today": frappe.db.count(
			"Consultation Lead", {"telecaller": user, "lead_date": today}
		),
		"pending_follow_ups": frappe.db.count(
			"Consultation Lead",
			{
				"telecaller": user,
				"lead_status": "Follow-up",
				"follow_up_date": ("<=", add_days(today, 0)),
			},
		),
	}


def sync_from_appointment(doc, method=None):
	"""Hooked on Patient Appointment. Keeps the lead status honest."""
	lead_name = frappe.db.get_value("Consultation Lead", {"patient_appointment": doc.name}, "name")
	if not lead_name:
		return

	updates = {}

	if doc.status == "Closed":
		updates = {"lead_status": "Consultation Done", "consultation_done": 1}
	elif doc.status == "Cancelled":
		updates = {"lead_status": "Follow-up", "consultation_done": 0}
	elif doc.status == "No Show":
		updates = {"lead_status": "Follow-up", "consultation_done": 0}

	if updates:
		frappe.db.set_value("Consultation Lead", lead_name, updates, update_modified=False)


@frappe.whitelist()
def resend_confirmation(lead_name):
	"""Powers the Resend Confirmation button on the form."""
	from doctor_consultation_meet.doctor_consultation_meet.doctype.consultation_lead.consultation_lead_notification import (
		send_booking_confirmation,
	)

	lead = frappe.get_doc("Consultation Lead", lead_name)
	lead.check_permission("write")
	send_booking_confirmation(lead, force=True)

	return frappe.db.get_value(
		"Consultation Lead",
		lead_name,
		["email_sent", "whatsapp_sent", "notification_remarks"],
		as_dict=True,
	)