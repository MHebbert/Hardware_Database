import mysql.connector
import pandas as pd

import os

# Change working directory to the script's location
os.chdir(os.path.dirname(os.path.abspath(__file__)))

conn = mysql.connector.connect(host="localhost",
                               port=3306, # Use your own port
                               user="root", # Use your own username
                               password="Dorgelo6!",  # Use your own password
                               database="my_database")

cursor = conn.cursor()

def insertShipment():
    shipment = pd.read_csv('shipment.csv')
    for _, row in shipment.iterrows():
        cursor.execute(
            "INSERT INTO Shipment (courier, shipmentDate, shipmentStatus) VALUES (%s, %s, %s)",
            (
                row['courier'],
                row['shipmentDate'],
                row['shipmentStatus']
            )
        )
    conn.commit()

def insertCustomer():
    customer = pd.read_csv('customer.csv')
    for _, row in customer.iterrows():
        cursor.execute(
            "INSERT INTO Customer (customerName, email, phoneNumber) VALUES (%s, %s, %s)",
            (
                row['customerName'],
                row['email'],
                row['phoneNumber']
            )
        )
    conn.commit()

def insertSupplier():
    supplier = pd.read_csv('supplier.csv')
    for _, row in supplier.iterrows():
        cursor.execute(
            "INSERT INTO Supplier (supplierName, contactInfo) VALUES (%s, %s)",
            (
                row['supplierName'],
                row['contactInfo']
            )
        )
    conn.commit()

def insertProjects():
    projects = pd.read_csv('projects.csv')

    cursor.execute("SELECT customerID FROM customer")
    customer_id_fks = pd.DataFrame({'customerID':[id[0] for id in cursor.fetchall()]})

    projects = expandForeignSet(projects, customer_id_fks) # Adds the FKs into the projects dataset
    
    for _, row in projects.iterrows():
        cursor.execute(
            "INSERT INTO Projects (company, budget, deadline, projectStatus, projectName, customerID) VALUES (%s, %s, %s, %s, %s, %s)",
            (   
                row['company'],
                row['budget'],
                row['deadline'],
                row['projectStatus'],
                row['projectName'], 
                row['customerID']
            )
        )
    conn.commit()

def insertLocation():
    location = pd.read_csv('location.csv') # A single file containing the locations for both suppliers and projects
    project_location = location.iloc[:1000,:].reset_index(drop=True) # Setting # of projects to be 1000
    supplier_location = location.iloc[1000:,:].reset_index(drop=True) # Arbitrarily giving the remaining locations to the 

    cursor.execute("SELECT projectID FROM projects")
    project_id_fk = pd.DataFrame({'projectID':[id[0] for id in cursor.fetchall()]}) # Each project should have exactly 1 location

    cursor.execute("SELECT supplierID FROM supplier")
    supplier_id_fks = pd.DataFrame({'supplierID':[id[0] for id in cursor.fetchall()]}) # Each supplier should have exactly 1 location

    project_location = pd.concat([project_location, project_id_fk], axis='columns')
    supplier_location = pd.concat([supplier_location, supplier_id_fks], axis='columns')

    for _, row in project_location.iterrows():
        cursor.execute(
            "INSERT INTO ProjectLocation (projectID, country, city, postalCode, provinceState, streetName) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                row['projectID'], 
                row['country'], 
                row['city'], 
                row['postalCode'], 
                row['provinceState'], 
                row['streetName'], 
            )
        )
    for _,row in supplier_location.iterrows():
        cursor.execute(
            "INSERT INTO SupplierLocation (supplierID, country, city, postalCode, provinceState, streetName) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                row['supplierID'], 
                row['country'], 
                row['city'], 
                row['postalCode'], 
                row['provinceState'], 
                row['streetName'], 
            )
        )
    conn.commit()

def insertProduct():
    product = pd.read_csv('product.csv')

    cursor.execute("SELECT supplierID FROM supplier")
    supplier_id_fks = pd.DataFrame({'supplierID':[id[0] for id in cursor.fetchall()]})

    product = expandForeignSet(product, supplier_id_fks)

    for _, row in product.iterrows():
        cursor.execute(
            "INSERT INTO Product (productName, quantity, productDescription, materialType, weight, price, supplierID) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (
                row['productName'],
                row['quantity'],
                row['productDescription'],
                row['materialType'], 
                row['weight'],
                row['price'], 
                row['supplierID'],
            )
        )
    conn.commit()

def insertOrders():
    orders = pd.read_csv('orders.csv')

    #cursor.execute("SELECT customerID FROM customer")
    #customer_id_fks = pd.DataFrame({'customerID':[id[0] for id in cursor.fetchall()]})
    cursor.execute("SELECT shipmentID FROM shipment")
    shipment_id_fks = pd.DataFrame({'shipmentID':[id[0] for id in cursor.fetchall()]})
    cursor.execute("SELECT productID FROM product")
    product_id_fks = pd.DataFrame({'productID':[id[0] for id in cursor.fetchall()]})
    cursor.execute("SELECT customerID, projectID FROM projects")
    customer_project_id_fks = cursor.fetchall()
    customer_project_id_fks = pd.DataFrame({'customerID': [customer_id_fk[0] for customer_id_fk in customer_project_id_fks], 'projectID': [project_id_fk[1] for project_id_fk in customer_project_id_fks]})

    
    orders = expandForeignSet(orders, customer_project_id_fks)
    orders = expandForeignSet(orders, shipment_id_fks)
    orders = expandForeignSet(orders, product_id_fks)


    for _, row in orders.iterrows():
        cursor.execute(
            "INSERT INTO Orders (orderDate, cost, customerID, shipmentID, productID, projectID) VALUES (%s, %s, %s, %s, %s, %s)",
            (
                row['orderDate'],
                row['cost'], 
                row['customerID'], 
                row['shipmentID'],
                row['productID'],
                row['projectID']
            )
        )
    conn.commit()

def insertOrderDetails():
    order_details = pd.read_csv('orderdetails.csv')

    cursor.execute("SELECT orderID, productID FROM orders ORDER BY orderID")
    order_product_tuple = cursor.fetchall()
    order_product_id_fks = pd.DataFrame({'orderID': [order_id_fk[0] for order_id_fk in order_product_tuple], 'productID': [product_id_fk[1] for product_id_fk in order_product_tuple]})

    order_details = expandForeignSet(order_product_id_fks, order_details) # order_product_id_fks are in the first slot because they are also the PKs

    for _, row in order_details.iterrows():
        cursor.execute(
            "INSERT INTO OrderDetails (orderID, productID, quantity, unitPrice) VALUES (%s, %s, %s, %s)",
            (
                row['orderID'],
                row['productID'], 
                row['quantity'],
                row['unitPrice']
            )
        )
    conn.commit()

def expandForeignSet(mergeSet, foreignSet): #For 1-Many and 1-1 relationships only
    row_difference = len(mergeSet) - len(foreignSet) # the merge set (many) should always have more or equal entries than the foreign set (1) (Does not support many-many)
    if row_difference > 0:
        random_duplicates = foreignSet.sample(n=row_difference, replace=True, random_state=42).reset_index(drop=True)
        id_fks = pd.concat([foreignSet, random_duplicates], ignore_index=True)
        id_fks = id_fks.sample(frac=1, random_state=42).reset_index(drop=True) # shuffles the foreign keys
        uniformSet = pd.concat([mergeSet, id_fks], axis='columns') # Adds the FKs into the new uniform dataset
    
    else: # In the case for row_difference = 0 (1-1), which is possible for a 1-many relationship
        shuffled_foreign_set = foreignSet.sample(frac=1, random_state=42).reset_index(drop=True) # shuffles the foreign keys
        uniformSet = pd.concat([mergeSet, shuffled_foreign_set], axis='columns')
    
    return uniformSet #returns the uniform dataset
    


# Call the functions to insert data
insertShipment()
insertCustomer()
insertSupplier()
insertProjects()
insertLocation()
insertProduct()
insertOrders()
insertOrderDetails()


# Close the connection
cursor.close()
conn.close()

#All csv files must be located in the same folder for script to function