import tkinter as tk  
from tkinter import ttk, messagebox, simpledialog  
from tkcalendar import DateEntry  
import sqlite3  
import os
from datetime import datetime

class DarkTheme:
    BG_COLOR = "#2b2b2b"
    FG_COLOR = "#ffffff"
    ACCENT_COLOR = "#007acc"
    SECONDARY_BG = "#3c3f41"
    HOVER_COLOR = "#404040"
    
    @staticmethod
    def apply_theme(root):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure common styles
        style.configure(".", 
            background=DarkTheme.BG_COLOR,
            foreground=DarkTheme.FG_COLOR,
            fieldbackground=DarkTheme.SECONDARY_BG,
            troughcolor=DarkTheme.SECONDARY_BG,
            selectbackground=DarkTheme.ACCENT_COLOR,
            selectforeground=DarkTheme.FG_COLOR
        )
        
        # Configure specific widget styles
        style.configure("TNotebook", background=DarkTheme.BG_COLOR)
        style.configure("TNotebook.Tab", 
            background=DarkTheme.SECONDARY_BG,
            foreground=DarkTheme.FG_COLOR,
            padding=[10, 5]
        )
        style.map("TNotebook.Tab",
            background=[("selected", DarkTheme.ACCENT_COLOR)],
            foreground=[("selected", DarkTheme.FG_COLOR)]
        )
        
        style.configure("TButton", 
            background=DarkTheme.ACCENT_COLOR,
            foreground=DarkTheme.FG_COLOR,
            padding=[10, 5]
        )
        style.map("TButton",
            background=[("active", DarkTheme.HOVER_COLOR)],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )
        
        style.configure("TEntry", 
            fieldbackground=DarkTheme.SECONDARY_BG,
            foreground=DarkTheme.FG_COLOR
        )
        
        style.configure("Treeview", 
            background=DarkTheme.SECONDARY_BG,
            foreground=DarkTheme.FG_COLOR,
            fieldbackground=DarkTheme.SECONDARY_BG
        )
        style.map("Treeview",
            background=[("selected", DarkTheme.ACCENT_COLOR)],
            foreground=[("selected", DarkTheme.FG_COLOR)]
        )
        
        # Configure root window
        root.configure(bg=DarkTheme.BG_COLOR)

class HotelManagementApp:  
    def __init__(self, root):  
        self.root = root  
        self.root.title("Hotel Management System")  
        self.root.geometry("1200x700")  
        
        # Add logged in state
        self.logged_in = False
        
        # Apply dark theme
        DarkTheme.apply_theme(root)
        
        # Configure styles for sidebar
        style = ttk.Style()
        style.configure("Sidebar.TFrame", 
                       background=DarkTheme.SECONDARY_BG)
        
        # Configure normal button style
        style.configure("SidebarBtn.TButton", 
                       background=DarkTheme.SECONDARY_BG,
                       foreground=DarkTheme.FG_COLOR,
                       borderwidth=0,
                       font=("Helvetica", 11),
                       padding=[20, 12],
                       anchor="w",  # Left align text
                       width=20)  # Fixed width
        
        # Configure hover and selected states using map
        style.map("SidebarBtn.TButton",
                 background=[("pressed", DarkTheme.HOVER_COLOR),
                           ("active", DarkTheme.HOVER_COLOR),
                           ("selected", DarkTheme.ACCENT_COLOR)],
                 foreground=[("pressed", DarkTheme.FG_COLOR),
                           ("active", DarkTheme.FG_COLOR),
                           ("selected", DarkTheme.FG_COLOR)])
        
        # Create main container
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create sidebar with fixed width
        self.sidebar = ttk.Frame(self.main_container, style="Sidebar.TFrame", width=250)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)  # Fix sidebar width
        
        # Create logo/title frame with proper padding
        logo_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        logo_frame.pack(fill=tk.X, pady=(30, 20))
        
        title_label = ttk.Label(logo_frame, 
                              text="Hotel\nManagement",
                              font=("Helvetica", 16, "bold"),
                              foreground=DarkTheme.FG_COLOR,
                              background=DarkTheme.SECONDARY_BG,
                              justify=tk.CENTER)
        title_label.pack(pady=10)
        
        # Create content frame
        self.content_frame = ttk.Frame(self.main_container, padding=20)
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame for navigation buttons with padding
        nav_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        nav_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Store buttons for state management
        self.nav_buttons = {}
        
        # Initialize frames dictionary
        self.frames = {}
        self.current_frame = None
        
        # Database initialization
        self.db_file = "hotel_management.db"
        self.initialize_database()
        
        # Create all frames
        self.create_all_frames()
        
        # Create navigation buttons
        self.create_nav_buttons()
        
        # Show login frame first
        self.show_frame("Login")

    def initialize_database(self):
        """Initialize database connection and create backup"""
        try:
            # Create backup of existing database if it exists
            if os.path.exists(self.db_file):
                backup_dir = "backups"
                if not os.path.exists(backup_dir):
                    os.makedirs(backup_dir)
                backup_file = os.path.join(backup_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
                with open(self.db_file, 'rb') as src, open(backup_file, 'wb') as dst:
                    dst.write(src.read())
                print(f"Database backup created: {backup_file}")

            # Connect to database with foreign key support
            self.conn = sqlite3.connect(self.db_file)
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            self.create_tables()
            
            # Check if we need to add test rooms
            cursor = self.conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM rooms")
            room_count = cursor.fetchone()[0]
            print(f"Current room count: {room_count}")

            if room_count == 0:
                print("No rooms found, adding test rooms...")
                # Add test rooms if database is empty
                test_rooms = [
                    (101, 'Deluxe', 'AC', 2500, 2, 1, 'available'),
                    (102, 'Normal', 'Non-AC', 1500, 2, 1, 'available'),
                    (103, 'Premium', 'AC', 3500, 3, 1, 'available'),
                    (104, 'Suite', 'AC', 5000, 4, 1, 'available'),
                    (201, 'Deluxe', 'AC', 2800, 2, 1, 'available'),
                    (202, 'Premium', 'AC', 3800, 3, 1, 'available')
                ]
                
                for room in test_rooms:
                    try:
                        cursor.execute("""
                            INSERT INTO rooms (room_number, room_type, ac_type, price, capacity, wifi, status)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, room)
                        print(f"Added room {room[0]} successfully")
                    except sqlite3.Error as e:
                        print(f"Error adding room {room[0]}: {str(e)}")
                
                self.conn.commit()
                
                # Verify rooms were added
                cursor.execute("SELECT COUNT(*) FROM rooms")
                new_room_count = cursor.fetchone()[0]
                print(f"New room count after adding test rooms: {new_room_count}")
                
            else:
                print("Rooms already exist in database")
                
        except sqlite3.Error as e:
            print(f"Database Error: {str(e)}")
            if hasattr(self, 'conn'):
                self.conn.rollback()
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
            raise
        except Exception as e:
            print(f"Unexpected Error: {str(e)}")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            raise

    def create_tables(self):  
        """Create the SQLite tables."""  
        cursor = self.conn.cursor()  
        cursor.execute("""  
        CREATE TABLE IF NOT EXISTS emp (  
            username TEXT PRIMARY KEY,  
            password TEXT NOT NULL  
        )  
        """)
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

    def create_nav_buttons(self):
        """Create navigation buttons in sidebar"""
        buttons_data = [
            ("Login", "Login", "🔑"),
            ("Add Room", "Add Room", "➕"),
            ("Book Room", "Book Room", "📝"),
            ("View Bookings", "Bookings", "📋"),
            ("Customer Info", "Customers", "👥")
        ]
        
        # Clear existing buttons if any
        for widget in self.sidebar.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.destroy()
        
        for frame_name, btn_text, icon in buttons_data:
            btn = ttk.Button(self.sidebar,
                           text=f" {icon}  {btn_text}",  # Add space for better icon alignment
                           style="SidebarBtn.TButton",
                           command=lambda f=frame_name: self.show_frame(f))
            btn.pack(fill=tk.X, padx=10, pady=2)
            self.nav_buttons[frame_name] = btn

    def create_all_frames(self):
        """Create all frames for different sections"""
        self.create_login_frame()
        self.create_add_room_frame()
        self.create_book_room_frame()
        self.create_view_bookings_frame()
        self.create_customer_info_frame()
    
    def show_frame(self, frame_name):
        """Show the selected frame and hide others"""
        # Check login state except for login frame
        if frame_name != "Login" and not self.logged_in:
            messagebox.showerror("Error", "Please login first")
            self.show_frame("Login")
            return

        # Hide current frame if exists
        if self.current_frame and self.current_frame in self.frames:
            self.frames[self.current_frame].pack_forget()
            if self.current_frame in self.nav_buttons:
                self.nav_buttons[self.current_frame].state(['!selected'])
        
        # Show selected frame
        if frame_name in self.frames:
            self.frames[frame_name].pack(in_=self.content_frame, fill=tk.BOTH, expand=True)
            self.current_frame = frame_name
            
            # Update button states
            if frame_name in self.nav_buttons:
                self.nav_buttons[frame_name].state(['selected'])

    def create_login_frame(self):
        """Create the frame for user login."""
        self.frames["Login"] = ttk.Frame(self.content_frame)
        
        # Create centered login container
        login_container = ttk.Frame(self.frames["Login"])
        login_container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Title
        title_label = ttk.Label(login_container, 
                              text="Welcome Back",
                              font=("Helvetica", 24, "bold"))
        title_label.pack(pady=20)

        # Subtitle
        subtitle_label = ttk.Label(login_container,
                                 text="Please login to continue",
                                 font=("Helvetica", 12))
        subtitle_label.pack(pady=(0, 20))

        # Login form frame
        login_form = ttk.Frame(login_container, padding="20")
        login_form.pack(pady=20)

        # Username
        username_frame = ttk.Frame(login_form)
        username_frame.pack(fill=tk.X, pady=10)
        ttk.Label(username_frame, text="Username",
                 font=("Helvetica", 10)).pack(anchor=tk.W)
        self.username_entry = ttk.Entry(username_frame, width=30)
        self.username_entry.pack(fill=tk.X, pady=(5, 0))

        # Password
        password_frame = ttk.Frame(login_form)
        password_frame.pack(fill=tk.X, pady=10)
        ttk.Label(password_frame, text="Password",
                 font=("Helvetica", 10)).pack(anchor=tk.W)
        self.password_entry = ttk.Entry(password_frame, show="*", width=30)
        self.password_entry.pack(fill=tk.X, pady=(5, 0))

        # Buttons frame
        btn_frame = ttk.Frame(login_form)
        btn_frame.pack(fill=tk.X, pady=20)

        # Login Button
        login_btn = ttk.Button(btn_frame, text="Login",
                             style="Accent.TButton",
                             command=self.login)
        login_btn.pack(side=tk.LEFT, padx=5)

        # Register Button
        register_btn = ttk.Button(btn_frame, text="Register",
                               command=self.register_user)
        register_btn.pack(side=tk.LEFT, padx=5)

    def create_add_room_frame(self):  
        """Create the frame for adding rooms."""  
        self.frames["Add Room"] = ttk.Frame(self.content_frame, padding="20")  
        
        # Title Frame
        title_frame = ttk.Frame(self.frames["Add Room"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, 
                              text="Add New Room",
                              font=("Helvetica", 20, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Main content frame with cards
        content_frame = ttk.Frame(self.frames["Add Room"])
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Card style configuration
        style = ttk.Style()
        style.configure("Card.TFrame", background=DarkTheme.SECONDARY_BG)
        style.configure("CardTitle.TLabel", 
                       font=("Helvetica", 12, "bold"),
                       foreground=DarkTheme.ACCENT_COLOR)
        
        # === Room Basic Info Card ===
        basic_info_card = ttk.Frame(content_frame, style="Card.TFrame", padding="15")
        basic_info_card.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(basic_info_card, text="Basic Information", 
                 style="CardTitle.TLabel").pack(fill=tk.X, pady=(0, 10))
        
        # Room Number
        room_num_frame = ttk.Frame(basic_info_card)
        room_num_frame.pack(fill=tk.X, pady=5)
        ttk.Label(room_num_frame, text="Room Number:").pack(side=tk.LEFT)
        self.room_number_entry = ttk.Entry(room_num_frame, width=20)
        self.room_number_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Room Type
        room_type_frame = ttk.Frame(basic_info_card)
        room_type_frame.pack(fill=tk.X, pady=5)
        ttk.Label(room_type_frame, text="Room Type:").pack(side=tk.LEFT)
        self.room_type_var = tk.StringVar()
        ttk.Combobox(room_type_frame, textvariable=self.room_type_var,
                    values=["Normal", "Deluxe", "Premium", "Suite"],
                    width=17).pack(side=tk.LEFT, padx=(10, 0))
        
        # === Room Features Card ===
        features_card = ttk.Frame(content_frame, style="Card.TFrame", padding="15")
        features_card.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(features_card, text="Room Features", 
                 style="CardTitle.TLabel").pack(fill=tk.X, pady=(0, 10))
        
        # Features grid
        features_grid = ttk.Frame(features_card)
        features_grid.pack(fill=tk.X)
        
        # AC Type
        ac_frame = ttk.Frame(features_grid)
        ac_frame.pack(fill=tk.X, pady=5)
        ttk.Label(ac_frame, text="AC/Non-AC:").pack(side=tk.LEFT)
        self.ac_var = tk.StringVar()
        ttk.Combobox(ac_frame, textvariable=self.ac_var,
                    values=["AC", "Non-AC"],
                    width=17).pack(side=tk.LEFT, padx=(10, 0))
        
        # Capacity
        capacity_frame = ttk.Frame(features_grid)
        capacity_frame.pack(fill=tk.X, pady=5)
        ttk.Label(capacity_frame, text="Capacity:").pack(side=tk.LEFT)
        self.capacity_var = tk.StringVar()
        ttk.Combobox(capacity_frame, textvariable=self.capacity_var,
                    values=["1", "2", "3", "4"],
                    width=17).pack(side=tk.LEFT, padx=(10, 0))
        
        # WiFi
        wifi_frame = ttk.Frame(features_grid)
        wifi_frame.pack(fill=tk.X, pady=5)
        self.wifi_var = tk.BooleanVar()
        ttk.Checkbutton(wifi_frame, text="Free Wi-Fi Available", 
                       variable=self.wifi_var).pack(side=tk.LEFT)
        
        # === Pricing Card ===
        pricing_card = ttk.Frame(content_frame, style="Card.TFrame", padding="15")
        pricing_card.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(pricing_card, text="Pricing Details", 
                 style="CardTitle.TLabel").pack(fill=tk.X, pady=(0, 10))
        
        price_frame = ttk.Frame(pricing_card)
        price_frame.pack(fill=tk.X)
        
        ttk.Label(price_frame, text="Price per Night (₹):").pack(side=tk.LEFT)
        self.price_entry = ttk.Entry(price_frame, width=20)
        self.price_entry.pack(side=tk.LEFT, padx=(10, 0))
        
        # Action Buttons
        button_frame = ttk.Frame(self.frames["Add Room"])
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Clear button
        ttk.Button(button_frame, text="Clear Fields",
                  command=self.clear_room_fields).pack(side=tk.LEFT, padx=5)
        
        # Add Room button with accent style
        style.configure("Accent.TButton",
                      background=DarkTheme.ACCENT_COLOR,
                      foreground=DarkTheme.FG_COLOR)
        
        ttk.Button(button_frame, text="Add Room",
                  style="Accent.TButton",
                  command=self.add_room).pack(side=tk.RIGHT, padx=5)

    def create_book_room_frame(self):  
        """Create the frame for booking rooms."""  
        self.frames["Book Room"] = ttk.Frame(self.content_frame, padding="20")  
        
        # Title Frame
        title_frame = ttk.Frame(self.frames["Book Room"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, 
                              text="Book a Room",
                              font=("Helvetica", 20, "bold"))
        title_label.pack(side=tk.LEFT)

        # Refresh button
        ttk.Button(title_frame, 
                  text="Refresh Room List",
                  command=self.refresh_room_list).pack(side=tk.RIGHT)

        # Create main container
        main_container = ttk.Frame(self.frames["Book Room"])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel - Room List
        left_panel = ttk.Frame(main_container)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Room List Frame
        room_list_frame = ttk.LabelFrame(left_panel, text="Available Rooms", padding=10)
        room_list_frame.pack(fill=tk.BOTH, expand=True)

        # Create Treeview for rooms
        columns = ("Room No.", "Type", "AC/Non-AC", "Price", "Capacity", "Status")
        self.available_rooms_tree = ttk.Treeview(room_list_frame, columns=columns, show="headings", height=10)
        
        # Set column headings and widths
        widths = [70, 100, 100, 80, 70, 80]
        for col, width in zip(columns, widths):
            self.available_rooms_tree.heading(col, text=col)
            self.available_rooms_tree.column(col, width=width)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(room_list_frame, orient=tk.VERTICAL, 
                                command=self.available_rooms_tree.yview)
        self.available_rooms_tree.configure(yscroll=scrollbar.set)

        # Pack the treeview and scrollbar
        self.available_rooms_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Right Panel - Booking Form
        right_panel = ttk.Frame(main_container)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        # Booking Form Frame
        booking_form = ttk.LabelFrame(right_panel, text="Booking Details", padding=10)
        booking_form.pack(fill=tk.BOTH, expand=True)

        # Customer Details
        ttk.Label(booking_form, text="Customer Name:").pack(anchor=tk.W, pady=(0, 5))
        self.person_name_entry = ttk.Entry(booking_form)
        self.person_name_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(booking_form, text="Number of Persons:").pack(anchor=tk.W, pady=(0, 5))
        self.num_persons_entry = ttk.Entry(booking_form)
        self.num_persons_entry.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(booking_form, text="Children:").pack(anchor=tk.W, pady=(0, 5))
        self.children_var = tk.StringVar()
        children_combo = ttk.Combobox(booking_form, textvariable=self.children_var, 
                                    values=["Yes", "No"], state="readonly")
        children_combo.pack(fill=tk.X, pady=(0, 10))

        # Dates
        dates_frame = ttk.Frame(booking_form)
        dates_frame.pack(fill=tk.X, pady=10)

        # Check-in date
        check_in_frame = ttk.Frame(dates_frame)
        check_in_frame.pack(fill=tk.X, pady=5)
        ttk.Label(check_in_frame, text="Check-in Date:").pack(side=tk.LEFT)
        self.check_in_entry = DateEntry(check_in_frame, width=20,
                                      background=DarkTheme.ACCENT_COLOR,
                                      foreground=DarkTheme.FG_COLOR,
                                      borderwidth=2)
        self.check_in_entry.pack(side=tk.RIGHT)

        # Check-out date
        check_out_frame = ttk.Frame(dates_frame)
        check_out_frame.pack(fill=tk.X, pady=5)
        ttk.Label(check_out_frame, text="Check-out Date:").pack(side=tk.LEFT)
        self.check_out_entry = DateEntry(check_out_frame, width=20,
                                       background=DarkTheme.ACCENT_COLOR,
                                       foreground=DarkTheme.FG_COLOR,
                                       borderwidth=2)
        self.check_out_entry.pack(side=tk.RIGHT)

        # Buttons
        button_frame = ttk.Frame(booking_form)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        ttk.Button(button_frame, text="Clear Form",
                  command=self.clear_booking_fields).pack(side=tk.LEFT, padx=5)

        self.book_room_btn = ttk.Button(button_frame, text="Book Selected Room",
                                      command=self.book_selected_room,
                                      state='disabled')
        self.book_room_btn.pack(side=tk.RIGHT, padx=5)

        # Bind selection event
        self.available_rooms_tree.bind('<<TreeviewSelect>>', self.on_room_select)

        # Initial load of rooms
        self.refresh_room_list()

    def create_view_bookings_frame(self):  
        """Create the frame for viewing bookings."""  
        self.frames["View Bookings"] = ttk.Frame(self.content_frame, padding="20")  
        
        # Title Frame
        title_frame = ttk.Frame(self.frames["View Bookings"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, 
                              text="Manage Bookings",
                              font=("Helvetica", 20, "bold"))
        title_label.pack(side=tk.LEFT)

        # Action Buttons Frame
        action_frame = ttk.Frame(title_frame)
        action_frame.pack(side=tk.RIGHT)
        
        ttk.Button(action_frame, text="View All Bookings", 
                  command=self.view_bookings).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Cancel Booking",
                  command=self.cancel_booking).pack(side=tk.LEFT, padx=5)

        # Bookings List Card
        bookings_card = ttk.Frame(self.frames["View Bookings"], style="Card.TFrame", padding="15")
        bookings_card.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(bookings_card, text="Current Bookings", 
                 style="CardTitle.TLabel").pack(fill=tk.X, pady=(0, 10))

        # Create Treeview for bookings
        columns = ("Booking ID", "Customer Name", "Room Number", "Check-in", "Check-out", "Status")
        self.bookings_tree = ttk.Treeview(bookings_card, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.bookings_tree.heading(col, text=col)
            self.bookings_tree.column(col, width=100)

        self.bookings_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(bookings_card, orient=tk.VERTICAL, 
                                command=self.bookings_tree.yview)
        self.bookings_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def create_customer_info_frame(self):  
        """Create the frame for customer info."""  
        self.frames["Customer Info"] = ttk.Frame(self.content_frame, padding="20")  
        
        # Title Frame
        title_frame = ttk.Frame(self.frames["Customer Info"])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = ttk.Label(title_frame, 
                              text="Customer Information",
                              font=("Helvetica", 20, "bold"))
        title_label.pack(side=tk.LEFT)

        # Refresh Button
        ttk.Button(title_frame, text="Refresh",
                  command=self.refresh_customer_info).pack(side=tk.RIGHT)

        # Customer List Card
        customer_card = ttk.Frame(self.frames["Customer Info"], style="Card.TFrame", padding="15")
        customer_card.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(customer_card, text="Current Customers", 
                 style="CardTitle.TLabel").pack(fill=tk.X, pady=(0, 10))

        # Create Treeview
        columns = ("Customer Name", "Room Number", "Price", "Check-in", "Check-out")
        self.customer_tree = ttk.Treeview(customer_card, columns=columns, show="headings")
        
        # Set column headings
        for col in columns:
            self.customer_tree.heading(col, text=col)
            self.customer_tree.column(col, width=150)

        self.customer_tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(customer_card, orient=tk.VERTICAL, 
                                command=self.customer_tree.yview)
        self.customer_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_room(self):  
        """Add a room to the database."""  
        try:
            room_type = self.room_type_var.get()  
            ac_type = self.ac_var.get()  
            room_number = self.room_number_entry.get().strip()  
            price = self.price_entry.get().strip()  
            wifi = self.wifi_var.get()
            capacity = self.capacity_var.get()

            if not all([room_type, ac_type, room_number, price, capacity]):
                raise ValueError("All fields must be filled")

            room_number = int(room_number)
            price = float(price)
            capacity = int(capacity)

            if price <= 0:
                raise ValueError("Price must be greater than 0")
            if capacity < 1 or capacity > 4:
                raise ValueError("Capacity must be between 1 and 4")

            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO rooms (room_number, room_type, ac_type, price, wifi, capacity, status)
                VALUES (?, ?, ?, ?, ?, ?, 'available')
            """, (room_number, room_type, ac_type, price, wifi, capacity))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Room added successfully!")
            self.clear_room_fields()
            
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Room number already exists")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to add room: {str(e)}")
            self.conn.rollback()

    def check_availability(self):
        """Check room availability and display available rooms."""
        try:
            # Input validation
            required_fields = {
                'Name': self.person_name_entry.get().strip(),
                'Room Type': self.booking_room_type_var.get(),
                'AC Type': self.booking_ac_var.get(),
                'Number of Persons': self.num_persons_entry.get().strip(),
                'Children': self.children_var.get(),
                'Budget': self.budget_entry.get().strip()
            }

            # Check for empty fields
            empty_fields = [field for field, value in required_fields.items() if not value]
            if empty_fields:
                raise ValueError(f"Please fill in the following fields: {', '.join(empty_fields)}")

            # Validate numeric fields
            try:
                budget = float(required_fields['Budget'])
                num_persons = int(required_fields['Number of Persons'])
                if budget <= 0:
                    raise ValueError("Budget must be greater than 0")
                if num_persons < 1:
                    raise ValueError("Number of persons must be at least 1")
                if num_persons > 4:
                    raise ValueError("Maximum capacity is 4 persons")
            except ValueError:
                raise ValueError("Invalid numeric value in budget or number of persons")

            # Check dates
            check_in = self.check_in_entry.get_date()
            check_out = self.check_out_entry.get_date()
            current_date = datetime.now().date()

            if check_in < current_date:
                raise ValueError("Check-in date cannot be in the past")
            if check_in >= check_out:
                raise ValueError("Check-out date must be after check-in date")

            # Format dates for SQLite
            check_in_str = check_in.strftime('%Y-%m-%d')
            check_out_str = check_out.strftime('%Y-%m-%d')

            # Clear existing items in the treeview
            for item in self.available_rooms_tree.get_children():
                self.available_rooms_tree.delete(item)

            # Search for available rooms
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT r.room_number, r.room_type, r.ac_type, r.price, r.capacity, r.wifi
                FROM rooms r
                WHERE r.room_type = ? 
                AND r.ac_type = ?
                AND r.price <= ?
                AND r.capacity >= ?
                AND r.status = 'available'
                AND r.room_number NOT IN (
                    SELECT room_number 
                    FROM bookings 
                    WHERE status = 'active'
                    AND (
                        (check_in_date <= ? AND check_out_date >= ?) OR
                        (check_in_date <= ? AND check_out_date >= ?) OR
                        (check_in_date >= ? AND check_out_date <= ?)
                    )
                )
                ORDER BY r.price ASC
            """, (
                required_fields['Room Type'],
                required_fields['AC Type'],
                budget,
                num_persons,
                check_in_str, check_in_str,
                check_out_str, check_out_str,
                check_in_str, check_out_str
            ))
            
            available_rooms = cursor.fetchall()

            if not available_rooms:
                messagebox.showinfo("No Rooms", "No rooms available matching your criteria.")
                self.book_room_btn.configure(state='disabled')
                return

            # Insert available rooms into treeview
            for room in available_rooms:
                # Convert wifi boolean to Yes/No
                wifi_status = "Yes" if room[5] else "No"
                values = (room[0], room[1], room[2], f"₹{room[3]}", room[4], wifi_status)
                self.available_rooms_tree.insert("", "end", values=values)

            # Enable the book room button
            self.book_room_btn.configure(state='normal')
            messagebox.showinfo("Success", f"Found {len(available_rooms)} available rooms matching your criteria.")

        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
            self.book_room_btn.configure(state='disabled')
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to check availability: {str(e)}")
            self.book_room_btn.configure(state='disabled')
            self.conn.rollback()

    def view_bookings(self):
        """View all current bookings."""
        try:
            # Clear existing items
            for item in self.bookings_tree.get_children():
                self.bookings_tree.delete(item)

            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT b.booking_id, b.person_name, b.room_number, 
                       b.check_in_date, b.check_out_date, b.status,
                       r.price, r.room_type, r.ac_type
                FROM bookings b
                JOIN rooms r ON b.room_number = r.room_number
                ORDER BY 
                    CASE b.status 
                        WHEN 'active' THEN 1 
                        WHEN 'cancelled' THEN 2 
                    END,
                    b.check_in_date DESC
            """)
            bookings = cursor.fetchall()

            # Insert into treeview with formatted dates
            for booking in bookings:
                # Convert date strings to datetime objects for formatting
                check_in = datetime.strptime(booking[3], '%Y-%m-%d').strftime('%d-%m-%Y')
                check_out = datetime.strptime(booking[4], '%Y-%m-%d').strftime('%d-%m-%Y')
                
                # Format values for display
                display_values = (
                    booking[0],  # Booking ID
                    booking[1],  # Customer Name
                    booking[2],  # Room Number
                    check_in,    # Check-in Date
                    check_out,   # Check-out Date
                    booking[5]   # Status
                )
                
                # Set tag for row color based on status
                tags = ('cancelled',) if booking[5] == 'cancelled' else ('active',)
                
                self.bookings_tree.insert("", "end", values=display_values, tags=tags)
            
            # Configure tag colors
            self.bookings_tree.tag_configure('cancelled', foreground='gray')
            self.bookings_tree.tag_configure('active', foreground=DarkTheme.FG_COLOR)
            
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to retrieve bookings: {str(e)}")

    def cancel_booking(self):
        """Cancel an existing booking."""
        try:
            # Get selected item
            selected_item = self.bookings_tree.selection()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select a booking to cancel.")
                return

            # Get booking details
            booking_values = self.bookings_tree.item(selected_item)['values']
            booking_id = booking_values[0]  # First column is booking ID
            customer_name = booking_values[1]  # Second column is customer name
            room_number = booking_values[2]  # Third column is room number
            current_status = booking_values[5]  # Sixth column is status

            if current_status == 'cancelled':
                messagebox.showinfo("Info", "This booking is already cancelled.")
                return

            confirm = messagebox.askyesno("Confirm Cancellation", 
                f"Are you sure you want to cancel booking for {customer_name}?")
            
            if confirm:
                cursor = self.conn.cursor()
                
                # Start transaction
                cursor.execute("BEGIN TRANSACTION")
                try:
                    # Update booking status
                    cursor.execute("""
                        UPDATE bookings 
                        SET status = 'cancelled' 
                        WHERE booking_id = ?
                    """, (booking_id,))

                    # Check if there are any active bookings for this room
                    cursor.execute("""
                        SELECT COUNT(*) 
                        FROM bookings 
                        WHERE room_number = ? 
                        AND status = 'active'
                        AND booking_id != ?
                    """, (room_number, booking_id))
                    
                    active_bookings = cursor.fetchone()[0]

                    # If no other active bookings, update room status to available
                    if active_bookings == 0:
                        cursor.execute("""
                            UPDATE rooms 
                            SET status = 'available' 
                            WHERE room_number = ?
                        """, (room_number,))

                    self.conn.commit()
                    messagebox.showinfo("Success", "Booking cancelled successfully!")
                    self.view_bookings()  # Refresh the bookings list
                    self.refresh_customer_info()  # Refresh customer info
                except sqlite3.Error as e:
                    self.conn.rollback()
                    raise e
        
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to cancel booking: {str(e)}")

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
                       b.check_in_date, b.check_out_date
                FROM bookings b
                JOIN rooms r ON b.room_number = r.room_number
                WHERE b.status = 'active'
                ORDER BY b.check_in_date
            """)
            
            # Insert into treeview
            for booking in cursor.fetchall():
                self.customer_tree.insert("", "end", values=booking)

        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Failed to refresh customer info: {str(e)}")

    def clear_room_fields(self):
        """Clear all room input fields."""
        self.room_type_var.set("")
        self.ac_var.set("")
        self.room_number_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)
        self.wifi_var.set(False)
        self.capacity_var.set("")

    def clear_booking_fields(self):
        """Clear all booking form fields."""
        self.person_name_entry.delete(0, tk.END)
        self.num_persons_entry.delete(0, tk.END)
        self.children_var.set("")
        self.check_in_entry.set_date(datetime.now())
        self.check_out_entry.set_date(datetime.now())
        
        # Clear any selection in the room list
        if hasattr(self, 'available_rooms_tree'):
            self.available_rooms_tree.selection_remove(
                self.available_rooms_tree.selection())
        
        # Disable book button
        if hasattr(self, 'book_room_btn'):
            self.book_room_btn.configure(state='disabled')

    def on_closing(self):
        """Handle application closing."""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.commit()
                self.conn.close()
            self.root.destroy()
        except sqlite3.Error as e:
            messagebox.showerror("Error", f"Error while closing: {str(e)}")
            self.root.destroy()

    def login(self):
        """Authenticate user login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password.")
            return

        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM emp WHERE username = ? AND password = ?", 
                         (username, password))
            user = cursor.fetchone()

            if user:
                self.logged_in = True
                messagebox.showinfo("Success", "Login successful!")
                self.show_frame("Add Room")  # Show main dashboard
            else:
                messagebox.showerror("Error", "Invalid username or password.")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Login failed: {str(e)}")

    def create_main_application(self):
        """Create the main application interface after login."""
        # Create all frames for different tabs  
        self.create_add_room_frame()  
        self.create_book_room_frame()  
        self.create_view_bookings_frame()  
        self.create_customer_info_frame()  

    def create_user(self, username, password):  
        """Create a new user in the database."""  
        cursor = self.conn.cursor()  
        cursor.execute("INSERT INTO emp (username, password) VALUES (?, ?)", (username, password))  
        self.conn.commit()

    def register_user(self):
        """Register a new user."""
        try:
            username = simpledialog.askstring("Register", "Enter username:")
            if not username:
                return
                
            password = simpledialog.askstring("Register", "Enter password:", show='*')
            if not password:
                return
                
            # Validate input
            if len(username) < 3:
                raise ValueError("Username must be at least 3 characters long")
            if len(password) < 6:
                raise ValueError("Password must be at least 6 characters long")

            self.create_user(username, password)
            messagebox.showinfo("Success", "User registered successfully!")
            
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists")
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to register user: {str(e)}")

    def book_selected_room(self):
        """Book the selected room."""
        try:
            # Get selected room
            selected_item = self.available_rooms_tree.selection()
            if not selected_item:
                messagebox.showwarning("No Selection", "Please select a room to book.")
                return

            # Get room details
            room_values = self.available_rooms_tree.item(selected_item)['values']
            room_number = room_values[0]  # First column is room number
            room_type = room_values[1]    # Second column is room type
            room_price = room_values[3]   # Fourth column is price
            room_capacity = room_values[4] # Fifth column is capacity
            room_status = room_values[5]   # Sixth column is status
            
            # Check if room is available
            if room_status != 'available':
                messagebox.showerror("Error", "This room is not available for booking.")
                return
            
            # Get customer details
            person_name = self.person_name_entry.get().strip()
            num_persons = self.num_persons_entry.get().strip()
            children = self.children_var.get()
            check_in = self.check_in_entry.get_date()
            check_out = self.check_out_entry.get_date()

            # Validate inputs
            if not person_name:
                messagebox.showerror("Error", "Please enter customer name.")
                self.person_name_entry.focus()
                return
                
            if not num_persons:
                messagebox.showerror("Error", "Please enter number of persons.")
                self.num_persons_entry.focus()
                return

            try:
                num_persons = int(num_persons)
                if num_persons < 1:
                    raise ValueError("Number of persons must be at least 1")
                if num_persons > room_capacity:
                    raise ValueError(f"Number of persons exceeds room capacity ({room_capacity})")
            except ValueError as e:
                if "exceeds room capacity" in str(e):
                    messagebox.showerror("Error", str(e))
                else:
                    messagebox.showerror("Error", "Please enter a valid number of persons.")
                self.num_persons_entry.focus()
                return

            if not children:
                messagebox.showerror("Error", "Please select Yes/No for children.")
                return

            # Validate dates
            today = datetime.now().date()
            if check_in < today:
                messagebox.showerror("Error", "Check-in date cannot be in the past.")
                return
            if check_out <= check_in:
                messagebox.showerror("Error", "Check-out date must be after check-in date.")
                return

            # Format dates for SQLite
            check_in_str = check_in.strftime('%Y-%m-%d')
            check_out_str = check_out.strftime('%Y-%m-%d')

            # Check for overlapping bookings
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM bookings 
                WHERE room_number = ? 
                AND status = 'active'
                AND (
                    (check_in_date <= ? AND check_out_date >= ?) OR
                    (check_in_date <= ? AND check_out_date >= ?) OR
                    (check_in_date >= ? AND check_out_date <= ?)
                )
            """, (room_number, check_in_str, check_in_str, check_out_str, check_out_str, check_in_str, check_out_str))
            
            if cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "This room is already booked for the selected dates.")
                return

            # Calculate total price (number of days * room price)
            price = float(room_price.replace('₹', ''))
            days = (check_out - check_in).days
            total_price = price * days

            # Confirm booking with total price
            confirm = messagebox.askyesno("Confirm Booking", 
                f"Do you want to book Room {room_number} for {person_name}?\n\n"
                f"Room Type: {room_type}\n"
                f"Price per day: ₹{price}\n"
                f"Number of days: {days}\n"
                f"Total Price: ₹{total_price:.2f}\n"
                f"Check-in: {check_in_str}\n"
                f"Check-out: {check_out_str}\n"
                f"Number of Persons: {num_persons}\n"
                f"Children: {children}")

            if confirm:
                cursor = self.conn.cursor()
                cursor.execute("BEGIN TRANSACTION")
                try:
                    # Insert booking record
                    cursor.execute("""
                        INSERT INTO bookings (
                            person_name, room_number, check_in_date, check_out_date,
                            num_persons, children, status
                        ) VALUES (?, ?, ?, ?, ?, ?, 'active')
                    """, (person_name, room_number, check_in_str, check_out_str,
                          num_persons, children))
                    
                    # Update room status
                    cursor.execute("""
                        UPDATE rooms SET status = 'booked'
                        WHERE room_number = ?
                    """, (room_number,))

                    self.conn.commit()
                    messagebox.showinfo("Success", 
                        f"Room booked successfully!\n\n"
                        f"Total amount to be paid: ₹{total_price:.2f}")
                    
                    # Clear form and refresh views
                    self.clear_booking_fields()
                    self.refresh_room_list()  # Refresh available rooms
                    self.view_bookings()  # Refresh bookings view if visible
                    
                except sqlite3.Error as e:
                    self.conn.rollback()
                    print(f"Database Error in book_selected_room: {str(e)}")
                    raise e
                except ValueError as e:
                    self.conn.rollback()
                    messagebox.showerror("Error", str(e))

        except ValueError as e:
            messagebox.showerror("Error", str(e))
        except sqlite3.Error as e:
            print(f"Database Error in book_selected_room: {str(e)}")
            messagebox.showerror("Database Error", f"Failed to book room: {str(e)}")
            if 'cursor' in locals():
                self.conn.rollback()
        except Exception as e:
            print(f"Unexpected Error in book_selected_room: {str(e)}")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")
            if 'cursor' in locals():
                self.conn.rollback()

    def check_database_content(self):
        """Check and print the content of the database tables"""
        try:
            cursor = self.conn.cursor()
            
            # Check rooms table
            print("\n=== Checking Rooms Table ===")
            cursor.execute("SELECT * FROM rooms")
            rooms = cursor.fetchall()
            if rooms:
                print("Found rooms:")
                for room in rooms:
                    print(f"Room {room[0]}: Type={room[1]}, AC={room[2]}, Price={room[3]}, Capacity={room[4]}, WiFi={room[5]}, Status={room[6]}")
            else:
                print("No rooms found in database")
            
            # Check bookings table
            print("\n=== Checking Bookings Table ===")
            cursor.execute("SELECT * FROM bookings")
            bookings = cursor.fetchall()
            if bookings:
                print("Found bookings:")
                for booking in bookings:
                    print(f"Booking {booking[0]}: Room={booking[2]}, Status={booking[7]}")
            else:
                print("No bookings found in database")
                
        except sqlite3.Error as e:
            print(f"Error checking database: {str(e)}")

    def view_all_available_rooms(self):
        """Display all available rooms without filters."""
        try:
            # Clear existing items in the treeview
            for item in self.available_rooms_tree.get_children():
                self.available_rooms_tree.delete(item)

            cursor = self.conn.cursor()
            
            # Get all rooms regardless of status
            cursor.execute("""
                SELECT room_number, room_type, ac_type, price, capacity, wifi, status
                FROM rooms
                ORDER BY room_type, price ASC
            """)
            
            all_rooms = cursor.fetchall()
            print(f"\nTotal rooms found: {len(all_rooms)}")
            
            if not all_rooms:
                print("No rooms found in database!")
                messagebox.showinfo("No Rooms", "No rooms have been added to the system yet.")
                return

            # Insert all rooms into treeview
            rooms_added = 0
            for room in all_rooms:
                # Convert wifi boolean to Yes/No
                wifi_status = "Yes" if room[5] else "No"
                status = room[6]
                
                # Add all rooms to the view
                values = (room[0], room[1], room[2], f"₹{room[3]}", room[4], wifi_status)
                item = self.available_rooms_tree.insert("", "end", values=values)
                
                # If room is not available, gray it out
                if status != 'available':
                    self.available_rooms_tree.tag_configure('booked', foreground='gray')
                    self.available_rooms_tree.item(item, tags=('booked',))
                else:
                    rooms_added += 1
                print(f"Added room {room[0]} with status: {status}")

            print(f"Total available rooms: {rooms_added}")
            
            if rooms_added == 0:
                messagebox.showinfo("No Available Rooms", "All rooms are currently booked or under maintenance.")

        except sqlite3.Error as e:
            print(f"Database Error in view_all_available_rooms: {str(e)}")
            messagebox.showerror("Database Error", f"Failed to retrieve rooms: {str(e)}")
        finally:
            # Always ensure book button is disabled when refreshing rooms
            self.book_room_btn.configure(state='disabled')

    def on_room_select(self, event):
        """Enable book button when a room is selected"""
        selected = self.available_rooms_tree.selection()
        if selected:
            self.book_room_btn.configure(state='normal')
        else:
            self.book_room_btn.configure(state='disabled')

    def refresh_room_list(self):
        """Refresh the room list with current data"""
        try:
            # Clear existing items
            for item in self.available_rooms_tree.get_children():
                self.available_rooms_tree.delete(item)

            cursor = self.conn.cursor()
            
            # Simple query to get room details
            cursor.execute("""
                SELECT r.room_number, r.room_type, r.ac_type, r.price, r.capacity, 
                       CASE WHEN b.status = 'active' THEN 'Booked' ELSE r.status END as current_status
                FROM rooms r
                LEFT JOIN bookings b ON r.room_number = b.room_number AND b.status = 'active'
                ORDER BY r.room_type, r.price
            """)
            
            rooms = cursor.fetchall()
            
            if not rooms:
                messagebox.showinfo("No Rooms", "No rooms are available in the system.")
                return
            
            # Add rooms to treeview
            for room in rooms:
                room_number, room_type, ac_type, price, capacity, status = room
                
                # Format the values for display
                display_values = (
                    room_number,
                    room_type,
                    ac_type,
                    f"₹{price}",
                    capacity,
                    status
                )
                
                item = self.available_rooms_tree.insert("", "end", values=display_values)
                
                # Gray out non-available rooms
                if status != 'available':
                    self.available_rooms_tree.tag_configure('unavailable', foreground='gray')
                    self.available_rooms_tree.item(item, tags=('unavailable',))

        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to refresh room list: {str(e)}")

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = HotelManagementApp(root)
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        