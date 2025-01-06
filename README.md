# Hardware_Database
Class Assignment to create database and GUI using SQL and python
## USAGE:

## this creates the tables
-> Creating_Tables_Modified.sql

## this adds 2-3 example entries to the tables
-> Data_Insertion_Modified.sql

## alternatively, navigate to \DATASET_LOADER and run:
-> sql_data_loader.py

## make sure to change your port, user and password based on your machine!!!


#################################

## CHANGELOG

-> changed all "name" variable into "customerName" to avoid conflicts with MySQL
-> changed "status" in shipment into "shipmentStatus" to avoid conflicts with MySQL
-> removed "status" in orders since it can be directly accessed in shipment
-> removed redundant "orderDetailsID" since they can be directly accessed with orderID and productID as CKs
-> split location table into projectLocation and supplierLocation to align with BCNF
-> removed the employee table
-> connected customer table to order table (1:1) -> (1:*)
-> changed multiplicities between product-supplier and product-project to no longer require many-many relationships
-> reorganized creating_tables.sql for insertion order clarity
-> reorganized data_insertion_demo.sql to follow insertion order (avoid insertion errors)

