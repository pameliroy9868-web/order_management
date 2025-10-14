# Order Management System

This Streamlit app extracts order details from PDFs and saves them to a PostgreSQL database.

## Requirements
- Python 3.9+
- PostgreSQL 12+
- Streamlit
- pdfplumber
- psycopg2
- pandas

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/order_management.git
cd order_management
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create PostgreSQL database and tables using SQL scripts inside `db_scripts` folder.

4. Update database connection details in `db/db.py` (host, user, password, port).

5. Run the Streamlit app:
```bash
streamlit run app.py
```

6. Upload PDF and save extracted orders to the database.