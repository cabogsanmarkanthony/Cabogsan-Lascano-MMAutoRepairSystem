import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime, date
import database  

#20 class
#32 methods
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

# UI FRAME CLASSES
# LOGIN/SIGNUP

class LoginSignupFrame(tk.Frame): 
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.content_frame = tk.Frame(self, bg=COLOR_BACKGROUND, relief=tk.RAISED, bd=2)
        self.content_frame.grid(row=1, column=1, padx=50, pady=50)

        self.inner_frames = {}
        
        login_frame = LoginFrame(self.content_frame, self)
        self.inner_frames["Login"] = login_frame
        login_frame.grid(row=0, column=0, sticky="nsew")

        signup_frame = SignupFrame(self.content_frame, self)
        self.inner_frames["Signup"] = signup_frame
        signup_frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_inner_frame("Login")

    def show_inner_frame(self, name): 
        frame = self.inner_frames[name]
        frame.tkraise()

    def handle_login(self, username, password):
        self.controller.process_login(username, password)

    def handle_signup(self, username, full_name, phone_no, password):
        self.controller.process_signup(username, full_name, phone_no, password)


class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND, padx=30, pady=30)
        self.controller = controller

        tk.Label(self, text="MM Auto Repair Shop", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=10)
        tk.Label(self, text="Login", font=FONT_HEADING, bg=COLOR_BACKGROUND).pack(pady=5)

        tk.Label(self, text="Username", bg=COLOR_BACKGROUND).pack(anchor='w', pady=(10, 0))
        self.username_entry = ttk.Entry(self, width=30)
        self.username_entry.pack(pady=5)
        self.username_entry.insert(0, "")

        tk.Label(self, text="Password", bg=COLOR_BACKGROUND).pack(anchor='w', pady=(10, 0))
        self.password_entry = ttk.Entry(self, width=30, show="*")
        self.password_entry.pack(pady=5)
        self.password_entry.insert(0, "")


        login_btn = tk.Button(self, text="Login", command=self._login_command, 
                              bg=COLOR_PRIMARY, fg="white", font=FONT_HEADING, width=25)
        login_btn.pack(pady=10)

        tk.Label(self, text="Don't have an account?", bg=COLOR_BACKGROUND).pack(pady=(20, 0))
        signup_link = tk.Label(self, text="Sign-up", fg="blue", cursor="hand2", bg=COLOR_BACKGROUND)
        signup_link.bind("<Button-1>", lambda e: controller.show_inner_frame("Signup"))
        signup_link.pack()
        
    def _login_command(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.controller.handle_login(username, password)
        

class SignupFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND, padx=30, pady=30)
        self.controller = controller

        tk.Label(self, text="MM Auto Repair Shop", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=10)
        tk.Label(self, text="Sign-Up", font=FONT_HEADING, bg=COLOR_BACKGROUND).pack(pady=5)

        fields = ["Username", "Full Name", "Phone No.", "Password"]
        self.entries = {}

        for field in fields:
            tk.Label(self, text=field, bg=COLOR_BACKGROUND).pack(anchor='w', pady=(5, 0))
            entry = ttk.Entry(self, width=30)
            if field == "Password":
                entry.config(show="*")
            entry.pack(pady=2)
            self.entries[field] = entry

        signup_btn = tk.Button(self, text="Sign-up", command=self._signup_command,
                               bg=COLOR_PRIMARY, fg="white", font=FONT_HEADING, width=25)
        signup_btn.pack(pady=15)

        tk.Label(self, text="Already have an account?", bg=COLOR_BACKGROUND).pack(pady=(10, 0))
        login_link = tk.Label(self, text="Login", fg="blue", cursor="hand2", bg=COLOR_BACKGROUND)
        login_link.bind("<Button-1>", lambda e: controller.show_inner_frame("Login"))
        login_link.pack()

    def _signup_command(self):
        username = self.entries["Username"].get()
        full_name = self.entries["Full Name"].get()
        phone_no = self.entries["Phone No."].get()
        password = self.entries["Password"].get()
        
        if not all([username, full_name, phone_no, password]):
            messagebox.showerror("Input Error", "All fields are required for sign-up.")
            return

        self.controller.handle_signup(username, full_name, phone_no, password)
        for entry in self.entries.values():
            entry.delete(0, tk.END)


# USER DASHBOARD

class UserDashboardFrame(tk.Frame): 
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        self.user_data = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Navigation Frame
        nav_frame = tk.Frame(self, bg=COLOR_PRIMARY, width=200)
        nav_frame.grid(row=0, column=0, sticky="ns")
        nav_frame.grid_propagate(False) 

        tk.Label(nav_frame, text="MM Auto Repair\n SHOP", bg=COLOR_PRIMARY, fg="white", font=FONT_HEADING).pack(pady=20)
        
        # Navigation Buttons
        nav_buttons = [
            ("Home", lambda: self.show_content_frame("Home")),
            ("Service Offers", lambda: self.show_content_frame("Offers")),
            ("Service Details", lambda: self.show_content_frame("Details")), 
            ("My Vehicles", lambda: self.show_content_frame("Vehicles")),
            ("Appointments", lambda: self.show_content_frame("Appointments")),
            ("Billing Invoice", lambda: self.show_content_frame("Billing")), 
            ("My Profile", lambda: self.show_content_frame("Profile")),
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(nav_frame, text=text, command=command, 
                            bg=COLOR_PRIMARY, fg="white", font=FONT_BODY, 
                            width=18, relief=tk.FLAT, activebackground="#5E633C")
            btn.pack(pady=5, padx=10)

        # Bottom Buttons
        tk.Button(nav_frame, text="History(Deleted/Canceled)", command=controller.show_deleted_items_history, 
                  bg="#4C4C4C", fg="white", font=FONT_BODY, 
                  width=18, relief=tk.FLAT).pack(pady=(10, 5))
        # MESSAGE BUTTON 
        tk.Button(nav_frame, text="Message Admin", command=lambda: self.show_content_frame("Message"), 
                  bg=COLOR_INFO, fg="white", font=FONT_BODY, 
                  width=18, relief=tk.FLAT).pack(pady=5, padx=10) 
        tk.Button(nav_frame, text="Logout", command=controller.logout, 
                  bg=COLOR_ERROR, fg="white", font=FONT_BODY, 
                  width=18, relief=tk.FLAT).pack(pady=(10, 10))

        # Content Container
        self.content_container = tk.Frame(self, bg=COLOR_BACKGROUND)
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)
        
        self.content_frames = {}
        for name, FrameClass in [
            ("Home", HomePanel), ("Offers", ServiceOffersFrame), 
            ("Details", ServiceDetailsFrame), ("Profile", ProfileFrame), 
            ("Vehicles", MyVehiclesFrame), ("Appointments", AppointmentFrame),
            ("Billing", BillingInvoiceFrame), ("Message", MessageFrame) 
        ]:
            frame = FrameClass(self.content_container, self.controller) 
            self.content_frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_content_frame("Home")

    def set_user_data(self, user_data): 
        self.user_data = user_data
        # Set partner_id for the chat frame (Admin ID is 1)
        self.content_frames["Message"].set_partner_id(1)
        self.show_content_frame("Home") 

    def show_content_frame(self, name): 
        self.current_content_frame = self.content_frames[name]
        if hasattr(self.current_content_frame, 'load_data'):
            self.current_content_frame.load_data() 
        self.current_content_frame.tkraise()


class HomePanel(tk.Frame): 
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        self.welcome_label = tk.Label(self, text="Welcome!", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY)
        self.welcome_label.pack(pady=(10, 5), anchor='w')
        self.last_login_label = tk.Label(self, text="", font=FONT_BODY, bg=COLOR_BACKGROUND)
        self.last_login_label.pack(pady=(0, 10), anchor='w')

        tiles_container = tk.Frame(self, bg=COLOR_BACKGROUND)
        tiles_container.pack(fill='x', pady=20)
        self.tiles = {}
        tile_titles = ["Upcoming Appointment", "Vehicle Status", "Service History Count", "Latest Status Message"] 
        
        for i, title in enumerate(tile_titles):
            tile = self._create_tile(tiles_container, title)
            tile.grid(row=0, column=i, padx=5, pady=10, sticky="ew")
            self.tiles[title] = tile

        for i in range(4): # Grid configuration for 4 tiles
            tiles_container.grid_columnconfigure(i, weight=1)
        
        # Shop Contact/Address Details
        contact_frame = tk.LabelFrame(self, text="Shop Contact & Address", font=FONT_HEADING, bg=COLOR_BACKGROUND, padx=10, pady=10)
        contact_frame.pack(fill='x', pady=20)
        
        tk.Label(contact_frame, text="Address: Brgy. 12, Nasugbu, Batangas", bg=COLOR_BACKGROUND, font=FONT_BODY).pack(anchor='w')
        tk.Label(contact_frame, text="Contact: 09362749687", bg=COLOR_BACKGROUND, font=FONT_BODY).pack(anchor='w')
        tk.Label(contact_frame, text="Email: mmautorepairshop@gmail.com", bg=COLOR_BACKGROUND, font=FONT_BODY).pack(anchor='w')
        
        tk.Label(self, text="Service Offers", font=FONT_HEADING, bg=COLOR_BACKGROUND).pack(pady=(20, 10), anchor='w')
        
        # Service Offers List 
        self.offers_list_frame = tk.Frame(self, bg='white', bd=1, relief=tk.SUNKEN)
        self.offers_list_frame.pack(fill='both', expand=True)

    def _create_tile(self, parent, title):
        frame = tk.Frame(parent, bg='white', bd=2, relief=tk.RAISED, padx=10, pady=10)
        tk.Label(frame, text=title, font=FONT_HEADING, bg='white', fg=COLOR_PRIMARY).pack(pady=(0, 5))
        
        # Label 1 (Main Data)
        label1 = tk.Label(frame, text="Loading...", font=("Arial", 12), bg="white")
        label1.pack(pady=(0, 5))
        frame.label1 = label1
        
        # Label 2 (Sub Data / Message)
        label2 = tk.Label(frame, text="", font=("Arial", 10, "bold"), padx=5, pady=2, wraplength=200)
        label2.pack(pady=(0, 10))
        frame.label2 = label2
        return frame

    def load_data(self):
        user = self.controller.current_user
        user_id = self.controller.get_current_user_id()
        if not user_id: return

        # 1. Welcome Section
        self.welcome_label.config(text=f"Welcome {user.get('full_name').split()[0]}")
        last_login_text = "N/A"
        if user.get('last_login'):
            last_login_text = datetime.strptime(user['last_login'], "%Y-%m-%d %H:%M:%S").strftime("%B %d, %Y at %I:%M %p")
        self.last_login_label.config(text=f"Last login date: {last_login_text}\n Note: We are not accepting night schedule, we are available only at 6:00 AM - 5:00 PM")

        # 2. Tile Data
        # Tile 1: Upcoming Appointment
        upcoming = database.get_upcoming_appointment(user_id)
        if upcoming:
            date_obj = datetime.strptime(upcoming['date'], "%Y-%m-%d").strftime("%B %d, %Y")
            time_obj = datetime.strptime(upcoming['time'], "%H:%M").strftime("%I:%M %p") # NEW: AM/PM
            self.tiles["Upcoming Appointment"].label1.config(text=upcoming['status'], fg=COLOR_PENDING if upcoming['status'] == 'Pending' else COLOR_SUCCESS)
            self.tiles["Upcoming Appointment"].label2.config(text=f"{date_obj}\n{time_obj}\nPlate: {upcoming['plate_no']}", bg='white')
        else:
            self.tiles["Upcoming Appointment"].label1.config(text="No Upcoming Appointment", fg=COLOR_PRIMARY)
            self.tiles["Upcoming Appointment"].label2.config(text="")

        # Tile 2: Vehicle Status
        vehicles = database.get_user_vehicles(user_id)
        self.tiles["Vehicle Status"].label1.config(text=f"{len(vehicles)} Vehicle(s) Registered", fg=COLOR_PRIMARY)
        self.tiles["Vehicle Status"].label2.config(text="All vehicles Ready", bg='white')

        # Tile 3: Service History Count
        history_count = database.get_completed_appointments_count(user_id) 
        
        # Temporarily use get_user_appointments and filter locally for a quick fix
        all_appts = database.get_user_appointments(user_id)
        history_count = sum(1 for appt in all_appts if appt['status'] == 'Completed')

        self.tiles["Service History Count"].label1.config(text=f"{history_count} Completed", fg=COLOR_SUCCESS)
        self.tiles["Service History Count"].label2.config(text="Services Done", bg='white')

        # Tile 4: Latest Status Message 
        latest_status = database.get_appointment_status_message(user_id)
        if latest_status:
            status = latest_status['status']
            message = latest_status['message']
            if status == 'Approved': color = COLOR_SUCCESS
            elif status == 'Rejected': color = COLOR_ERROR
            elif status == 'Completed': color = COLOR_SUCCESS
            elif status == 'Canceled': color = COLOR_INFO
            else: color = COLOR_PRIMARY
            
            self.tiles["Latest Status Message"].label1.config(text=status, fg=color)
            self.tiles["Latest Status Message"].label2.config(text=message or "No message.", bg='white')
        else:
            self.tiles["Latest Status Message"].label1.config(text="No Recent Status", fg=COLOR_PRIMARY)
            self.tiles["Latest Status Message"].label2.config(text="Book an appointment!", bg='white')

        # 3. Service Offers List
        for widget in self.offers_list_frame.winfo_children():
            widget.destroy()
            
        offers = database.get_all_service_offers()
        if offers:
            for i, offer in enumerate(offers):
                text = f"{i+1}. {offer['service_name']} (Labor Rate: PHP {offer['labor_rate']:.2f})"
                tk.Label(self.offers_list_frame, text=text, bg='white', font=FONT_BODY, anchor='w', justify='left').pack(fill='x', padx=10, pady=2)
        else:
            tk.Label(self.offers_list_frame, text="No service offers available.", bg='white', font=FONT_BODY).pack(padx=10, pady=10)


class ServiceOffersFrame(tk.Frame): 
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        tk.Label(self, text="Service Offers (Current Rates)", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(0, 20), anchor='w')
        
        # Create a scrollable frame
        self.canvas = tk.Canvas(self, bg=COLOR_BACKGROUND, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLOR_BACKGROUND)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def load_data(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        offers = database.get_all_service_offers()
        if offers:
            tk.Label(self.scrollable_frame, text="Service Name", font=FONT_HEADING, bg=COLOR_BACKGROUND, padx=10, pady=5).grid(row=0, column=0, sticky='w')
            tk.Label(self.scrollable_frame, text="Labor Rate (PHP)", font=FONT_HEADING, bg=COLOR_BACKGROUND, padx=10, pady=5).grid(row=0, column=1, sticky='w')
            tk.Frame(self.scrollable_frame, height=1, bg='gray').grid(row=1, column=0, columnspan=2, sticky="ew")

            for i, offer in enumerate(offers):
                row_num = i + 2
                tk.Label(self.scrollable_frame, text=offer['service_name'], font=FONT_BODY, bg=COLOR_BACKGROUND, padx=10, pady=5, anchor='w').grid(row=row_num, column=0, sticky='w')
                tk.Label(self.scrollable_frame, text=f"PHP {offer['labor_rate']:.2f}", font=FONT_BODY, bg=COLOR_BACKGROUND, padx=10, pady=5, anchor='w').grid(row=row_num, column=1, sticky='w')
        else:
            tk.Label(self.scrollable_frame, text="No service offers available.", font=FONT_BODY, bg=COLOR_BACKGROUND).pack(padx=10, pady=10)


# Service Details Frame
class ServiceDetailsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        tk.Label(self, text="Auto Repair Services Details", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(0, 20), anchor='w')

        # Create a scrollable canvas
        canvas = tk.Canvas(self, bg=COLOR_BACKGROUND)
        v_scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='white', padx=20, pady=20)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=v_scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")

        self.content_frame = scrollable_frame
        self._populate_details()

    def _add_detail(self, title, content):
        tk.Label(self.content_frame, text=f"{title}", font=FONT_HEADING, bg='white', fg=COLOR_PRIMARY, anchor='w', justify='left').pack(fill='x', pady=(10, 0))
        tk.Label(self.content_frame, text=content, font=FONT_BODY, bg='white', anchor='w', justify='left', wraplength=800).pack(fill='x', pady=(0, 10))
        tk.Frame(self.content_frame, height=1, bg='lightgray').pack(fill='x')

    def _populate_details(self):
        details = [
            ("1. Oil Change", "An oil change is like a refreshing drink for your car’s engine. It involves draining the old, dirty oil and replacing it with fresh, clean oil. Typically, MM auto repair shops will also replace the oil filter during this service. Getting regular oil changes is vital to keep your engine running smoothly and to prevent any unwanted breakdowns on the road. The number of times you need to change the oil depends on the type of vehicle, so it’s best to consult your vehicle's manual for the recommended schedule."),
            ("2. Brake Repair and Inspection", "Your safety on the road depends on your vehicle’s ability to stop when needed. That’s why MM auto repair shops are well-versed in providing comprehensive brake repair and inspection services. If you hear any squeaks, squeals, or grinding noises when you hit the brakes, it’s a clear sign that a visit to the auto repair shop is in order. Expert mechanics can identify and fix various brake issues like leaking brake fluid and malfunctioning brake systems."),
            ("3. Tire Services", "Tires are the shoes of your car, and just like shoes, they require proper maintenance. MM auto repair shops offer a range of tire services, including: Tire rotation, Wheel alignment, Tire balancing, Tire replacement, Tire patching or repair with the same price. Ensuring your tires are in good condition and properly aligned can improve fuel efficiency and extend the life of your tires. So, when your vehicle needs new kicks or some tire TLC, you know where to go—an auto repair shop!"),
            ("4. Battery Services", "Imagine this: You’re all set to hit the road, but your car won’t start. One of the most common culprits for this frustrating situation is a dead battery. But fret not, because MM auto repair shops are here to help! We can test your battery’s health and, if needed, provide a replacement. MM auto repair shops also offer battery charging services, so if your battery is running low on juice, they can give it a good recharge."),
            ("5. Electrical System Repairs", "Modern vehicles are like high-tech gadgets on wheels, packed with various electronic systems and gizmos. However, these systems can sometimes go haywire, resulting in issues such as: Dead starters, Failed alternators, Malfunctioning power windows, Other electrical component problems. Luckily, MM auto repair shops have skilled technicians who specialize in diagnosing and fixing these electrical gremlins. So, if your vehicle is experiencing any electrical hiccups, taking it to an auto repair shop should be your next move."),
            ("6. Heating and Air Conditioning (A/C) Repairs", "Driving in sweltering heat or icy cold temperatures is no fun, which is why a fully functional A/C or heating system is a godsend. MM Auto repair shop can help you stay comfortable on the road by providing services for: A/C recharge, Heater core repair, Blower motor replacement also with the same price, Other A/C and heating system repairs. So, if you’re feeling the heat or shivering like a leaf, head on over to an auto repair shop to get your air conditioning fixed or heating system back in shape."),
            ("7. Engine Diagnostic Services", "Consider engine diagnostic services as a trip to the doctor for your car’s engine. When your check engine light comes on or if your car is not performing as it should, the skilled mechanics at MM auto repair shops can diagnose your vehicle for problems. This can involve using specialized equipment to retrieve error codes from your vehicle’s onboard computer, as well as good old-fashioned mechanical know-how to inspect the various components of your engine."),
            ("8. Suspension and Steering System Repairs", "These ensure a smooth and controlled ride. That said, MM auto repair shops can address the following issues: Worn-out shocks and struts, Steering wheel alignment problems, Other suspension and steering component repairs. If you’re experiencing a bumpy ride or wrestling with a stubborn steering wheel, it’s time to make a beeline for an auto repair shop."),
            ("9. Transmission Repair", "This can be quite expensive and time-consuming, so it’s good to know that MM auto repair shops have got you covered in this area. We can fix a range of transmission problems, including: Clutch repairs, Transmission fluid leaks, Complete transmission replacements (in some cases), Other transmission-related services. If you notice any grinding gears, slipping transmissions, or other signs of transmission trouble, don’t delay an inspection—seeking the expertise of an auto repair shop can save you from even costlier repairs down the road."),
        ]
        
        for title, content in details:
            self._add_detail(title, content)
            
    def load_data(self):
        pass 


class MyVehiclesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        tk.Label(self, text="My Vehicles", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(0, 20), anchor='w')

        btn_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="Add Vehicle", command=self._show_add_vehicle_dialog, 
                  bg=COLOR_SUCCESS, fg="white", font=FONT_BODY).pack(side='left', padx=5)

        tk.Button(btn_frame, text="Delete Selected Vehicle", command=self._delete_vehicle_command,
                  bg=COLOR_ERROR, fg="white", font=FONT_BODY).pack(side='left', padx=5)

        columns = ('ID', 'Brand', 'Model', 'PlateNo')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Brand', text='Brand')
        self.tree.heading('Model', text='Model')
        self.tree.heading('PlateNo', text='Plate No.')

        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Brand', width=150)
        self.tree.column('Model', width=150)
        self.tree.column('PlateNo', width=100, anchor='center')
        
        self.tree.pack(fill='both', expand=True, pady=10)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        user_id = self.controller.get_current_user_id()
        if user_id:
            vehicles = database.get_user_vehicles(user_id)
            for vehicle in vehicles:
                self.tree.insert('', tk.END, values=(
                    vehicle['vehicle_id'], vehicle['brand'], vehicle['model'], vehicle['plate_no']
                ), tags=(vehicle['vehicle_id'], vehicle['plate_no']))

    def _show_add_vehicle_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add New Vehicle")
        dialog.transient(self.controller)
        dialog.grab_set()
        dialog.lift()
        dialog.config(bg=COLOR_BACKGROUND)

        entries = {}
        fields = ["Brand:", "Model:", "Plate No.:"]

        for i, field in enumerate(fields):
            tk.Label(dialog, text=field, bg=COLOR_BACKGROUND).grid(row=i, column=0, sticky='w', padx=10, pady=5)
            entry = ttk.Entry(dialog, width=30)
            entry.grid(row=i, column=1, padx=10, pady=5)
            entries[field] = entry

        def save_vehicle():
            brand = entries["Brand:"].get().strip()
            model = entries["Model:"].get().strip()
            plate_no = entries["Plate No.:"].get().strip().upper()
            
            if not all([brand, model, plate_no]):
                messagebox.showerror("Input Error", "All fields are required.")
                return

            self.controller.process_add_vehicle(brand, model, plate_no)
            dialog.destroy()

        tk.Button(dialog, text="Add", command=save_vehicle, bg=COLOR_SUCCESS, fg="white").grid(row=len(fields), column=1, pady=10, sticky='e', padx=10)
        
    def _delete_vehicle_command(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a vehicle to delete.")
            return

        vehicle_id = self.tree.item(selected_item, 'values')[0]
        plate_no = self.tree.item(selected_item, 'values')[3]
        
        # User deletion handled by admin-level function as it does the log and cascade delete
        self.controller.delete_vehicle_by_admin(vehicle_id, plate_no) 


class AppointmentFrame(tk.Frame): # (Appointment management with multi-select, time validation, cancel, delete, reschedule)
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller

        tk.Label(self, text="Appointment Management", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(0, 20), anchor='w')

        main_paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned_window.pack(fill='both', expand=True)

        # Booking Panel
        booking_frame = tk.Frame(main_paned_window, bg=COLOR_BACKGROUND)
        main_paned_window.add(booking_frame, weight=1)
        tk.Label(booking_frame, text="Book New Appointment", font=FONT_HEADING, bg=COLOR_BACKGROUND).pack(anchor='w', pady=(0, 10))

        form_fields_frame = tk.Frame(booking_frame, bg=COLOR_BACKGROUND)
        form_fields_frame.pack(anchor='w')
        self.entries = {}
        self.service_listbox = None

        fields = [("Vehicle Plate No. / Model:", 'vehicle'), ("Select Date (YYYY-MM-DD):", 'date'), ("Select Time (HH:MM):", 'time')]
        for i, (label_text, key) in enumerate(fields):
            tk.Label(form_fields_frame, text=label_text, bg=COLOR_BACKGROUND).grid(row=i, column=0, sticky='w', padx=5, pady=5)
            if key == 'vehicle':
                combo = ttk.Combobox(form_fields_frame, state="readonly", width=40)
                combo.grid(row=i, column=1, sticky='w', padx=5, pady=5)
                self.entries[key] = combo
            else:
                entry = ttk.Entry(form_fields_frame, width=40)
                entry.grid(row=i, column=1, sticky='w', padx=5, pady=5)
                self.entries[key] = entry
        
        self.entries['date'].insert(0, date.today().strftime("%Y-%m-%d"))
        self.entries['time'].insert(0, "10:00") # Default to a valid time

        # Multi-Select Service Listbox
        tk.Label(form_fields_frame, text="Select Service Type:", bg=COLOR_BACKGROUND).grid(row=len(fields), column=0, sticky='w', padx=5, pady=5)
        
        service_list_frame = tk.Frame(form_fields_frame, bg='white', bd=1, relief=tk.SUNKEN)
        service_list_frame.grid(row=len(fields), column=1, sticky='w', padx=5, pady=10)
        
        self.service_listbox = tk.Listbox(service_list_frame, selectmode=tk.MULTIPLE, height=8, width=43)
        self.service_listbox.pack(side=tk.LEFT, fill=tk.Y)
        
        service_scrollbar = ttk.Scrollbar(service_list_frame, orient="vertical", command=self.service_listbox.yview)
        service_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.service_listbox.config(yscrollcommand=service_scrollbar.set)
        
        tk.Button(booking_frame, text="Book Appointment", command=self._book_appointment, 
                  bg=COLOR_SUCCESS, fg="white", font=FONT_HEADING).pack(anchor='e', pady=15, padx=5)

        # Status & History Panel
        status_frame = tk.Frame(main_paned_window, bg=COLOR_BACKGROUND)
        main_paned_window.add(status_frame, weight=2)
        tk.Label(status_frame, text="Appointment History", font=FONT_HEADING, bg=COLOR_BACKGROUND).pack(anchor='w', pady=(0, 10))

        # Action Buttons for History
        action_btn_frame = tk.Frame(status_frame, bg=COLOR_BACKGROUND)
        action_btn_frame.pack(fill='x', pady=5)

        tk.Button(action_btn_frame, text="Reschedule Selected", command=self._show_reschedule_dialog,
                  bg=COLOR_INFO, fg="white", font=FONT_BODY).pack(side='left', padx=5) 
        
        tk.Button(action_btn_frame, text="Cancel Selected", command=self._cancel_appointment_command,
                  bg=COLOR_PENDING, fg="white", font=FONT_BODY).pack(side='left', padx=5) 
                  
        tk.Button(action_btn_frame, text="Delete Selected", command=self._delete_appointment_command,
                  bg=COLOR_ERROR, fg="white", font=FONT_BODY).pack(side='right', padx=5) 

        # Treeview Setup
        columns = ('ID', 'Date', 'Time', 'PlateNo', 'Service', 'Cost', 'Status')
        self.tree = ttk.Treeview(status_frame, columns=columns, show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Time', text='Time')
        self.tree.heading('PlateNo', text='Plate No.')
        self.tree.heading('Service', text='Service(s)')
        self.tree.heading('Cost', text='Total Cost')
        self.tree.heading('Status', text='Status')

        self.tree.column('ID', width=30, anchor='center')
        self.tree.column('Date', width=80)
        self.tree.column('Time', width=60, anchor='center')
        self.tree.column('PlateNo', width=80, anchor='center')
        self.tree.column('Service', width=150)
        self.tree.column('Cost', width=70, anchor='e')
        self.tree.column('Status', width=80, anchor='center')
        
        self.tree.tag_configure('Pending', background='#F0E68C')
        self.tree.tag_configure('Approved', background='#98FB98')
        self.tree.tag_configure('Rejected', background='#FFA07A')
        self.tree.tag_configure('Completed', background='#00BFFF')
        self.tree.tag_configure('Canceled', background='#ADD8E6') 

        self.tree.pack(fill='both', expand=True, pady=10)

    def load_data(self):
        self._populate_combo_boxes()
        self._populate_treeview()

    def _populate_combo_boxes(self): # Populate Vehicle Combobox
        user_id = self.controller.get_current_user_id()
        if user_id:
            vehicles = database.get_user_vehicles(user_id)
            vehicle_options = [f"{v['plate_no']} / {v['model']}" for v in vehicles]
            self.entries['vehicle']['values'] = vehicle_options
            if vehicle_options:
                self.entries['vehicle'].set(vehicle_options[0])

        # Populate Service Listbox
        self.service_listbox.delete(0, tk.END)
        offers = database.get_all_service_offers()
        self.service_map = {offer['service_name']: offer['service_id'] for offer in offers}
        self.service_list = offers # Store full list
        
        for offer in offers:
            self.service_listbox.insert(tk.END, f"{offer['service_name']} (PHP {offer['labor_rate']:.2f})")

    def _populate_treeview(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        user_id = self.controller.get_current_user_id()
        if user_id:
            appointments = database.get_user_appointments(user_id)
            for appt in appointments:               
                status = appt['status']
                tags = (appt['appointment_id'], status) 

                services_display = appt['services_names'].replace(' | ', ', ') if appt['services_names'] else 'N/A'
                total_cost_display = f"PHP {appt['total_cost']:.2f}" if appt['total_cost'] is not None else 'N/A'
                time_display = datetime.strptime(appt['time'], "%H:%M").strftime("%I:%M %p") # NEW: AM/PM

                self.tree.insert('', tk.END, values=(
                    appt['appointment_id'], 
                    appt['date'], 
                    time_display, 
                    appt['plate_no'], 
                    services_display,
                    total_cost_display,
                    status
                ), tags=(appt['appointment_id'], status))
                
                # Apply color tag
                self.tree.item(self.tree.get_children()[-1], tags=(appt['appointment_id'], status, status))

    def _book_appointment(self):
        vehicle_text = self.entries['vehicle'].get()
        date_str = self.entries['date'].get()
        time_str = self.entries['time'].get()
        
        # Get selected services IDs
        selected_indices = self.service_listbox.curselection()
        selected_services = [self.service_list[i] for i in selected_indices]
        service_ids = [s['service_id'] for s in selected_services]
        
        if not vehicle_text:
            messagebox.showerror("Input Error", "Please select a vehicle.")
            return

        self.controller.book_appointment(vehicle_text, service_ids, date_str, time_str)
        
    def _get_selected_appt(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select an appointment from the history list.")
            return None, None, None
        
        values = self.tree.item(selected_item, 'values')
        appt_id = values[0]
        status = values[6]
        return appt_id, status, selected_item

    def _show_reschedule_dialog(self):
        appt_id, status, selected_item = self._get_selected_appt()
        if not appt_id:
            return
            
        if status in ('Approved', 'Completed', 'Canceled'):
            messagebox.showerror("Action Error", f"Cannot reschedule appointment with status '{status}'. Only Pending or Rejected appointments can be rescheduled.")
            return

        dialog = tk.Toplevel(self)
        dialog.title(f"Reschedule Appointment ID {appt_id}")
        dialog.transient(self.controller)
        dialog.grab_set()
        dialog.lift()
        dialog.config(bg=COLOR_BACKGROUND)

        tk.Label(dialog, text=f"Current Date: {self.tree.item(selected_item, 'values')[1]}", bg=COLOR_BACKGROUND).pack(pady=5)
        tk.Label(dialog, text=f"Current Time: {self.tree.item(selected_item, 'values')[2]}", bg=COLOR_BACKGROUND).pack(pady=5)

        tk.Label(dialog, text="New Date (YYYY-MM-DD):", bg=COLOR_BACKGROUND).pack(pady=(10, 0))
        new_date_entry = ttk.Entry(dialog, width=30)
        new_date_entry.insert(0, self.tree.item(selected_item, 'values')[1])
        new_date_entry.pack(pady=2)

        tk.Label(dialog, text="New Time (HH:MM):", bg=COLOR_BACKGROUND).pack(pady=(10, 0))
        new_time_entry = ttk.Entry(dialog, width=30)
        new_time_entry.insert(0, datetime.strptime(self.tree.item(selected_item, 'values')[2], "%I:%M %p").strftime("%H:%M")) 
        new_time_entry.pack(pady=2)

        def perform_reschedule():
            date_str = new_date_entry.get()
            time_str = new_time_entry.get()
            self.controller.reschedule_appointment(appt_id, date_str, time_str)
            dialog.destroy()

        tk.Button(dialog, text="Confirm Reschedule", command=perform_reschedule, 
                  bg=COLOR_SUCCESS, fg="white").pack(pady=15)

    def _cancel_appointment_command(self):
        appt_id, status, selected_item = self._get_selected_appt()
        if not appt_id:
            return
            
        if status in ('Completed', 'Canceled'):
            messagebox.showerror("Action Error", f"Appointment already in final/canceled state: '{status}'. Cannot cancel.")
            return

        self.controller.cancel_appointment_by_user(appt_id)

    def _delete_appointment_command(self):
        appt_id, status, selected_item = self._get_selected_appt()
        if not appt_id:
            return
            
        if status not in ('Canceled', 'Rejected'):
            messagebox.showerror("Action Error", f"Only Canceled or Rejected appointments can be permanently deleted from history by the user.")
            return
            
        self.controller.delete_appointment_by_user(appt_id, status)


class BillingInvoiceFrame(tk.Frame): #Billing Invoice Frame
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        tk.Label(self, text="Billing Invoice History", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(0, 20), anchor='w')

        # Treeview for Billing History
        columns = ('ID', 'Date', 'Time', 'PlateNo', 'Status', 'Total Cost')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('ID', text='Appt ID')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Time', text='Time')
        self.tree.heading('PlateNo', text='Plate No.')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Total Cost', text='Total Cost')

        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Date', width=100)
        self.tree.column('Time', width=70, anchor='center')
        self.tree.column('PlateNo', width=100, anchor='center')
        self.tree.column('Status', width=100, anchor='center')
        self.tree.column('Total Cost', width=100, anchor='e')
        
        self.tree.pack(fill='x', pady=10)
        
        self.tree.bind('<<TreeviewSelect>>', self._show_invoice_details)

        # Invoice Details Panel
        self.details_frame = tk.LabelFrame(self, text="Selected Invoice Details", font=FONT_HEADING, bg=COLOR_BACKGROUND, padx=10, pady=10)
        self.details_frame.pack(fill='both', expand=True, pady=10)
        
        self.details_label = tk.Label(self.details_frame, text="Select an appointment to view its invoice.", justify='left', anchor='nw', bg=COLOR_BACKGROUND, font=FONT_BODY)
        self.details_label.pack(fill='both', expand=True)
        
    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        user_id = self.controller.get_current_user_id()
        if user_id:
            # Only show appointments with a cost (those that have services) and are not soft-deleted
            appointments = database.get_user_appointments(user_id) 
            for appt in appointments:
                # The billing invoice is most relevant for Approved/Completed, but history should include all
                if appt['is_deleted'] == 0:
                    total_cost_display = f"PHP {appt['total_cost']:.2f}" if appt['total_cost'] is not None else 'N/A'
                    time_display = datetime.strptime(appt['time'], "%H:%M").strftime("%I:%M %p") 
                    
                    self.tree.insert('', tk.END, values=(
                        appt['appointment_id'], appt['date'], time_display, 
                        appt['plate_no'], appt['status'], total_cost_display
                    ), tags=(appt['appointment_id']))
        
        self.details_label.config(text="Select an appointment to view its invoice.")
        
    def _show_invoice_details(self, event):
        selected_item = self.tree.focus()
        if not selected_item:
            return
            
        appt_id = self.tree.item(selected_item, 'values')[0]
        invoice_data = database.get_billing_invoice(appt_id)
        
        if not invoice_data:
            self.details_label.config(text="Error: Could not retrieve invoice details.")
            return
            
        # Format the invoice details
        detail_text = f"APPOINTMENT ID: {invoice_data['appointment_id']}\n"
        detail_text += f"STATUS: {invoice_data['status']}\n"
        detail_text += f"CUSTOMER: {invoice_data['full_name']} (Tel: {invoice_data['phone_no']})\n"
        detail_text += f"VEHICLE: {invoice_data['brand']} {invoice_data['model']} (Plate: {invoice_data['plate_no']})\n"
        detail_text += f"DATE/TIME: {invoice_data['date']} at {datetime.strptime(invoice_data['time'], '%H:%M').strftime('%I:%M %p')}\n"
        detail_text += "\n--- SERVICES ---\n"
        
        for i, service in enumerate(invoice_data['services']):
            detail_text += f"{i+1}. {service['service_name']} - PHP {service['labor_rate']:.2f}\n"
            
        detail_text += f"\nTOTAL LABOR COST: PHP {invoice_data['total_labor_cost']:.2f}\n"
        detail_text += "\n--- STATUS MESSAGE ---\n"
        detail_text += f"{invoice_data['status_message'] or 'N/A'}\n"
        
        self.details_label.config(text=detail_text)


class ProfileFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        
        tk.Label(self, text="My Profile", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky='w', padx=5) 
        
        fields = ["username", "full_name", "phone_no", "password"]
        labels = ["Username:", "Full Name:", "Phone No.:", "New Password (Leave blank to keep current):"]
        self.entries = {}
        
        for i, (key, label_text) in enumerate(zip(fields, labels)):
            row_index = i + 1
            tk.Label(self, text=label_text, bg=COLOR_BACKGROUND).grid(row=row_index, column=0, sticky='w', padx=5, pady=5)
            entry = ttk.Entry(self, width=40)
            if key == 'password':
                entry.config(show="*")

            entry.grid(row=row_index, column=1, sticky='w', padx=5, pady=5)
            self.entries[key] = entry
            
        save_btn = tk.Button(self, text="Save Changes", command=self._save_profile, bg=COLOR_SUCCESS, fg="white", font=FONT_HEADING, width=20)
        save_btn.grid(row=len(fields) + 1, column=1, pady=20, sticky='w', padx=5)
        
    def load_data(self):
        user = self.controller.current_user

        for key, entry in self.entries.items():
            entry.config(state='normal') 
            entry.delete(0, tk.END)
            if key == 'username':
                entry.insert(0, user.get(key, ''))
            elif key != 'password':
                entry.insert(0, user.get(key, ''))
            
    def _save_profile(self):
        user_id = self.controller.get_current_user_id()
        if not user_id: return

    def _save_profile(self):
        user = self.controller.current_user
        
        new_username = self.entries['username'].get()
        new_full_name = self.entries['full_name'].get()
        new_phone_no = self.entries['phone_no'].get()
        new_password = self.entries['password'].get() 
        
        # Basic validation
        if not all([new_username, new_full_name, new_phone_no]):
            messagebox.showerror("Error", "Username, Full Name, and Phone No. cannot be empty.")
            return

        result = database.update_user_profile(
            user['user_id'],
            new_username,
            new_full_name,
            new_phone_no,
            new_password if new_password else None 
        )

        if result.startswith("Success"):
            messagebox.showinfo("Success", result)
            
            updated_user = database.get_user_by_username(new_username) 
            if updated_user:
                self.controller.current_user = updated_user 
                
            self.load_data() 

            self.entries['password'].delete(0, tk.END) 
        else:
            messagebox.showerror("Update Failed", result)
#Message Panel Frame
class MessageFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        self.partner_id = None # Set to Admin ID 1 for User, or a specific User ID for Admin
        self.is_admin = False
        
        self.header_label = tk.Label(self, text="Message", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY)
        self.header_label.pack(pady=(0, 10), anchor='w')

        # Chat display area (Scrollable)
        message_canvas_frame = tk.Frame(self, bg='white', bd=1, relief=tk.SUNKEN)
        message_canvas_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.canvas = tk.Canvas(message_canvas_frame, bg='white', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(message_canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Input Frame
        input_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        input_frame.pack(fill='x', pady=5)
        
        self.message_entry = ttk.Entry(input_frame, width=80, font=FONT_BODY)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.send_button = tk.Button(input_frame, text="Send", command=self._send_message,
                                     bg=COLOR_PRIMARY, fg="white", font=FONT_BODY)
        self.send_button.pack(side=tk.RIGHT)

    def set_partner_id(self, partner_id, partner_name="Admin"):
        self.partner_id = partner_id
        current_user_type = self.controller.current_user.get('user_type', 0)
        self.is_admin = current_user_type == 1
        
        if self.is_admin:
            self.header_label.config(text=f"Admin Chatting with: {partner_name}")
        else:
            self.header_label.config(text="Chat with Admin")

    def load_data(self):
        # Clear previous messages
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        user_id = self.controller.get_current_user_id()
        if not user_id or not self.partner_id:
            tk.Label(self.scrollable_frame, text="Select a user to start chat, or refresh.", bg='white').pack(padx=10, pady=10)
            return

        # Partner is Admin (ID 1) for a regular user
        partner_id = 1 if not self.is_admin else self.partner_id
        
        messages = database.get_messages(user_id, partner_id)
        
        if not messages:
            tk.Label(self.scrollable_frame, text="No messages yet. Send a message to start the chat!", bg='white').pack(padx=10, pady=10)

        for msg in messages:
            is_sender = msg['sender_id'] == user_id
            
            # Message layout
            msg_frame = tk.Frame(self.scrollable_frame, bg='white')
            msg_frame.pack(fill='x', pady=2, padx=5, anchor='w' if not is_sender else 'e')
            
            # Sender/Time info
            sender_name = "You" if is_sender else msg['sender_username']
            info_label = tk.Label(msg_frame, text=f"{sender_name} - {msg['timestamp']}", font=("Arial", 8), fg='gray', bg='white')
            info_label.pack(anchor='w' if not is_sender else 'e')
            
            # Content bubble
            bubble_color = "#E0F7FA" if not is_sender else "#C8E6C9"
            content_label = tk.Label(msg_frame, text=msg['content'], font=FONT_BODY, bg=bubble_color, 
                                     wraplength=500, justify='left', bd=1, relief=tk.SOLID, padx=8, pady=4)
            content_label.pack(anchor='w' if not is_sender else 'e')

        self.scrollable_frame.update_idletasks()
        self.canvas.yview_moveto(1.0) # Scroll to bottom

    def _send_message(self):
        content = self.message_entry.get().strip()
        if not content:
            return

        sender_id = self.controller.get_current_user_id()
        
        # User (non-admin) always sends to Admin (ID 1)
        if not self.is_admin:
            receiver_id = 1
        # Admin sends to the currently selected user (self.partner_id)
        else:
            receiver_id = self.partner_id
            if not receiver_id:
                messagebox.showerror("Chat Error", "Admin must select a user to chat with.")
                return

        success, message = database.send_message(sender_id, receiver_id, content)

        if success:
            self.message_entry.delete(0, tk.END)
            self.load_data() # Reload chat
        else:
            messagebox.showerror("Send Failed", message)

# ADMIN DASHBOARD 

class AdminDashboardFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        self.admin_data = {}
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        nav_frame = tk.Frame(self, bg=COLOR_PRIMARY, width=200)
        nav_frame.grid(row=0, column=0, sticky="ns")
        nav_frame.grid_propagate(False)

        tk.Label(nav_frame, text="ADMIN\n DASHBOARD", bg=COLOR_PRIMARY, fg="white", font=FONT_HEADING).pack(pady=20)

        nav_buttons = [
            ("Admin Home", lambda: self.show_content_frame("AdminHome")),
            ("Manage Users", lambda: self.show_content_frame("ManageUsers")),
            ("Manage Services", lambda: self.show_content_frame("ManageOffers")),
            ("View All Vehicles", lambda: self.show_content_frame("ManageVehicles")),
            ("Appointments", lambda: self.show_content_frame("ManageAppointments")),
            ("Reports", lambda: self.show_content_frame("Reports")),
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(nav_frame, text=text, command=command, 
                            bg=COLOR_PRIMARY, fg="white", font=FONT_BODY, 
                            width=18, relief=tk.FLAT, activebackground="#5E633C")
            btn.pack(pady=5, padx=10)
            
        # Bottom Buttons
        tk.Button(nav_frame, text="Deleted Items History", command=controller.show_deleted_items_history, 
                  bg="#4C4C4C", fg="white", font=FONT_BODY, 
                  width=18, relief=tk.FLAT).pack(pady=(10, 5)) 

        # MESSAGE BUTTON 
        tk.Button(nav_frame, text="Message Customer", command=lambda: self.show_content_frame("Message"), 
                  bg=COLOR_INFO, fg="white", font=FONT_BODY, 
                  width=18, relief=tk.FLAT).pack(pady=5, padx=10) 
        tk.Button(nav_frame, text="Logout", command=controller.logout, 
                  bg=COLOR_ERROR, fg="white", font=FONT_BODY, 
                  width=18, relief=tk.FLAT).pack(pady=(10, 10))

        self.content_container = tk.Frame(self, bg=COLOR_BACKGROUND)
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)
        
        self.content_frames = {}
        for name, FrameClass in [
            ("AdminHome", AdminHomePanel), ("ManageUsers", ManageUsersFrame), 
            ("ManageOffers", ManageOffersFrame), ("ManageVehicles", ManageVehiclesFrame),
            ("ManageAppointments", ManageAppointmentsFrame), ("Reports", ReportsFrame), 
            ("Message", AdminMessageFrame) 
        ]:
            frame = FrameClass(self.content_container, self.controller)
            self.content_frames[name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_content_frame("AdminHome")

    def set_admin_data(self, admin_data):
        self.admin_data = admin_data  # Admin Message Frame defaults to no partner
        self.content_frames["Message"].set_partner_id(None, "No Customer Selected")
        self.show_content_frame("AdminHome")

    def show_content_frame(self, name):
        self.current_content_frame = self.content_frames[name]
        if hasattr(self.current_content_frame, 'load_data'):
            self.current_content_frame.load_data()
        self.current_content_frame.tkraise()


class AdminHomePanel(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        tk.Label(self, text="Admin Overview", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(10, 20), anchor='w')

        tiles_container = tk.Frame(self, bg=COLOR_BACKGROUND)
        tiles_container.pack(fill='x', pady=20)
        self.tiles = {}
        tile_titles = ["Total Customers", "Pending Appointments", "Total Revenue"]

        for i, title in enumerate(tile_titles):
            tile = self._create_tile(tiles_container, title)
            tile.grid(row=0, column=i, padx=10, pady=10, sticky="ew")
            self.tiles[title] = tile

        for i in range(3):
            tiles_container.grid_columnconfigure(i, weight=1)

    def _create_tile(self, parent, title):
        frame = tk.Frame(parent, bg='white', bd=2, relief=tk.RAISED, padx=10, pady=10)
        tk.Label(frame, text=title, font=FONT_HEADING, bg='white', fg=COLOR_PRIMARY).pack(pady=(0, 5))
        label1 = tk.Label(frame, text="Loading...", font=("Arial", 20, "bold"), bg="white")
        label1.pack(pady=(0, 5))
        frame.label1 = label1
        return frame

    def load_data(self):
        self.tiles["Total Customers"].label1.config(text=str(database.get_total_active_customers()), fg=COLOR_SUCCESS)
        self.tiles["Pending Appointments"].label1.config(text=str(database.get_pending_appointments_count()), fg=COLOR_PENDING)
        self.tiles["Total Revenue"].label1.config(text=f"PHP {database.get_total_service_revenue():,.2f}", fg=COLOR_PRIMARY)


class ManageUsersFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        tk.Label(self, text="Manage Users", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(0, 20), anchor='w')

        # Treeview Setup
        columns = ('ID', 'Username', 'Name', 'Phone', 'Type', 'Last Login')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Username', text='Username')
        self.tree.heading('Name', text='Full Name')
        self.tree.heading('Phone', text='Phone No.')
        self.tree.heading('Type', text='User Type')
        self.tree.heading('Last Login', text='Last Login')
        
        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Username', width=120)
        self.tree.column('Name', width=180)
        self.tree.column('Phone', width=100)
        self.tree.column('Type', width=80, anchor='center')
        self.tree.column('Last Login', width=150)
        self.tree.pack(fill='both', expand=True, pady=10)
        
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # Action Buttons
        btn_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        btn_frame.pack(fill='x', pady=5)

    def _on_select(self, event):
        pass

    def _chat_with_selected(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a user to chat with.")
            return

        values = self.tree.item(selected_item, 'values')
        user_id = values[0]
        username = values[1]
        
        if user_id == self.controller.get_current_user_id():
            messagebox.showinfo("Chat Info", "You are chatting with yourself (Admin).")
            partner_id = 1
        else:
            partner_id = int(user_id)

        # Set the partner ID in the AdminMessageFrame and switch frame
        self.controller.frames["AdminDashboard"].content_frames["Message"].set_partner_id(partner_id, username)
        self.controller.frames["AdminDashboard"].show_content_frame("Message")


    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        users = database.get_all_users()
        for user in users:
            user_type_text = "Admin" if user['user_type'] == 1 else "Customer"
            last_login_text = user['last_login'] if user['last_login'] else 'N/A'
            
            tags = (user['user_id'],)

            self.tree.insert('', tk.END, values=(
                user['user_id'], user['username'], user['full_name'], user['phone_no'], user_type_text, last_login_text
            ), tags=tags)


class ManageOffersFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        tk.Label(self, text="Manage Service Offers/Inventory", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(0, 20), anchor='w')

        # Action Buttons
        btn_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="Add New Offer", command=lambda: self._show_offer_dialog(), 
                  bg=COLOR_SUCCESS, fg="white", font=FONT_BODY).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Edit Selected Offer", command=lambda: self._edit_selected_offer(), 
                  bg=COLOR_PENDING, fg="white", font=FONT_BODY).pack(side='left', padx=5)
                  
        tk.Button(btn_frame, text="Delete Selected Offer", command=lambda: self._delete_selected_offer(), 
                  bg=COLOR_ERROR, fg="white", font=FONT_BODY).pack(side='left', padx=5) 
        # Treeview Setup
        columns = ('ID', 'Service Name', 'Labor Rate')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Service Name', text='Service Name')
        self.tree.heading('Labor Rate', text='Labor Rate (PHP)')

        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('Service Name', width=300)
        self.tree.column('Labor Rate', width=150, anchor='e')
        
        self.tree.pack(fill='both', expand=True, pady=10)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        self.offers = database.get_all_service_offers()
        for offer in self.offers:
            self.tree.insert('', tk.END, values=(
                offer['service_id'], offer['service_name'], f"{offer['labor_rate']:.2f}"
            ), tags=(offer['service_id'],))
            
        # Also refresh user service offers
        if "UserDashboard" in self.controller.frames and self.controller.frames["UserDashboard"].winfo_exists():
            self.controller.frames["UserDashboard"].content_frames["Home"].load_data()

    def _get_selected_offer(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a service offer to edit.")
            return None

        service_id = self.tree.item(selected_item, 'values')[0]
        offer_data = next((o for o in self.offers if str(o['service_id']) == service_id), None)
        return offer_data

    def _show_offer_dialog(self, offer_data=None):
        is_edit = offer_data is not None
        dialog = tk.Toplevel(self)
        dialog.title("Edit Offer" if is_edit else "Add New Offer")
        dialog.transient(self.controller)
        dialog.grab_set()
        dialog.lift()
        dialog.config(bg=COLOR_BACKGROUND)

        tk.Label(dialog, text="Service Name:", bg=COLOR_BACKGROUND).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        name_entry = ttk.Entry(dialog, width=35)
        name_entry.grid(row=0, column=1, pady=5)
        
        tk.Label(dialog, text="Labor Rate (PHP):", bg=COLOR_BACKGROUND).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        rate_entry = ttk.Entry(dialog, width=35)
        rate_entry.grid(row=1, column=1, pady=5)

        if is_edit:
            name_entry.insert(0, offer_data['service_name'])
            rate_entry.insert(0, offer_data['labor_rate'])

        def save_offer():
            name = name_entry.get().strip()
            rate_str = rate_entry.get().strip()
            
            try:
                rate = float(rate_str)
            except ValueError:
                messagebox.showerror("Input Error", "Labor Rate must be a valid number.")
                return
                
            if not name or rate <= 0:
                messagebox.showerror("Input Error", "Service Name is required and Rate must be positive.")
                return
            
            if is_edit:
                success, message = database.update_service_offer(offer_data['service_id'], name, rate)
            else:
                success, message = database.add_service_offer(name, rate)

            if success:
                messagebox.showinfo("Success", message)
                self.load_data()
                dialog.destroy()
            else:
                messagebox.showerror("Error", message)

        tk.Button(dialog, text="Save", command=save_offer, bg=COLOR_PRIMARY, fg="white").grid(row=2, column=1, pady=10, sticky='e', padx=5)

    def _edit_selected_offer(self):
        offer_data = self._get_selected_offer()
        if offer_data:
            self._show_offer_dialog(offer_data)

    def _delete_selected_offer(self):
        offer_data = self._get_selected_offer()
        if not offer_data:
            return
            
        if not messagebox.askyesno("Confirm Deletion", f"Are you sure you want to permanently delete the service '{offer_data['service_name']}'?"):
            return

        deleter_id = self.controller.get_current_user_id()
        success, message = database.delete_service_offer(deleter_id, offer_data['service_id'])
        
        if success:
            messagebox.showinfo("Success", message)
            self.load_data()
        else:
            messagebox.showerror("Failed", message)


class ManageVehiclesFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        tk.Label(self, text="View All Vehicles", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(0, 20), anchor='w')

        btn_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="Delete Selected Vehicle", command=self._delete_vehicle_command,
                  bg=COLOR_ERROR, fg="white", font=FONT_BODY).pack(side='left', padx=5) 

        columns = ('ID', 'User ID', 'Brand', 'Model', 'PlateNo')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('User ID', text='User ID')
        self.tree.heading('Brand', text='Brand')
        self.tree.heading('Model', text='Model')
        self.tree.heading('PlateNo', text='Plate No.')

        self.tree.column('ID', width=50, anchor='center')
        self.tree.column('User ID', width=70, anchor='center')
        self.tree.column('Brand', width=150)
        self.tree.column('Model', width=150)
        self.tree.column('PlateNo', width=100, anchor='center')
        
        self.tree.pack(fill='both', expand=True, pady=10)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        vehicles = database.get_all_vehicles()
        for vehicle in vehicles:
            self.tree.insert('', tk.END, values=(
                vehicle['vehicle_id'], vehicle['user_id'], vehicle['brand'], vehicle['model'], vehicle['plate_no']
            ), tags=(vehicle['vehicle_id'], vehicle['plate_no']))

    def _delete_vehicle_command(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a vehicle to delete.")
            return

        vehicle_id = self.tree.item(selected_item, 'values')[0]
        plate_no = self.tree.item(selected_item, 'values')[4]
        
        self.controller.delete_vehicle_by_admin(vehicle_id, plate_no)


class ManageAppointmentsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        tk.Label(self, text="Manage Appointments", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(0, 20), anchor='w')

        # Action Buttons
        btn_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="Approve", command=lambda: self._update_status('Approved'), 
                  bg=COLOR_SUCCESS, fg="white", font=FONT_BODY).pack(side='left', padx=5)
        
        tk.Button(btn_frame, text="Reject", command=lambda: self._update_status('Rejected'), 
                  bg=COLOR_ERROR, fg="white", font=FONT_BODY).pack(side='left', padx=5)
                  
        tk.Button(btn_frame, text="Mark Complete", command=lambda: self._update_status('Completed'), 
                  bg=COLOR_INFO, fg="white", font=FONT_BODY).pack(side='left', padx=5)

        tk.Button(btn_frame, text="Delete Selected (Rejected/Completed Only)", command=self._delete_appointment_command, 
                  bg=COLOR_ERROR, fg="white", font=FONT_BODY).pack(side='right', padx=5) 

        # Treeview Setup
        columns = ('ID', 'Name', 'PlateNo', 'Date', 'Time', 'Service', 'Cost', 'Status')
        self.tree = ttk.Treeview(self, columns=columns, show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Customer Name')
        self.tree.heading('PlateNo', text='Plate No.')
        self.tree.heading('Date', text='Date')
        self.tree.heading('Time', text='Time')
        self.tree.heading('Service', text='Service(s)')
        self.tree.heading('Cost', text='Total Cost')
        self.tree.heading('Status', text='Status')

        self.tree.column('ID', width=40, anchor='center')
        self.tree.column('Name', width=150)
        self.tree.column('PlateNo', width=80, anchor='center')
        self.tree.column('Date', width=80)
        self.tree.column('Time', width=60, anchor='center')
        self.tree.column('Service', width=180)
        self.tree.column('Cost', width=70, anchor='e')
        self.tree.column('Status', width=80, anchor='center')
        
        self.tree.tag_configure('Pending', background='#F0E68C')
        self.tree.tag_configure('Approved', background='#98FB98')
        self.tree.tag_configure('Rejected', background='#FFA07A')
        self.tree.tag_configure('Completed', background='#00BFFF')
        self.tree.tag_configure('Canceled', background='#ADD8E6') 

        self.tree.pack(fill='both', expand=True, pady=10)

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        appointments = database.get_all_appointments()
        for appt in appointments:
            if appt['is_deleted'] == 0: 
                status = appt['status']
                
                services_display = appt['services_names'].replace(' | ', ', ') if appt['services_names'] else 'N/A'
                total_cost_display = f"PHP {appt['total_cost']:.2f}" if appt['total_cost'] is not None else 'N/A'
                time_display = datetime.strptime(appt['time'], "%H:%M").strftime("%I:%M %p") 
                
                self.tree.insert('', tk.END, values=(
                    appt['appointment_id'], appt['full_name'], appt['plate_no'], appt['date'], appt['time'], 
                    services_display, total_cost_display, status
                ), tags=(appt['appointment_id'], status))
                
                # Apply color tag
                self.tree.item(self.tree.get_children()[-1], tags=(appt['appointment_id'], status, status))

    def _update_status(self, new_status):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select an appointment to update.")
            return

        values = self.tree.item(selected_item, 'values')
        appt_id = values[0]
        customer_name = values[1]
        
        if new_status == 'Approved' and values[7] in ('Approved', 'Completed', 'Canceled'):
            messagebox.showwarning("Status Error", f"Appointment is already {values[7]}. Cannot re-approve.")
            return
            
        self.controller.update_appt_status(appt_id, new_status, customer_name)
        self.load_data()

    def _delete_appointment_command(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select an appointment to delete.")
            return
            
        values = self.tree.item(selected_item, 'values')
        appt_id = values[0]
        status = values[7]
        
        self.controller.delete_appointment_by_admin(appt_id, status)
        self.load_data()


class ReportsFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=COLOR_BACKGROUND)
        self.controller = controller
        tk.Label(self, text="Reports and Analytics", font=FONT_TITLE, bg=COLOR_BACKGROUND, fg=COLOR_PRIMARY).pack(pady=(0, 20), anchor='w')

        # Report Type Selection
        self.report_type = tk.StringVar(value='Revenue') 
        report_types = ['Revenue', 'Daily Appointments']
        
        tk.Label(self, text="Select Report Type:", bg=COLOR_BACKGROUND).pack(anchor='w', pady=(5, 0))
        ttk.Combobox(self, textvariable=self.report_type, values=report_types, state="readonly", width=30).pack(anchor='w', pady=5)
        
        # Date Input for Daily Appointments
        date_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        date_frame.pack(anchor='w')
        tk.Label(date_frame, text="Date (YYYY-MM-DD):", bg=COLOR_BACKGROUND).pack(side='left', padx=(0, 5))
        self.date_entry = ttk.Entry(date_frame, width=20)
        self.date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
        self.date_entry.pack(side='left')

        tk.Button(self, text="Generate Report", command=self.load_data, 
                  bg=COLOR_PRIMARY, fg="white", font=FONT_BODY, width=20).pack(anchor='w', pady=10)

        # Output Area (Scrollable Text)
        self.report_output_frame = tk.Frame(self, bg='white', bd=1, relief=tk.SUNKEN)
        self.report_output_frame.pack(fill='both', expand=True)

        self.output_text = tk.Text(self.report_output_frame, wrap='word', height=20, bg='white', font=("Courier", 10))
        self.output_text.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(self.report_output_frame, command=self.output_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.output_text.config(yscrollcommand=scrollbar.set)

    def load_data(self):
        report_type = self.report_type.get()
        self.output_text.delete('1.0', tk.END)
        report_output = ""
        
        if report_type == 'Revenue':
            total_customers = database.get_total_active_customers()
            pending_appointments = database.get_pending_appointments_count()
            total_revenue = database.get_total_service_revenue()

            report_output += "REVENUE AND BUSINESS SUMMARY\n\n"
            report_output += f"Total Active Customers: {total_customers}\n"
            report_output += f"Pending Appointments for Review: {pending_appointments}\n"
            report_output += f"Total Revenue (from Completed Services): PHP {total_revenue:,.2f}\n"

        elif report_type == 'Daily Appointments':
            report_date = self.date_entry.get()
            try:
                datetime.strptime(report_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Input Error", "Invalid date format. Use YYYY-MM-DD.")
                return

            appointments = database.get_todays_appointments(report_date)
            
            report_output += f"DAILY APPOINTMENT REPORT FOR: {report_date}\n\n"
            report_output += f"Total Appointments Scheduled: {len(appointments)}\n\n"
            
            if appointments:
                report_output += "{:<25} {:<15} {:<10} {:<30}\n".format("Customer Name", "Plate No.", "Status", "Service Type") 
                report_output += "=" * 85 + "\n"
                for appt in appointments:
                    report_output += "{:<25} {:<15} {:<10} {:<30}\n".format(
                        appt['full_name'], appt['plate_no'], appt['status'], appt['service_type']
                    )
            else:
                report_output += "No appointments scheduled for this date."

        self.output_text.insert(tk.END, report_output)


class AdminMessageFrame(MessageFrame): #Admin's version of MessageFrame which needs user selection logic
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self.partner_id = None
        self.is_admin = True
        
        # User selection dropdown for Admin
        select_frame = tk.Frame(self, bg=COLOR_BACKGROUND)
        select_frame.pack(fill='x', pady=5)
        
        tk.Label(select_frame, text="Select Customer:", bg=COLOR_BACKGROUND).pack(side=tk.LEFT, padx=5)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(select_frame, textvariable=self.customer_var, state="readonly", width=40)
        self.customer_combo.pack(side=tk.LEFT, padx=5)
        self.customer_combo.bind("<<ComboboxSelected>>", self._on_customer_select)
        
        # Re-pack header label
        self.header_label.pack_forget()
        self.header_label.pack(pady=(0, 10), anchor='w')

    def load_data(self): # Only reload users on initial load
        if not self.customer_combo['values']:
            self._load_customer_options()
            
        if self.partner_id:
            super().load_data()
        else:
            for widget in self.scrollable_frame.winfo_children():
                widget.destroy()
            tk.Label(self.scrollable_frame, text="Please select a customer to start a chat.", bg='white').pack(padx=10, pady=10)

    def _load_customer_options(self):
        users = database.get_all_users()
        customer_options = []
        self.customer_map = {}
        for user in users:
            if user['user_type'] == 0:
                option = f"{user['full_name']} ({user['username']})"
                customer_options.append(option)
                self.customer_map[option] = user['user_id']
                
        self.customer_combo['values'] = customer_options
        self.customer_var.set("Select a customer...")

    def _on_customer_select(self, event):
        selected_option = self.customer_var.get()
        if selected_option in self.customer_map:
            user_id = self.customer_map[selected_option]
            self.set_partner_id(user_id, selected_option)
            self.load_data()
        
    def set_partner_id(self, partner_id, partner_name="No Customer Selected"):
        self.partner_id = partner_id
        self.header_label.config(text=f"Admin Chatting with: {partner_name}")
      
        if partner_id:
            for option, u_id in self.customer_map.items():
                if u_id == partner_id:
                    self.customer_var.set(option)
                    break