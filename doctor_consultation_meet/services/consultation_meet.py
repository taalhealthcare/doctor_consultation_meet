import frappe

from doctor_consultation_meet.services.google_calendar import (
    create_google_calendar_event_with_meet,
    GoogleIntegrationError,
)
from doctor_consultation_meet.services.utils import (
    get_settings,
    is_online_consultation,
    log_error,
    set_consultation_status,
)


def on_doctor_consultation_after_insert(doc, method=None):
    try:
        settings = get_settings()

        if not settings.enabled:
            return

        if not settings.auto_create_on_insert:
            return

        if not is_online_consultation(doc):
            return

        if doc.g_meet or doc.google_event_id:
            return

        frappe.db.set_value(
            "Doctor Consultation",
            doc.name,
            "meet_generation_status",
            "Queued",
            update_modified=True
        )
        frappe.db.commit()

        frappe.enqueue(
            "doctor_consultation_meet.services.consultation_meet.generate_meet_for_consultation",
            queue="default",
            timeout=300,
            consultation_name=doc.name,
            enqueue_after_commit=True,
        )

    except Exception:
        log_error(
            title="Doctor Consultation Meet enqueue failed",
            message=frappe.get_traceback(),
            consultation_name=doc.name,
        )
        frappe.db.commit()


@frappe.whitelist()
def generate_meet_for_consultation(consultation_name):
    try:
        consultation = frappe.get_doc("Doctor Consultation", consultation_name)

        if not is_online_consultation(consultation):
            return {
                "ok": True,
                "message": "Consultation is not Online. No Meet generated."
            }

        if consultation.g_meet and consultation.google_event_id:
            return {
                "ok": True,
                "message": "Meet already generated.",
                "meet_link": consultation.g_meet,
                "event_id": consultation.google_event_id,
            }

        set_consultation_status(consultation.name, "Pending")
        frappe.db.commit()

        result = create_google_calendar_event_with_meet(consultation)
        meet_link = result["meet_link"]
        event_id = result["event_id"]
        request_id = result["request_id"]

        frappe.db.set_value(
            "Doctor Consultation",
            consultation.name,
            {
                "g_meet": meet_link,
                "google_event_id": event_id,
                "google_meet_request_id": request_id,
            },
            update_modified=True,
        )

        upsert_erp_meet_record(consultation, meet_link)
        set_consultation_status(consultation.name, "Success")
        frappe.db.commit()

        return {
            "ok": True,
            "message": "Meet generated successfully.",
            "meet_link": meet_link,
            "event_id": event_id,
        }

    except GoogleIntegrationError as e:
        set_consultation_status(consultation_name, "Failed", str(e))
        log_error(
            title="Google Meet generation failed",
            message=str(e),
            consultation_name=consultation_name,
        )
        frappe.db.commit()
        return {"ok": False, "message": str(e)}

    except Exception:
        error_message = frappe.get_traceback()
        set_consultation_status(consultation_name, "Failed", error_message)
        log_error(
            title="Unexpected meet generation error",
            message=error_message,
            consultation_name=consultation_name,
        )
        frappe.db.commit()
        return {"ok": False, "message": "Unexpected error. Check Error Log."}


def upsert_erp_meet_record(consultation, meet_link):
    erp_meet_name = frappe.db.get_value(
        "ERP Meet",
        {"doctor_consultation_ref": consultation.name},
        "name"
    )

    if not erp_meet_name and consultation.email_to:
        erp_meet_name = frappe.db.get_value(
            "ERP Meet",
            {
                "email": consultation.email_to,
                "client_name": consultation.patient_name
            },
            "name"
        )

    if erp_meet_name:
        frappe.db.set_value(
            "ERP Meet",
            erp_meet_name,
            {
                "google_meet": meet_link,
                "doctor_consultation_ref": consultation.name
            },
            update_modified=True
        )
    else:
        doc = frappe.get_doc({
            "doctype": "ERP Meet",
            "client_name": consultation.patient_name,
            "email": consultation.email_to,
            "google_meet": meet_link,
            "doctor_consultation_ref": consultation.name,
        })
        doc.insert(ignore_permissions=True)

    frappe.db.commit()


@frappe.whitelist()
def retry_generate_meet(consultation_name):
    frappe.enqueue(
        "doctor_consultation_meet.services.consultation_meet.generate_meet_for_consultation",
        queue="default",
        timeout=300,
        consultation_name=consultation_name,
        enqueue_after_commit=True,
    )
    frappe.db.commit()
    return {"ok": True, "message": "Retry job queued."}