import requests
from frappe import _
from frappe.utils import random_string
import frappe

# http://127.0.0.1:8000/api/method/erp_dev_task.api.save_pincodes
# http://127.0.0.1:8000/api/method/erp_dev_task.api.get_pincode_and_taluk_data

def create_sales_order_if_delhi(doc, method):
    if not doc.customer_primary_address:
        return
    # print(doc.customer_primary_address)
    address = frappe.get_doc('Address', doc.customer_primary_address)
    if 'delhi' not in address.city.lower():
        return

    items = [
        {"item_code": "Item 1", "qty": 1},
        {"item_code": "Item 2", "qty": 1},
        {"item_code": "Item 3", "qty": 1}
    ]

    sales_order = frappe.get_doc({
        "doctype": "Sales Order",
        "customer": doc.name,
        "delivery_date": frappe.utils.add_days(frappe.utils.nowdate(), 7),  # 7 days from now
        "items": items
    })

    try:
        sales_order.insert()
        frappe.db.commit()
    except Exception as e:
        frappe.log_error(f"Failed SO for customer {doc.name}: {str(e)}")
        # frappe.throw(f"Could not create Sales Order for {doc.name}")


import frappe
from frappe.model.delete_doc import delete_doc

def delete_sales_order_if_exists(doc, method):
    sales_orders = frappe.get_all("Sales Order", filters={"customer": doc.name})

    for so in sales_orders:
        try:
            sales_order_doc = frappe.get_doc("Sales Order", so.name)

            if sales_order_doc.docstatus == 1:  
                sales_order_doc.cancel()
            delete_doc("Sales Order", sales_order_doc.name, force=1, ignore_permissions=True, ignore_missing=True)
            
        except Exception as e:
            frappe.log_error(f"Error while deleting Sales Order {so.name} for customer {doc.name}: {str(e)}")
            frappe.throw(f"Failed to delete Sales Order for {doc.name}")



url = "https://raw.githubusercontent.com/mithunsasidharan/India-Pincode-Lookup/master/pincodes.json"

@frappe.whitelist(allow_guest=True)
def save_pincodes():
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # frappe.log_error(len(data))
            # print('----------------------------------------------',len(data),type(data))
            # data=[{"officeName":"Ada B.O","pincode":504293,"taluk":"Asifabad","districtName":"Adilabad","stateName":"ANDHRA PRADESH"},{"officeName":"Andugulpet B.O","pincode":504231,"taluk":"Luxettipet","districtName":"Adilabad","stateName":"ANDHRA PRADESH"},{"officeName":"Annaram B.O","pincode":504201,"taluk":"Chennur","districtName":"Adilabad","stateName":"ANDHRA PRADESH"},{"officeName":"Arli (T) B.O","pincode":504312,"taluk":"Adilabad","districtName":"Adilabad","stateName":"ANDHRA PRADESH"}]
            c=0
            for item in data:
                pincode = item.get('pincode')
                taluk_name = item.get('taluk')
                c=c+1
                # if c%1==0:print('+++++++++',c)
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
        
        # Commit all
        frappe.db.commit()
        return {'status': 'success', 'message': 'Data successfully populated'}


@frappe.whitelist(allow_guest=True)
def get_pincode_and_taluk_data(search_param=None):
    # print('-------------',search_param)
    try:
        query = """
            SELECT p.officeName, p.pincode, p.districtName, p.stateName, t.title as taluk
            FROM `tabPincode` p
            LEFT JOIN`tabTaluk` t ON p.taluk = t.name
            WHERE
                p.officeName LIKE %(search_param)s OR
                p.districtName LIKE %(search_param)s OR
                p.stateName LIKE %(search_param)s OR
                p.pincode LIKE %(search_param)s OR
                t.title LIKE %(search_param)s
        """
        
        search_param = f"%{search_param}%"
        data = frappe.db.sql(query, {'search_param': search_param}, as_dict=True)
        # print(data,search_param)
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
