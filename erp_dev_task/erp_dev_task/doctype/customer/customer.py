import frappe
import random

def after_insert(doc, method):
    """
    Whenever a customer is created with address as Delhi then new sales order should be
    created with items with random values
    """
    if (doc.state == "Delhi" or doc.city == "Delhi"):
        CreateSalesOrder(doc).create()
    
class CreateSalesOrder():
    def __init__(self, doc):
        self.customer = doc
        
    def create(self):
        self.create_sales_order()
        self.update_sales_order_header_fields()
        self.create_sales_order_items()
        self.save_sales_order()
        
    def create_sales_order(self):
        self.sales_order = frappe.new_doc("Sales Order")
        
    def update_sales_order_header_fields(self):
        self.sales_order.customer = self.customer.customer_name
        self.sales_order.order_type = "Sales"
        self.sales_order.transaction_date = frappe.utils.nowdate()
        self.sales_order.set_warehouse = "Finished Goods - SSD"
    
    def create_sales_order_items(self):
        items = frappe.db.get_all("Item", filters={"item_group": "Products"}, fields=["name"], pluck="name")
        for item in items:
            self.sales_order.append("items", {
                "item_code": item,
                "qty": random.randint(50, 1000),
                "rate": 100,
                "uom": "Nos",
                "delivery_date": self.sales_order.get("transaction_date")
            })
            
    def save_sales_order(self):
        self.sales_order.insert()
        
def on_trash(doc, method):
    """
    Whenever a customer is deleted, all related sales orders should also be deleted
    """
    sales_order_docs = frappe.get_all("Sales Order", filters={"customer": doc.customer_name}, fields=["name"], pluck="name")
    for sales_order in sales_order_docs:
        frappe.delete_doc("Sales Order", sales_order)
    