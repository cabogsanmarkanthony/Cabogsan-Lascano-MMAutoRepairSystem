import tkinter as tk
from tkinter import messagebox
from datetime import datetime, date, time
import database  
import frontend  

#CONSTANTS (Colors/Fonts)
COLOR_PRIMARY = "#787F56"   # Olive Green
COLOR_BACKGROUND = "#E2D4B9" # Light Beige
COLOR_SUCCESS = "#4CAF50"   # Green
COLOR_PENDING = "#FFA500"   # Orange
COLOR_ERROR = "#F44336"     # Red
COLOR_INFO = "#2196F3"      # Blue (For Canceled status)

FONT_TITLE = ("Helvetica", 24, "bold")
FONT_HEADING = ("Helvetica", 14, "bold")
FONT_BODY = ("Helvetica", 10)
#1class 
#20 methods
# SESSION CONTROLLER METHODS
class MMAutoRepairShop(tk.Tk): #parent class
    def __init__(self):
        super().__init__()
        self.title("MM Auto Repair Shop")
        self.geometry("1000x600")
        self.state('zoomed') 
        self.config(bg=COLOR_BACKGROUND)

        # Initialize DB
        database.create_tables()
        database.setup_initial_data() 

        # Session Management
        self.current_user = None # Holds user dict after login/signup
        
        # Frame Setup (Screen Manager)
        container = tk.Frame(self, bg=COLOR_BACKGROUND)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        login_signup_frame = frontend.LoginSignupFrame(container, self)
        self.frames["LoginSignup"] = login_signup_frame
        login_signup_frame.grid(row=0, column=0, sticky="nsew")

        user_dashboard_frame = frontend.UserDashboardFrame(container, self)
        self.frames["UserDashboard"] = user_dashboard_frame
        user_dashboard_frame.grid(row=0, column=0, sticky="nsew")

        admin_dashboard_frame = frontend.AdminDashboardFrame(container, self)
        self.frames["AdminDashboard"] = admin_dashboard_frame
        admin_dashboard_frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginSignup")

    def show_frame(self, name):
        frame = self.frames[name]
        frame.tkraise()

    def process_login(self, username, password):
        user = database.get_user_by_username(username)
        if user and user['password'] == password:
            self.current_user = user
            database.update_last_login(user['user_id'])
            messagebox.showinfo("Login Success", f"Welcome, {user['full_name']}!")
            if user['user_type'] == 1:
                self.frames["AdminDashboard"].set_admin_data(user)
                self.show_frame("AdminDashboard")
            else:
                self.frames["UserDashboard"].set_user_data(user)
                self.show_frame("UserDashboard")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def process_signup(self, username, full_name, phone_no, password):
        if not (username and full_name and phone_no and password):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        success, message = database.register_new_user(username, full_name, phone_no, password)
        if success:
            messagebox.showinfo("Sign-up Success", message)
            self.frames["LoginSignup"].show_inner_frame("Login")
        else:
            messagebox.showerror("Sign-up Failed", message)

    def logout(self):
        self.current_user = None
        messagebox.showinfo("Logged Out", "You have been successfully logged out.")
        self.show_frame("LoginSignup")
        # Clear entries in login frame for security
        self.frames["LoginSignup"].inner_frames["Login"].username_entry.delete(0, tk.END)
        self.frames["LoginSignup"].inner_frames["Login"].password_entry.delete(0, tk.END)

    def get_current_user_id(self):
        return self.current_user['user_id'] if self.current_user else None

    def save_user_profile(self, user_id, full_name, phone_no, new_password):
        database.update_user_profile(user_id, full_name, phone_no, new_password)
        # Re-fetch user data to update the session info
        self.current_user = database.get_user_by_username(self.current_user['username']) 
        messagebox.showinfo("Success", "Profile updated successfully.")
        
    # VEHICLE METHODS
    def process_add_vehicle(self, brand, model, plate_no):
        user_id = self.get_current_user_id()
        if not user_id:
            messagebox.showerror("Error", "User not logged in.")
            return

        success, message = database.add_vehicle(user_id, brand, model, plate_no)
        if success:
            messagebox.showinfo("Success", message)
            # Reload vehicles list
            self.frames["UserDashboard"].content_frames["Vehicles"].load_data() 
        else:
            messagebox.showerror("Failed", message)

    def delete_vehicle_by_admin(self, vehicle_id, plate_no):
        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete vehicle {plate_no} and all its associated appointments?"):
            return
            
        deleter_id = self.get_current_user_id()
        success, message = database.delete_vehicle(deleter_id, vehicle_id)
        if success:
            messagebox.showinfo("Success", message)
            # Reload Admin vehicle list
            self.frames["AdminDashboard"].content_frames["ManageVehicles"].load_data()
        else:
            messagebox.showerror("Failed", message)

    # APPOINTMENT METHODS
    def book_appointment(self, vehicle_text, service_ids, date_str, time_str):
        # 1. Parse vehicle info
        vehicle_map = {f"{v['plate_no']} / {v['model']}": v['vehicle_id'] for v in database.get_user_vehicles(self.get_current_user_id())}
        vehicle_id = vehicle_map.get(vehicle_text)
        user_id = self.get_current_user_id()

        if not vehicle_id:
            raise ValueError("Selected vehicle is not valid.")
        
        # 2. Basic date/time validation
        try:
            appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            appt_time = datetime.strptime(time_str, "%H:%M").time()
            now = datetime.now()
            
            if appt_date < now.date():
                 raise ValueError("Cannot book an appointment for a past date.")

            # Check for same day and past time
            if appt_date == now.date() and appt_time < now.time():
                 raise ValueError("Cannot book an appointment for a time that has already passed today.")

            # Check shop hours (6:00 AM to 5:00 PM)
            min_time = time(6, 0)
            max_time = time(17, 0) # 5:00 PM
            if not (min_time <= appt_time <= max_time):
                 raise ValueError("The shop is only open from 6:00 AM to 5:00 PM.")

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return 

        # 3. Process booking
        if not service_ids:
            messagebox.showerror("Input Error", "Please select at least one service.")
            return

        success, message = database.add_appointment(user_id, vehicle_id, service_ids, date_str, time_str)
        
        if success:
            messagebox.showinfo("Booking Success", message)
            # Reload appointments list in the UI
            self.frames["UserDashboard"].content_frames["Appointments"].load_data() 
            self.frames["UserDashboard"].content_frames["Home"].load_data() # Reload for new status tile
        else:
            messagebox.showerror("Booking Failed", message)

    def update_appt_status(self, appointment_id, new_status, full_name): #Updates the appointment status from Admin Panel.
        database.update_appointment_status(appointment_id, new_status, full_name)
        messagebox.showinfo("Success", f"Appointment status updated to {new_status}.")
        # Reload both admin and user panels that show status/messages
        self.frames["AdminDashboard"].content_frames["ManageAppointments"].load_data()
        if "UserDashboard" in self.frames and self.frames["UserDashboard"].winfo_exists():
            self.frames["UserDashboard"].content_frames["Home"].load_data()

    def delete_appointment_by_admin(self, appointment_id, status): #Deletes an appointment if status is Rejected or Completed.
        if status not in ('Rejected', 'Completed'): 
             messagebox.showerror("Error", f"Only appointments with status 'Rejected' or 'Completed' can be permanently deleted by Admin. Current status: {status}")
             return

        if not messagebox.askyesno("Confirm Permanent Deletion", f"Are you sure you want to permanently delete appointment ID {appointment_id}? This action cannot be undone."):
            return

        deleter_id = self.get_current_user_id()
        success, message = database.delete_appointment(deleter_id, appointment_id, status)
        
        if success:
            messagebox.showinfo("Success", message)
            self.frames["AdminDashboard"].content_frames["ManageAppointments"].load_data()
        else:
            messagebox.showerror("Failed", message)

    def cancel_appointment_by_user(self, appointment_id): #User cancels an appointment.
        if not messagebox.askyesno("Confirm Cancellation", f"Are you sure you want to cancel appointment ID {appointment_id}?"):
            return
            
        user_id = self.get_current_user_id()
        success, message = database.cancel_appointment(user_id, appointment_id)
        
        if success:
            messagebox.showinfo("Success", message)
            self.frames["UserDashboard"].content_frames["Appointments"].load_data()
            self.frames["UserDashboard"].content_frames["Home"].load_data()
        else:
            messagebox.showerror("Failed", message)
            
    def delete_appointment_by_user(self, appointment_id, status): #User permanently deletes a Canceled/Rejected appointment.
        if status not in ('Canceled', 'Rejected'):
             messagebox.showerror("Error", f"Only appointments with status 'Canceled' or 'Rejected' can be permanently deleted by User. Current status: {status}")
             return

        if not messagebox.askyesno("Confirm Permanent Deletion", f"Are you sure you want to permanently delete appointment ID {appointment_id}? This removes it from your history."):
            return

        user_id = self.get_current_user_id()
        success, message = database.delete_appointment(user_id, appointment_id, status)
        
        if success:
            messagebox.showinfo("Success", message)
            self.frames["UserDashboard"].content_frames["Appointments"].load_data()
        else:
            messagebox.showerror("Failed", message)

    def reschedule_appointment(self, appointment_id, date_str, time_str): #Handles the user's request to reschedule.
        try:
            appt_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            appt_time = datetime.strptime(time_str, "%H:%M").time()
            now = datetime.now()
            
            if appt_date < now.date():
                 raise ValueError("Cannot reschedule to a past date.")

            if appt_date == now.date() and appt_time < now.time():
                 raise ValueError("Cannot reschedule to a time that has already passed today.")

            min_time = time(6, 0)
            max_time = time(17, 0) 
            if not (min_time <= appt_time <= max_time):
                 raise ValueError("The shop is only open from 6:00 AM to 5:00 PM.")

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input for rescheduling: {e}")
            return
            
        success, message = database.reschedule_appointment(appointment_id, date_str, time_str)
        
        if success:
            messagebox.showinfo("Success", message)
            self.frames["UserDashboard"].content_frames["Appointments"].load_data()
            self.frames["UserDashboard"].content_frames["Home"].load_data()
            self.frames["AdminDashboard"].content_frames["ManageAppointments"].load_data()
        else:
            messagebox.showerror("Failed", message)

    #CHAT/MESSAGE METHODS
    def send_chat_message(self, content): #Admin or User sends a message to the Admin/User.
        sender_id = self.get_current_user_id()
        
        # Admin ID is always 1 (from setup_initial_data)
        admin_id = 1
        
        if self.current_user['user_type'] == 1:          
            pass
    #HISTORY METHODS 
    def show_deleted_items_history(self):
        user_id = self.get_current_user_id()
        user_type = self.current_user.get('user_type', 0)
        history = database.get_deleted_items_history(user_id, user_type)
        
        details = "--- DELETED/CANCELED ITEMS HISTORY ---\n\n"
        if history:
            for item in history:
                details += f"ID: {item['history_id']} | Type: {item['item_type']} | Deleted By: {item['deleter_username']}\n"
                details += f"Date: {item['deleted_at']}\n"
                details += f"Details: {item['details']}\n"
                details += "-" * 50 + "\n"
        else:
            details += "No deletion history available."
            
        messagebox.showinfo("Deletion History", details)
        

if __name__ == "__main__":
    app = MMAutoRepairShop()
    app.mainloop()