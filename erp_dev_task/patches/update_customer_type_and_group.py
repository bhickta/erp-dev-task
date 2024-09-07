import frappe
from frappe.utils import getdate

def execute():
    # print('---------------patch called--------------------')
    # frappe.log_error('patch')
    mumbai_customers = frappe.get_all('Customer', 
                                      filters={"customer_primary_address": ["!=", ""]}, 
                                      fields=['name', 'customer_primary_address'])
    
    for customer in mumbai_customers:
        address = frappe.get_doc('Address', customer.customer_primary_address)
        if 'mumbai' in address.city.lower():
            frappe.db.set_value('Customer', customer.name, 'customer_type', 'Corporate')

            # ----------------------------
    old_customers = frappe.get_all('Customer',
                                   filters={"creation": ["<", "2023-01-01"]},
                                   fields=["name"])
    for customer in old_customers:
        frappe.db.set_value('Customer', customer.name, 'customer_group', 'Old Customers')

    frappe.db.commit()

execute()