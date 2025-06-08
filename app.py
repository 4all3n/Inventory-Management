from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import pandas as pd
import os
from datetime import datetime
from openpyxl import load_workbook
import openpyxl

app = Flask(__name__)
app.secret_key = 'your_secret_key'

EXCEL_FILE = "data/inventory_data.xlsx"

def initialize_excel_file(filepath):
    required_sheets = {
        "inventory": ['HSN_Code', 'Product_Name', 'Units', 'Cost', 'Selling_Price','Total_cost'],
        "products": ['HSN_Code', 'Product_Name', 'Cost', 'Selling_Price'],
        "customers": ['Customer_ID', 'Name', 'Email', 'Address'],
        "vendors": ['HSN_Code', 'Vendor_Name', 'Product_Name', 'Phone', 'Email', 'Address'],
        "purchases": ['HSN_Code', 'Product_Name', 'Vendor', 'Date', 'Units', 'Cost_per_Unit', 'Total_Cost'],
        "sales": ['HSN_Code', 'Product_Name', 'Customer', 'Date', 'Units', 'Selling_Price_per_Unit', 'Total_Amount'],
    }

    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if not os.path.exists(filepath):
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet, headers in required_sheets.items():
                df = pd.DataFrame(columns=headers)
                df.to_excel(writer, sheet_name=sheet, index=False)
        print("✅ Excel file and sheets created.")
    else:
        workbook = load_workbook(filepath)
        existing_sheets = workbook.sheetnames
        with pd.ExcelWriter(filepath, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
            for sheet, headers in required_sheets.items():
                if sheet not in existing_sheets:
                    df = pd.DataFrame(columns=headers)
                    df.to_excel(writer, sheet_name=sheet, index=False)
                    print(f"✅ Sheet '{sheet}' created.")

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add_customer', methods=['GET', 'POST'])
def add_customer_route():
    if request.method == 'POST':
        cust_id = request.form['cust_id']
        name = request.form['name']
        email = request.form['email']
        address = request.form['address']

        try:
            df_customer = pd.read_excel(EXCEL_FILE, sheet_name='customers')
        except ValueError:
            df_customer = pd.DataFrame(columns=['Customer_ID', 'Name', 'Email', 'Address'])

        if cust_id in df_customer['Customer_ID'].astype(str).values:
            flash("Customer ID already exists. Please use a different ID.")
            return redirect(url_for('add_customer_route'))

        new_customer = {
            'Customer_ID': cust_id,
            'Name': name,
            'Email': email,
            'Address': address
        }

        df_customer = pd.concat([df_customer, pd.DataFrame([new_customer])], ignore_index=True)

        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_customer.to_excel(writer, sheet_name='customers', index=False)

        flash("Customer added successfully!")
        return redirect(url_for('add_customer_route'))

    return render_template('add_customer.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product_route():
    if request.method == 'POST':
        hsn_code = request.form.get('hsn_code').strip()
        product_name = request.form.get('product_name').strip()
        cost = request.form.get('cost').strip()
        selling_price = request.form.get('selling_price').strip()

        if not hsn_code or not product_name or not cost or not selling_price:
            flash("All fields are required.", "danger")
            return redirect(url_for('add_product_route'))

        try:
            cost = float(cost)
            selling_price = float(selling_price)

            xls = pd.ExcelFile(EXCEL_FILE)

            df_products = pd.read_excel(xls, sheet_name='products')
            new_product = pd.DataFrame([{
                'HSN_Code': hsn_code,
                'Product_Name': product_name,
                'Cost': cost,
                'Selling_Price': selling_price
            }])
            df_products = pd.concat([df_products, new_product], ignore_index=True)

            df_inventory = pd.read_excel(xls, sheet_name='inventory')
            new_inventory = pd.DataFrame([{
                'HSN_Code': hsn_code,
                'Product_Name': product_name,
                'Units': 0,
                'Cost': cost,
                'Selling_Price': selling_price,
                'Total_cost': 0
            }])
            df_inventory = pd.concat([df_inventory, new_inventory], ignore_index=True)

            with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_products.to_excel(writer, sheet_name='products', index=False)
                df_inventory.to_excel(writer, sheet_name='inventory', index=False)

            flash("✅ Product added successfully!", "success")
            return redirect(url_for('add_product_route'))

        except Exception as e:
            print("Error:", e)
            flash("❌ Failed to add product. Please try again.", "danger")
            return redirect(url_for('add_product_route'))

    return render_template('add_product.html')

@app.route('/add_vendor', methods=['GET', 'POST'])
def add_vendor_route():
    df_product = pd.read_excel(EXCEL_FILE, sheet_name='products')
    product_dict = df_product.set_index('HSN_Code')['Product_Name'].to_dict()

    if request.method == 'POST':
        hsn_code = request.form['hsn_code']
        vendor_name = request.form['vendor_name']
        product_name = request.form['product_name']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']

        df_vendor = pd.read_excel(EXCEL_FILE, sheet_name='vendors')
        new_row = {
            'HSN_Code': hsn_code,
            'Vendor_Name': vendor_name,
            'Product_Name': product_name,
            'Phone': phone,
            'Email': email,
            'Address': address
        }
        df_vendor = pd.concat([df_vendor, pd.DataFrame([new_row])], ignore_index=True)

        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df_vendor.to_excel(writer, sheet_name='vendors', index=False)

        flash("Vendor added successfully!")
        return redirect(url_for('add_vendor_route'))

    return render_template('add_vendor.html', product_dict=product_dict)

@app.route('/add_purchase', methods=['GET', 'POST'])
def add_purchase():
    vendor_df = pd.read_excel(EXCEL_FILE, sheet_name="vendors")

    hsn_codes = sorted(vendor_df['HSN_Code'].dropna().unique())
    product_names = sorted(vendor_df['Product_Name'].dropna().unique())
    vendors = sorted(vendor_df['Vendor_Name'].dropna().unique())

     # Load inventory sheet
    try:
        inventory_df = pd.read_excel(EXCEL_FILE, sheet_name="inventory")
    except:
        inventory_df = pd.DataFrame(columns=[
        'HSN_Code', 'Product_Name', 'Units', 'Cost', 'Selling_Price', 'Total_cost'
    ])

    hsn_to_product = dict(zip(vendor_df['HSN_Code'].astype(str), vendor_df['Product_Name']))
    hsn_to_selling_price = dict(zip(inventory_df['HSN_Code'].astype(str), inventory_df['Selling_Price'].fillna(0).astype(float)))

   

    if request.method == 'POST':
        hsn_code = request.form['hsn_code']
        product_name = request.form['product_name']
        vendor = request.form['vendor']
        date = request.form['date']
        units = int(request.form['units'])
        cost_per_unit = float(request.form['cost_per_unit'])
        total_cost = units * cost_per_unit
        
        

        try:
            purchase_df = pd.read_excel(EXCEL_FILE, sheet_name="purchases")
        except:
            purchase_df = pd.DataFrame(columns=[
                'HSN_Code', 'Product_Name', 'Vendor', 'Date',
                'Units', 'Cost_per_Unit', 'Total_Cost'
            ])

        new_row = pd.DataFrame([{
            'HSN_Code': hsn_code,
            'Product_Name': product_name,
            'Vendor': vendor,
            'Date': date,
            'Units': units,
            'Cost_per_Unit': cost_per_unit,
            'Total_Cost': total_cost
        }])
        purchase_df = pd.concat([purchase_df, new_row], ignore_index=True)

        try:
            inventory_df = pd.read_excel(EXCEL_FILE, sheet_name="inventory")
        except:
            inventory_df = pd.DataFrame(columns=[
                'HSN_Code', 'Product_Name', 'Units', 'Cost', 'Selling_Price', 'Total_cost'
            ])

                # Clean values for safer comparison
        hsn_code = str(hsn_code).strip()
        product_name = str(product_name).strip()

        inventory_df['HSN_Code'] = inventory_df['HSN_Code'].astype(str).str.strip()
        inventory_df['Product_Name'] = inventory_df['Product_Name'].astype(str).str.strip()

        match = (
            (inventory_df['HSN_Code'] == hsn_code) &
            (inventory_df['Product_Name'] == product_name)
        )

        if match.any():
            # Update existing inventory entry
            inventory_df.loc[match, 'Units'] = (
                inventory_df.loc[match, 'Units'].astype(float) + units
            )
            inventory_df.loc[match, 'Cost'] = cost_per_unit
            inventory_df.loc[match, 'Total_cost'] = (
                inventory_df.loc[match, 'Units'].astype(float) * cost_per_unit
            )
        else:
            # Add new entry
            new_inv = pd.DataFrame([{
                'HSN_Code': hsn_code,
                'Product_Name': product_name,
                'Units': units,
                'Cost': cost_per_unit,
                'Selling_Price': 0,  # default
                'Total_cost': units * cost_per_unit
            }])
            inventory_df = pd.concat([inventory_df, new_inv], ignore_index=True)


        if match.any():
            inventory_df.loc[match, 'Units'] += units
            # Optionally update cost and total cost
            inventory_df.loc[match, 'Cost'] = cost_per_unit
            inventory_df.loc[match, 'Total_cost'] = inventory_df.loc[match, 'Units'] * cost_per_unit
        else:
            new_inv = pd.DataFrame([{
                'HSN_Code': hsn_code,
                'Product_Name': product_name,
                'Units': units,
                'Cost': cost_per_unit,
                'Selling_Price': 0,  # Default, update later if needed
                'Total_cost': units * cost_per_unit
            }])
            inventory_df = pd.concat([inventory_df, new_inv], ignore_index=True)

        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            purchase_df.to_excel(writer, sheet_name="purchases", index=False)
            inventory_df.to_excel(writer, sheet_name="inventory", index=False)

        flash("✅ Purchase added and inventory updated successfully!")
        return redirect('/add_purchase')

    return render_template("add_purchase.html",
                           hsn_codes=hsn_codes,
                           product_names=product_names,
                           vendors=vendors,
                           hsn_to_product=hsn_to_product,
                           hsn_to_selling_price=hsn_to_selling_price)



@app.route('/add_sales', methods=['GET', 'POST'])
def add_sales():
    wb = openpyxl.load_workbook(EXCEL_FILE)
    inventory_sheet = wb['inventory']
    sales_sheet = wb['sales']
    customer_sheet = wb['customers']

    # ---- Prepare dropdown mappings ----
    hsn_to_product = {}
    product_to_hsn = {}
    selling_prices = {}
    stocks = {}

    for row in inventory_sheet.iter_rows(min_row=2, values_only=True):
        hsn, product, stock, _, selling_price, _ = row
        if hsn is None or product is None:
            continue
        hsn = str(hsn)
        hsn_to_product[hsn] = product
        product_to_hsn[product] = hsn
        selling_prices[hsn] = selling_price
        stocks[hsn] = stock

    customers = []
    for row in customer_sheet.iter_rows(min_row=2, values_only=True):
        cust_id, name = row[:2]
        if cust_id and name:
            customers.append(f"{cust_id} - {name}")

    # ---- Handle Form POST ----
    if request.method == 'POST':
        hsn_code = request.form['hsn_code']
        product_name = request.form['product_name']
        customer = request.form['customer']
        date = request.form['date']
        units = int(request.form['units'])
        selling_price = float(request.form['selling_price'])
        total_cost = units * selling_price

        available_stock = stocks.get(hsn_code, 0)

        if units > available_stock:
            flash(f"❌ Not enough stock available. Only {available_stock} units left.", 'error')
            return redirect('/add_sales')

        # ✅ Add entry to Sales sheet (using pandas)
        try:
            sales_df = pd.read_excel(EXCEL_FILE, sheet_name="sales")
        except:
            sales_df = pd.DataFrame(columns=[
                'HSN_Code', 'Product_Name', 'Customer', 'Date',
                'Units', 'Selling_Price_per_Unit', 'Total_Amount'
            ])

        new_row = pd.DataFrame([{
            'HSN_Code': hsn_code,
            'Product_Name': product_name,
            'Customer': customer,
            'Date': date,
            'Units': units,
            'Selling_Price_per_Unit': selling_price,
            'Total_Amount': total_cost
        }])
        sales_df = pd.concat([sales_df, new_row], ignore_index=True)

        # ✅ Update inventory stock using openpyxl
        for row in inventory_sheet.iter_rows(min_row=2):
            cell_hsn = str(row[0].value)
            if cell_hsn == hsn_code:
                row[2].value = row[2].value - units  # Subtract sold units
                break

        # Save both sheets
        wb.save(EXCEL_FILE)
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            sales_df.to_excel(writer, sheet_name="sales", index=False)

        flash("✅ Sale added successfully!")
        return redirect('/add_sales')

    # Render sales form
    return render_template(
        'add_sales.html',
        hsn_to_product=hsn_to_product,
        product_to_hsn=product_to_hsn,
        selling_prices=selling_prices,
        stocks=stocks,
        customers=customers
    )



# Route for viewing all sheets
@app.route('/sheets')
def view_all_sheets():
    sheets = ['customers', 'products', 'vendors', 'purchases', 'sales', 'inventory']
    return render_template('view_all_sheets.html', sheets=sheets)

# Route for viewing individual sheet data
@app.route('/sheets/<sheet_name>')
def view_sheet(sheet_name): 

    try:
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)
        headers = df.columns.tolist()
        rows = df.values.tolist()
    except Exception as e:
        return f"Error loading sheet '{sheet_name}': {e}", 500

    return render_template('view_sheet.html', sheet_name=sheet_name, headers=headers, rows=rows)

@app.route('/sheets/<sheet_name>/edit/<int:row_index>', methods=['GET', 'POST'])
def edit_row(sheet_name, row_index):
    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet_name)

    if row_index < 1 or row_index > len(df)+1:
        return f"Invalid row index: {row_index}", 404

    if request.method == 'POST':
        for header in df.columns:
            df.at[row_index - 2, header] = request.form.get(header)
        df.to_excel(EXCEL_FILE, sheet_name=sheet_name, index=False)
        return redirect(url_for('view_sheet', sheet_name=sheet_name))

    headers = df.columns.tolist()
    row_data = df.iloc[row_index - 2].tolist()
    zipped = list(zip(headers, row_data))

    return render_template('edit_row.html', sheet_name=sheet_name, zipped=zipped)

@app.route('/sheets/<sheet_name>/delete/<int:row_index>', methods=['GET'])
def delete_row(sheet_name, row_index):
    excel_path = "data/inventory_data.xlsx"  # Replace with your actual path
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    if row_index - 1 >= len(df) or row_index - 1 < 0:
        flash('Invalid row index!', 'danger')
        return redirect(url_for('view_sheet', sheet_name=sheet_name))

    df = df.drop(df.index[row_index - 1]).reset_index(drop=True)

    with pd.ExcelWriter(excel_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    flash('Row deleted successfully!', 'success')
    return redirect(url_for('view_sheet', sheet_name=sheet_name))


if __name__ == '__main__':
    initialize_excel_file(EXCEL_FILE)
    app.run(debug=True)
