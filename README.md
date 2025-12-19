MM Auto Repair Shop Management System - Manual
This document provides an overview, installation instructions, and a user guide for the MM Auto Repair Shop Management System, a desktop application built using Python and the Tkinter library.

1. Overview
The MM Auto Repair Shop Management System is a simple GUI application designed to manage customer, vehicle, and appointment data for an auto repair shop. It uses an SQLite database for data persistence.
Key Features
User Authentication: Separate login/signup for regular users (Customers) and an Admin account.
Database Management: Initializes and manages all application data using SQLite, including foreign key constraints and basic CRUD operations.
Customer Features (User Dashboard):
View Service Offers and details.
Register and manage personal vehicles (My Vehicles tab).
Book, reschedule, or cancel service appointments (Appointments tab).
View a history of completed services (Billing Invoice tab).
Send messages to the Admin (Message Admin button).
View a history of deleted or canceled items (History button).
Administrator Features (Admin Dashboard):
Manage all customer accounts (Manage Users).
Manage and update service inventory and labor rates (Manage Offers).
View and manage all registered vehicles (Manage Vehicles).
Approve, reject, complete, or delete customer appointments (Manage Appointments).
Generate simple reports (e.g., total customers, pending appointments, total revenue) (Reports).
Chat with individual customers (Message tab).

2. Installation
Prerequisites
The application is written in Python and uses standard libraries with the exception of the sqlite3 module (which is usually included with Python).
Python 3.x: Ensure you have a working Python installation.
Tkinter: This is the GUI library used and is typically included with standard Python installations.
Required Files: You need all three core Python files: backend.py, frontend.py, and database.py.
Setup Steps
Obtain the Files: Download or clone the project files (backend.py, frontend.py, database.py) into a single directory.
Database Initialization: The application will automatically create the database file (mm_auto_repair.db) and set up the necessary tables the first time it runs.
Run the Application: Open your terminal or command prompt, navigate to the directory where the files are saved, and run the main application file: backend.py  The application will launch in a new window titled "MM Auto Repair Shop".

3. Instructions
3.1 Startup and LoginWhen the application starts, it presents the Login/Sign-up screen.
Initial Admin Access (First Run)
A default Administrator account is automatically created in the database.
Field     Value
Username  Admin
Password  admin123

Customer Sign-up
On the Login screen, click the "Sign-up" link at the bottom.
Fill in the required fields: Username, Full Name, Phone No., and Password.
Click the "Sign-up" button. A success message will appear, and you can then return to the Login screen.

3.2 User (Customer) Instructions
After logging in, you will see the User Dashboard with a navigation panel on the left.

Panel	                   Functionality
Home	                   Provides a summary dashboard: welcome message, last login time, shop contact details, a list of service offers, and status tiles (e.g., upcoming appointment, service history count).

Service Offers	           Lists all available services and their current labor rates in detail.
Service Details	           Provides detailed descriptions for all service categories.
My Vehicles	               Action: Click the "Add New Vehicle" button to register a vehicle by providing its Brand, Model, and Plate No.. You can also delete registered vehicles.

Appointments	           Action: Select a registered vehicle, choose one or more services from the list, and select a desired date/time to Book an appointment. You can also Cancel, Reschedule, or Delete (if already Rejected/Canceled) existing appointments.

Billing Invoice	           Shows a history of appointments. Select a Completed appointment and click "Generate Invoice" to view a detailed service breakdown and total cost.

My Profile	               Allows you to update your Full Name, Phone No., Username, or set a New Password.
Message Admin	           Allows you to send real-time chat messages to the system Administrator.

3.3 Administrator Instructions
After logging in with the Admin account, you will see the Admin Dashboard.

Panel	                Functionality
Admin Home	            Provides an overview of business metrics (Total Customers, Pending Appointments, Total Revenue).
Manage Users	        Displays a list of all customers. Allows the Admin to view and delete customer accounts.
Manage Offers	        Manage the service price list: Add New Offer, Edit, or Delete existing services and their labor rates.
Manage Vehicles	        View a list of all vehicles registered in the system by all customers. Allows deletion of vehicles.
Manage Appointments	    Primary Management Tool: View all appointments. Select an appointment to Approve, Reject, Mark as Completed, or Delete. Approving/Rejecting requires entering a status message.

Reports	                Allows generating reports based on date range (e.g., appointments by date).
Message	                Allows the Admin to select a customer from a dropdown menu and start a one-on-one chat.