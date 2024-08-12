# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe,requests
from frappe.model.document import Document


class LeadIntegration(Document):
	@frappe.whitelist()
	def pull_leads(self):
		if self.lead_application == "Trade India":
			url = f"{self.url}?userid={self.user_id}&profile_id={self.profile_id}&key={self.key}&from_date={self.from_date}&to_date={self.to_date}"
			frappe.log_error("url",url)
			leads = requests.get(url = url).json()
			frappe.log_error(f"leads from {self.from_date} to {self.to_date}",leads)
