import sqlite3
from datetime import datetime
#36 method used
#relational data models using sqlite
#Lists of Dictionaries: Multi-row queries, such as get_all_appointments()
#Dictionaries (dict): Every database query function (like get_user_by_username or get_vehicle_by_id)
DATABASE_NAME = "mm_auto_repair.db"

def get_db_connection():
    # Connects to the database and returns the connection object
    conn = sqlite3.connect(DATABASE_NAME)
    # Enable foreign key support for cascade deletes
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table (0 for regular user, 1 for Admin)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            phone_no TEXT NOT NULL,
            user_type INTEGER DEFAULT 0,
            last_login TEXT 
        )
    """)
    
    # Vehicles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            vehicle_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            plate_no TEXT UNIQUE NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    # Service Offers (Inventory/Pricing)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_offers (
            service_id INTEGER PRIMARY KEY,
            service_name TEXT UNIQUE NOT NULL,
            labor_rate REAL NOT NULL 
        )
    """)
    
    # Appointments table (Updated for multi-service support and status messages)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            vehicle_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending', -- Pending, Approved, Rejected, Canceled, Completed
            status_message TEXT,
            is_deleted INTEGER DEFAULT 0, -- 1 if soft-deleted by user/admin
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
        )
    """)

    # Appointment Services (M:M relationship for multiple services per appointment)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointment_services (
            appt_service_id INTEGER PRIMARY KEY,
            appointment_id INTEGER NOT NULL,
            service_id INTEGER NOT NULL,
            service_name TEXT NOT NULL, -- Store name for history even if offer changes
            labor_rate REAL NOT NULL, -- Store rate at time of booking
            FOREIGN KEY (appointment_id) REFERENCES appointments(appointment_id) ON DELETE CASCADE,
            FOREIGN KEY (service_id) REFERENCES service_offers(service_id)
        )
    """)

    # Messages/Chat table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            message_id INTEGER PRIMARY KEY,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (sender_id) REFERENCES users(user_id),
            FOREIGN KEY (receiver_id) REFERENCES users(user_id)
        )
    """)

    # Deleted Items History table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deleted_items_history (
            history_id INTEGER PRIMARY KEY,
            deleter_id INTEGER, -- The user_id who deleted it (Admin or User)
            item_type TEXT NOT NULL, -- e.g., 'Vehicle', 'Appointment', 'Service Offer'
            item_id INTEGER NOT NULL,
            details TEXT, -- Formatted string of item details (NO JSON)
            deleted_at TEXT NOT NULL
        )
    """)


    conn.commit()
    conn.close()

def setup_initial_data(): #set up the default admin user and service offers.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check and insert Admin if not exists
    cursor.execute("SELECT user_id FROM users WHERE username = 'Admin'")
    if cursor.fetchone() is None:
        try:
            # user_type 1 for Admin
            cursor.execute("INSERT INTO users (username, password, full_name, phone_no, user_type) VALUES (?, ?, ?, ?, ?)", 
                           ('Admin', 'admin123', 'Admin', '09991234567', 1))
        except sqlite3.IntegrityError:
            pass 
    
    # Check and insert default service offers
    default_offers = [
        ('Oil Change', 145.00), ('Brake Repair and Inspection', 500.00), ('Electrical System Repairs', 1000.00),
        ('Engine Diagnostic Services', 600.00), ('Tire Services', 250.00), ('Battery Services', 450.00),
        ('Heating and Air Conditioning (A/C) Repairs', 1500.00), ('Suspension and Steering System Repairs', 750.00), 
        ('Transmission Repair', 2000.00)
    ]
    for name, rate in default_offers:
        cursor.execute("SELECT service_id FROM service_offers WHERE service_name = ?", (name,))
        if cursor.fetchone() is None:
            try:
                cursor.execute("INSERT INTO service_offers (service_name, labor_rate) VALUES (?, ?)", (name, rate))
            except sqlite3.IntegrityError:
                pass 

    conn.commit()
    conn.close()

#helper function
def _format_details(data): #Formats a dictionary into a simple string.
    return " | ".join([f"{k}: {v}" for k, v in data.items()])

def log_deleted_item(deleter_id, item_type, item_id, details_dict):
    conn = get_db_connection()
    cursor = conn.cursor()
    details = _format_details(details_dict)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO deleted_items_history (deleter_id, item_type, item_id, details, deleted_at)
        VALUES (?, ?, ?, ?, ?)
    """, (deleter_id, item_type, item_id, details, now))
    conn.commit()
    conn.close()
    return True

# user function

def get_user_by_username(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    # SELECT * is used to get all columns, including 'password'
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        # Get column names for dictionary conversion
        cols = [col[0] for col in cursor.description]
        return dict(zip(cols, user_data))
    return None

def update_last_login(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE users SET last_login = ? WHERE user_id = ?", (now, user_id))
    conn.commit()
    conn.close()

def register_new_user(username, full_name, phone_no, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password, full_name, phone_no, user_type) VALUES (?, ?, ?, ?, ?)", 
                       (username, password, full_name, phone_no, 0))
        conn.commit()
        conn.close()
        return True, "Registration successful. You can now log in."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists. Please choose a different one."
    except Exception as e:
        conn.close()
        return False, f"An unexpected error occurred: {e}"


def update_user_profile(user_id, username, full_name, phone_no, new_password=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT user_id FROM users WHERE username = ? AND user_id != ?", (username, user_id))
        if cursor.fetchone():
            return "Error: Username already exists. Please choose a different one."
            
        if new_password:
            import hashlib
            hashed_password = hashlib.sha256(new_password.encode('utf-8')).hexdigest()
            
            query = """
                UPDATE users SET 
                    username = ?, 
                    full_name = ?, 
                    phone_no = ?,
                    password = ? 
                WHERE user_id = ?
            """
            params = (username, full_name, phone_no, hashed_password, user_id)
        else:
            query = """
                UPDATE users SET 
                    username = ?, 
                    full_name = ?, 
                    phone_no = ?
                WHERE user_id = ?
            """
            params = (username, full_name, phone_no, user_id)
            
        cursor.execute(query, params)
        conn.commit()
        return "Success: Profile updated successfully."
        
    except sqlite3.Error as e:
        return f"Database Error: {e}"
        
    finally:
        conn.close()

# vehicle function

def get_user_vehicles(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles WHERE user_id = ?", (user_id,))
    vehicles_data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in vehicles_data]

def add_vehicle(user_id, brand, model, plate_no):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO vehicles (user_id, brand, model, plate_no) VALUES (?, ?, ?, ?)", (user_id, brand, model, plate_no.upper()))
        conn.commit()
        conn.close()
        return True, "Vehicle added successfully."
    except sqlite3.IntegrityError:
        conn.close()
        return False, f"Plate number '{plate_no}' already exists in the system."

def delete_vehicle(user_id, vehicle_id): #Deletes a vehicle and logs the action.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Get vehicle details for logging (and check if it belongs to user if user_id is provided)
    cursor.execute("SELECT * FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
    vehicle = cursor.fetchone()
    if not vehicle:
        conn.close()
        return False, "Vehicle not found."
    
    cols = [col[0] for col in cursor.description]
    vehicle_details = dict(zip(cols, vehicle))
    
    # 2. Delete associated appointments (cascaded from appointments to appointment_services is needed)
    cursor.execute("DELETE FROM appointments WHERE vehicle_id = ?", (vehicle_id,))
    
    # 3. Then delete the vehicle
    cursor.execute("DELETE FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
    conn.commit()
    conn.close()

    # 4. Log deletion
    log_deleted_item(user_id, 'Vehicle', vehicle_id, vehicle_details)
    return True, f"Vehicle (Plate: {vehicle_details['plate_no']}) and associated appointments deleted."

def get_vehicle_by_id(vehicle_id): #Fetches a vehicle by ID.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
    vehicle_data = cursor.fetchone()
    conn.close()
    if vehicle_data:
        cols = [col[0] for col in cursor.description]
        return dict(zip(cols, vehicle_data))
    return None

# appointment function

def get_service_offers_by_id(service_ids): #Fetches service offers by a list of IDs.
    if not service_ids:
        return []
    conn = get_db_connection()
    cursor = conn.cursor()
    # Use IN clause for multiple IDs
    placeholders = ','.join('?' for _ in service_ids)
    cursor.execute(f"SELECT * FROM service_offers WHERE service_id IN ({placeholders})", service_ids)
    offers_data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in offers_data]

def add_appointment(user_id, vehicle_id, service_ids, date_str, time_str): #Adds a new appointment with multiple services.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check for existing pending/approved appointment for the same time slot
    cursor.execute("""
        SELECT 1 FROM appointments 
        WHERE date = ? AND time = ? AND status IN ('Pending', 'Approved', 'Completed') AND is_deleted = 0
    """, (date_str, time_str))
    if cursor.fetchone():
        conn.close()
        return False, "The selected date and time is already booked or is too soon. Please choose another slot."

    # 1. Insert into appointments table
    try:
        cursor.execute("""
            INSERT INTO appointments (user_id, vehicle_id, date, time, status) 
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, vehicle_id, date_str, time_str, 'Pending'))
        appointment_id = cursor.lastrowid
    except Exception as e:
        conn.close()
        return False, f"Failed to create appointment: {e}"

    # 2. Get current service rates and insert into appointment_services
    selected_services = get_service_offers_by_id(service_ids)
    if not selected_services:
        conn.rollback()
        conn.close()
        return False, "No valid services selected."

    for service in selected_services:
        try:
            cursor.execute("""
                INSERT INTO appointment_services (appointment_id, service_id, service_name, labor_rate)
                VALUES (?, ?, ?, ?)
            """, (appointment_id, service['service_id'], service['service_name'], service['labor_rate']))
        except Exception as e:
            conn.rollback()
            conn.close()
            return False, f"Failed to add service detail: {e}"
            
    conn.commit()
    conn.close()
    return True, "Appointment booked! Awaiting admin approval."

def get_user_appointments(user_id): #Fetches all appointments (including canceled/deleted, with service details) for a user.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            a.appointment_id, a.date, a.time, a.status, a.status_message, a.is_deleted, 
            v.plate_no, v.brand, v.model,
            GROUP_CONCAT(s.service_name, ' | ') AS services_names,
            SUM(s.labor_rate) AS total_cost
        FROM appointments a
        JOIN vehicles v ON a.vehicle_id = v.vehicle_id
        LEFT JOIN appointment_services s ON a.appointment_id = s.appointment_id
        WHERE a.user_id = ? 
        GROUP BY a.appointment_id
        ORDER BY a.date DESC, a.time DESC
    """, (user_id,))
    
    appointments_data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in appointments_data]

def get_all_appointments(): #Fetches all appointments (Admin view, with user and service details).
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            a.appointment_id, a.date, a.time, a.status, a.status_message, a.is_deleted,
            u.full_name, u.phone_no,
            v.plate_no, v.brand, v.model,
            GROUP_CONCAT(s.service_name, ' | ') AS services_names,
            SUM(s.labor_rate) AS total_cost
        FROM appointments a
        JOIN users u ON a.user_id = u.user_id
        JOIN vehicles v ON a.vehicle_id = v.vehicle_id
        LEFT JOIN appointment_services s ON a.appointment_id = s.appointment_id
        GROUP BY a.appointment_id
        ORDER BY a.date DESC, a.time DESC
    """)
    
    appointments_data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in appointments_data]

def get_upcoming_appointment(user_id): #Fetches the nearest appointment that is Pending or Approved.
    now = datetime.now()
    now_date = now.strftime("%Y-%m-%d")
    now_time = now.strftime("%H:%M")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            a.status, v.plate_no, a.date, a.time
        FROM appointments a
        JOIN vehicles v ON a.vehicle_id = v.vehicle_id
        WHERE a.user_id = ? AND a.status IN ('Pending', 'Approved') AND a.is_deleted = 0
        AND (a.date > ? OR (a.date = ? AND a.time > ?))
        ORDER BY a.date ASC, a.time ASC
        LIMIT 1
    """, (user_id, now_date, now_date, now_time))
    
    upcoming = cursor.fetchone()
    conn.close()
    
    if upcoming:
        cols = ['status', 'plate_no', 'date', 'time']
        return dict(zip(cols, upcoming))
    return None

def update_appointment_status(appointment_id, new_status, full_name=None): #Updates the appointment status and sets the corresponding status message.
    conn = get_db_connection()
    cursor = conn.cursor()

    if new_status == 'Approved':
        message = "Appointment Approved please bring your vehicle at our shop to start the process, Thank you!"
    elif new_status == 'Rejected':
        message = "Sorry we are not available on that schedule, please reschedule your appointment, Thank you!"
    elif new_status == 'Completed':
        message = f"Good day {full_name or ''} your vehicle is ready to drive again, you can now come to our shop again to pick-up this, prepare the exact amount of payment for our services. thank you for trusting our shop!."
    else:
        message = None # For Pending, Canceled etc.

    cursor.execute("UPDATE appointments SET status = ?, status_message = ? WHERE appointment_id = ?",
                   (new_status, message, appointment_id))
    conn.commit()
    conn.close()

def delete_appointment(deleter_id, appointment_id, status): #Permanently deletes an appointment and logs the action.
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Get appointment details for logging
    cursor.execute("""
        SELECT 
            a.appointment_id, a.date, a.time, a.status, u.username, v.plate_no, SUM(s.labor_rate) AS total_cost
        FROM appointments a
        JOIN users u ON a.user_id = u.user_id
        JOIN vehicles v ON a.vehicle_id = v.vehicle_id
        LEFT JOIN appointment_services s ON a.appointment_id = s.appointment_id
        WHERE a.appointment_id = ?
        GROUP BY a.appointment_id
    """, (appointment_id,))
    appt = cursor.fetchone()
    if not appt:
        conn.close()
        return False, "Appointment not found."
        
    cols = ['appointment_id', 'date', 'time', 'status', 'username', 'plate_no', 'total_cost']
    appt_details = dict(zip(cols, appt))
    
    # 2. Delete the appointment (appointment_services will cascade delete)
    cursor.execute("DELETE FROM appointments WHERE appointment_id = ?", (appointment_id,))
    conn.commit()
    conn.close()

    # 3. Log deletion
    log_deleted_item(deleter_id, 'Appointment', appointment_id, appt_details)
    return True, f"Appointment (ID: {appointment_id}, Status: {status}) permanently deleted."

def cancel_appointment(user_id, appointment_id): #Cancels an appointment (soft-delete and status update) and logs the action.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Get appointment details for logging
    cursor.execute("""
        SELECT 
            a.appointment_id, a.date, a.time, a.status, u.username, v.plate_no
        FROM appointments a
        JOIN users u ON a.user_id = u.user_id
        JOIN vehicles v ON a.vehicle_id = v.vehicle_id
        WHERE a.appointment_id = ?
    """, (appointment_id,))
    appt = cursor.fetchone()
    if not appt:
        conn.close()
        return False, "Appointment not found."
    
    cols = ['appointment_id', 'date', 'time', 'status', 'username', 'plate_no']
    appt_details = dict(zip(cols, appt))
    
    # 2. Update status and soft delete flag
    cursor.execute("UPDATE appointments SET status = 'Canceled', status_message = 'Appointment canceled by user.', is_deleted = 1 WHERE appointment_id = ?", (appointment_id,))
    conn.commit()
    conn.close()

    # 3. Log cancellation
    log_deleted_item(user_id, 'Appointment_Canceled', appointment_id, appt_details)
    return True, f"Appointment (ID: {appointment_id}) has been successfully canceled."

def reschedule_appointment(appointment_id, new_date, new_time): #Reschedules an appointment (updates date/time and resets status to Pending).
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check for time slot availability
    cursor.execute("""
        SELECT 1 FROM appointments 
        WHERE date = ? AND time = ? AND status IN ('Pending', 'Approved', 'Completed') AND appointment_id != ? AND is_deleted = 0
    """, (new_date, new_time, appointment_id))
    if cursor.fetchone():
        conn.close()
        return False, "The selected date and time is already booked. Please choose another slot."

    # Update appointment details
    cursor.execute("UPDATE appointments SET date = ?, time = ?, status = 'Pending', status_message = NULL WHERE appointment_id = ?", 
                   (new_date, new_time, appointment_id))
    conn.commit()
    conn.close()
    return True, "Appointment successfully rescheduled. Awaiting admin approval."

def get_appointment_status_message(user_id): #Fetches the status and message of the latest approved/rejected/completed/canceled appointment.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT status, status_message 
        FROM appointments 
        WHERE user_id = ? AND status IN ('Approved', 'Rejected', 'Completed', 'Canceled')
        ORDER BY appointment_id DESC
        LIMIT 1
    """, (user_id,))
    
    status_data = cursor.fetchone()
    conn.close()
    if status_data:
        return {'status': status_data[0], 'message': status_data[1]}
    return None

def get_billing_invoice(appointment_id): #Fetches all necessary data to generate a billing invoice."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Fetch appointment and user/vehicle details
    cursor.execute("""
        SELECT 
            a.appointment_id, a.date, a.time, a.status, a.status_message, 
            u.full_name, u.phone_no, u.username,
            v.plate_no, v.brand, v.model
        FROM appointments a
        JOIN users u ON a.user_id = u.user_id
        JOIN vehicles v ON a.vehicle_id = v.vehicle_id
        WHERE a.appointment_id = ?
    """, (appointment_id,))
    appt_data = cursor.fetchone()

    if not appt_data:
        conn.close()
        return None

    cols = ['appointment_id', 'date', 'time', 'status', 'status_message', 'full_name', 'phone_no', 'username', 'plate_no', 'brand', 'model']
    invoice = dict(zip(cols, appt_data))

    # 2. Fetch service details and calculate total
    cursor.execute("""
        SELECT service_name, labor_rate 
        FROM appointment_services 
        WHERE appointment_id = ?
    """, (appointment_id,))
    
    services_data = cursor.fetchall()
    service_cols = ['service_name', 'labor_rate']
    invoice['services'] = [dict(zip(service_cols, row)) for row in services_data]
    invoice['total_labor_cost'] = sum(s['labor_rate'] for s in invoice['services'])

    conn.close()
    return invoice

# SERVICE OFFER FUNCTIONS (CRUD) 

def get_all_service_offers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM service_offers ORDER BY service_name")
    offers_data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in offers_data]

def update_service_offer(service_id, service_name, labor_rate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE service_offers SET service_name = ?, labor_rate = ? WHERE service_id = ?",
                       (service_name, labor_rate, service_id))
        conn.commit()
        conn.close()
        return True, "Service offer updated successfully."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Service name already exists."
    except Exception as e:
        conn.close()
        return False, f"Error updating service offer: {e}"
    
def add_service_offer(service_name, labor_rate):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO service_offers (service_name, labor_rate) VALUES (?, ?)", 
                       (service_name, labor_rate))
        conn.commit()
        conn.close()
        return True, "Service offer added successfully."
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Service name already exists."
    except Exception as e:
        conn.close()
        return False, f"Error adding service offer: {e}"

def delete_service_offer(deleter_id, service_id): #Deletes a service offer and logs the action.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Get service details for logging
    cursor.execute("SELECT * FROM service_offers WHERE service_id = ?", (service_id,))
    service = cursor.fetchone()
    if not service:
        conn.close()
        return False, "Service offer not found."
        
    cols = [col[0] for col in cursor.description]
    service_details = dict(zip(cols, service))
    
    # 2. Delete the service offer
    cursor.execute("DELETE FROM service_offers WHERE service_id = ?", (service_id,))
    conn.commit()
    conn.close()

    # 3. Log deletion (NOTE: Existing appointment_services will retain the name/rate)
    log_deleted_item(deleter_id, 'Service Offer', service_id, service_details)
    return True, f"Service offer '{service_details['service_name']}' permanently deleted."

# MESSAGE FUNCTIONS

def send_message(sender_id, receiver_id, content): #Sends a new chat message.
    conn = get_db_connection()
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %I:%M %p")
    try:
        cursor.execute("""
            INSERT INTO messages (sender_id, receiver_id, content, timestamp)
            VALUES (?, ?, ?, ?)
        """, (sender_id, receiver_id, content, now))
        conn.commit()
        conn.close()
        return True, "Message sent."
    except Exception as e:
        conn.close()
        return False, f"Failed to send message: {e}"

def get_messages(user_id, partner_id): #Fetches all messages between two users (Admin and a Customer).
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            m.message_id, m.sender_id, m.content, m.timestamp,
            s.username AS sender_username
        FROM messages m
        JOIN users s ON m.sender_id = s.user_id
        WHERE (m.sender_id = ? AND m.receiver_id = ?) OR (m.sender_id = ? AND m.receiver_id = ?)
        ORDER BY m.timestamp ASC
    """, (user_id, partner_id, partner_id, user_id))
    
    messages_data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in messages_data]

# REPORTS/SUMMARY FUNCTIONS

def get_total_active_customers():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(user_id) FROM users WHERE user_type = 0")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_pending_appointments_count():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(appointment_id) FROM appointments WHERE status = 'Pending' AND is_deleted = 0")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_total_service_revenue():
    # Placeholder: Sum of labor rates for completed services (using the new table)
    conn = get_db_connection()
    cursor = conn.cursor()
    # Join appointment_services with appointments to only sum completed ones
    cursor.execute("""
        SELECT IFNULL(SUM(aps.labor_rate), 0)
        FROM appointment_services AS aps
        JOIN appointments a ON aps.appointment_id = a.appointment_id
        WHERE a.status = 'Completed'
    """)
    revenue = cursor.fetchone()[0]
    conn.close()
    return revenue

def get_todays_appointments(date_str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            u.full_name, v.plate_no, a.status, 
            GROUP_CONCAT(s.service_name, ', ') AS service_type
        FROM appointments a
        JOIN users u ON a.user_id = u.user_id
        JOIN vehicles v ON a.vehicle_id = v.vehicle_id
        LEFT JOIN appointment_services s ON a.appointment_id = s.appointment_id
        WHERE a.date = ?
        GROUP BY a.appointment_id
        ORDER BY a.time
    """, (date_str,))
    
    appointments_data = cursor.fetchall()
    cols = ['full_name', 'plate_no', 'status', 'service_type']
    conn.close()
    return [dict(zip(cols, row)) for row in appointments_data]

def get_deleted_items_history(user_id, user_type):
    """Fetches deleted items history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if user_type == 1: # Admin: see all
        cursor.execute("""
            SELECT history_id, item_type, details, deleted_at, u.username AS deleter_username
            FROM deleted_items_history h
            LEFT JOIN users u ON h.deleter_id = u.user_id
            ORDER BY deleted_at DESC
        """)
    else: # User: only see their own cancellations
        cursor.execute("""
            SELECT history_id, item_type, details, deleted_at, 'You' AS deleter_username
            FROM deleted_items_history 
            WHERE item_type = 'Appointment_Canceled' AND deleter_id = ?
            ORDER BY deleted_at DESC
        """, (user_id,))

    history_data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in history_data]

def get_all_users(): #Fetches all users (including Admin) without their password.
    conn = get_db_connection()
    cursor = conn.cursor()
    # Exclude the password column for safety
    cursor.execute("SELECT user_id, username, full_name, phone_no, user_type, last_login FROM users ORDER BY user_id")
    users_data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in users_data]

def get_completed_appointments_count(user_id): #Counts the number of completed appointments for a specific user.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(appointment_id) FROM appointments WHERE user_id = ? AND status = 'Completed' AND is_deleted = 0", (user_id,))
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_all_vehicles(): #Fetches all vehicles in the system, including the customer's name.
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            v.vehicle_id, v.brand, v.model, v.plate_no, v.user_id, u.full_name AS customer_name
        FROM vehicles v
        JOIN users u ON v.user_id = u.user_id
        ORDER BY customer_name, v.plate_no
    """)
    vehicles_data = cursor.fetchall()
    cols = [col[0] for col in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in vehicles_data]