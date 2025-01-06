import tkinter as tk
from tkinter import ttk
import mysql.connector
from datetime import datetime

class MySQLApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MySQL Database Interface")
        
        # Initialize frames for different pages
        self.login_frame = tk.Frame(root)
        self.project_frame = tk.Frame(root)
        self.order_frame = tk.Frame(root)
        
        # Initialize tables
        self.project_tree = None
        self.order_tree = None
        
        # Show the login page initially
        self.show_login_page()

    def connect_db(self):
        # Function to connect to the MySQL database
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                port=,  # Use your own port
                user="root",  # Use your own username
                password="",  # Use your own password
                database="my_database"
            )
            self.cursor = self.conn.cursor(dictionary=True)
        except mysql.connector.Error as err:
            print(f"Error: {err}")
            self.conn = None
            self.cursor = None

    def show_login_page(self):
        self.clear_frames()
        self.login_frame.pack(fill="both", expand=True)

        # Existing Customer Login
        tk.Label(self.login_frame, text="Login (Existing Customer):", font=("Helvetica", 14)).pack(pady=10)

        tk.Label(self.login_frame, text="Email:").pack(pady=5)
        self.email_entry = tk.Entry(self.login_frame)
        self.email_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Customer ID:").pack(pady=5)
        self.customer_id_entry = tk.Entry(self.login_frame)
        self.customer_id_entry.pack(pady=5)

        submit_button = tk.Button(self.login_frame, text="Login", command=self.login)
        submit_button.pack(pady=10)

        # Divider
        ttk.Separator(self.login_frame, orient="horizontal").pack(fill="x", pady=20)

        # New Customer Registration
        tk.Label(self.login_frame, text="Register (New Customer):", font=("Helvetica", 14)).pack(pady=10)

        tk.Label(self.login_frame, text="Name:").pack(pady=5)
        self.new_name_entry = tk.Entry(self.login_frame)
        self.new_name_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Email:").pack(pady=5)
        self.new_email_entry = tk.Entry(self.login_frame)
        self.new_email_entry.pack(pady=5)

        tk.Label(self.login_frame, text="Phone Number:").pack(pady=5)
        self.new_phone_entry = tk.Entry(self.login_frame)
        self.new_phone_entry.pack(pady=5)

        register_button = tk.Button(self.login_frame, text="Register", command=self.register_new_customer)
        register_button.pack(pady=10)

    def register_new_customer(self):
        try:
            # Ensure database connection is established
            if not hasattr(self, 'conn') or not self.conn:
                self.connect_db()
            if not self.conn or not self.cursor:
                print("Failed to connect to the database.")
                return

            # Fetch inputs
            customer_name = self.new_name_entry.get().strip()
            email = self.new_email_entry.get().strip()
            phone_number = self.new_phone_entry.get().strip()

            # Validate inputs
            if not customer_name or not email or not phone_number:
                print("All fields are required.")
                return

            # Generate a new customer ID
            self.cursor.execute("SELECT MAX(customerID) AS max_id FROM Customer")
            max_id_result = self.cursor.fetchone()
            new_customer_id = (max_id_result['max_id'] or 0) + 1

            # Insert new customer
            self.cursor.execute(
                "INSERT INTO Customer (customerID, customerName, email, phoneNumber) VALUES (%s, %s, %s, %s)",
                (new_customer_id, customer_name, email, phone_number)
            )
            self.conn.commit()

            print(f"New customer registered successfully with ID {new_customer_id}!")
        except mysql.connector.Error as err:
            print(f"Database Error: {err}")

    def login(self):
        email = self.email_entry.get()
        customer_id = self.customer_id_entry.get()
        
        self.connect_db()
        if not self.conn:
            print("Failed to connect to the database.")
            return

        if email == "admin" and customer_id == "admin":
            self.admin = True
            self.show_project_page(admin=True)
        else:
            query = "SELECT * FROM Customer WHERE email = %s AND customerID = %s"
            self.cursor.execute(query, (email, customer_id))
            customer = self.cursor.fetchone()
            if customer:
                self.customer_id = customer_id
                self.admin = False
                self.show_project_page(admin=False)
            else:
                print("Invalid login credentials.")

    def show_project_page(self, admin=False):
        self.clear_frames()
        self.project_frame.pack(fill="both", expand=True)

        # Project page title
        if hasattr(self, 'project_title_label'):
            self.project_title_label.destroy()
        self.project_title_label = tk.Label(self.project_frame, text="Projects", font=("Helvetica", 16))
        self.project_title_label.pack(pady=10, anchor="w")

        # Scrollable table
        if self.project_tree:
            self.project_tree.destroy()
        self.project_tree = ttk.Treeview(
            self.project_frame, 
            columns=("Project ID", "Company", "Budget", "Deadline", "Project Status", "Project Name", "Customer ID", "Country", "City", "Postal Code", "Province/State", "Street Name"), 
            show="headings"
        )
        
        for col in self.project_tree["columns"]:
            self.project_tree.heading(
                col, text=col, 
                command=lambda c=col: self.sort_treeview(self.project_tree, c, False)
            )
        self.project_tree.pack(pady=10, fill="both", expand=True)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.project_frame, orient="vertical", command=self.project_tree.yview)
        self.project_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # Bind double-click event to open orders page
        self.project_tree.bind("<Double-1>", self.on_project_double_click)

        # New Project button
        if hasattr(self, 'new_project_button'):
            self.new_project_button.destroy()
        self.new_project_button = tk.Button(self.project_frame, text="New Project", command=self.new_project_ui)
        self.new_project_button.pack(pady=10)

        # Finish Project button
        if hasattr(self, 'finish_project_button'):
            self.finish_project_button.destroy()
        self.finish_project_button = tk.Button(self.project_frame, text="Finish Project", command=self.finish_project_ui)
        self.finish_project_button.pack(pady=10)

        # Delete Project button
        if hasattr(self, 'delete_button'):
            self.delete_button.destroy()
        self.delete_button = tk.Button(self.project_frame, text="Delete Project", command=self.delete_project_ui)
        self.delete_button.pack(pady=10)

        # Load project data
        self.load_projects(admin)

    def delete_project_ui(self):
        selected_item = self.project_tree.selection()
        if not selected_item:
            print("Please select a project to delete.")
            return

        project_id = self.project_tree.item(selected_item, "values")[0]
        project_status = self.project_tree.item(selected_item, "values")[4]  # Assuming 5th column is projectStatus

        if project_status not in ("Completed", "Cancelled"):
            print("Only projects with status 'Completed' or 'Cancelled' can be deleted.")
            return

        # Confirm deletion
        confirm_window = tk.Toplevel(self.root)
        confirm_window.title("Confirm Deletion")

        tk.Label(confirm_window, text=f"Are you sure you want to delete Project ID {project_id}?").pack(pady=10)

        def confirm_delete():
            try:
                self.cursor.execute("DELETE FROM Projects WHERE projectID = %s", (project_id,))
                self.conn.commit()
                print(f"Project {project_id} deleted successfully!")
                self.load_projects(admin=self.admin)
                confirm_window.destroy()
            except mysql.connector.Error as err:
                print(f"Error: {err}")

        tk.Button(confirm_window, text="Yes, Delete", command=confirm_delete).pack(side="left", padx=10, pady=10)
        tk.Button(confirm_window, text="No, Cancel", command=confirm_window.destroy).pack(side="right", padx=10, pady=10)

    def new_project_ui(self):
        project_window = tk.Toplevel(self.root)
        project_window.title("New Project")

        tk.Label(project_window, text="Enter Company Name:").pack(pady=5)
        company_name_entry = tk.Entry(project_window)
        company_name_entry.pack(pady=5)

        tk.Label(project_window, text="Enter Budget:").pack(pady=5)
        budget_entry = tk.Entry(project_window)
        budget_entry.pack(pady=5)

        tk.Label(project_window, text="Enter Deadline (YYYY-MM-DD HH:MM:SS):").pack(pady=5)
        deadline_entry = tk.Entry(project_window)
        deadline_entry.pack(pady=5)

        tk.Label(project_window, text="Enter Project Name:").pack(pady=5)
        project_name_entry = tk.Entry(project_window)
        project_name_entry.pack(pady=5)

        tk.Label(project_window, text="Enter Customer ID:").pack(pady=5)
        customer_id_entry = tk.Entry(project_window)
        customer_id_entry.pack(pady=5)

        def submit_project():
            try:
                company_name = company_name_entry.get()
                budget = float(budget_entry.get())
                deadline = deadline_entry.get()
                project_name = project_name_entry.get()
                customer_id = int(customer_id_entry.get())
                
                self.cursor.execute(
                    "INSERT INTO Projects (company, budget, deadline, projectStatus, projectName, customerID) VALUES (%s, %s, %s, %s, %s, %s)",
                    (company_name, budget, deadline, 'In Progress', project_name, customer_id)
                )
                self.conn.commit()
                print("New project created successfully!")
                project_window.destroy()
                self.load_projects(admin=self.admin)
            except mysql.connector.Error as err:
                print(f"Error: {err}")
            except ValueError:
                print("Invalid input. Please try again.")

        tk.Button(project_window, text="Submit", command=submit_project).pack(pady=10)

    def finish_project_ui(self):
        selected_item = self.project_tree.selection()
        if selected_item:
            project_id = self.project_tree.item(selected_item, 'values')[0]
            confirm_finish_window = tk.Toplevel(self.root)
            confirm_finish_window.title("Confirm Finish Project")

            tk.Label(confirm_finish_window, text=f"Are you sure you want to mark Project ID {project_id} as completed?").pack(pady=10)

            def confirm_finish():
                try:
                    # Update the projectStatus in the Projects table
                    self.cursor.execute("UPDATE Projects SET projectStatus = 'Completed' WHERE projectID = %s", (project_id,))
                    self.conn.commit()
                    tk.Label(confirm_finish_window, text="Project marked as completed successfully.", justify="left").pack(pady=10)
                    print(f"Project ID {project_id} has been successfully marked as completed.")
                    self.load_projects(admin=self.admin)
                except mysql.connector.Error as err:
                    print(f"Error: {err}")

            tk.Button(confirm_finish_window, text="Yes, Finish Project", command=confirm_finish).pack(pady=5)
            tk.Button(confirm_finish_window, text="No, Go Back", command=confirm_finish_window.destroy).pack(pady=5)

    def on_project_double_click(self, event):
        selected_item = self.project_tree.selection()
        if selected_item:
            project_id = self.project_tree.item(selected_item, 'values')[0]
            self.show_order_page(project_id)

    def show_order_page(self, project_id=None):
        self.clear_frames()
        self.order_frame.pack(fill="both", expand=True)

        # Orders page title
        if not hasattr(self, 'order_title_label'):
            self.order_title_label = tk.Label(self.order_frame, text="Orders", font=("Helvetica", 16))
        self.order_title_label.pack(pady=10)

        # Scrollable table for orders
        if self.order_tree is None:
            self.order_tree = ttk.Treeview(
                self.order_frame, 
                columns=("Order ID", "Order Date", "Cost", "Customer ID", "Shipment ID", "Product ID", "Project ID", "Shipment Date", "Shipment Status", "Courier"), 
                show="headings"
            )
            for col in self.order_tree["columns"]:
                self.order_tree.heading(col, text=col, command=lambda c=col: self.sort_treeview(self.order_tree, c, False))
            self.order_tree.pack(pady=10, fill="both", expand=True)

            # Add scrollbar
            scrollbar = ttk.Scrollbar(self.order_frame, orient="vertical", command=self.order_tree.yview)
            self.order_tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side="right", fill="y")

        # Add buttons (back, create, cancel, track, generate receipt)
        if not hasattr(self, 'back_button'):
            self.back_button = tk.Button(self.order_frame, text="Back", command=lambda: self.show_project_page(admin=self.admin))
        self.back_button.pack(pady=10)

        if not hasattr(self, 'create_order_button'):
            self.create_order_button = tk.Button(self.order_frame, text="Create Order", command=self.create_order_ui)
        self.create_order_button.pack(pady=10)

        if not hasattr(self, 'cancel_order_button'):
            self.cancel_order_button = tk.Button(self.order_frame, text="Cancel Order", command=self.cancel_order_ui)
        self.cancel_order_button.pack(pady=10)

        if not hasattr(self, 'track_order_button'):
            self.track_order_button = tk.Button(self.order_frame, text="Track Order", command=self.track_order_ui)
        self.track_order_button.pack(pady=10)

        if not hasattr(self, 'generate_receipt_button'):
            self.generate_receipt_button = tk.Button(self.order_frame, text="Generate Receipt", command=self.generate_order_receipt)
        self.generate_receipt_button.pack(pady=10)

        # Load orders for the selected project
        if project_id:
            self.load_orders(project_id)

    def sort_treeview(self, treeview, col, reverse):
       
        # Get all data from the Treeview
        data = [(treeview.set(k, col), k) for k in treeview.get_children('')]

        # Sort data based on type (numeric or string)
        try:
            data.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            data.sort(key=lambda t: t[0], reverse=reverse)

        # Rearrange items in sorted order
        for index, (val, k) in enumerate(data):
            treeview.move(k, '', index)

        # Reverse the sorting order for the next click
        treeview.heading(col, command=lambda: self.sort_treeview(treeview, col, not reverse))
        
    def generate_order_receipt(self):
        # Create a new window for generating an order receipt
        receipt_window = tk.Toplevel(self.root)
        receipt_window.title("Generate Order Receipt")
        
        tk.Label(receipt_window, text="Enter Order ID:").pack(pady=5)
        order_id_entry = tk.Entry(receipt_window)
        order_id_entry.pack(pady=5)
        
        def submit_receipt():
            try:
                order_id = int(order_id_entry.get())
                query = """
                SELECT DISTINCT
                    o.orderID AS "Order ID",
                    c.customerName AS "Customer Name",
                    c.email AS "Email",
                    c.phoneNumber AS "Phone Number",
                    o.orderDate AS "Order Date",
                    p.productName AS "Product Name",
                    od.quantity AS "Quantity",
                    od.unitPrice AS "Unit Price",
                    (od.quantity * od.unitPrice) AS "Total Price",
                    o.cost AS "Order Total",
                    s.courier AS "Shipping Courier",
                    s.shipmentDate AS "Shipping Date",
                    s.shipmentStatus AS "Shipment Status"
                FROM Orders o
                LEFT JOIN Customer c ON o.customerID = c.customerID
                LEFT JOIN OrderDetails od ON o.orderID = od.orderID
                LEFT JOIN Product p ON od.productID = p.productID
                LEFT JOIN Shipment s ON o.shipmentID = s.shipmentID
                WHERE o.orderID = %s
                """
                self.cursor.execute(query, (order_id,))
                receipt = self.cursor.fetchall()
                
                # Display the receipt details
                receipt_text = "\n".join([f"{key}: {value}" for key, value in receipt[0].items()]) if receipt else "No order found."
                tk.Label(receipt_window, text=receipt_text, justify="left").pack(pady=10)
            except mysql.connector.Error as err:
                print(f"Error: {err}")
            except ValueError:
                print("Invalid input. Please try again.")

        tk.Button(receipt_window, text="Generate Receipt", command=submit_receipt).pack(pady=10)

    def create_order_ui(self):
        order_window = tk.Toplevel(self.root)
        order_window.title("Create Order")

        

        # Product ID
        tk.Label(order_window, text="Enter Product ID:").pack(pady=5)
        product_id_entry = tk.Entry(order_window)
        product_id_entry.pack(pady=5)

        # Quantity
        tk.Label(order_window, text="Enter Quantity:").pack(pady=5)
        quantity_entry = tk.Entry(order_window)
        quantity_entry.pack(pady=5)

        # Unit Price
        tk.Label(order_window, text="Enter Unit Price:").pack(pady=5)
        unit_price_entry = tk.Entry(order_window)
        unit_price_entry.pack(pady=5)

        def submit_order():
            try:
                # Fetch inputs
                product_id = int(product_id_entry.get())
                quantity = int(quantity_entry.get())
                unit_price = float(unit_price_entry.get())

                # Calculate total cost
                total_cost = quantity * unit_price
                order_date = datetime.now()

                # Determine customer ID
                customer_id = 0 if self.admin else int(self.customer_id)

                # Generate a new shipment ID
                self.cursor.execute(
                    "INSERT INTO Shipment (shipmentStatus, courier) VALUES (%s, %s)",
                    ("Pending", "Unknown")  # Default values; adjust if necessary
                )
                shipment_id = self.cursor.lastrowid

                # Fetch the project ID associated with the logged-in customer
                self.cursor.execute(
                    "SELECT projectID FROM Projects WHERE customerID = %s LIMIT 1", (customer_id,)
                )
                project = self.cursor.fetchone()
                if not project:
                    raise ValueError("No project found for the current customer.")
                project_id = project['projectID']

                # Insert into Orders table
                self.cursor.execute(
                    "INSERT INTO Orders (orderDate, cost, customerID, shipmentID, productID, projectID) VALUES (%s, %s, %s, %s, %s, %s)",
                    (order_date, total_cost, customer_id, shipment_id, product_id, project_id)
                )
                order_id = self.cursor.lastrowid

                # Insert into OrderDetails table
                self.cursor.execute(
                    "INSERT INTO OrderDetails (orderID, productID, quantity, unitPrice) VALUES (%s, %s, %s, %s)",
                    (order_id, product_id, quantity, unit_price)
                )

                # Commit transaction
                self.conn.commit()
                print(f"Order {order_id} created successfully with Shipment ID {shipment_id}!")
                order_window.destroy()
            except mysql.connector.Error as err:
                print(f"Database Error: {err}")
            except ValueError as ve:
                print(f"Error: {ve}")

        # Submit button
        tk.Button(order_window, text="Submit Order", command=submit_order).pack(pady=10)

    def cancel_order_ui(self):
        selected_item = self.order_tree.selection()
        if selected_item:
            order_id = self.order_tree.item(selected_item, 'values')[0]
            confirm_cancel_window = tk.Toplevel(self.root)
            confirm_cancel_window.title("Confirm Cancellation")

            tk.Label(confirm_cancel_window, text=f"Are you sure you want to cancel Order ID {order_id}?").pack(pady=10)

            def confirm_cancel():
                try:
                    self.cursor.execute("SELECT shipmentID FROM Orders WHERE orderID = %s", (order_id,))
                    result = self.cursor.fetchone()

                    if result:
                        shipment_id = result['shipmentID']
                        
                        # Update the shipmentStatus in the Shipment table
                        self.cursor.execute("UPDATE Shipment SET shipmentStatus = 'Cancelled' WHERE shipmentID = %s", (shipment_id,))
                        self.conn.commit()

                        tk.Label(confirm_cancel_window, text="Order cancelled successfully.", justify="left").pack(pady=10)
                        print(f"Order ID {order_id} has been successfully cancelled.")
                    else:
                        tk.Label(confirm_cancel_window, text="Order not found.", justify="left").pack(pady=10)
                except mysql.connector.Error as err:
                    print(f"Error: {err}")

            tk.Button(confirm_cancel_window, text="Yes, Cancel Order", command=confirm_cancel).pack(pady=5)
            tk.Button(confirm_cancel_window, text="No, Go Back", command=confirm_cancel_window.destroy).pack(pady=5)

    def track_order_ui(self):
        selected_item = self.order_tree.selection()
        if selected_item:
            order_id = self.order_tree.item(selected_item, 'values')[0]
            track_window = tk.Toplevel(self.root)
            track_window.title("Track Order")

            def submit_track():
                try:
                    # Fetch order status and shipment details from the database
                    self.cursor.execute(
                        "SELECT s.courier, s.shipmentStatus, s.shipmentDate "
                        "FROM Orders o JOIN Shipment s ON o.shipmentID = s.shipmentID WHERE o.orderID = %s",
                        (order_id,)
                    )
                    result = self.cursor.fetchone()

                    if result:
                        # Display detailed tracking information
                        tk.Label(track_window, text=f"Order ID: {order_id}", font=("Helvetica", 14)).pack(pady=5)
                        tk.Label(track_window, text=f"Courier: {result['courier']}", justify="left").pack(pady=5)
                        tk.Label(track_window, text=f"Shipment Status: {result['shipmentStatus']}", justify="left").pack(pady=5)
                        tk.Label(track_window, text=f"Shipment Date: {result['shipmentDate']}", justify="left").pack(pady=5)
                    else:
                        tk.Label(track_window, text="Order not found.", justify="left").pack(pady=10)
                except mysql.connector.Error as err:
                    print(f"Error: {err}")

            # Trigger tracking details
            submit_track()

            # Close button to exit the tracking window
            tk.Button(track_window, text="Close", command=track_window.destroy).pack(pady=10)

    def load_projects(self, admin):
        if admin:
            query = "SELECT p.*, l.country, l.city, l.postalCode, l.provinceState, l.streetName FROM Projects p LEFT JOIN ProjectLocation l ON p.projectID = l.projectID"
            self.cursor.execute(query)
        else:
            query = "SELECT p.*, l.country, l.city, l.postalCode, l.provinceState, l.streetName FROM Projects p LEFT JOIN ProjectLocation l ON p.projectID = l.projectID WHERE p.customerID = %s"
            self.cursor.execute(query, (self.customer_id,))
        projects = self.cursor.fetchall()

        for row in self.project_tree.get_children():
            self.project_tree.delete(row)

        for project in projects:
            self.project_tree.insert("", "end", values=(
                project['projectID'], project['company'], project['budget'], project['deadline'],
                project['projectStatus'], project['projectName'], project['customerID'],
                project.get('country', ''), project.get('city', ''), project.get('postalCode', ''),
                project.get('provinceState', ''), project.get('streetName', '')
            ))

    def load_orders(self, project_id):
        query = "SELECT o.*, s.shipmentDate, s.shipmentStatus, s.courier FROM Orders o LEFT JOIN Shipment s ON o.shipmentID = s.shipmentID WHERE o.projectID = %s"
        self.cursor.execute(query, (project_id,))
        orders = self.cursor.fetchall()

        for row in self.order_tree.get_children():
            self.order_tree.delete(row)

        for order in orders:
            self.order_tree.insert("", "end", values=(
                order['orderID'], order['orderDate'], order['cost'], order['customerID'], 
                order['shipmentID'], order['productID'], order['ProjectID'],
                order.get('shipmentDate', ''), order.get('shipmentStatus', ''), order.get('courier', '')))

    def clear_frames(self):
        for frame in (self.login_frame, self.project_frame, self.order_frame):
            frame.pack_forget()

if __name__ == "__main__":
    root = tk.Tk()
    app = MySQLApp(root)
    root.geometry("800x600")
    root.mainloop()
