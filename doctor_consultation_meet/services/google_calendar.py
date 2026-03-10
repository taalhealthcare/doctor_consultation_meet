import json
import requests
import frappe
from frappe.utils import get_datetime, add_to_date

from doctor_consultation_meet.services.utils import get_settings


GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_CALENDAR_BASE = "https://www.googleapis.com/calendar/v3"


class GoogleIntegrationError(Exception):
    pass


def save_settings_value(fieldname, value):
    doc = frappe.get_single("Doctor Consultation Meet Settings")
    doc.set(fieldname, value)
    doc.save(ignore_permissions=True)
    frappe.db.commit()


def get_access_token():
    settings = get_settings()

    if not settings.enabled:
        raise GoogleIntegrationError("Integration is disabled in Doctor Consultation Meet Settings.")

    if not settings.google_client_id or not settings.get_password("google_client_secret"):
        raise GoogleIntegrationError("Google client ID / secret is missing.")

    refresh_token = settings.get_password("google_refresh_token")
    if not refresh_token:
        raise GoogleIntegrationError("Google refresh token is missing. Complete OAuth first.")

    payload = {
        "client_id": settings.google_client_id,
        "client_secret": settings.get_password("google_client_secret"),
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }

    response = requests.post(GOOGLE_TOKEN_URL, data=payload, timeout=30)

    if response.status_code != 200:
        raise GoogleIntegrationError(
            f"Token refresh failed. HTTP {response.status_code}. Response: {response.text}"
        )

    data = response.json()
    access_token = data.get("access_token")

    if not access_token:
        raise GoogleIntegrationError(f"Token refresh response missing access_token: {data}")

    save_settings_value("google_access_token", access_token)
    return access_token


def build_event_payload(consultation_doc):
    settings = get_settings()

    if not consultation_doc.appointment_date:
        raise GoogleIntegrationError("appointment_date is required.")

    if not consultation_doc.time:
        raise GoogleIntegrationError("time is required.")

    raw_time = (consultation_doc.time or "").strip()

    # Supports:
    # 01:30 PM
    # 01:30 PM - 02:00 PM
    start_time_text = raw_time.split("-")[0].strip()

    dt_string = f"{consultation_doc.appointment_date} {start_time_text}"
    start_dt = get_datetime(dt_string)

    duration_minutes = settings.default_event_duration_minutes or 30
    end_dt = add_to_date(start_dt, minutes=duration_minutes, as_datetime=True)
    timezone = settings.event_timezone or "Asia/Kolkata"

    patient_name = consultation_doc.patient_name or consultation_doc.name
    specialist = consultation_doc.book_specialist or "Doctor Consultation"

    request_id = consultation_doc.google_meet_request_id or f"consultation-{consultation_doc.name}"

    payload = {
        "summary": f"{specialist} - {patient_name}",
        "description": (
            f"Doctor Consultation: {consultation_doc.name}\n"
            f"Patient: {consultation_doc.patient_name or ''}\n"
            f"Email: {consultation_doc.email_to or ''}\n"
            f"Phone: {consultation_doc.mobile_number or ''}\n"
            f"Mode: {consultation_doc.mode_of_consultation or ''}\n"
            f"Payment Status: {consultation_doc.payment_status or ''}"
        ),
        "start": {
            "dateTime": start_dt.isoformat(),
            "timeZone": timezone
        },
        "end": {
            "dateTime": end_dt.isoformat(),
            "timeZone": timezone
        },
        "conferenceData": {
            "createRequest": {
                "requestId": request_id,
                "conferenceSolutionKey": {
                    "type": "hangoutsMeet"
                }
            }
        },
        "guestsCanModify": False,
        "guestsCanInviteOthers": False
    }

    if consultation_doc.location:
        payload["location"] = consultation_doc.location

    attendees = []
    if consultation_doc.email_to:
        attendees.append({"email": consultation_doc.email_to})

    if attendees:
        payload["attendees"] = attendees

    return payload, request_id


def create_google_calendar_event_with_meet(consultation_doc):
    settings = get_settings()
    access_token = get_access_token()
    payload, request_id = build_event_payload(consultation_doc)

    calendar_id = settings.google_calendar_id or "primary"
    url = f"{GOOGLE_CALENDAR_BASE}/calendars/{calendar_id}/events?conferenceDataVersion=1&sendUpdates=none"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=45)

    if response.status_code not in (200, 201):
        raise GoogleIntegrationError(
            f"Google Calendar event create failed. HTTP {response.status_code}. Response: {response.text}"
        )

    data = response.json()
    event_id = data.get("id")
    hangout_link = data.get("hangoutLink")

    if not hangout_link:
        entry_points = data.get("conferenceData", {}).get("entryPoints", [])
        for row in entry_points:
            if row.get("entryPointType") == "video" and row.get("uri"):
                hangout_link = row.get("uri")
                break

    if not event_id:
        raise GoogleIntegrationError(f"Google response missing event id: {data}")

    if not hangout_link:
        raise GoogleIntegrationError(f"Google response missing Meet link: {data}")

    return {
        "event_id": event_id,
        "meet_link": hangout_link,
        "request_id": request_id,
        "raw_response": data
    }