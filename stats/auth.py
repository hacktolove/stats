import frappe
import json
import requests
from frappe import _
from requests import HTTPError, Response, JSONDecodeError
from requests.auth import HTTPBasicAuth
from frappe.utils.oauth import get_oauth2_authorize_url, get_oauth_keys, redirect_post_login
from frappe.sessions import Session, clear_sessions, delete_session
from frappe.auth import clear_cookies
from frappe.handler import logout,web_logout
ALLOWED_PATHS = ["/api/method/stats.auth.call_stats_erpnext"]

@frappe.whitelist(allow_guest=True)
def call_stats_erpnext(**kwargs):
	pass
	# frappe.msgprint(_("Sucess"),indicator="green",	alert=True,)

@frappe.whitelist()
def validate_portal_user(**kwargs):
	try:
		stats_settings = frappe.get_cached_doc('Stats Settings ST', 'Stats Settings ST')
		if stats_settings.enable_portal_login==1:
			# frappe.local.login_manager.logout()
			print("A","inside hook====")
			# frappe.request.data =b'{"userId": "XG9QUZuxfORkbw==", "token": "XG5dkHbzklE90Ele700AgRB6+npsHc37h66aBvL7pJj3SZA=", "ipAddress": "XG9Pr7PGK6v0hrRUNCc=", "app": "HbfADiJc", "time": "XGhl62LL+X6z9A==", "lang": "DKE=", "email": "DzuUgCQu20v+fnyzMaGOjvdPiXk="}'
			print("B",frappe.request,frappe.request.path)
			if frappe.request and frappe.request.path and frappe.request.path in ALLOWED_PATHS:
				print("1")
				if frappe.local.form_dict:	
					userId=frappe.local.form_dict.get("userId")
					token=frappe.local.form_dict.get("token")
					ipAddress=frappe.local.form_dict.get("ipAddress")
					app=frappe.local.form_dict.get("app")
					time=frappe.local.form_dict.get("time")
					lang=frappe.local.form_dict.get("lang")
					email=frappe.local.form_dict.get("email")
					query_data={"userId":userId,"token":token,"ipAddress":ipAddress,"app":app,"time":time,"lang":lang,"email":email}
					print("query_data",query_data)
					print("2")
					headers={"Content-type": "application/json"}
					post_data = json.dumps(query_data)
					print("post_data",post_data)
					hard_coded_url= 'https://gsn-prd.stats.gov.sa/stats/integration/api/v1/internal-integration/check'
					url = stats_settings.portal_auth_url or hard_coded_url
					# url='http://127.0.0.1:8000/api/method/stats.auth.portal_auth_fake'
					response = requests.post(url, headers=headers, data=post_data)
					print("+++",response,"=="*100,response.content,response.json())
					user_email=None
					if response.status_code == 200:
						print("33")
						response_data = json.loads(response.content)
						print("response_data-----",response_data)
						if response_data.get("email"):
							user_email=response_data.get("email")
						elif response_data.get("data") :
							response_data = json.loads(response_data.get("data"))
							user_email=response_data.get("email")
						elif response_data.get("result") :
							response_data = json.loads(response_data.get("result"))
							user_email=response_data.get("email")
						print("user_email",user_email)
						if user_email!=None:
							user_exists=frappe.db.exists("User", user_email, cache=True)
							print("user_exists",user_exists)
							if user_exists!=None:
								print("user_email11",user_email)
								# frappe.set_user(user_email)
								frappe.local.login_manager.login_as(user_email)
								desk_user=frappe.db.get_value("User",user_email, "user_type") == "System User"
								redirect_post_login(desk_user=desk_user)
							else:
								frappe.throw(_("User not found"))
				else:
					pass
			else:
				pass
		else:
			pass
	except Exception:
		frappe.log_error()
 
@frappe.whitelist(allow_guest=True)	
def portal_auth_fake(*kwargs):
	request_data = json.loads(frappe.request.data)
	user_email= 'budget_officer@demo.com' or 'demo1@demo.com' or 'payroll_user@demo.com' 
	response_string= {"userId": "userId_e90f5403fa8d","appEnv": "appEnv_cfdcf6401ef3","email": user_email}
	response_data=json.dumps(response_string)
	# headers={"Content-type": "application/json"}
	# hard_coded_url= 'http://127.0.0.1:8000/api/method/stats.auth.validate_portal_user'	
	frappe.response['data']=response_data

@frappe.whitelist(allow_guest=True)
def on_logout():
	print("====="*10)
	print("inside on_logout")
	redirect_url=None
	stats_settings = frappe.get_cached_doc('Stats Settings ST', 'Stats Settings ST')
	if stats_settings.enable_portal_login==1:
		portal_url_to_call_on_logout=stats_settings.portal_url_to_call_on_logout
		if portal_url_to_call_on_logout:
			logout()
			redirect_url=portal_url_to_call_on_logout
			return {"redirect_url": redirect_url}
		else:
			logout()
			return {"redirect_url": redirect_url}
	else:
		logout()
		return {"redirect_url": redirect_url}