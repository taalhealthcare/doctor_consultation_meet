app_name = "doctor_consultation_meet"
app_title = "Doctor Consultation Meet"
app_publisher = "Taalplus CHC Private Limited"
app_description = "Google Meet automation for Doctor Consultation"
app_email = "contact@taalhealthcare.com"
app_license = "MIT"

doc_events = {
    "Doctor Consultation": {
        "after_insert": "doctor_consultation_meet.services.consultation_meet.on_doctor_consultation_after_insert"
    }
}
