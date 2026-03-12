import frappe

from doctor_consultation_meet.services.utils import log_error


def build_notification_message(consultation, meet_link):
    patient_name = consultation.patient_name or "Patient"
    appointment_date = consultation.appointment_date or ""
    appointment_time = consultation.time or ""
    specialist = consultation.book_specialist or "Doctor Consultation"

    subject = "Your Online Consultation Meeting Details"

    message = f"""
    <p>Hello {patient_name},</p>

    <p>Your online consultation has been scheduled on <b>{appointment_date}</b> at <b>{appointment_time}</b>.</p>

    <p><b>Specialist:</b> {specialist}</p>
    <p><b>Meeting Link:</b> <a href="{meet_link}">{meet_link}</a></p>

    <p>Please join the meeting a few minutes before the scheduled time.</p>

    <p>Regards,<br>
    Taalplus CHC Private Limited</p>
    """

    whatsapp_text = (
        f"Hello {patient_name},\n\n"
        f"Your online consultation has been scheduled on {appointment_date} at {appointment_time}.\n"
        f"Specialist: {specialist}\n"
        f"Meeting Link: {meet_link}\n\n"
        f"Please join the meeting a few minutes before the scheduled time.\n\n"
        f"Regards,\n"
        f"Taalplus CHC Private Limited"
    )

    return subject, message, whatsapp_text


def send_email_notification(consultation, meet_link):
    if not consultation.email_to:
        return

    subject, message, _ = build_notification_message(consultation, meet_link)

    try:
        frappe.sendmail(
            recipients=[consultation.email_to],
            subject=subject,
            message=message,
            now=True,
        )
    except Exception:
        log_error(
            title="Doctor Consultation email notification failed",
            message=frappe.get_traceback(),
            consultation_name=consultation.name,
        )


def send_whatsapp_notification_placeholder(consultation, meet_link):
    """
    IMPORTANT:
    Replace this placeholder with your ACTUAL WhatsApp provider integration.

    Do not invent a generic WhatsApp send API here.
    WhatsApp sending depends on your configured provider/template flow.
    """
    if not consultation.mobile_number:
        return

    _, _, whatsapp_text = build_notification_message(consultation, meet_link)

    # For now, only log what would be sent.
    # Replace this with your real provider-specific send function.
    frappe.logger().info(
        {
            "consultation": consultation.name,
            "mobile_number": consultation.mobile_number,
            "whatsapp_message_preview": whatsapp_text,
        }
    )