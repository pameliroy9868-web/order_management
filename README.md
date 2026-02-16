# Order Management System

A Streamlit-based application to scan order PDFs, edit extracted data, save it to PostgreSQL, and track order status changes.

---

## Features

- Scan order PDFs and extract order details.
- Edit extracted orders before saving.
- Save orders to PostgreSQL database.
- Search orders by Company Name, Order ID, Courier Partner, or SKU.
- Track order status changes (e.g., Picked Up, Delivered) with full history.
- Change order status and see the sequence flow.

---

## Prerequisites

- Python 3.10+
- PostgreSQL 12+
- Git

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository_url>
cd order_management

# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate

pip install --upgrade pip
pip install -r requirements.txt


CREATE DATABASE orders_db;


streamlit run app.py


if plotly is not installed - 
python -m pip install plotly


