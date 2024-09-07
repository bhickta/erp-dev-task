import json
import frappe
from frappe.model.document import Document
from werkzeug.wrappers import Response
from frappe.utils import response as r
import requests
from frappe import _

# http://127.0.0.1:8000/api/method/erp_dev_task.erp_dev_task.doctype.pincode.api.save_pincodes

url = "https://raw.githubusercontent.com/mithunsasidharan/India-Pincode-Lookup/master/pincodes.json"

@frappe.whitelist(allow_guest=True)
def save_pincodes():
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # frappe.log_error(len(data))
            print('----------------------------------------------',len(data),type(data))
            # data=[{"officeName":"Ada B.O","pincode":504293,"taluk":"Asifabad","districtName":"Adilabad","stateName":"ANDHRA PRADESH"},{"officeName":"Andugulpet B.O","pincode":504231,"taluk":"Luxettipet","districtName":"Adilabad","stateName":"ANDHRA PRADESH"},{"officeName":"Annaram B.O","pincode":504201,"taluk":"Chennur","districtName":"Adilabad","stateName":"ANDHRA PRADESH"},{"officeName":"Arli (T) B.O","pincode":504312,"taluk":"Adilabad","districtName":"Adilabad","stateName":"ANDHRA PRADESH"}]
            c=0
            for item in data:
                pincode = item.get('pincode')
                taluk_name = item.get('taluk')
                c=c+1
                if c%1000==0:print('+++++++++',c)
                # chk pincode exists
                existing_pincode = frappe.db.exists('Pincode', {'pincode': pincode})
                
                if not existing_pincode:
                    # chk Taluk 
                    taluk = frappe.db.get_value('Taluk', {'title': taluk_name})
                    if not taluk:
                        taluk_doc = frappe.get_doc({
                            'doctype': 'Taluk',
                            'title': taluk_name
                        })
                        taluk_doc.insert()
                        taluk = taluk_doc.name
                    
                    # Create the Pincode document
                    pincode_doc = frappe.get_doc({
                        'doctype': 'Pincode',
                        'officename': item.get('officeName'),
                        'pincode': pincode,
                        'taluk': taluk,
                        'districtname': item.get('districtName'),
                        'statename': item.get('stateName')
                    })
                    pincode_doc.insert()
        
        # Commit (all or none)
        frappe.db.commit()
        return {'status': 'success', 'message': 'Data successfully populated'}


@frappe.whitelist(allow_guest=True)
def get_pincode_and_taluk_data(search_param=None):
    try:
        # Construct the query
        query = """
            SELECT
                p.officeName, p.pincode, p.districtName, p.stateName, t.title as taluk
            FROM
                `tabPincode` p
            LEFT JOIN
                `tabTaluk` t ON p.taluk = t.name
            WHERE
                p.officeName LIKE %(search_param)s OR
                p.districtName LIKE %(search_param)s OR
                p.stateName LIKE %(search_param)s OR
                p.pincode LIKE %(search_param)s OR
                t.title LIKE %(search_param)s
        """
        
        search_param = f"%{search_param}%"
        data = frappe.db.sql(query, {'search_param': search_param}, as_dict=True)

        if not data:
            return {
                "status": "error",
                "message": "No offices found for the provided district, state, and pincode.",
                "data": []
            }

        return {
            "status": "success",
            "message": "Successfully fetched the data",
            "data": data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "data": []
        }
