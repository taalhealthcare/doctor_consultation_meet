import requests
import frappe

from doctor_consultation_meet.services.utils import get_settings, log_error


GRAPH_API_VERSION = "v22.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"


class WhatsAppIntegrationError(Exception):
    pass


def sanitize_mobile_number(number):
    """
    Meta expects the recipient number in international format digits only.
    Example for India: 918604449446
    """
    if not number:
        return ""

    cleaned = "".join(ch for ch in str(number) if ch.isdigit())

    # Simple India fallback:
    # If user saved 10 digits like 8604449446, convert to 918604449446
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

    template_name = getattr(settings, "whatsapp_template_name", None)
    if not template_name:
        raise WhatsAppIntegrationError("WhatsApp template name is missing.")

    template_language = getattr(settings, "whatsapp_template_language", None) or "en_US"

    return {
        "phone_number_id": phone_number_id,
        "access_token": access_token,
        "template_name": template_name,
        "template_language": template_language,
    }


def send_whatsapp_template_message(consultation, meet_link):
    """
    Send WhatsApp template message using Meta Cloud API.
    """
    config = get_whatsapp_config()

    to_number = sanitize_mobile_number(consultation.mobile_number)
    if not to_number:
        raise WhatsAppIntegrationError("Doctor Consultation mobile_number is missing or invalid.")

    url = f"{GRAPH_API_BASE}/{config['phone_number_id']}/messages"

    headers = {
        "Authorization": f"Bearer {config['access_token']}",
        "Content-Type": "application/json",
    }

    patient_name = consultation.patient_name or "Patient"
    appointment_date = str(consultation.appointment_date or "")
    appointment_time = consultation.time or ""
    specialist = consultation.book_specialist or "Doctor Consultation"

    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "template",
        "template": {
            "name": config["template_name"],
            "language": {
                "code": config["template_language"]
            }
        }
    }

    # hello_world has no body variables
    # Custom templates can receive dynamic variables
    if config["template_name"] != "hello_world":
        payload["template"]["components"] = [
            {
                "type": "body",
                "parameters": [
                    {"type": "text", "text": patient_name},
                    {"type": "text", "text": appointment_date},
                    {"type": "text", "text": appointment_time},
                    {"type": "text", "text": specialist},
                    {"type": "text", "text": meet_link},
                ]
            }
        ]

    response = requests.post(url, headers=headers, json=payload, timeout=30)

    if response.status_code not in (200, 201):
        raise WhatsAppIntegrationError(
            f"WhatsApp send failed. HTTP {response.status_code}. Response: {response.text}"
        )

    return response.json()


def safe_send_whatsapp_template_message(consultation, meet_link):
    """
    Never break Meet creation if WhatsApp sending fails.
    """
    try:
        return send_whatsapp_template_message(consultation, meet_link)
    except Exception:
        log_error(
            title="Doctor Consultation WhatsApp notification failed",
            message=frappe.get_traceback(),
            consultation_name=consultation.name,
        )
        return None