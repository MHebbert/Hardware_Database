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
                port=3306,  # Use your own port
                user="root",  # Use your own username
                password="Dorgelo6!",  # Use your own password
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

        # Email and Customer ID input fields
        tk.Label(self.login_frame, text="Email:").pack(pady=10)
        self.email_entry = tk.Entry(self.login_frame)
        self.email_entry.pack(pady=5)
        
        tk.Label(self.login_frame, text="Customer ID:").pack(pady=10)
        self.customer_id_entry = tk.Entry(self.login_frame)
        self.customer_id_entry.pack(pady=5)
        
        # Submit button
        submit_button = tk.Button(self.login_frame, text="Submit", command=self.login)
        submit_button.pack(pady=20)

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
        self.project_tree = ttk.Treeview(self.project_frame, columns=("Project ID", "Company", "Budget", "Deadline", "Project Status", "Project Name", "Customer ID", "Country", "City", "Postal Code", "Province/State", "Street Name"), show="headings")
        self.project_tree.heading("Project ID", text="Project ID")
        self.project_tree.heading("Company", text="Company")
        self.project_tree.heading("Budget", text="Budget")
        self.project_tree.heading("Deadline", text="Deadline")
        self.project_tree.heading("Project Status", text="Project Status")
        self.project_tree.heading("Project Name", text="Project Name")
        self.project_tree.heading("Customer ID", text="Customer ID")
        self.project_tree.heading("Country", text="Country")
        self.project_tree.heading("City", text="City")
        self.project_tree.heading("Postal Code", text="Postal Code")
        self.project_tree.heading("Province/State", text="Province/State")
        self.project_tree.heading("Street Name", text="Street Name")
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

        # Load project data
        self.load_projects(admin)

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
            self.order_tree = ttk.Treeview(self.order_frame, columns=("Order ID", "Order Date", "Cost", "Customer ID", "Shipment ID", "Product ID", "Project ID", "Shipment Date", "Shipment Status", "Courier"), show="headings")
            self.order_tree.heading("Order ID", text="Order ID")
            self.order_tree.heading("Order Date", text="Order Date")
            self.order_tree.heading("Cost", text="Cost")
            self.order_tree.heading("Customer ID", text="Customer ID")
            self.order_tree.heading("Shipment ID", text="Shipment ID")
            self.order_tree.heading("Product ID", text="Product ID")
            self.order_tree.heading("Project ID", text="Project ID")
            self.order_tree.heading("Shipment Date", text="Shipment Date")
            self.order_tree.heading("Shipment Status", text="Shipment Status")
            self.order_tree.heading("Courier", text="Courier")
            self.order_tree.pack(pady=10, fill="both", expand=True)

            # Add scrollbar
            scrollbar = ttk.Scrollbar(self.order_frame, orient="vertical", command=self.order_tree.yview)
            self.order_tree.configure(yscroll=scrollbar.set)
            scrollbar.pack(side="right", fill="y")

        # Back button
        if not hasattr(self, 'back_button'):
            self.back_button = tk.Button(self.order_frame, text="Back", command=lambda: self.show_project_page(admin=self.admin))
        self.back_button.pack(pady=10)

        # Create Order button
        if not hasattr(self, 'create_order_button'):
            self.create_order_button = tk.Button(self.order_frame, text="Create Order", command=self.create_order_ui)
        self.create_order_button.pack(pady=10)

        # Cancel Order button
        if not hasattr(self, 'cancel_order_button'):
            self.cancel_order_button = tk.Button(self.order_frame, text="Cancel Order", command=self.cancel_order_ui)
        self.cancel_order_button.pack(pady=10)

        # Track Order button
        if not hasattr(self, 'track_order_button'):
            self.track_order_button = tk.Button(self.order_frame, text="Track Order", command=self.track_order_ui)
        self.track_order_button.pack(pady=10)

        # Load orders for the selected project
        if project_id:
            self.load_orders(project_id)

    def create_order_ui(self):
        order_window = tk.Toplevel(self.root)
        order_window.title("Create Order")

        tk.Label(order_window, text="Enter Employee ID:").pack(pady=5)
        employee_id_entry = tk.Entry(order_window)
        employee_id_entry.pack(pady=5)

        tk.Label(order_window, text="Enter Shipment ID:").pack(pady=5)
        shipment_id_entry = tk.Entry(order_window)
        shipment_id_entry.pack(pady=5)

        tk.Label(order_window, text="Enter Products (product_id, quantity, unit_price) as comma-separated values:").pack(pady=5)
        products_entry = tk.Entry(order_window)
        products_entry.pack(pady=5)

        def submit_order():
            try:
                employee_id = int(employee_id_entry.get())
                shipment_id = int(shipment_id_entry.get())
                products_input = products_entry.get()
                products = [tuple(map(eval, p.strip().split())) for p in products_input.split(',')]
                order_date = datetime.now()
                total_cost = sum(quantity * unit_price for _, quantity, unit_price in products)
                self.cursor.execute(
                    "INSERT INTO Orders (orderDate, status, cost, placedBy, trackedWith) VALUES (%s, %s, %s, %s, %s)",
                    (order_date, 1, total_cost, employee_id, shipment_id)
                )
                order_id = self.cursor.lastrowid
                for product_id, quantity, unit_price in products:
                    self.cursor.execute(
                        "INSERT INTO OrderDetails (orderID, productID, quantity, unitPrice) VALUES (%s, %s, %s, %s)",
                        (order_id, product_id, quantity, unit_price)
                    )
                self.conn.commit()
                print(f"Order {order_id} created successfully!")
                order_window.destroy()
            except mysql.connector.Error as err:
                print(f"Error: {err}")
            except ValueError:
                print("Invalid input. Please try again.")

        tk.Button(order_window, text="Submit", command=submit_order).pack(pady=10)

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
