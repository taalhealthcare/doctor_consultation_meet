app_name = "doctor_consultation_meet"
app_title = "Doctor Consultation Meet"
app_publisher = "Taalplus CHC Private Limited"
app_description = "Google Meet automation for Doctor Consultation"
app_email = "contact@taalhealthcare.com"
app_license = "MIT"


# ----------------------------------------------------------------------
# Document events
# ----------------------------------------------------------------------
doc_events = {
    # Existing: generates the Google Meet for online consultations
    "Doctor Consultation": {
        # New: picks the doctor from the speciality, before the Meet job runs,
        # so the invite, emails and WhatsApps all carry the right doctor.
        "before_insert": "doctor_consultation_meet.services.doctor_routing.assign_doctor",
        "after_insert": "doctor_consultation_meet.services.consultation_meet.on_doctor_consultation_after_insert",
        # New: pushes the Meet link + send status back onto the Consultation Lead
        "on_update": "doctor_consultation_meet.doctor_consultation_meet.doctype.consultation_lead.consultation_lead_notification.sync_from_doctor_consultation",
    },
    # New: flips the lead to "Consultation Done" when the doctor closes the appointment
    "Patient Appointment": {
        "on_update": "doctor_consultation_meet.doctor_consultation_meet.doctype.consultation_lead.consultation_lead.sync_from_appointment",
    },
}


# ----------------------------------------------------------------------
# Scheduled jobs
# ----------------------------------------------------------------------
scheduler_events = {
    "cron": {
        # Appointment reminders: day-before and same-day, Online and In-Clinic.
        "*/30 * * * *": [
            "doctor_consultation_meet.services.reminder.send_appointment_reminders",
        ],
    },
}


# ----------------------------------------------------------------------
# Post-migrate setup
# Seeds masters, states, roles, permissions and email templates.
# Every write is checked first, so this is safe to run on every deploy.
# ----------------------------------------------------------------------
after_migrate = "doctor_consultation_meet.doctor_consultation_meet.setup.lead_setup.setup_consultation_lead_masters"