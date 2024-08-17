# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe,requests,json
from frappe.utils import today
from datetime import datetime
from frappe.model.document import Document

class Go1LeadIntegration(Document):
	@frappe.whitelist()
	def pull_leads(self):
		try:
			if self.lead_app == "Trade India":
				date = today()
				url = f"{self.url}?userid={self.user_id}&profile_id={self.profile_id}&key={self.key}&from_date={self.from_date}&to_date={self.to_date}"
				frappe.log_error("url",url)
				leads = requests.get(url = url).json()
				frappe.log_error(f"Trade India leads from {date} to {date}",leads)
				self.create_lead(leads,self.lead_app)
			elif self.lead_app == "IndiaMart":
					date = datetime.now()
					# start_date = date.strftime("%d-%b-%Y")
					start_date_obj = datetime.strptime(self.from_date,"%Y-%m-%d")
					end_date_obj = datetime.strptime(self.to_date,"%Y-%m-%d")
					start_date = start_date_obj.strftime("%d-%b-%Y")
					#same as previous line for self.end_date
					end_date = end_date_obj.strftime("%d-%b-%Y")
					url = f"{self.url}/?glusr_crm_key={self.key}&start_time={start_date}&end_time={end_date}"
					leads = requests.get(url = url).json()
					if not leads.get('MESSAGE'):
						self.create_lead(leads,self.lead_app)
					else:
						return leads
					frappe.log_error(f"INDIA MARTleads",leads)
		except Exception:
			frappe.log_error("failed",frappe.get_traceback())
	
	def create_lead(self,data,source):
		if source == "Trade India":
			if not frappe.db.exists("Lead Source",{"source_name":"Trade India"}):
				#Create new lead source
				frappe.get_doc({"doctype":"Lead Source","source_name":"Trade India"}).insert(ignore_permissions=True)
			#loop through the data and create leads ,in exists also validate rfi_id if not exist
			for d in data:
				if not frappe.db.exists("Lead",{"source":source,"custom_rfi_id":d.get("rfi_id")}):
					if not d['sender_name'] == "Phone Inquiry":
						frappe.get_doc({
							"doctype":"Lead",
							"first_name":d.get("sender_name"),
							"source":source,
							"custom_rfi_id":d.get('rfi_id'),
							"email_id":d['sender_email'] if d.get('sender_email') else "",
							"lead_status":"Open",
							"custom_sender_company":d['sender_co'],
							"custom_minimum_order_value":d['order_value_min'] if 'order_value_min' in d else "",
							"country":d["sender_country"],
							"city":d['sender_city'],
							"state":d['sender_state'],
							"custom_product_name":d['product_name'] if d.get('product_name') else "",
							"custom_product_quantity":d['quantity'] if d.get('quantity') else "",
							"custom_subject":d['subject'],
							"custom_message":d['message'],
							# "custom_product_enquired":"Rocotile",
							# "custom_customer_category":"B2C",
							"mobile_no":d['sender_mobile'],
							"whatsapp_no":d['sender_mobile'],
						}).insert(ignore_permissions=True)
		elif source == "IndiaMart":
			if not frappe.db.exists("Lead Source",{"source_name":source}):
				#Create new lead source
				frappe.get_doc({"doctype":"Lead Source","source_name":source}).insert(ignore_permissions=True)
			frappe.log_error("data type for indiamart",type(data))
			for d in data['RESPONSE']:
				if not frappe.db.exists("Lead",{"source":source,"custom_im_query_id":d.get("UNIQUE_QUERY_ID")}):
						# if not d['sender_name'] == "Phone Inquiry":
						code = d['SENDER_COUNTRY_ISO'].lower()
						country = frappe.db.get_value("Country",{"code":code})
						frappe.get_doc({
							"doctype":"Lead",
							"first_name":d.get("SENDER_NAME"),
							"source":source,
							"custom_im_query_id":d.get('UNIQUE_QUERY_ID'),
							"email_id":d['SENDER_EMAIL'] if d.get('SENDER_EMAIL') else "",
							"lead_status":"Open",
							"custom_sender_company":d['SENDER_COMPANY'],
							"country":country if country else "",
							"city":d['SENDER_CITY'],
							"state":d['SENDER_STATE'],
							"custom_product_name":d['QUERY_PRODUCT_NAME'],
							"custom_subject":d['SUBJECT'],
							"custom_message":d['QUERY_MESSAGE'],
							"custom_address":d['SENDER_ADDRESS'],
							"custom_pincode":d['SENDER_PINCODE'] if d.get('SENDER_PINCODE') else "",
							# "custom_product_enquired":"Rocotile",
							# "custom_customer_category":"B2C",
							"mobile_no":d['SENDER_MOBILE'],
							"whatsapp_no":d['SENDER_MOBILE'],
						}).insert(ignore_permissions=True)