import frappe
import requests
from frappe import _

PINCODE_URL = "https://raw.githubusercontent.com/mithunsasidharan/India-Pincode-Lookup/master/pincodes.json"

@frappe.whitelist()
def populate_pincode_data():
    try:
        populator = PincodeDataPopulator(PINCODE_URL)
        populator.fetch_pincode_data()
        populator.process_pincode_data()

        return {"status": "success", "message": "Pincode data has been populated successfully."}

    except Exception as e:
        frappe.throw(_("An error occurred while populating the data: {0}").format(str(e)))

class PincodeDataPopulator:
    def __init__(self, url):
        self.url = url
        self.pincode_data = None
        self.batch_size = None

    def fetch_pincode_data(self):
        """Fetch the pincode data from the URL."""
        response = requests.get(self.url)
        if response.status_code != 200:
            frappe.throw(_("Failed to fetch data from source"))
        self.pincode_data = response.json()
        self.batch_size = len(self.pincode_data) // 20

    def process_pincode_data(self):
        """Process pincode data in batches."""
        for batch_index, batched_pincode in enumerate(frappe.utils.create_batch(self.pincode_data, self.batch_size)):
            self.process_batch(batched_pincode)

    def process_batch(self, batched_pincode):
        """Process a single batch of pincode data."""
        for entry in batched_pincode:
            self.process_entry(entry)

    def process_entry(self, entry):
        """Process a single pincode entry."""
        pincode = entry.get('pincode')
        taluk_name = entry.get('taluk')
        office_name = entry.get('officeName')
        district_name = entry.get('districtName')
        state_name = entry.get('stateName')

        # Skip if pincode already exists
        if frappe.db.exists("Pincode", {"pincode": pincode}):
            return

        # Ensure Taluk exists or create a new one
        taluk = self.get_or_create_taluk(taluk_name)

        # Create and insert the Pincode document
        self.create_pincode_document(pincode, office_name, taluk, district_name, state_name)

    def get_or_create_taluk(self, taluk_name):
        """Retrieve or create a Taluk record."""
        taluk = frappe.db.get_value("Taluk", {"title": taluk_name})
        if not taluk:
            taluk_doc = frappe.get_doc({
                "doctype": "Taluk",
                "title": taluk_name
            })
            taluk_doc.insert()
            taluk = taluk_doc.name
        return taluk

    def create_pincode_document(self, pincode, office_name, taluk, district, state):
        """Create and insert a Pincode document."""
        pincode_doc = frappe.get_doc({
            "doctype": "Pincode",
            "office_name": office_name,
            "pincode": pincode,
            "taluk": taluk,
            "district": district,
            "state": state
        })
        pincode_doc.insert()
        frappe.db.commit()



@frappe.whitelist(allow_guest=True)
def get_pincode_data(search=None):
    try:
        query = """
            SELECT 
                `tabPincode`.`name`, 
                `tabPincode`.`office_name`, 
                `tabPincode`.`pincode`, 
                `tabPincode`.`district`, 
                `tabPincode`.`state`, 
                `tabTaluk`.`title` as taluk
            FROM `tabPincode`
            LEFT JOIN 
                `tabTaluk`
            ON 
                `tabPincode`.`taluk` = `tabTaluk`.`name`
        """
        
        if search:
            search_filter = """ 
            WHERE 
                `tabPincode`.`office_name` LIKE %(search)s
                OR `tabPincode`.`pincode` LIKE %(search)s
                OR `tabPincode`.`district` LIKE %(search)s
                OR `tabPincode`.`state` LIKE %(search)s
                OR `tabTaluk`.`title` LIKE %(search)s
            """
            query += search_filter

        data = frappe.db.sql(query, {"search": "%" + search + "%"} if search else {}, as_dict=True)

        # Check if any data was found
        if not data:
            return {
                "status": "error",
                "message": _("No offices found for the provided district, state, and pincode."),
                "data": []
            }

        # If data is found, return success response
        return {
            "status": "success",
            "message": _("Successfully fetched the data"),
            "data": data
        }

    except Exception as e:
        frappe.throw(_("An error occurred while fetching the data: {0}").format(str(e)))
