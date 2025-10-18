# Inventory-Management

A simple, beginner-friendly Inventory Management web app built with Python and Flask that stores data in an Excel workbook. This project demonstrates basic CRUD (Create, Read, Update, Delete) operations for products, customers, vendors, purchases, sales, and inventory using familiar tools like Flask, pandas and openpyxl.

## What this project uses
- Framework: Flask (simple Python web framework)
- Data handling: pandas (read/write Excel sheets as DataFrames)
- Excel engine: openpyxl (read/write Excel (.xlsx) files)
- Storage: a local Excel file located at `data/inventory_data.xlsx`
- Templates: Jinja2 HTML templates in the `templates/` folder for UI

This setup intentionally avoids a SQL database to keep the project approachable for beginners who may not have a database server available.

## Main features / Functionality
- Add and view customers
- Add and view products
- Add and view vendors
- Record purchases (updates inventory quantities)
- Record sales (checks and updates inventory quantities)
- Edit and delete rows from any sheet (customers, products, vendors, purchases, sales, inventory)
- View all sheets and inspect row-level data

## High-level how it works (for beginners)

1. The app is a Flask web server (`app.py`) that responds to browser requests and renders HTML pages.
2. Data is stored in an Excel workbook with multiple sheets: `customers`, `products`, `vendors`, `purchases`, `sales`, and `inventory`.
3. When the app starts, it ensures the Excel file exists and creates any missing sheets with header rows (`initialize_excel_file`).
4. When you add a product, customer, or vendor, the server reads the corresponding sheet into a pandas DataFrame, appends the new row, and writes the sheet back to the Excel file.
5. Purchases and sales are recorded in their respective sheets. Adding a purchase increases inventory (or creates a new inventory row). Adding a sale checks that enough stock exists and then reduces the inventory.
6. Editing or deleting a purchase/sale will also attempt to adjust inventory accordingly so quantities stay consistent.

## File overview
- `app.py` - main Flask application with all routes and logic.
- `data/` - folder that holds the Excel workbook (`inventory_data.xlsx`). The file is created automatically when you run the app the first time.
- `templates/` - HTML templates used by Flask to render pages (for example `add_product.html`, `add_sales.html`, `view_sheet.html`, etc.).

## Getting started (Windows)

Prerequisites:
- Python 3.8+ installed and available on your PATH
- A terminal (PowerShell is used in examples below)

1. (Optional) Create a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Run the app:

```powershell
python app.py
```

4. Open a browser and go to:

http://127.0.0.1:5000/

You should see the home page and be able to navigate to add customers, products, purchases, sales, and view sheets.

## Notes and tips
- The Excel file is stored at `data/inventory_data.xlsx`. Back it up if you need to preserve data.
- This app uses Excel as a lightweight database; it works well for small projects but is not suitable for high-concurrency production use. For a production app, consider switching to a proper database like SQLite, PostgreSQL, or MySQL.
- Many operations are done by reading/writing entire sheets. That is simple but can be slow for very large datasets.
- The app uses `flash()` messages to show success or error messages (these appear on the rendered pages). The `app.secret_key` is set in `app.py` — for production, use a secure secret and keep it out of source control.

## Possible next steps / improvements
- Add a requirements-locked file (e.g., `pip freeze > requirements.txt`) to pin versions.
- Replace Excel storage with SQLite or another database and use SQLAlchemy for ORM.
- Add user authentication to protect access to the inventory.
- Add automated tests for the Flask routes and data logic.

## Troubleshooting
- If you get errors reading the Excel file, delete `data/inventory_data.xlsx` and restart the app — it will recreate the file.
- If a page shows a Python error in the browser, check the terminal where the Flask server is running for the traceback.
