import frappe
from frappe.utils import now_datetime

SETTINGS_DOCTYPE = "Doctor Consultation Meet Settings"


def get_settings():
    return frappe.get_single(SETTINGS_DOCTYPE)


def log_error(title, message, consultation_name=None):
    full_message = message
    if consultation_name:
        full_message = f"Consultation: {consultation_name}\n\n{message}"

    frappe.log_error(title=title, message=full_message)


def set_consultation_status(consultation_name, status, error_message=None):
    updates = {"meet_generation_status": status}

    if error_message:
        updates["meet_last_error"] = error_message
    else:
        updates["meet_last_error"] = None

    if status == "Success":
        updates["meet_generated_on"] = now_datetime()

    frappe.db.set_value("Doctor Consultation", consultation_name, updates, update_modified=True)


def normalize_mode(value):
    return (value or "").strip().lower()


def is_online_consultation(doc):
    return normalize_mode(doc.mode_of_consultation) == "online"