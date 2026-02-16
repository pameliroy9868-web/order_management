import pdfplumber
import re


# -------- COURIER --------
def extract_courier(text):
    match = re.search(r"(Delhivery|Shadowfax|Amazon|BlueDart|Ecom Express)", text, re.I)
    return match.group(1) if match else ""


# -------- CUSTOMER NAME --------
def extract_customer_name(text):

    lines = text.split("\n")

    for i, line in enumerate(lines):
        if  "Customer Address" in line.strip():
            # find first valid name line after this
            for j in range(i+1, min(i+6, len(lines))):

                candidate = lines[j].strip()

                # skip empty or numeric-only lines
                if candidate and not candidate.isdigit():
                    return candidate

    return ""


def extract_amounts(text):

    gross_amount = ""
    discount = ""
    taxable_amount = ""
    total_other_charges = ""

    # MAIN PRODUCT LINE
    main_match = re.search(
        r'\b\d{6}\s+\d+\s+Rs\.([\d\.]+)\s+Rs\.([\d\.]+)\s+Rs\.([\d\.]+)',
        text
    )

    if main_match:

        gross_amount = main_match.group(1)
        discount = main_match.group(2)
        taxable_amount = main_match.group(3)


    # OTHER CHARGES
    other_match = re.search(
        r'Other Charges.*?Rs\.([\d\.]+)',
        text,
        re.DOTALL
    )

    if other_match:
        total_other_charges = other_match.group(1)


    return gross_amount, discount, taxable_amount, total_other_charges


def extract_fields_robust(text):

    lines = [l.strip() for l in text.split("\n") if l.strip()]

    purchase_order = ""
    invoice_no = ""
    order_date = ""
    invoice_date = ""

    total_lines = len(lines)

    for i, line in enumerate(lines):

        # CASE: all labels in one line
        if ("Purchase Order No." in line and
            "Invoice No." in line and
            "Order Date" in line and
            "Invoice Date" in line):

            if i + 1 < total_lines:

                values_line = lines[i+1]

                parts = values_line.split()

                if len(parts) >= 4:

                    purchase_order = parts[0]
                    invoice_no = parts[1]
                    order_date = parts[2]
                    invoice_date = parts[3]

                    return purchase_order, invoice_no, order_date, invoice_date


        # CASE: labels on separate lines (fallback)
        if line == "Purchase Order No." and i+1 < total_lines:
            purchase_order = lines[i+1]

        elif line == "Invoice No." and i+1 < total_lines:
            invoice_no = lines[i+1]

        elif line == "Order Date" and i+1 < total_lines:
            order_date = lines[i+1]

        elif line == "Invoice Date" and i+1 < total_lines:
            invoice_date = lines[i+1]

    return purchase_order, invoice_no, order_date, invoice_date


# -------- COMPANY --------
def extract_company(text):
    match = re.search(r"Sold by\s*:\s*(.*)", text)
    return match.group(1).strip() if match else ""



# -------- ORDER DATE --------
def extract_order_date(text):
    match = re.search(r"Order Date\s*\n([\d\.\/\-]+)", text)
    return match.group(1) if match else ""


# -------- INVOICE DATE --------
def extract_invoice_date(text):
    match = re.search(r"Invoice Date\s*\n([\d\.\/\-]+)", text)
    return match.group(1) if match else ""


# -------- AWB --------
def extract_awb(text):

    # extract number between Return Code and Product Details
    match = re.search(
        r"Return Code\s*\n(?:.*\n)*?(\d{12,20})\nProduct Details",
        text
    )

    if match:
        return match.group(1)

    # fallback: any standalone 12–20 digit number
    match2 = re.search(r"\b(\d{12,20})\b", text)

    return match2.group(1) if match2 else ""


# -------- SKU, QTY, ORDER ID --------
def extract_sku_qty_orderid(text):

    lines = text.split("\n")

    for i, line in enumerate(lines):

        if "SKU Size Qty Color Order No." in line:

            if i + 1 >= len(lines):
                continue

            data_line = lines[i+1].strip()

            # Example:
            # AP 10 LBL HAND WHSAJ Free Size 1 NA 195585332065791872_1

            # ORDER ID (always last pattern number_number)
            order_match = re.search(r'(\d+_\d+)$', data_line)
            order_id = order_match.group(1) if order_match else ""

            # QTY
            qty_match = re.search(r'Free Size\s+(\d+)', data_line)
            qty = qty_match.group(1) if qty_match else ""

            # SKU
            sku_match = re.search(r'^(.*?)\s+Free Size', data_line)
            sku = sku_match.group(1).strip() if sku_match else ""
            
            return sku, qty, order_id

    return "", "", ""


# -------- HSN --------
def extract_hsn(text):
    match = re.search(r"\n(\d{6})\s+1\s+Rs", text)
    return match.group(1) if match else ""


# -------- MAIN FUNCTION --------
def extract_orders(pdf_path):

    orders = []

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            text = page.extract_text()
    
           

            if not text:
                continue

            sku, qty, order_id = extract_sku_qty_orderid(text)
            _, invoice_no, order_date, invoice_date = extract_fields_robust(text)
            gross_amount, discount, taxable_amount, total_other_charges = extract_amounts(text)

            print("Extracted Fields:", invoice_no, order_date, invoice_date)

            order = {

                "customer_name": extract_customer_name(text),

                "courier_partner": extract_courier(text),

                "company_name": extract_company(text),

                "tax_invoice_no": invoice_no,

                "order_date": order_date,

                "invoice_date": invoice_date,

                "awb_number": extract_awb(text),

                "order_id": order_id,

                "sku_id": sku,

                "qty": qty,

                "hsn": extract_hsn(text),
                "gross_amount": gross_amount,
                 "discount": discount,
                   "taxable_amount": taxable_amount,
                     "total_other_charges": total_other_charges
}

            

            orders.append(order)

    return orders