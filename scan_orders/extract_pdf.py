import pdfplumber
import re

def extract_orders(pdf_file):
    orders = []
    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
        invoices = text.split("Customer Address")
        for inv in invoices[1:]:
            order_data = {
                "courier_partner": "",
                "company_name": "",
                "tax_invoice_no": "",
                "invoice_date": "",
                "order_date": "",
                "awb_number": "",
                "order_id": "",
                "sku_id": "",
                "qty": "",
                "hsn": "",
                "gross_amount": "",
                "discount": "",
                "taxable_amount": "",
                "total_other_charges": ""
            }
            courier_match = re.search(r"(Delhivery|Shadowfax|Meesho)", inv, re.IGNORECASE)
            if courier_match:
                order_data["courier_partner"] = courier_match.group(1)
            awb_match = re.search(r"\n([A-Z0-9]{10,})\nProduct Details", inv)
            if awb_match:
                order_data["awb_number"] = awb_match.group(1)
            company_match = re.search(r"Sold by\s*:\s*(.*?)\n", inv)
            if company_match:
                order_data["company_name"] = company_match.group(1).strip()
            tax_invoice_match = re.search(r"Invoice No\.\s*([A-Za-z0-9]+)", inv)
            if tax_invoice_match:
                order_data["tax_invoice_no"] = tax_invoice_match.group(1)
            order_date_match = re.search(r"Order Date\s*([\d]{2}\.[\d]{2}\.[\d]{4})", inv)
            invoice_date_match = re.search(r"Invoice Date\s*([\d]{2}\.[\d]{2}\.[\d]{4})", inv)
            if order_date_match:
                order_data["order_date"] = order_date_match.group(1)
            if invoice_date_match:
                order_data["invoice_date"] = invoice_date_match.group(1)
            order_id_match = re.search(r"Order No\.\s*([0-9_]+)", inv)
            if order_id_match:
                order_data["order_id"] = order_id_match.group(1)
            sku_match = re.search(r"Product Details.*?\n(.*?)\s+Free Size\s+(\d+)", inv, re.DOTALL)
            if sku_match:
                order_data["sku_id"] = sku_match.group(1).strip()
                order_data["qty"] = sku_match.group(2)
            hsn_line = re.search(r"\n(\d{6})\s+\d+\s+Rs\.([\d\.]+)\s+Rs\.([\d\.]+)\s+Rs\.([\d\.]+)", inv)
            if hsn_line:
                order_data["hsn"] = hsn_line.group(1)
                order_data["gross_amount"] = hsn_line.group(2)
                order_data["discount"] = hsn_line.group(3)
                order_data["taxable_amount"] = hsn_line.group(4)
            other_match = re.search(r"Other Charges.*?Rs\.([\d\.]+)", inv)
            if other_match:
                order_data["total_other_charges"] = other_match.group(1)
            orders.append(order_data)
    return orders