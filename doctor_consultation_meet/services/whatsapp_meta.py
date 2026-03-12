import requests
import frappe

from doctor_consultation_meet.services.utils import get_settings, log_error


GRAPH_API_VERSION = "v22.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class WhatsAppIntegrationError(Exception):
    pass


def sanitize_mobile_number(number):
    if not number:
        return ""

    cleaned = "".join(ch for ch in str(number) if ch.isdigit())

    if len(cleaned) == 10:
        cleaned = "91" + cleaned

    return cleaned


def get_whatsapp_config():
    settings = get_settings()

    if not getattr(settings, "whatsapp_enabled", 0):
        raise WhatsAppIntegrationError("WhatsApp is disabled in Doctor Consultation Meet Settings.")

    phone_number_id = getattr(settings, "whatsapp_phone_number_id", None)
    if not phone_number_id:
        raise WhatsAppIntegrationError("WhatsApp Phone Number ID is missing.")

    access_token = settings.get_password("whatsapp_access_token")
    if not access_token:
        raise WhatsAppIntegrationError("WhatsApp access token is missing.")

    patient_template_name = getattr(settings, "whatsapp_template_name", None)
    if not patient_template_name:
        raise WhatsAppIntegrationError("WhatsApp template name is missing.")

    patient_template_language = getattr(settings, "whatsapp_template_language", None) or "en_US"

    doctor_template_name = getattr(settings, "doctor_whatsapp_template_name", None) or "doctor_consultation_meet_details"
    doctor_template_language = getattr(settings, "doctor_whatsapp_template_language", None) or "en_US"

    return {
        "phone_number_id": phone_number_id,
        "access_token": access_token,
        "patient_template_name": patient_template_name,
        "patient_template_language": patient_template_language,
        "doctor_template_name": doctor_template_name,
        "doctor_template_language": doctor_template_language,
    }


def send_template_message(to_number, template_name, template_language, body_parameters=None):
    config = get_whatsapp_config()

    sanitized_number = sanitize_mobile_number(to_number)
    if not sanitized_number:
        raise WhatsAppIntegrationError("Recipient mobile number is missing or invalid.")

    url = f"{GRAPH_API_BASE}/{config['phone_number_id']}/messages"

    headers = {
        "Authorization": f"Bearer {config['access_token']}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": sanitized_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": template_language
            }
        }
    }

    if body_parameters:
        payload["template"]["components"] = [
            {
                "type": "body",
                "parameters": [{"type": "text", "text": str(value)} for value in body_parameters]
            }
        ]

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code not in (200, 201):
        raise WhatsAppIntegrationError(
            f"WhatsApp send failed. HTTP {response.status_code}. Response: {response.text}"
        )

    return response.json()


def safe_send_patient_whatsapp(consultation, meet_link):
    try:
        config = get_whatsapp_config()

        if config["patient_template_name"] == "hello_world":
            return send_template_message(
                to_number=consultation.mobile_number,
                template_name=config["patient_template_name"],
                template_language=config["patient_template_language"],
            )

        return send_template_message(
            to_number=consultation.mobile_number,
            template_name=config["patient_template_name"],
            template_language=config["patient_template_language"],
            body_parameters=[
                consultation.patient_name or "Patient",
                consultation.appointment_date or "",
                consultation.time or "",
                consultation.book_specialist or "Doctor Consultation",
                meet_link,
            ],
        )
    except Exception:
        log_error(
            title="Patient WhatsApp notification failed",
            message=frappe.get_traceback(),
            consultation_name=consultation.name,
        )
        return None


def safe_send_doctor_whatsapp(consultation, meet_link):
    try:
        config = get_whatsapp_config()

        return send_template_message(
            to_number=consultation.doctor_mobile,
            template_name=config["doctor_template_name"],
            template_language=config["doctor_template_language"],
            body_parameters=[
                consultation.doctor_name or "Doctor",
                consultation.appointment_date or "",
                consultation.time or "",
                consultation.patient_name or "Patient",
                consultation.book_specialist or "Doctor Consultation",
                meet_link,
            ],
        )
    except Exception:
        log_error(
            title="Doctor WhatsApp notification failed",
            message=frappe.get_traceback(),
            consultation_name=consultation.name,
        )
        return None