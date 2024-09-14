import frappe

def execute():
    """
    Update the customer group for all customers created before 2023-01-01 to be Old Customers.
    """
    if not frappe.db.exists("Customer Group", {"customer_group_name": "Old Customer"}):
        frappe.get_doc({
            "doctype": "Customer Group",
            "customer_group_name": "Old Customer",
            "parent_customer_group": "All Customer Groups",
        }).insert()
        
    frappe.db.sql("""
        UPDATE `tabCustomer`
        SET `customer_group` = 'Old Customers'
        WHERE `creation` < '2023-01-01'
    """)
    frappe.db.commit()