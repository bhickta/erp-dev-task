import frappe


def execute():
    """
    Update the customer type for all customers with addresses in Mumbai to be Corporate.
    """
    query = """
        SELECT 
            `tabDynamic Link`.`link_name` as name
        FROM 
            `tabAddress`
        LEFT JOIN
            `tabDynamic Link`
        ON 
            `tabAddress`.`name` = `tabDynamic Link`.`parent`
        WHERE
            `tabAddress`.`city`='Mumbai'
    """
    customers = frappe.db.sql(query, as_dict=True)
    
    for customer in customers:
        customer = customer.get("name")
        frappe.db.set_value("Customer", customer, "customer_type", "Corporate")