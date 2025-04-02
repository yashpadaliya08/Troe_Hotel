import tkinter as tk  
from tkinter import ttk, messagebox, simpledialog  
from tkcalendar import DateEntry  
import sqlite3  
import os
from datetime import datetime
import hashlib

class HotelManagementApp:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("Hotel Management System")  
        self.root.geometry("1024x768")

        # Hotel Management System Color Scheme
        self.COLORS = {
            'white': "#FFFFFF",      # Soft White - Main background
            'charcoal': "#333333",   # Charcoal Gray - Text
            'blue': "#4A90E2",       # Cool Blue - Interactive elements
            'beige': "#F5F5DC",      # Soft Beige - Secondary background
            'orange': "#FF9500",     # Warm Orange - Call to action
            'green': "#7ED957",      # Muted Green - Success messages
            'light_gray': "#F0F0F0", # Light Gray - Borders
            'dark_gray': "#7D7D7D",  # Dark Gray - Secondary text
            'new_color': "#FF5733",  # New button color (example)
            'new_color_active': "#C70039"  # New active button color (example)
        }

        # Configure window
        self.root.configure(bg=self.COLORS['beige'])

        # Initialize variables before creating frames
        self.initialize_variables()
        
        # Database initialization
        self.db_file = "hotel_management.db"
        self.initialize_database()

        # Configure styles
        self.setup_styles()

        # Create main container
        self.main_container = ttk.Frame(self.root, style='Main.TFrame')
        self.main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # Create header
        self.create_header()

        # Create Notebook
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill='both', expand=True, pady=(20, 0))

        # Create frames
        self.create_add_room_frame()
        self.create_book_room_frame()
        self.create_view_bookings_frame()
        self.create_customer_info_frame()

    def initialize_variables(self):
        """Initialize all variables needed for the application."""
        # Add Room variables
        self.room_type_var = tk.StringVar(value="Normal")
        self.ac_var = tk.StringVar(value="AC")
        self.wifi_var = tk.BooleanVar(value=True)
        self.capacity_var = tk.StringVar(value="2")
        self.status_var = tk.StringVar(value="available")

        # Book Room variables
        self.booking_room_type_var = tk.StringVar()
        self.booking_ac_var = tk.StringVar()
        self.num_persons_var = tk.StringVar(value="1")
        self.children_var = tk.StringVar(value="No")

    def create_header(self):
        """Create application header."""
        header = ttk.Frame(self.main_container, style='Header.TFrame')
        header.pack(fill='x', pady=(0, 20))

        title = ttk.Label(header, 
                         text="Hotel Management System",
                         style='HeaderTitle.TLabel')
        title.pack(side='left')

        # Add current date
        date = datetime.now().strftime("%B %d, %Y")
        date_label = ttk.Label(header, 
                             text=date,
                             style='HeaderDate.TLabel')
        date_label.pack(side='right')

    def setup_styles(self):
        """Configure ttk styles for the application"""
        self.style = ttk.Style()
        
        # Define the 'surface' style
        self.style.configure('surface', background=self.COLORS['white'])  # or any color you prefer
        
        # Define the 'alternate_row' style
        self.style.configure('alternate_row', background=self.COLORS['light_gray'])  # or any color you prefer
        
        # Main Frame
        self.style.configure('Main.TFrame',
                           background=self.COLORS['beige'])

        # Header Styles
        self.style.configure('Header.TFrame',
                           background=self.COLORS['beige'])
        self.style.configure('HeaderTitle.TLabel',
                           background=self.COLORS['beige'],
                           foreground=self.COLORS['blue'],
                           font=('Helvetica', 24, 'bold'))
        self.style.configure('HeaderDate.TLabel',
                           background=self.COLORS['beige'],
                           foreground=self.COLORS['dark_gray'],
                           font=('Helvetica', 12))

        # Content Frame
        self.style.configure('Content.TFrame',
                           background=self.COLORS['white'])

        # Form Styles
        self.style.configure('Form.TFrame',
                           background=self.COLORS['white'])
        self.style.configure('Form.TLabel',
                           background=self.COLORS['white'],
                           foreground=self.COLORS['charcoal'],
                           font=('Helvetica', 10))
        self.style.configure('FormHeader.TLabel',
                           background=self.COLORS['white'],
                           foreground=self.COLORS['blue'],
                           font=('Helvetica', 16, 'bold'))

        # Button Styles
        self.style.configure('Primary.TButton',
                           background=self.COLORS['new_color'],
                           foreground=self.COLORS['white'],
                           padding=(20, 10),
                           font=('Helvetica', 10, 'bold'))
        self.style.map('Primary.TButton',
                      background=[('active', self.COLORS['new_color_active'])])
        
        self.style.configure('Secondary.TButton',
                           background=self.COLORS['new_color'],
                           foreground=self.COLORS['white'],
                           padding=(20, 10),
                           font=('Helvetica', 10))
        self.style.map('Secondary.TButton',
                      background=[('active', self.COLORS['new_color_active'])])

        # Treeview Styles
        self.style.configure('Treeview',
                           background=self.COLORS['white'],
                           foreground=self.COLORS['charcoal'],
                           rowheight=30,
                           fieldbackground=self.COLORS['white'])
        self.style.configure('Treeview.Heading',
                           background=self.COLORS['blue'],
                           foreground=self.COLORS['white'],
                           font=('Helvetica', 10, 'bold'))
        self.style.map('Treeview',
                      background=[('selected', self.COLORS['light_gray'])],
                      foreground=[('selected', self.COLORS['charcoal'])])

        # Notebook Styles
        self.style.configure('TNotebook',
                           background=self.COLORS['beige'])
        self.style.configure('TNotebook.Tab',
                           background=self.COLORS['white'],
                           foreground=self.COLORS['charcoal'],
                           padding=[20, 10],
                           font=('Helvetica', 10))
        self.style.map('TNotebook.Tab',
                      background=[('selected', self.COLORS['blue'])],
                      foreground=[('selected', self.COLORS['white'])])

        # Entry Styles
        self.style.configure('TEntry',
                           fieldbackground=self.COLORS['white'],
                           foreground=self.COLORS['charcoal'])

        # Combobox Styles
        self.style.configure('TCombobox',
                           background=self.COLORS['white'],
                           foreground=self.COLORS['charcoal'])

    def initialize_database(self):
        """Initialize database connection and create backup"""
        try:
            # Create backup of existing database if it exists
            if os.path.exists(self.db_file):
                backup_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_file = f"backup_{backup_time}.db"
                try:
                    with open(self.db_file, 'rb') as src, open(backup_file, 'wb') as dst:
                        dst.write(src.read())
                except IOError as e:
                    print(f"Warning: Could not create backup: {str(e)}")

            # Create or connect to database
            self.conn = sqlite3.connect(self.db_file)
            
            # Enable foreign key support
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            self.create_tables()
            
            print("Database initialized successfully")
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {str(e)}")
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
            raise Exception("Database initialization failed")

    def create_tables(self):
        """Create the SQLite tables with enhanced structure."""
        try:
            cursor = self.conn.cursor()
            
            # Room table with capacity
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS rooms (
                room_number INTEGER PRIMARY KEY,
                room_type TEXT NOT NULL,
                ac_type TEXT NOT NULL,
                price REAL NOT NULL CHECK (price > 0),
                capacity INTEGER NOT NULL CHECK (capacity > 0 AND capacity <= 4),
                wifi INTEGER NOT NULL,
                status TEXT DEFAULT 'available' CHECK (status IN ('available', 'booked', 'maintenance'))
            )
            """)

            # Booking table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name TEXT NOT NULL,
                room_number INTEGER NOT NULL,
                check_in_date DATE NOT NULL,
                check_out_date DATE NOT NULL,
                num_persons INTEGER NOT NULL,
                children TEXT NOT NULL,
                status TEXT DEFAULT 'active',
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_number) REFERENCES rooms(room_number)
            )
            """)
            
            self.conn.commit()
            print("Tables created successfully")
            
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Error creating tables: {str(e)}")
            messagebox.showerror("Database Error", f"Failed to create tables: {str(e)}")
            raise Exception("Table creation failed")

    def create_add_room_frame(self):
        """Create the frame for adding rooms with fixed width."""
        self.frame_add_room = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.frame_add_room, text="Add Room")

        # Main container with fixed width
        main_container = ttk.Frame(self.frame_add_room, style='Content.TFrame')
        main_container.pack(fill='both', expand=True, padx=50, pady=20)
        
        # Ensure main container maintains a minimum width
        main_container.grid_columnconfigure(0, minsize=600)

        # Header
        header_frame = ttk.Frame(main_container, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(header_frame, text="Add New Room",
                 style='FormHeader.TLabel').pack()

        # Form container with grid layout
        form_container = ttk.Frame(main_container, style='Form.TFrame')
        form_container.pack(fill='both', expand=True)
        
        # Configure grid columns
        form_container.grid_columnconfigure(1, weight=1, minsize=200)
        
        # Room Number
        ttk.Label(form_container, text="Room Number:", 
                 style='Form.TLabel').grid(row=0, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        self.room_number_entry = ttk.Entry(form_container, width=30)
        self.room_number_entry.grid(row=0, column=1, sticky='w')

        # Room Type
        ttk.Label(form_container, text="Room Type:", 
                 style='Form.TLabel').grid(row=1, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        room_type_combo = ttk.Combobox(form_container, 
                                      textvariable=self.room_type_var,
                                      values=["Normal", "Deluxe", "Premium", "Suite"],
                                      state="readonly", width=27)
        room_type_combo.grid(row=1, column=1, sticky='w')

        # AC Type
        ttk.Label(form_container, text="AC/Non-AC:", 
                 style='Form.TLabel').grid(row=2, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        ac_combo = ttk.Combobox(form_container, 
                               textvariable=self.ac_var,
                               values=["AC", "Non-AC"],
                               state="readonly", width=27)
        ac_combo.grid(row=2, column=1, sticky='w')

        # Price
        ttk.Label(form_container, text="Price per Night:", 
                 style='Form.TLabel').grid(row=3, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        self.price_entry = ttk.Entry(form_container, width=30)
        self.price_entry.grid(row=3, column=1, sticky='w')

        # Capacity
        ttk.Label(form_container, text="Capacity:", 
                 style='Form.TLabel').grid(row=4, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        capacity_combo = ttk.Combobox(form_container, 
                                    textvariable=self.capacity_var,
                                    values=["1", "2", "3", "4"],
                                    state="readonly", width=27)
        capacity_combo.grid(row=4, column=1, sticky='w')

        # WiFi
        ttk.Label(form_container, text="Free Wi-Fi:", 
                 style='Form.TLabel').grid(row=5, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        wifi_check = ttk.Checkbutton(form_container, variable=self.wifi_var)
        wifi_check.grid(row=5, column=1, sticky='w')

        # Room Status
        ttk.Label(form_container, text="Room Status:", 
                 style='Form.TLabel').grid(row=6, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        status_combo = ttk.Combobox(form_container, 
                                  textvariable=self.status_var,
                                  values=["available", "maintenance"],
                                  state="readonly", width=27)
        status_combo.grid(row=6, column=1, sticky='w')

        # Buttons frame
        button_frame = ttk.Frame(main_container, style='Form.TFrame')
        button_frame.pack(fill='x', pady=20)

        # Configure button frame columns
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Add Room Button
        ttk.Button(button_frame, text="Add Room",
                  command=self.add_room,
                  style='Primary.TButton', width=20).grid(row=0, column=0, padx=5)

        # Clear Button
        ttk.Button(button_frame, text="Clear",
                  command=self.clear_room_fields,
                  style='Secondary.TButton', width=20).grid(row=0, column=1, padx=5)

        # View Rooms Button
        ttk.Button(button_frame, text="View Rooms",
                  command=self.view_rooms,
                  style='Secondary.TButton', width=20).grid(row=0, column=2, padx=5)

    def create_book_room_frame(self):
        """Create the frame for booking rooms with improved layout."""
        self.frame_book_room = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.frame_book_room, text="Book Room")

        # Main container with fixed width
        main_container = ttk.Frame(self.frame_book_room, style='Content.TFrame')
        main_container.pack(fill='both', expand=True, padx=50, pady=20)
        
        # Ensure main container maintains a minimum width
        main_container.grid_columnconfigure(0, minsize=600)

        # Header
        header_frame = ttk.Frame(main_container, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(header_frame, text="Book a Room",
                 style='FormHeader.TLabel').pack()

        # Form container with grid layout
        form_container = ttk.Frame(main_container, style='Form.TFrame')
        form_container.pack(fill='both', expand=True)
        
        # Configure grid columns
        form_container.grid_columnconfigure(1, weight=1, minsize=200)

        # Customer Name
        ttk.Label(form_container, text="Name:", 
                 style='Form.TLabel').grid(row=0, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        self.person_name_entry = ttk.Entry(form_container, width=30)
        self.person_name_entry.grid(row=0, column=1, sticky='w')

        # Room Type
        ttk.Label(form_container, text="Room Type:", 
                 style='Form.TLabel').grid(row=1, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        room_type_combo = ttk.Combobox(form_container, 
                                      textvariable=self.booking_room_type_var,
                                      values=["Normal", "Deluxe", "Premium", "Suite"],
                                      state="readonly", width=27)
        room_type_combo.grid(row=1, column=1, sticky='w')

        # Check-in Date
        ttk.Label(form_container, text="Check-in Date:", 
                 style='Form.TLabel').grid(row=2, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        self.check_in_entry = DateEntry(form_container, width=27, 
                                      background=self.COLORS['blue'],
                                      foreground=self.COLORS['white'],
                                      borderwidth=2,
                                      date_pattern='yyyy-mm-dd')
        self.check_in_entry.grid(row=2, column=1, sticky='w')

        # Check-out Date
        ttk.Label(form_container, text="Check-out Date:", 
                 style='Form.TLabel').grid(row=3, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        self.check_out_entry = DateEntry(form_container, width=27, 
                                       background=self.COLORS['blue'],
                                       foreground=self.COLORS['white'],
                                       borderwidth=2,
                                       date_pattern='yyyy-mm-dd')
        self.check_out_entry.grid(row=3, column=1, sticky='w')

        # Number of Persons
        ttk.Label(form_container, text="Number of Persons:", 
                 style='Form.TLabel').grid(row=4, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        num_persons_combo = ttk.Combobox(form_container, 
                                        textvariable=self.num_persons_var,
                                        values=["1", "2", "3", "4"],
                                        state="readonly", width=27)
        num_persons_combo.grid(row=4, column=1, sticky='w')

        # Children
        ttk.Label(form_container, text="Children:", 
                 style='Form.TLabel').grid(row=5, column=0, padx=(0, 10), 
                                         pady=10, sticky='e')
        children_combo = ttk.Combobox(form_container, 
                                     textvariable=self.children_var,
                                     values=["Yes", "No"],
                                     state="readonly", width=27)
        children_combo.grid(row=5, column=1, sticky='w')

        # Button frame
        button_frame = ttk.Frame(main_container, style='Form.TFrame')
        button_frame.pack(fill='x', pady=20)

        # Configure button frame columns
        button_frame.grid_columnconfigure(0, weight=1)

        # Check Availability Button
        ttk.Button(button_frame, text="Check Availability",
                  command=self.check_availability,
                  style='Primary.TButton', width=20).grid(row=0, column=0)

    def create_view_bookings_frame(self):
        """Create the frame for viewing bookings with improved layout."""
        self.frame_view_bookings = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.frame_view_bookings, text="View Bookings")

        # Main container with fixed width
        main_container = ttk.Frame(self.frame_view_bookings, style='Content.TFrame')
        main_container.pack(fill='both', expand=True, padx=50, pady=20)
        
        # Ensure main container maintains a minimum width
        main_container.grid_columnconfigure(0, minsize=600)

        # Header
        header_frame = ttk.Frame(main_container, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(header_frame, text="Booking Management",
                 style='FormHeader.TLabel').pack()

        # Button container with grid layout
        button_frame = ttk.Frame(main_container, style='Form.TFrame')
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Configure button frame columns
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Buttons
        ttk.Button(button_frame, text="View All Bookings",
                  command=self.view_bookings,
                  style='Primary.TButton', width=20).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="View Rooms",
                  command=self.view_rooms,
                  style='Secondary.TButton', width=20).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Cancel Booking",
                  command=self.cancel_booking,
                  style='Secondary.TButton', width=20).grid(row=0, column=2, padx=5)

        # Create Treeview with scrollbar
        tree_frame = ttk.Frame(main_container, style='Content.TFrame')
        tree_frame.pack(fill='both', expand=True)

        columns = ("Booking ID", "Customer", "Room", "Check-in", "Check-out", "Status")
        self.booking_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Configure columns with specific widths
        widths = {
            "Booking ID": 100,
            "Customer": 200,
            "Room": 100,
            "Check-in": 100,
            "Check-out": 100,
            "Status": 100
        }
        
        for col in columns:
            self.booking_tree.heading(col, text=col)
            self.booking_tree.column(col, width=widths[col], anchor='center')

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                   command=self.booking_tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, 
                                   command=self.booking_tree.xview)
        self.booking_tree.configure(yscroll=y_scrollbar.set, xscroll=x_scrollbar.set)

        # Pack elements
        self.booking_tree.pack(side='left', fill='both', expand=True)
        y_scrollbar.pack(side='right', fill='y')
        x_scrollbar.pack(side='bottom', fill='x')

    def create_customer_info_frame(self):
        """Create the frame for customer information with improved layout."""
        self.frame_customer_info = ttk.Frame(self.notebook, style='Content.TFrame')
        self.notebook.add(self.frame_customer_info, text="Customer Info")

        # Main container with fixed width
        main_container = ttk.Frame(self.frame_customer_info, style='Content.TFrame')
        main_container.pack(fill='both', expand=True, padx=50, pady=20)
        
        # Ensure main container maintains a minimum width
        main_container.grid_columnconfigure(0, minsize=600)

        # Header
        header_frame = ttk.Frame(main_container, style='Content.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        ttk.Label(header_frame, text="Customer Information",
                 style='FormHeader.TLabel').pack()

        # Button frame
        button_frame = ttk.Frame(main_container, style='Form.TFrame')
        button_frame.pack(fill='x', pady=(0, 20))
        
        # Configure button frame columns
        button_frame.grid_columnconfigure(0, weight=1)

        # Refresh button
        ttk.Button(button_frame, text="Refresh Information",
                  command=self.refresh_customer_info,
                  style='Primary.TButton', width=20).grid(row=0, column=0)

        # Create Treeview with scrollbar
        tree_frame = ttk.Frame(main_container, style='Content.TFrame')
        tree_frame.pack(fill='both', expand=True)

        columns = ("Customer Name", "Room Number", "Price", "Check-in", "Check-out", "Status")
        self.customer_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Configure columns with specific widths
        widths = {
            "Customer Name": 200,
            "Room Number": 100,
            "Price": 100,
            "Check-in": 100,
            "Check-out": 100,
            "Status": 100
        }
        
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=widths[col], anchor='center')

        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                   command=self.customer_tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, 
                                   command=self.customer_tree.xview)
        self.customer_tree.configure(yscroll=y_scrollbar.set, xscroll=x_scrollbar.set)

        # Pack elements
        self.customer_tree.pack(side='left', fill='both', expand=True)
        y_scrollbar.pack(side='right', fill='y')
        x_scrollbar.pack(side='bottom', fill='x')

    def add_room(self):
        """Add a room with validation and error handling."""
        try:
            # Get input values
            room_number = self.room_number_entry.get().strip()
            room_type = self.room_type_var.get()
            ac_type = self.ac_var.get()
            price = self.price_entry.get().strip()
            capacity = int(self.capacity_var.get())
            wifi = 1 if self.wifi_var.get() else 0
            status = self.status_var.get()

            # Input validation
            if not all([room_number, room_type, ac_type, price]):
                raise ValueError("All fields must be filled")

            if not room_number.isalnum():
                raise ValueError("Room number must contain only letters and numbers")

            try:
                price = float(price)
                if price <= 0:
                    raise ValueError("Price must be greater than 0")
            except ValueError:
                raise ValueError("Price must be a valid number")

            def insert_room(cursor):
                # Check if room number already exists
                cursor.execute("SELECT room_number FROM rooms WHERE room_number = ?", 
                             (room_number,))
                if cursor.fetchone():
                    raise ValueError("Room number already exists")

                cursor.execute("""
                    INSERT INTO rooms (room_number, room_type, ac_type, price, 
                                     capacity, wifi, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (room_number, room_type, ac_type, price, capacity, wifi, status))

            if self.execute_db_operation(insert_room):
                messagebox.showinfo("Success", "Room added successfully!")
                self.clear_room_fields()
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def check_availability(self):
        """Check room availability with improved error handling."""
        try:
            # Get input values
            check_in = self.check_in_entry.get_date()
            check_out = self.check_out_entry.get_date()
            room_type = self.booking_room_type_var.get()
            
            if not all([check_in, check_out, room_type]):
                raise ValueError("Please fill all required fields")

            # Ensure check-in is before check-out
            if check_in >= check_out:
                raise ValueError("Check-in date must be before check-out date")

            def find_available_rooms(cursor):
                cursor.execute(""" 
                    SELECT r.room_number, r.room_type, r.ac_type, r.price,
                           CASE WHEN r.wifi = 1 THEN 'Yes' ELSE 'No' END as wifi,
                           (SELECT COUNT(*) FROM bookings b WHERE b.room_number = r.room_number AND b.status = 'active') as booked
                    FROM rooms r
                    WHERE r.room_type = ?
                    AND r.status = 'available'
                    AND r.room_number NOT IN (
                        SELECT room_number
                        FROM bookings
                        WHERE status = 'active'
                        AND (
                            (check_in_date < ? AND check_out_date > ?)
                        )
                    )
                """, (room_type, check_out.strftime('%Y-%m-%d'), 
                     check_in.strftime('%Y-%m-%d')))
                return cursor.fetchall()

            available_rooms = self.execute_db_operation(find_available_rooms)

            if not available_rooms:
                messagebox.showinfo("No Rooms", 
                                  "No rooms available for the selected dates.")
                return

            self.show_available_rooms(
                available_rooms,
                self.person_name_entry.get(),
                check_in.strftime('%Y-%m-%d'),
                check_out.strftime('%Y-%m-%d'),
                self.num_persons_var.get(),
                self.children_var.get()
            )

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Database operation failed: {str(e)}")
        except Exception as e:
            messagebox.showerror("Unexpected Error", f"An unexpected error occurred: {str(e)}")

    def show_available_rooms(self, available_rooms, person_name, check_in_date, 
                           check_out_date, num_persons, children):
        """Show available rooms in a new window."""
        room_select_window = tk.Toplevel(self.root)
        room_select_window.title("Available Rooms")
        room_select_window.geometry("800x500")
        room_select_window.configure(bg=self.COLORS['beige'])

        # Header
        header_frame = ttk.Frame(room_select_window, style='Header.TFrame')
        header_frame.pack(fill='x', padx=20, pady=20)
        
        ttk.Label(header_frame, 
                 text="Available Rooms for Your Dates",
                 style='HeaderTitle.TLabel').pack()

        # Create Treeview
        tree_frame = ttk.Frame(room_select_window, style='Content.TFrame')
        tree_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        columns = ("Room Number", "Type", "AC/Non-AC", "Price", "WiFi", "Booked")
        room_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            room_tree.heading(col, text=col)
            room_tree.column(col, width=150)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, 
                                command=room_tree.yview)
        room_tree.configure(yscroll=scrollbar.set)
        
        # Pack Treeview and scrollbar
        room_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Insert available rooms with alternating colors
        for i, room in enumerate(available_rooms):
            room_tree.insert("", "end", values=room, 
                           tags=('evenrow' if i % 2 == 0 else 'oddrow'))

        room_tree.tag_configure('evenrow', background=self.COLORS['light_gray'])
        room_tree.tag_configure('oddrow', background=self.COLORS['white'])

        # Button frame
        button_frame = ttk.Frame(room_select_window, style='Content.TFrame')
        button_frame.pack(fill='x', padx=20, pady=20)

        ttk.Button(button_frame, 
                  text="Book Selected Room",
                  style='Primary.TButton',
                  command=lambda: self.book_selected_room(
                      room_tree, room_select_window, person_name,
                      check_in_date, check_out_date, num_persons, children
                  )).pack(pady=10)

    def show_booking_confirmation(self, room_data, check_in_date, check_out_date, total_price):
        """Show booking confirmation window."""
        confirm_window = tk.Toplevel(self.root)
        confirm_window.title("Booking Confirmation")
        confirm_window.geometry("400x500")
        confirm_window.configure(bg=self.COLORS['background'])

        # Main container
        main_frame = ttk.Frame(confirm_window, style='Content.TFrame')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Success icon or message
        ttk.Label(main_frame, 
                 text="✓ Booking Confirmed!",
                 style='HeaderTitle.TLabel').pack(pady=(0, 20))

        # Details frame
        details_frame = ttk.Frame(main_frame, style='Form.TFrame')
        details_frame.pack(fill='both', expand=True)

        # Booking details
        details = [
            ("Room Number:", room_data[0]),
            ("Room Type:", room_data[1]),
            ("Check-in:", check_in_date),
            ("Check-out:", check_out_date),
            ("Total Price:", f"${total_price:.2f}")
        ]

        for label, value in details:
            row_frame = ttk.Frame(details_frame, style='Form.TFrame')
            row_frame.pack(fill='x', pady=5)
            ttk.Label(row_frame, text=label, 
                     style='Form.TLabel').pack(side='left')
            ttk.Label(row_frame, text=str(value), 
                     style='Form.TLabel').pack(side='right')

        # OK button
        ttk.Button(main_frame, 
                  text="OK",
                  style='Primary.TButton',
                  command=confirm_window.destroy).pack(pady=20)

    def view_bookings(self):
        """View all current bookings."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT b.booking_id, b.person_name, b.room_number, 
                       b.check_in_date, b.check_out_date, b.status
                FROM bookings b
                ORDER BY b.check_in_date
            """)
            bookings = cursor.fetchall()

            # Clear existing items
            for item in self.booking_tree.get_children():
                self.booking_tree.delete(item)

            # Insert new bookings with alternating colors
            for i, booking in enumerate(bookings):
                self.booking_tree.insert("", "end", values=booking,
                                       tags=('evenrow' if i % 2 == 0 else 'oddrow'))

            self.booking_tree.tag_configure('evenrow', background=self.COLORS['white'])
            self.booking_tree.tag_configure('oddrow', background=self.COLORS['white'])

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to retrieve bookings: {str(e)}")

    def view_rooms(self):
        """View all rooms in a new window with fixed column widths."""
        try:
            def fetch_rooms(cursor):
                cursor.execute("""
                    SELECT room_number, room_type, ac_type, price, capacity,
                           CASE WHEN wifi = 1 THEN 'Yes' ELSE 'No' END as wifi,
                           status
                    FROM rooms
                    ORDER BY room_number
                """)
                return cursor.fetchall()

            rooms = self.execute_db_operation(fetch_rooms)

            if not rooms:
                messagebox.showinfo("No Rooms", "No rooms are currently registered.")
                return

            # Create a new window with fixed size
            room_window = tk.Toplevel(self.root)
            room_window.title("Room Details")
            room_window.geometry("1000x600")
            room_window.configure(bg=self.COLORS['beige'])

            # Create main container
            main_container = ttk.Frame(room_window, style='Content.TFrame')
            main_container.pack(fill='both', expand=True, padx=20, pady=20)

            # Header
            ttk.Label(main_container, text="Room Information",
                     style='FormHeader.TLabel').pack(fill='x', pady=(0, 20))

            # Create Treeview with specific column widths
            columns = ("Room Number", "Type", "AC/Non-AC", "Price", 
                      "Capacity", "WiFi", "Status")
            room_tree = ttk.Treeview(main_container, columns=columns, 
                                   show="headings", style='Treeview')
            
            # Configure column widths
            widths = {
                "Room Number": 100,
                "Type": 150,
                "AC/Non-AC": 100,
                "Price": 100,
                "Capacity": 80,
                "WiFi": 80,
                "Status": 100
            }
            
            for col in columns:
                room_tree.heading(col, text=col)
                room_tree.column(col, width=widths[col], anchor='center')

            # Add scrollbars
            y_scrollbar = ttk.Scrollbar(main_container, orient=tk.VERTICAL, 
                                      command=room_tree.yview)
            x_scrollbar = ttk.Scrollbar(main_container, orient=tk.HORIZONTAL, 
                                      command=room_tree.xview)
            room_tree.configure(yscroll=y_scrollbar.set, xscroll=x_scrollbar.set)
            
            # Pack elements
            room_tree.pack(side='left', fill='both', expand=True)
            y_scrollbar.pack(side='right', fill='y')
            x_scrollbar.pack(side='bottom', fill='x')

            # Insert room data with alternating colors
            for i, room in enumerate(rooms):
                room_tree.insert("", "end", values=room,
                               tags=('evenrow' if i % 2 == 0 else 'oddrow'))

            # Configure row colors
            room_tree.tag_configure('evenrow', background=self.COLORS['white'])
            room_tree.tag_configure('oddrow', background=self.COLORS['white'])

        except Exception as e:
            messagebox.showerror("Error", f"Failed to view rooms: {str(e)}")

    def cancel_booking(self):
        """Cancel an existing booking."""
        try:
            selected_item = self.booking_tree.selection()
            if not selected_item:
                messagebox.showwarning("Selection Required", 
                                     "Please select a booking to cancel.")
                return

            booking_data = self.booking_tree.item(selected_item[0])['values']
            booking_id = booking_data[0]
            room_number = booking_data[2]

            confirm = messagebox.askyesno("Confirm Cancellation", 
                f"Are you sure you want to cancel booking ID {booking_id}?")
            
            if confirm:
                cursor = self.conn.cursor()
                # Update booking status
                cursor.execute("""
                    UPDATE bookings 
                    SET status = 'cancelled' 
                    WHERE booking_id = ?
                """, (booking_id,))

                # Update room status
                cursor.execute("""
                    UPDATE rooms 
                    SET status = 'available' 
                    WHERE room_number = ?
                """, (room_number,))

                self.conn.commit()
                messagebox.showinfo("Success", "Booking cancelled successfully!")
                self.view_bookings()
                self.refresh_customer_info()

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to cancel booking: {str(e)}")
            self.conn.rollback()

    def refresh_customer_info(self):
        """Refresh the customer information display."""
        try:
            # Clear existing items
            for item in self.customer_tree.get_children():
                self.customer_tree.delete(item)

            # Fetch current bookings
            cursor = self.conn.cursor()
            cursor.execute(""" 
                SELECT b.person_name, b.room_number, r.price, 
                       b.check_in_date, b.check_out_date, b.status
                FROM bookings b
                JOIN rooms r ON b.room_number = r.room_number
                WHERE b.status = 'active'
                ORDER BY b.check_in_date
            """)
            
            # Insert into treeview with alternating colors
            for i, booking in enumerate(cursor.fetchall()):
                self.customer_tree.insert("", "end", values=booking,
                                        tags=('evenrow' if i % 2 == 0 else 'oddrow'))

            self.customer_tree.tag_configure('evenrow', background=self.COLORS['white'])
            self.customer_tree.tag_configure('oddrow', background=self.COLORS['white'])

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to refresh customer info: {str(e)}")

    def clear_room_fields(self):
        """Clear all room input fields."""
        self.room_number_entry.delete(0, tk.END)
        self.room_type_var.set("Normal")
        self.ac_var.set("AC")
        self.price_entry.delete(0, tk.END)
        self.capacity_var.set("2")
        self.wifi_var.set(True)
        self.status_var.set("available")

    def clear_booking_fields(self):
        """Clear all booking input fields."""
        self.person_name_entry.delete(0, tk.END)
        self.booking_room_type_var.set("")
        self.booking_ac_var.set("")
        self.num_persons_entry.delete(0, tk.END)
        self.children_var.set("")
        self.budget_entry.delete(0, tk.END)

    def cleanup(self):
        """Clean up resources before closing."""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.commit()
                self.conn.close()
                self.conn = None
        except sqlite3.Error as e:
            print(f"Error during cleanup: {str(e)}")

    def on_closing(self):
        """Handle application closing."""
        try:
            self.cleanup()
            messagebox.showinfo("Goodbye", "Thank you for using Hotel Management System!")
            self.root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error while closing: {str(e)}")
            self.root.destroy()

    def execute_db_operation(self, operation_func):
        """Safely execute a database operation with error handling."""
        if not hasattr(self, 'conn') or self.conn is None:
            self.initialize_database()
            
        cursor = self.conn.cursor()
        try:
            result = operation_func(cursor)
            self.conn.commit()
            return result
        except sqlite3.Error as e:
            self.conn.rollback()
            print(f"Database operation error: {str(e)}")
            messagebox.showerror("Database Error", f"Operation failed: {str(e)}")
            return None

    def verify_database_structure(self):
        """Verify that all required tables and columns exist."""
        try:
            cursor = self.conn.cursor()
            
            # Check rooms table structure
            cursor.execute("PRAGMA table_info(rooms)")
            rooms_columns = {row[1] for row in cursor.fetchall()}
            required_rooms_columns = {
                'room_number', 'room_type', 'ac_type', 
                'price', 'wifi', 'status'
            }
            
            # Check bookings table structure
            cursor.execute("PRAGMA table_info(bookings)")
            bookings_columns = {row[1] for row in cursor.fetchall()}
            required_bookings_columns = {
                'booking_id', 'person_name', 'room_number',
                'check_in_date', 'check_out_date', 'num_persons',
                'children', 'status', 'booking_date'
            }
            
            # If any required columns are missing, recreate the tables
            if not (required_rooms_columns.issubset(rooms_columns) and 
                    required_bookings_columns.issubset(bookings_columns)):
                print("Database structure mismatch, recreating tables...")
                
                # Drop existing tables
                cursor.execute("DROP TABLE IF EXISTS bookings")
                cursor.execute("DROP TABLE IF EXISTS rooms")
                
                # Recreate tables
                self.create_tables()
                
            self.conn.commit()
            return True
            
        except sqlite3.Error as e:
            print(f"Error verifying database structure: {str(e)}")
            return False

    def debug_database(self):
        """Print current database structure for debugging."""
        try:
            cursor = self.conn.cursor()
            
            # Print rooms table structure
            print("\nRooms table structure:")
            cursor.execute("PRAGMA table_info(rooms)")
            for row in cursor.fetchall():
                print(row)
            
            # Print bookings table structure
            print("\nBookings table structure:")
            cursor.execute("PRAGMA table_info(bookings)")
            for row in cursor.fetchall():
                print(row)
            
        except sqlite3.Error as e:
            print(f"Error debugging database: {str(e)}")

    def book_selected_room(self, room_tree, room_select_window, person_name,
                           check_in_date, check_out_date, num_persons, children):
        """Book the selected room."""
        selected_item = room_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a room to book.")
            return

        room_data = room_tree.item(selected_item[0])['values']
        room_number = room_data[0]  # Assuming the first column is Room Number

        try:
            def insert_booking(cursor):
                cursor.execute(""" 
                    INSERT INTO bookings (person_name, room_number, check_in_date, 
                                          check_out_date, num_persons, children)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (person_name, room_number, check_in_date, check_out_date, 
                      num_persons, children))

            self.execute_db_operation(insert_booking)
            messagebox.showinfo("Success", f"Room {room_number} booked successfully!")
            room_select_window.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to book room: {str(e)}")

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Management System - Login")
        self.root.geometry("400x300")

        # Create main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill='both', expand=True, padx=40, pady=40)

        # Create login form
        self.create_login_form()

        # Database connection
        self.db_file = "hotel_management.db"
        self.conn = sqlite3.connect(self.db_file)
        self.conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support

        # Ensure emp table exists
        self.create_emp_table()

    def create_emp_table(self):
        """Create the emp table if it doesn't exist."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS emp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL
                )
            """)
            self.conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error creating emp table: {str(e)}")

    def create_login_form(self):
        """Create the login form"""
        # Header
        ttk.Label(self.main_container,
                 text="Login to Hotel Management System",
                 font=('Helvetica', 16)).pack(pady=(0, 20))

        # Username
        ttk.Label(self.main_container,
                 text="Username:").pack(anchor='w')
        self.username_entry = ttk.Entry(self.main_container, width=30)
        self.username_entry.pack(fill='x', pady=(0, 10))

        # Password
        ttk.Label(self.main_container,
                 text="Password:").pack(anchor='w')
        self.password_entry = ttk.Entry(self.main_container, show="•", width=30)
        self.password_entry.pack(fill='x', pady=(0, 20))

        # Login button
        ttk.Button(self.main_container,
                  text="Login",
                  command=self.login).pack(fill='x')

        # Register button
        ttk.Button(self.main_container,
                  text="Register",
                  command=self.open_registration_window).pack(fill='x', pady=(10, 0))

    def login(self):
        """Handle login attempt"""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        # Hash the password for comparison
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Check the username and password against the database
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM emp WHERE username = ? AND password = ?", (username, hashed_password))
            user = cursor.fetchone()

            if user:
                messagebox.showinfo("Success", "Login successful!")
                self.root.destroy()  # Close the login window
                self.open_main_app()  # Open the main application
            else:
                messagebox.showerror("Error", "Invalid username or password")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error during login: {str(e)}")

    def open_main_app(self):
        """Open the main application window"""
        app_window = tk.Tk()
        app = HotelManagementApp(app_window)
        app_window.protocol("WM_DELETE_WINDOW", app.on_closing)
        app_window.mainloop()

    def open_registration_window(self):
        """Open the registration window"""
        registration_window = tk.Toplevel(self.root)
        registration_window.title("Register")
        registration_window.geometry("400x300")

        # Create registration form
        ttk.Label(registration_window, text="Register a New Account", font=('Helvetica', 16)).pack(pady=(0, 20))

        ttk.Label(registration_window, text="Username:").pack(anchor='w')
        username_entry = ttk.Entry(registration_window, width=30)
        username_entry.pack(fill='x', pady=(0, 10))

        ttk.Label(registration_window, text="Password:").pack(anchor='w')
        password_entry = ttk.Entry(registration_window, show="•", width=30)
        password_entry.pack(fill='x', pady=(0, 20))

        ttk.Button(registration_window, text="Register", 
                  command=lambda: self.register(username_entry.get(), password_entry.get())).pack(fill='x')

    def register(self, username, password):
        """Handle user registration"""
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO emp (username, password) VALUES (?, ?)", (username, hashed_password))
            self.conn.commit()
            messagebox.showinfo("Success", "Registration successful! You can now log in.")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists. Please choose a different username.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Error during registration: {str(e)}")

    def cleanup(self):
        """Clean up resources before closing."""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def on_closing(self):
        """Handle application closing."""
        self.cleanup()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    login = LoginWindow(root)
    root.mainloop()
    
        
