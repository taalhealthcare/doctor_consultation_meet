import frappe

from doctor_consultation_meet.services.utils import log_error

# ----------------------------------------------------------------------
# Brand tokens. Change a colour or a contact detail here only.
# ----------------------------------------------------------------------
GOLD = "#BD9148"
LIME = "#ACC323"
INK = "#2B2B2B"
MUTED = "#7A7266"
SAND_PAGE = "#F4EFE6"
SAND_PANEL = "#FAF6EF"
LINE = "#E6DCCB"

BRAND_NAME = "TAAL+ Complete Health Care"
BRAND_SHORT = "Taalplus CHC Private Limited"
SUPPORT_PHONE = "+91 97669 20606"
WEBSITE = "www.taalhealthcare.com"
WEBSITE_URL = "https://www.taalhealthcare.com"

ADMIN_EMAIL = "taalhealthcare5@gmail.com"

SERIF = "Georgia, 'Times New Roman', Times, serif"
SANS = "Arial, 'Helvetica Neue', Helvetica, sans-serif"


# ----------------------------------------------------------------------
# Shell
# ----------------------------------------------------------------------
def esc(value):
	"""Keep a stray < or & in a patient name from breaking the layout."""
	return frappe.utils.escape_html(value or "")


def detail_row(label, value, last=False):
	border = "" if last else f"border-bottom:1px solid {LINE};"
	return f"""
					<tr>
						<td style="padding:12px 0;{border}font-family:{SANS};font-size:13px;color:{MUTED};width:38%;" valign="top">{esc(label)}</td>
						<td style="padding:12px 0;{border}font-family:{SANS};font-size:15px;color:{INK};font-weight:bold;" valign="top">{esc(value) or "-"}</td>
					</tr>"""


def button(url, text):
	if not url:
		return ""
	return f"""
			<tr>
				<td align="center" style="padding:4px 32px 8px 32px;">
					<table role="presentation" cellpadding="0" cellspacing="0" border="0">
						<tr>
							<td align="center" bgcolor="{GOLD}" style="border-radius:4px;">
								<a href="{url}" target="_blank" style="display:inline-block;padding:15px 34px;font-family:{SANS};font-size:15px;font-weight:bold;color:#FFFFFF;text-decoration:none;letter-spacing:0.3px;">{text}</a>
							</td>
						</tr>
					</table>
				</td>
			</tr>
			<tr>
				<td align="center" style="padding:0 32px 8px 32px;font-family:{SANS};font-size:12px;color:{MUTED};line-height:18px;word-break:break-all;">
					Or open this link: <a href="{url}" target="_blank" style="color:{GOLD};text-decoration:none;">{url}</a>
				</td>
			</tr>"""


def render_email(preheader, greeting, intro, date_text, time_text, rows_html, meet_link, button_text, note, show_support=True):
	support_block = ""
	if show_support:
		support_block = f"""
					<br>Need help? Call or WhatsApp us on <span style="color:{INK};">{SUPPORT_PHONE}</span>."""

	return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(BRAND_NAME)}</title>
</head>
<body style="margin:0;padding:0;background-color:{SAND_PAGE};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;">{esc(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{SAND_PAGE};">
	<tr>
		<td align="center" style="padding:28px 12px;">

		<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;background-color:#FFFFFF;border:1px solid {LINE};border-radius:6px;">

			<tr><td style="height:5px;line-height:5px;font-size:0;background-color:{GOLD};">&nbsp;</td></tr>

			<tr>
				<td style="padding:26px 32px 18px 32px;border-bottom:1px solid {LINE};">
					<div style="font-family:{SERIF};font-size:21px;color:{INK};letter-spacing:0.2px;">TAAL<span style="color:{GOLD};">+</span> <span style="font-size:15px;color:{MUTED};">Complete Health Care</span></div>
				</td>
			</tr>

			<tr>
				<td style="padding:28px 32px 6px 32px;font-family:{SANS};font-size:16px;color:{INK};">{esc(greeting)}</td>
			</tr>
			<tr>
				<td style="padding:0 32px 22px 32px;font-family:{SANS};font-size:15px;line-height:23px;color:{MUTED};">{esc(intro)}</td>
			</tr>

			<tr>
				<td style="padding:0 32px 24px 32px;">
					<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:{SAND_PANEL};border-left:3px solid {LIME};border-radius:3px;">
						<tr>
							<td style="padding:20px 22px;">
								<div style="font-family:{SANS};font-size:12px;color:{MUTED};padding-bottom:6px;">Appointment</div>
								<div style="font-family:{SERIF};font-size:24px;color:{INK};line-height:30px;">{esc(date_text)}</div>
								<div style="font-family:{SERIF};font-size:19px;color:{GOLD};line-height:26px;">{esc(time_text)}</div>
							</td>
						</tr>
					</table>
				</td>
			</tr>

			<tr>
				<td style="padding:0 32px 22px 32px;">
					<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">{rows_html}
					</table>
				</td>
			</tr>
{button(meet_link, button_text)}
			<tr>
				<td style="padding:16px 32px 30px 32px;font-family:{SANS};font-size:13px;line-height:21px;color:{MUTED};">{esc(note)}</td>
			</tr>

			<tr>
				<td style="padding:22px 32px;background-color:{SAND_PANEL};border-top:1px solid {LINE};border-radius:0 0 6px 6px;font-family:{SANS};font-size:12px;line-height:20px;color:{MUTED};">
					<span style="font-family:{SERIF};font-size:14px;color:{INK};">{esc(BRAND_SHORT)}</span><br>
					<a href="{WEBSITE_URL}" target="_blank" style="color:{GOLD};text-decoration:none;">{WEBSITE}</a>{support_block}
				</td>
			</tr>

		</table>

		<div style="font-family:{SANS};font-size:11px;color:{MUTED};padding-top:14px;">This is an automated message about your appointment.</div>

		</td>
	</tr>
</table>
</body>
</html>"""


# ----------------------------------------------------------------------
# Patient
# ----------------------------------------------------------------------
def build_patient_notification_message(consultation, meet_link):
	patient_name = consultation.patient_name or "Patient"
	specialist = consultation.book_specialist or "Doctor Consultation"

	rows = (
		detail_row("Specialist", specialist)
		+ detail_row("Doctor", consultation.doctor_name or "")
		+ detail_row("Consultation mode", consultation.mode_of_consultation or "Online", last=True)
	)

	subject = "Your online consultation is confirmed"

	message = render_email(
		preheader=f"Your consultation is confirmed for {consultation.appointment_date or ''} at {consultation.time or ''}.",
		greeting=f"Hello {patient_name},",
		intro="Your online consultation is confirmed. The details are below.",
		date_text=consultation.appointment_date or "",
		time_text=consultation.time or "",
		rows_html=rows,
		meet_link=meet_link,
		button_text="Join the consultation",
		note="Please join a few minutes before the scheduled time. Use a quiet place with a stable internet connection, and keep any earlier reports with you.",
	)

	return subject, message


# ----------------------------------------------------------------------
# Doctor
# ----------------------------------------------------------------------
def build_doctor_notification_message(consultation, meet_link):
	doctor_name = consultation.doctor_name or "Doctor"
	patient_name = consultation.patient_name or "Patient"

	rows = (
		detail_row("Patient", patient_name)
		+ detail_row("Specialist", consultation.book_specialist or "Doctor Consultation")
		+ detail_row("Contact number", consultation.mobile_number or "")
		+ detail_row("Email", consultation.email_to or "", last=True)
	)

	subject = f"New online consultation: {patient_name}"

	message = render_email(
		preheader=f"New consultation on {consultation.appointment_date or ''} at {consultation.time or ''}.",
		greeting=f"Hello {doctor_name},",
		intro="An online consultation has been scheduled with you.",
		date_text=consultation.appointment_date or "",
		time_text=consultation.time or "",
		rows_html=rows,
		meet_link=meet_link,
		button_text="Join the consultation",
		note="Please join a few minutes before the scheduled time.",
		show_support=False,
	)

	return subject, message


# ----------------------------------------------------------------------
# Admin
# ----------------------------------------------------------------------
def build_admin_notification_message(consultation, meet_link):
	rows = (
		detail_row("Patient", consultation.patient_name or "")
		+ detail_row("Doctor", consultation.doctor_name or "")
		+ detail_row("Specialist", consultation.book_specialist or "")
		+ detail_row("Contact number", consultation.mobile_number or "")
		+ detail_row("Payment status", consultation.payment_status or "")
		+ detail_row("Booking ID", consultation.name or "", last=True)
	)

	subject = f"New consultation booked: {consultation.patient_name or 'Patient'}"

	message = render_email(
		preheader=f"New booking on {consultation.appointment_date or ''} at {consultation.time or ''}.",
		greeting="Hello Admin,",
		intro="A new online consultation has been booked.",
		date_text=consultation.appointment_date or "",
		time_text=consultation.time or "",
		rows_html=rows,
		meet_link=meet_link,
		button_text="Open the meeting",
		note="Please join at least 5 minutes before the scheduled time. You are responsible for letting both the doctor and the patient into the meeting.",
		show_support=False,
	)

	return subject, message


# ----------------------------------------------------------------------
# Senders
# ----------------------------------------------------------------------
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


def send_admin_email_notification(consultation, meet_link):
	"""Sends the appointment notification to Admin."""

	subject, message = build_admin_notification_message(consultation, meet_link)

	try:
		frappe.sendmail(
			recipients=[ADMIN_EMAIL],
			subject=subject,
			message=message,
			now=True,
		)
	except Exception:
		log_error(
			title="Admin email notification failed",
			message=frappe.get_traceback(),
			consultation_name=consultation.name,
		)