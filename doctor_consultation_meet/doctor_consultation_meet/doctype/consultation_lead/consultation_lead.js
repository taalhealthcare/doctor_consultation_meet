// Copyright (c) 2026, TAAL+ Healthcare and contributors
// For license information, please see license.txt

const STATUS_HELP = {
	"New": "Enquiry received. Call the patient and change the status.",
	"Contacted": "You spoke to them. Set a Follow-up Date if they need time.",
	"Interested": "They want a consultation. Set a Follow-up Date to close it.",
	"Appointment Booked": "Pick the Mode, fill Date, Time and Doctor, then save. Everything else is automatic.",
	"Consultation Done": "The doctor has completed this consultation.",
	"Follow-up": "A reminder task has been created for you on the Follow-up Date.",
	"Not Converted": "Please pick a Reason so the team knows what to improve.",
	"Invalid": "Wrong number, test entry or spam.",
};

const STATUS_COLOUR = {
	"New": "blue",
	"Contacted": "orange",
	"Interested": "purple",
	"Appointment Booked": "green",
	"Consultation Done": "green",
	"Follow-up": "orange",
	"Not Converted": "red",
	"Invalid": "gray",
};

frappe.ui.form.on("Consultation Lead", {
	setup(frm) {
		// Never let a telecaller pick a disabled master value.
		["chief_concern", "drop_reason", "preferred_time_slot"].forEach((field) => {
			frm.set_query(field, () => ({ filters: { disabled: 0 } }));
		});

		frm.set_query("doctor_preference", () => ({ filters: { status: "Active" } }));
		frm.set_query("doctor_assigned", () => ({ filters: { status: "Active" } }));

		frm.set_query("state", () => {
			const country = frm.doc.region === "International" ? frm.doc.country : "India";
			return country ? { filters: { country: country } } : {};
		});
	},

	onload(frm) {
		// Remember the last used Source / Campaign / Region for this browser session.
		if (frm.is_new()) {
			["lead_source", "campaign", "region", "state"].forEach((field) => {
				const remembered = frappe.consultation_lead_defaults?.[field];
				if (remembered && !frm.doc[field]) {
					frm.set_value(field, remembered);
				}
			});
		}
	},

	refresh(frm) {
		show_status_banner(frm);
		add_shortcut_buttons(frm);

		if (!frm.is_new()) {
			frm.add_custom_button(__("Call Patient"), () => {
				window.open("tel:+91" + frm.doc.mobile_no);
			});
		}

		// Only offer a resend once an appointment actually exists.
		if (frm.doc.patient_appointment) {
			frm.add_custom_button(__("Resend Confirmation"), () => {
				frappe.call({
					method:
						"doctor_consultation_meet.doctor_consultation_meet.doctype.consultation_lead.consultation_lead.resend_confirmation",
					args: { lead_name: frm.doc.name },
					freeze: true,
					freeze_message: __("Sending..."),
					callback() {
						frm.reload_doc();
						frappe.show_alert({ message: __("Sent."), indicator: "green" });
					},
				});
			});
		}

		show_notification_banner(frm);

		if (frm.doc.doctor_consultation_ref) {
			frm.add_custom_button(__("Open Doctor Consultation"), () => {
				frappe.set_route("Form", "Doctor Consultation", frm.doc.doctor_consultation_ref);
			});
		}
	},

	after_save(frm) {
		frappe.consultation_lead_defaults = {
			lead_source: frm.doc.lead_source,
			campaign: frm.doc.campaign,
			region: frm.doc.region,
			state: frm.doc.state,
		};
	},

	lead_status(frm) {
		show_status_banner(frm);

		// Nudge a sensible follow-up date instead of leaving them guessing.
		if (["Contacted", "Interested", "Follow-up"].includes(frm.doc.lead_status) && !frm.doc.follow_up_date) {
			frm.set_value("follow_up_date", frappe.datetime.add_days(frappe.datetime.get_today(), 2));
		}

		if (frm.doc.lead_status === "Appointment Booked") {
			if (!frm.doc.appointment_date && frm.doc.preferred_date) {
				frm.set_value("appointment_date", frm.doc.preferred_date);
			}
			if (!frm.doc.doctor_assigned && frm.doc.doctor_preference) {
				frm.set_value("doctor_assigned", frm.doc.doctor_preference);
			}
		}
	},

	mobile_no(frm) {
		const number = (frm.doc.mobile_no || "").replace(/\D/g, "");
		if (number.length < 8) return;

		frappe.call({
			method:
				"doctor_consultation_meet.doctor_consultation_meet.doctype.consultation_lead.consultation_lead.lookup_by_mobile",
			args: { mobile_no: frm.doc.mobile_no },
			callback(r) {
				const match = r.message;
				if (!match || !match.name) return;

				// Fill in what we already know. Never overwrite what was typed.
				["patient_name", "gender", "dob", "chief_concern", "state", "city", "region"].forEach((field) => {
					if (match[field] && !frm.doc[field]) {
						frm.set_value(field, match[field]);
					}
				});

				if (match.found_in === "lead") {
					frappe.show_alert(
						{
							message: __("Repeat caller. Last status: {0}", [match.lead_status]),
							indicator: "orange",
						},
						7
					);
				} else {
					frappe.show_alert(
						{ message: __("Existing patient found. Details filled in."), indicator: "blue" },
						7
					);
				}
			},
		});
	},

	dob(frm) {
		if (!frm.doc.dob) return;
		const years = moment().diff(moment(frm.doc.dob), "years");
		frm.set_value("age", years);
	},

	chief_concern(frm) {
		if (!frm.doc.chief_concern || frm.doc.doctor_preference) return;

		frappe.db.get_value("Chief Concern", frm.doc.chief_concern, "default_practitioner").then((r) => {
			if (r.message && r.message.default_practitioner) {
				frm.set_value("doctor_preference", r.message.default_practitioner);
			}
		});
	},

	consultation_mode(frm) {
		if (frm.doc.consultation_mode === "In-Clinic") {
			frm.set_value("meet_link", null);
			if (!frm.doc.clinic_location) {
				frappe.db
					.get_single_value("Doctor Consultation Meet Settings", "clinic_address")
					.then((address) => {
						if (address) frm.set_value("clinic_location", address);
					});
			}
		} else {
			frm.set_value("clinic_location", null);
		}
	},

	region(frm) {
		if (frm.doc.region === "National") {
			frm.set_value("country", "India");
		}
		frm.set_value("state", null);
	},
});

function show_status_banner(frm) {
	frm.dashboard.clear_headline();

	const status = frm.doc.lead_status;
	if (!status) return;

	frm.dashboard.set_headline(
		`<span class="indicator ${STATUS_COLOUR[status] || "gray"}">${__(status)}</span>
		 <span class="text-muted"> &mdash; ${__(STATUS_HELP[status] || "")}</span>`
	);
}

function add_shortcut_buttons(frm) {
	if (frm.is_new()) return;

	// One-tap status moves, so a telecaller rarely opens the dropdown.
	const moves = {
		"New": ["Contacted", "Not Converted", "Invalid"],
		"Contacted": ["Interested", "Follow-up", "Not Converted"],
		"Interested": ["Appointment Booked", "Follow-up", "Not Converted"],
		"Follow-up": ["Interested", "Appointment Booked", "Not Converted"],
	};

	(moves[frm.doc.lead_status] || []).forEach((next) => {
		frm.add_custom_button(
			__(next),
			() => {
				frm.set_value("lead_status", next);
				frm.save();
			},
			__("Move To")
		);
	});
}

function show_notification_banner(frm) {
	if (!frm.doc.patient_appointment) return;

	const email = frm.doc.email_sent
		? `<span class="indicator green">${__("Email sent")}</span>`
		: `<span class="indicator red">${__("Email not sent")}</span>`;

	const whatsapp = frm.doc.whatsapp_sent
		? `<span class="indicator green">${__("WhatsApp sent")}</span>`
		: `<span class="indicator red">${__("WhatsApp not sent")}</span>`;

	// Online doctors are notified by the Doctor Consultation pipeline, not here.
	const doctor =
		frm.doc.consultation_mode === "Online"
			? ""
			: frm.doc.doctor_notified
				? `&nbsp; <span class="indicator green">${__("Doctor notified")}</span>`
				: `&nbsp; <span class="indicator red">${__("Doctor not notified")}</span>`;

	const mode =
		frm.doc.consultation_mode === "Online"
			? `<span class="indicator blue">${__("Online")}</span>`
			: `<span class="indicator orange">${__("In-Clinic")}</span>`;

	frm.dashboard.add_comment(`${mode} &nbsp; ${email} &nbsp; ${whatsapp}${doctor}`, "blue", true);
}