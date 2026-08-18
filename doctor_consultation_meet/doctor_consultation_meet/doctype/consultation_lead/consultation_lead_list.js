// Colour-coded list view so a telecaller can read their day at a glance.
frappe.listview_settings["Consultation Lead"] = {
	add_fields: ["lead_status", "follow_up_date", "mobile_no", "patient_name"],

	filters: [["lead_status", "!=", "Invalid"]],

	get_indicator(doc) {
		const map = {
			"New": "blue",
			"Contacted": "orange",
			"Interested": "purple",
			"Appointment Booked": "green",
			"Consultation Done": "darkgrey",
			"Follow-up": "yellow",
			"Not Converted": "red",
			"Invalid": "gray",
		};

		// Overdue follow-ups shout the loudest.
		if (doc.lead_status === "Follow-up" && doc.follow_up_date < frappe.datetime.get_today()) {
			return [__("Follow-up Overdue"), "red", "lead_status,=,Follow-up"];
		}

		return [__(doc.lead_status), map[doc.lead_status] || "gray", "lead_status,=," + doc.lead_status];
	},

	onload(listview) {
		listview.page.add_inner_button(__("My Follow-ups Today"), () => {
			frappe.set_route("List", "Consultation Lead", {
				telecaller: frappe.session.user,
				lead_status: "Follow-up",
				follow_up_date: ["<=", frappe.datetime.get_today()],
			});
		});

		listview.page.add_inner_button(__("My Leads Today"), () => {
			frappe.set_route("List", "Consultation Lead", {
				telecaller: frappe.session.user,
				lead_date: frappe.datetime.get_today(),
			});
		});
	},
};