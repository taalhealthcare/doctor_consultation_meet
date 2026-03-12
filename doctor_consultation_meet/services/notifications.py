import frappe

from doctor_consultation_meet.services.utils import log_error


def build_patient_notification_message(consultation, meet_link):
    patient_name = consultation.patient_name or "Patient"
    appointment_date = consultation.appointment_date or ""
    appointment_time = consultation.time or ""
    specialist = consultation.book_specialist or "Doctor Consultation"

    subject = "Your Online Consultation Meeting Details"

    email_message = f"""
    <p>Hello {patient_name},</p>

    <p>Your online consultation has been scheduled on <b>{appointment_date}</b> at <b>{appointment_time}</b>.</p>

    <p><b>Specialist:</b> {specialist}</p>
    <p><b>Meeting Link:</b> <a href="{meet_link}">{meet_link}</a></p>

    <p>Please join the meeting a few minutes before the scheduled time.</p>

    <p>Regards,<br>
    Taalplus CHC Private Limited</p>
    """

    return subject, email_message


def build_doctor_notification_message(consultation, meet_link):
    doctor_name = consultation.doctor_name or "Doctor"
    patient_name = consultation.patient_name or "Patient"
    appointment_date = consultation.appointment_date or ""
    appointment_time = consultation.time or ""
    specialist = consultation.book_specialist or "Doctor Consultation"

    subject = "New Online Consultation Meeting Details"

    email_message = f"""
    <p>Hello Dr. {doctor_name},</p>

    <p>An online consultation has been scheduled on <b>{appointment_date}</b> at <b>{appointment_time}</b>.</p>

    <p><b>Patient:</b> {patient_name}</p>
    <p><b>Specialist:</b> {specialist}</p>
    <p><b>Meeting Link:</b> <a href="{meet_link}">{meet_link}</a></p>

    <p>Please join the meeting a few minutes before the scheduled time.</p>

    <p>Regards,<br>
    Taalplus CHC Private Limited</p>
    """

    return subject, email_message


def send_patient_email_notification(consultation, meet_link):
    if not consultation.email_to:
        return

    subject, message = build_patient_notification_message(consultation, meet_link)

    try:
        frappe.sendmail(
            recipients=[consultation.email_to],
            subject=subject,
            message=message,
            now=True,
        )
    except Exception:
        log_error(
            title="Patient email notification failed",
            message=frappe.get_traceback(),
            consultation_name=consultation.name,
        )


def send_doctor_email_notification(consultation, meet_link):
    if not consultation.doctor_email:
        return

    subject, message = build_doctor_notification_message(consultation, meet_link)

    try:
        frappe.sendmail(
            recipients=[consultation.doctor_email],
            subject=subject,
            message=message,
            now=True,
        )
    except Exception:
        log_error(
            title="Doctor email notification failed",
            message=frappe.get_traceback(),
            consultation_name=consultation.name,
        )