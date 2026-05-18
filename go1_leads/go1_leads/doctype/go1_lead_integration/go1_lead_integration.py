# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

# pyrefly: ignore [missing-import]
import frappe,requests,json
# pyrefly: ignore [missing-import]
from frappe.utils import today
from datetime import datetime
# pyrefly: ignore [missing-import]
from frappe.model.document import Document

class Go1LeadIntegration(Document):
	@frappe.whitelist()
	def pull_leads(self,lead_app,credentials=None):
		try:
			if lead_app == "Trade India":
				date = today()
				if credentials:
					url = f"{credentials.url}?userid={credentials.user_id}&profile_id={credentials.profile_id}&key={credentials.key}&from_date={date}&to_date={date}"
				else:
					url = f"{self.url}?userid={self.user_id}&profile_id={self.profile_id}&key={self.key}&from_date={self.from_date if self.from_date else date}&to_date={self.to_date if self.to_date else date}"
				
				frappe.log_error(f"Trade India Pull Attempt", "Trade India Integration")
				response = requests.get(url = url)
				leads = response.json()
				if type(leads) == str:
					frappe.throw(leads)
				self.create_lead(leads,lead_app)
				
			elif lead_app == "Indiamart":
					if credentials:
						start_date_obj = datetime.strptime(today(),"%Y-%m-%d")
						end_date_obj = datetime.strptime(today(),"%Y-%m-%d")
						key = credentials.key
						url = credentials.url
					else:
						start_date_obj = datetime.strptime(self.from_date,"%Y-%m-%d")
						end_date_obj = datetime.strptime(self.to_date,"%Y-%m-%d") 
						key = self.key
						url = self.url
					
					base_url = url.rstrip('/')
					start_date = start_date_obj.strftime("%d-%b-%Y")
					end_date = end_date_obj.strftime("%d-%b-%Y")
					
					final_url = f"{base_url}/?glusr_crm_key={key}&start_time={start_date}&end_time={end_date}"
					
					# FIX: Use a short title and put the long URL in the message body
					masked_url = final_url.replace(key, "********")
					frappe.log_error(title="IndiaMart Pull Attempt", message=f"URL: {masked_url}")

					response = requests.get(url = final_url)
					leads = response.json()
					
					# FIX: Short title for raw response
					frappe.log_error(title="IndiaMart API Response", message=json.dumps(leads, indent=2))

					if leads.get('CODE') == 200:
						self.create_lead(leads,lead_app)
					elif leads.get('CODE') == 429:
						msg = f"Rate Limit (429): {leads.get('MESSAGE')}"
						frappe.msgprint(msg)
						frappe.log_error(title="IndiaMart Rate Limit", message=msg)
					else:
						msg = f"Error ({leads.get('CODE')}): {leads.get('MESSAGE')}"
						frappe.log_error(title="IndiaMart Error", message=msg)

		except Exception:
			frappe.log_error(title="IndiaMart Sync Failed", message=frappe.get_traceback())
	
	def create_lead(self,data,source):
		if source == "Trade India":
			if not frappe.db.exists("Lead Source",{"source_name":"Trade India"}):
				frappe.get_doc({"doctype":"Lead Source","source_name":"Trade India"}).insert(ignore_permissions=True)
			
			count = 0
			for d in data:
				if not frappe.db.exists("Lead",{"source":source,"custom_rfi_id":d.get("rfi_id")}):
					if not d['sender_name'] == "Phone Inquiry":
						self.create_tradeindia_lead(d)
						count += 1
			frappe.log_error(title="Trade India Process Complete", message=f"Created {count} leads")
						
		elif source == "Indiamart":
			if not frappe.db.exists("Lead Source",{"source_name":source}):
				frappe.get_doc({"doctype":"Lead Source","source_name":source}).insert(ignore_permissions=True)
			
			count = 0
			for d in data.get('RESPONSE', []):
				query_id = d.get("UNIQUE_QUERY_ID")
				if not frappe.db.exists("Lead",{"source":source,"custom_im_query_id":query_id}):
					try:
						self.create_indiamart_lead(d)
						count += 1
					except Exception:
						frappe.log_error(title=f"Lead Creation Failed: {query_id}", message=frappe.get_traceback())
			
			frappe.log_error(title="IndiaMart Process Complete", message=f"New leads created: {count}")
		
	def create_tradeindia_lead(self,d,source = "Trade India"):
		frappe.get_doc({
						"doctype":"Lead",
						"first_name":d.get("sender_name"),
						"source":source,
						"custom_inquiry_type":d.get('inquiry_type'),
						"custom_rfi_id":d.get('rfi_id'),
						"email_id":d.get('sender_email', ""),
						"lead_status":"Open",
						"custom_sender_company":d.get('sender_co'),
						"custom_minimum_order_value":d.get('order_value_min', ""),
						"country":d.get("sender_country"),
						"city":d.get('sender_city'),
						"state":d.get('sender_state'),
						"custom_product_name":d.get('product_name', ""),
						"custom_product_quantity":d.get('quantity', ""),
						"custom_subject":d.get('subject'),
						"custom_message":d.get('message'),
						"custom_address":d.get('address', ""),
						"mobile_no":d.get('sender_mobile'),
						"whatsapp_no":d.get('sender_mobile')[3:] if (d.get('sender_mobile') and d.get('sender_mobile')[0:3] == "+91") else d.get('sender_mobile'),
					}).insert(ignore_permissions = True,ignore_mandatory = True)
		
	def create_indiamart_lead(self,d,source = "IndiaMart"):
		query_type_map = {
			"W" : "Direct & ASTBUY Enquiries",
			"B" : "Buy-Leads",
			"P" : "PNS Calls",
			"V" : "Catalog-view Leads",
			"BIZ" : "Catalog-view Leads",
			"WA": "WhatsApp Enquiries"
		}
		
		iso_code = d.get('SENDER_COUNTRY_ISO', '').lower()
		country = frappe.db.get_value("Country", {"code": iso_code}) if iso_code else None
		
		mobile = d.get('SENDER_MOBILE', '')
		whatsapp = mobile
		if mobile and mobile.startswith("+91-"):
			whatsapp = mobile[4:]

		frappe.get_doc({
			"doctype":"Lead",
			"first_name":d.get("SENDER_NAME"),
			"source":source,
			"custom_inquiry_type":query_type_map.get(d.get("QUERY_TYPE"), "Other"),
			"custom_im_query_id":d.get('UNIQUE_QUERY_ID'),
			"email_id":d.get('SENDER_EMAIL', ""),
			"lead_status":"Open",
			"custom_sender_company":d.get('SENDER_COMPANY'),
			"country":country if country else "",
			"city":d.get('SENDER_CITY'),
			"state":d.get('SENDER_STATE'),
			"custom_product_name":d.get('QUERY_PRODUCT_NAME'),
			"custom_subject":d.get('SUBJECT'),
			"custom_message":d.get('QUERY_MESSAGE'),
			"custom_pincode":d.get('SENDER_PINCODE', ""),
			"custom_call_duration":d.get("CALL_DURATION"),
			"mobile_no":mobile,
			"whatsapp_no":whatsapp,
		}).insert(ignore_permissions = True,ignore_mandatory = True)

@frappe.whitelist()
def sync_leads():
		try:
			lead_integrations = frappe.get_all("Go1 Lead Integration", fields=["name", "lead_app"])
			for integration in lead_integrations:
				doc = frappe.get_doc("Go1 Lead Integration", integration.name)
				doc.pull_leads(doc.lead_app, credentials=doc)
		except Exception:
			frappe.log_error(title="Go1 Leads Sync Global Error", message=frappe.get_traceback())