# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe,requests,json
from frappe.utils import today
from datetime import datetime
from frappe.model.document import Document

class Go1LeadIntegration(Document):
	@frappe.whitelist()
	def pull_leads(self,lead_app,credentials=None):
		try:
			if lead_app == "Trade India":
				date = today()
				if credentials:
					product_enquired = credentials.product_enquired	
					url = f"{credentials.url}?userid={credentials.user_id}&profile_id={credentials.profile_id}&key={credentials.key}&from_date={date}&to_date={date}"
				else:
					product_enquired = self.product_enquired
					url = f"{self.url}?userid={self.user_id}&profile_id={self.profile_id}&key={self.key}&from_date={self.from_date if self.from_date else date}&to_date={self.to_date if self.to_date else date}"
				frappe.log_error("Trade india url",url)
				response = requests.get(url = url)
				leads = response.json()
				frappe.log_error(f"Trade India leads from {date} to {date}",leads)
				if type(leads) == str:
					frappe.throw(leads)
				self.create_lead(leads,lead_app,product_enquired = product_enquired)
			elif lead_app == "Indiamart":
					date = datetime.now()
					# start_date = date.strftime("%d-%b-%Y")
					if credentials:
						start_date_obj = datetime.strptime(today(),"%Y-%m-%d")
						end_date_obj = datetime.strptime(today(),"%Y-%m-%d")
						key = credentials.key
						url = credentials.url
						product_enquired = credentials.product_enquired
					else:
						start_date_obj = datetime.strptime(self.from_date,"%Y-%m-%d")
						end_date_obj = datetime.strptime(self.to_date,"%Y-%m-%d") 
						key = self.key
						url = self.url
						product_enquired = self.product_enquired
					#Change date format from yyyy-mm-dd to 13-Aug-2022
					start_date = start_date_obj.strftime("%d-%b-%Y")
					end_date = end_date_obj.strftime("%d-%b-%Y")
					url = f"{url}/?glusr_crm_key={key}&start_time={start_date}&end_time={end_date}"
					frappe.log_error("Indiamart url",url)
					leads = requests.get(url = url).json()
					self.create_lead(leads,lead_app , product_enquired)
		except Exception:
			frappe.log_error("failed",frappe.get_traceback())
	
	def create_lead(self,data,source,product_enquired = None):
		if source == "Trade India":
			frappe.log_error("product Enquired",product_enquired)
			if not frappe.db.exists("Lead Source",{"source_name":"Trade India"}):
				#Create new lead source
				frappe.get_doc({"doctype":"Lead Source","source_name":"Trade India"}).insert(ignore_permissions=True)
			#loop through the data and create leads ,in exists also validate rfi_id if not exist
			for d in data:
				if not frappe.db.exists("Lead",{"source":source,"custom_rfi_id":d.get("rfi_id")}):
					if not d['sender_name'] == "Phone Inquiry":
						frappe.log_error("number type",type(d['sender_mobile']))
						frappe.log_error("number equal",d['sender_mobile'][3:])
						self.create_tradeindia_lead(d,product_enquired)
						
		elif source == "Indiamart":
			frappe.log_error("product Enquired",product_enquired)
			if not frappe.db.exists("Lead Source",{"source_name":source}):
				#Create new lead source
				frappe.get_doc({"doctype":"Lead Source","source_name":source}).insert(ignore_permissions=True)
			for d in data['RESPONSE']:
				if not frappe.db.exists("Lead",{"source":source,"custom_im_query_id":d.get("UNIQUE_QUERY_ID")}):
					self.create_indiamart_lead(d,product_enquired = product_enquired)	
		
	def create_tradeindia_lead(self,d,product_enquired=None,source = "Trade India"):
		frappe.get_doc({
						"doctype":"Lead",
						"first_name":d.get("sender_name"),
						"source":source,
						"custom_inquiry_type":d['inquiry_type'],
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
						"custom_product_enquired":product_enquired, # homegenie field
						"custom_customer_category":"B2B", #homegenie field
						"custom_address":d['address'] if d.get('address') else "",
						"mobile_no":d['sender_mobile'],
						"whatsapp_no":d['sender_mobile'][3:] if (d.get('sender_mobile')[0:3] == "+91") else d['sender_mobile'],
					}).insert(ignore_permissions = True,ignore_mandatory = True)
		
	def create_indiamart_lead(self,d,product_enquired=None,source = "IndiaMart"):
		query_type = {
			"W" : "Direct & ASTBUY Enquiries",
			"B" : "Buy-Leads",
			"P" : "PNS Calls",
			"V" : "Catalog-view Leads",
			"BIZ" : "Catalog-view Leads",
			"WA": "WhatsApp Enquiries"
		}
		code = d['SENDER_COUNTRY_ISO'].lower()
		country = frappe.db.get_value("Country",{"code":code})
		frappe.get_doc({
			"doctype":"Lead",
			"first_name":d.get("SENDER_NAME"),
			"source":source,
			"custom_inquiry_type":query_type.get(d["QUERY_TYPE"]) if d.get("QUERY_TYPE") else "",
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
			# "custom_address":d['SENDER_ADDRESS'] if d.get('SENDER_ADDRESS') else "",
			"custom_pincode":d['SENDER_PINCODE'] if d.get('SENDER_PINCODE') else "",
			"custom_product_enquired":product_enquired,
			"custom_customer_category":"B2B",
			"custom_call_duration":d["CALL_DURATION"],
			"mobile_no":d['SENDER_MOBILE'],
			"whatsapp_no":d['SENDER_MOBILE'][4:] if (d.get('SENDER_MOBILE')[0:4] == "+91-") else d['SENDER_MOBILE'],
		}).insert(ignore_permissions = True,ignore_mandatory = True)

@frappe.whitelist()
def sync_leads():
		try:
			lead_integration = frappe.get_list("Go1 Lead Integration",["*"])
			for i in lead_integration:
				doc = frappe.get_doc("Go1 Lead Integration",i.name)
				frappe.get_doc("Go1 Lead Integration",doc.name).pull_leads(doc.lead_app,credentials = doc)
		except Exception:
			frappe.log_error("sync lead error",frappe.get_traceback())