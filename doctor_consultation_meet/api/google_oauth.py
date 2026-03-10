import requests
import urllib.parse
import frappe
from frappe.utils import now_datetime, add_to_date

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


def get_settings_doc():
    return frappe.get_single("Doctor Consultation Meet Settings")


def get_redirect_uri():
    base_url = frappe.utils.get_url()
    return f"{base_url}/api/method/doctor_consultation_meet.api.google_oauth.callback"


@frappe.whitelist()
def get_google_authorize_url():
    settings = get_settings_doc()

    if not settings.google_client_id:
        frappe.throw("Google client ID is missing in Doctor Consultation Meet Settings.")

    state = frappe.generate_hash(length=32)
    settings.oauth_state = state
    settings.save(ignore_permissions=True)

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": get_redirect_uri(),
        "response_type": "code",
        "scope": "https://www.googleapis.com/auth/calendar",
        "access_type": "offline",
        "prompt": "consent",
        "state": state,
    }

    return f"{GOOGLE_AUTH_URL}?{urllib.parse.urlencode(params)}"


@frappe.whitelist(allow_guest=True)
def callback(code=None, state=None, error=None):
    settings = get_settings_doc()

    if error:
        settings.last_auth_status = f"OAuth error: {error}"
        settings.save(ignore_permissions=True)
        return "Google OAuth failed. Check settings."

    if not code:
        settings.last_auth_status = "OAuth failed: code missing"
        settings.save(ignore_permissions=True)
        return "OAuth code missing."

    if state != settings.oauth_state:
        settings.last_auth_status = "OAuth failed: invalid state"
        settings.save(ignore_permissions=True)
        return "Invalid OAuth state."

    token_payload = {
        "code": code,
        "client_id": settings.google_client_id,
        "client_secret": settings.get_password("google_client_secret"),
        "redirect_uri": get_redirect_uri(),
        "grant_type": "authorization_code",
    }

    response = requests.post(GOOGLE_TOKEN_URL, data=token_payload, timeout=30)

    if response.status_code != 200:
        settings.last_auth_status = f"Token exchange failed. HTTP {response.status_code}. {response.text}"
        settings.save(ignore_permissions=True)
        return "Token exchange failed. Check settings."

    data = response.json()

    if data.get("refresh_token"):
        settings.google_refresh_token = data["refresh_token"]

    if data.get("access_token"):
        settings.google_access_token = data["access_token"]

    if data.get("expires_in"):
        expiry = add_to_date(now_datetime(), seconds=int(data["expires_in"]), as_datetime=True)
        settings.google_token_expiry = expiry

    settings.last_auth_status = "Google OAuth completed successfully."
    settings.save(ignore_permissions=True)

    return "Google OAuth completed successfully. You can close this page."