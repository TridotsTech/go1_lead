# Copyright (c) 2024, Tridots Tech and contributors
# For license information, please see license.txt

import frappe,requests,json
from frappe.model.document import Document


class Go1FBLeadForm(Document):
	def before_save(self):
		if not self.form_id:
			self.status = "Draft"
		if self.form_id and self.status == "Draft":
			self.status = "Published"


@frappe.whitelist()
def push_lead_form(doc,page_data,selected_page):
	doc = json.loads(doc)
	access_token = frappe.db.get_value("Go1 Lead Integration",{"lead_app":"Facebook"},"access_token")
	payload = {}
	page_data = json.loads(page_data)
	for i in page_data:
		if i['name'] == selected_page:
			page_id = i['id']
	url = f"https://graph.facebook.com/v20.0/{page_id}/leadgen_forms"
	headers = {"Authorization":"Bearer "+access_token}
	payload['access_token'] = access_token
	payload['name'] = doc['form_name']
	questions = []
	for i in doc['lead_questions']:
		if i['type'] == "Select":
			options = []
			if i.get('options'):
				values = i.get('options').splitlines()
				for vdx,v in enumerate(values):
					options.append({"value":v,"key":v})
			frappe.log_error("options",options)
			questions.append({"type":"CUSTOM",
					 "key":i.get('label'),
					 "label":i.get('label'),"options":options})
		elif i['type'] == "Data":
			questions.append({"type":"CUSTOM","key":i['label'],"label":i['label']})
		else:
			questions.append({"type":f"{i['type'].upper().replace(' ','_')}","key":i['type']})
	payload['questions'] = questions
	payload['privacy_policy'] = {'url': frappe.db.get_value('Go1 Lead Integration',
											{'lead_app':'Facebook'},
											'privacy_policy_url'),"link_text":"Privacy Policy"}
	payload['follow_up_action_url'] = frappe.db.get_value("Go1 Lead Integration",
										{'lead_app':"Facebook"},
										'follow_up_url')
	frappe.log_error('url',url)
	frappe.log_error("payload",payload)
	form_response = requests.post(url = url,json = payload,headers = headers)
	frappe.log_error("form response",form_response.json())
	if form_response.status_code == 200:
		return {"status":"success","message":form_response.json()}
	

@frappe.whitelist()
def pull_fb_lead(doc):
	doc = json.loads(doc)
	frappe.log_error("pull fb lead",doc)
	access_token = frappe.db.get_value("Go1 Lead Integration",{"lead_app":"Facebook"},"access_token")
	if access_token:
		url = f"https://graph.facebook.com/v14.0/{doc['form_id']}/leads"
		headers = {"Authorization":"Bearer "+access_token}
		response = requests.get(url = url,headers = headers)
		if response.status_code == 200:
			for i in response.json()['data']:
				create_fb_lead(i,doc['form_id'])
			# return {"status":"success","message":response.json()}
	else:
		frappe.throw("Set Credentials for facebook")
@frappe.whitelist()
def get_fb_pages(doc):
	doc = json.loads(doc)
	page_url = f"https://graph.facebook.com/v14.0/me/accounts"
	access_token = frappe.db.get_value("Go1 Lead Integration",{"lead_app":"Facebook"},"access_token")
	if access_token:
		headers = {"Authorization":"Bearer "+access_token}
		response = requests.get(url = page_url,headers = headers)
		if response.status_code == 200:
			return {"status":"success","message":response.json(),"access_token":access_token}
	else:
		frappe.throw("Set Credentials for facebook")

def create_fb_lead(data,form_id):
	lead_source = frappe.db.exists("Lead Source",{'name':"Facebook"})
	if not lead_source:
		lead_doc = frappe.get_doc({
			"doctype":"Lead Source",
			"source_name":"Facebook"
		})
		lead_doc.insert(ignore_permissions=True)
		frappe.db.commit()
		lead_source = lead_doc.name
	json_data=[]
	json_data.append(data)
	for i in data['field_data']:
		if i.get('name') == "Email":
			email = i.get('values')[0]
		if i.get('name') == "Full Name":
			full_name = i.get('values')[0]
		if i.get('name') == "First Name":
			first_name = i.get('values')[0]
		if i.get("name") == "Last Name":
			last_name = i.get('values')[0]
	lead = frappe.db.exists("Lead",{'custom_fb_lead_id':data['id']})
	if not lead:
		lead_doc = frappe.get_doc({
			"doctype":"Lead",
			"source":lead_source,
			"custom_fb_lead_id":data['id'],
			"custom_fb_form_id":form_id,
			"custom_fb_data":json.dumps(json_data),
			"email_id":email ,
			"first_name":first_name if first_name else "",
			"last_name":last_name if last_name else "",
			})
		lead_doc.insert(ignore_permissions = True,ignore_mandatory = True)
		frappe.db.commit()
		frappe.log_error("fb data",json_data)


@frappe.whitelist(allow_guest=True)
def create_fb_lead_frappecrm(data,form_id):
	try:
		email, first_name, last_name, full_name = "","","",""
		lead_source = frappe.db.exists("CRM Lead Source",{'name':"Facebook"})
		if not lead_source:
			lead_doc = frappe.get_doc({
				"doctype":"CRM Lead Source",
				"source_name":"Facebook"
			})
			lead_doc.insert(ignore_permissions=True)
			frappe.db.commit()
			lead_source = lead_doc.name
		json_data=[]
		json_data.append(data)
		frappe.log_error("Data",[type(data),data])
		for i in data['field_data']:
			if frappe.scrub(i.get('name')) == "email":
				email = i.get('values')[0]
			if frappe.scrub(i.get('name')) == "full_name":
				full_name = i.get('values')[0]
			if frappe.scrub(i.get('name')) == "first_name":
				first_name = i.get('values')[0]
			if frappe.scrub(i.get("name")) == "last_name":
				last_name = i.get('values')[0]
		lead = frappe.db.exists("CRM Lead",{'custom_fb_lead_id':data['id']})
		frappe.log_error("Lead Email",email)
		if not lead:
			lead_doc = frappe.get_doc({
				"doctype":"CRM Lead",
				"source":lead_source,
				"custom_fb_lead_id":data['id'],
				"custom_fb_form_id":form_id,
				"custom_fb_data":json.dumps(json_data),
				"email_id":email if email else "" ,
				"first_name":first_name if first_name else (full_name if full_name else ""),
				"last_name":last_name if last_name else "",
				})
			lead_doc.insert(ignore_permissions = True,ignore_mandatory = True)
			frappe.db.commit()
			frappe.log_error("fb data",json_data)
	except:
		frappe.log_error("LeadGen Create Lead Error",[data,frappe.get_traceback()])

@frappe.whitelist(allow_guest = True)
def handleFaceBookWebhook():
	if frappe.request.method == "POST":
		data = frappe.request.data
		createLead(data)
		return "OK", 200
	elif frappe.request.method == "GET":
		from werkzeug.wrappers import Response
		response = Response()
		
		hub_mode = frappe.request.args.get("hub.mode")
		hub_challenge = frappe.request.args.get("hub.challenge")
		hub_verify_token = frappe.request.args.get("hub.verify_token")

		verify_token = frappe.db.get_value("Go1 Lead Integration",{"lead_app":"Facebook"},"verify_token")

		if hub_mode == "subscribe" and hub_verify_token == verify_token:
			response.mimetype = "text/plain"
			response.data = hub_challenge
			return response
		else:
			frappe.response.status_code = 403
			return "Verification failed"
	else:
		return "Invalid request", 400


import json
import requests
@frappe.whitelist(allow_guest=True)
def createLead(data):
	try:
		dataDict = data.decode()
		finalData = json.loads(dataDict)
		# frappe.log_error("LeadGen Webhook Data",finalData)
		
		leadgen_id = finalData["entry"][0]["changes"][0]["value"]["leadgen_id"]
		page_id = finalData["entry"][0]["changes"][0]["value"]["page_id"]
		form_id = finalData["entry"][0]["changes"][0]["value"]["form_id"]
		ad_id = finalData["entry"][0]["changes"][0]["value"]["ad_id"]

		access_token = frappe.db.get_value("Go1 Lead Integration",{"lead_app":"Facebook"},"access_token")

		### API for Fetching FormData
		url=f"https://graph.facebook.com/v18.0/{leadgen_id}"
		fieldsList = json.dumps(["field_data","ad_name","campaign_id","campaign_name","platform"])
		r = requests.get(url = url, params = {"access_token":access_token,"fields":fieldsList})

		get_data=r.json()

		installed_apps = frappe.db.get_all("Installed Application",pluck="app_name")
		if "crm" in installed_apps:
			create_fb_lead_frappecrm(get_data,form_id)
		else:
			if "erpnext" in installed_apps:
				create_fb_lead(get_data,form_id)
			else:
				frappe.log_error("App Required","ERPNext or FrappeCRM required to fetch leads from FaceBook via Webhooks.")
	except:
		frappe.log_error("LeadGen Webhook Failed",[data,frappe.get_traceback()])
