import tkinter as tk  
from tkinter import ttk, messagebox, simpledialog  
from tkcalendar import DateEntry  
import sqlite3  
import os
from datetime import datetime

class DashboardButton(tk.Frame):
    """Custom button widget for dashboard"""
    def __init__(self, parent, title, description, icon_char, command, color):
        super().__init__(parent, bg=color)
        
        # Create inner frame with border effect and padding
        inner_frame = tk.Frame(self, bg='white', padx=20, pady=20)
        inner_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        # Icon label with larger font
        icon_label = tk.Label(inner_frame, text=icon_char, 
                            font=('Helvetica', 48), bg='white')
        icon_label.pack(pady=(0, 10))
        
        # Title with larger font
        title_label = tk.Label(inner_frame, text=title, 
                             font=('Helvetica', 16, 'bold'), 
                             bg='white')
        title_label.pack()
        
        # Make the whole button clickable
        for widget in [self, inner_frame, icon_label, title_label]:
            widget.bind('<Button-1>', lambda e: command())
        
        # Hover effect
        def on_enter(e):
            inner_frame.configure(bg='#f5f5f5')
            for w in [icon_label, title_label]:
                w.configure(bg='#f5f5f5')
            
        def on_leave(e):
            inner_frame.configure(bg='white')
            for w in [icon_label, title_label]:
                w.configure(bg='white')
            
        for widget in [self, inner_frame, icon_label, title_label]:
            widget.bind('<Enter>', on_enter)
            widget.bind('<Leave>', on_leave)

class ModernWindow(tk.Toplevel):
    """Base class for modern window design"""
    def __init__(self, parent, title, size="800x600"):
        # Initialize window after checking parent
        if not isinstance(parent, tk.Tk) and not isinstance(parent, tk.Toplevel):
            parent = parent.winfo_toplevel()
        
        super().__init__(parent)
        
        # Store reference to parent and setup window
        self.parent = parent
        self.title(title)
        self.geometry(size)
        
        # Make window modal
        self.transient(parent)
        self.grab_set()
        
        # Center window on parent
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        self.geometry(f"+{x}+{y}")
        
        # Get colors from parent
        if hasattr(parent, 'colors'):
            self.colors = parent.colors
        else:
            # Default colors if parent doesn't have colors
            self.colors = {
                'primary': '#2c3e50',      # Dark blue
                'secondary': '#3498db',    # Light blue
                'accent1': '#e74c3c',      # Red
                'accent2': '#2ecc71',      # Green
                'accent3': '#f1c40f',      # Yellow
                'accent4': '#9b59b6',      # Purple
                'bg': '#ecf0f1',          # Light gray
                'text': '#2c3e50'         # Dark blue
            }
        
        # Configure window
        self.configure(bg=self.colors['bg'])
        
        # Create main container
        self.container = tk.Frame(self, bg='white', padx=40, pady=40)
        self.container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header
        self.create_header(title)
        
        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_header(self, title):
        """Create window header"""
        header = tk.Frame(self.container, bg='white')
        header.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(header, text=title,
                font=('Helvetica', 24, 'bold'),
                bg='white',
                fg=self.colors['primary']).pack()
        
        ttk.Separator(header, orient='horizontal').pack(fill=tk.X, pady=(20, 0))
        
    def on_closing(self):
        """Handle window closing"""
        try:
            self.grab_release()
            self.destroy()
        except Exception:
            pass

class LoginWindow(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.configure(bg='white')
        
        # Create main container with padding
        self.container = tk.Frame(self, bg='white', padx=40, pady=40)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Create login form
        self.create_login_form()
        
    def create_login_form(self):
        """Create the login form"""
        # Logo/Icon
        icon_label = tk.Label(self.container, text="🏨", font=('Helvetica', 64), bg='white')
        icon_label.pack(pady=(0, 20))
        
        # Title
        title = tk.Label(self.container, 
                        text="Hotel Management System",
                        font=('Helvetica', 18, 'bold'),
                        bg='white',
                        fg='#2c3e50')
        title.pack(pady=(0, 30))
        
        # Username
        username_frame = tk.Frame(self.container, bg='white')
        username_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(username_frame, text="Username:", 
                font=('Helvetica', 12),
                bg='white').pack(anchor='w')
        
        self.username_entry = ttk.Entry(username_frame, width=30, font=('Helvetica', 11))
        self.username_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Password
        password_frame = tk.Frame(self.container, bg='white')
        password_frame.pack(fill=tk.X, pady=(0, 30))
        
        tk.Label(password_frame, text="Password:", 
                font=('Helvetica', 12),
                bg='white').pack(anchor='w')
        
        self.password_entry = ttk.Entry(password_frame, width=30, font=('Helvetica', 11), show='•')
        self.password_entry.pack(fill=tk.X, pady=(5, 0))
        
        # Login Button
        login_btn = tk.Button(self.container,
                            text="Login",
                            font=('Helvetica', 12, 'bold'),
                            bg='#2ecc71',
                            fg='white',
                            padx=30,
                            pady=10,
                            command=self.login)
        login_btn.pack(pady=(0, 15))
        
        # Register Link
        register_frame = tk.Frame(self.container, bg='white')
        register_frame.pack()
        
        tk.Label(register_frame, 
                text="Don't have an account? ",
                font=('Helvetica', 10),
                bg='white').pack(side=tk.LEFT)
        
        register_link = tk.Label(register_frame,
                               text="Register",
                               font=('Helvetica', 10, 'bold'),
                               fg='#3498db',
                               cursor='hand2',
                               bg='white')
        register_link.pack(side=tk.LEFT)
        register_link.bind('<Button-1>', lambda e: self.register())

    def login(self):
        """Handle login"""
        try:
            username = self.username_entry.get().strip()
            password = self.password_entry.get().strip()
            
            if not username or not password:
                messagebox.showerror("Error", "Please enter both username and password")
                return
            
            cursor = self.parent.conn.cursor()
            cursor.execute("SELECT * FROM emp WHERE username = ? AND password = ?", 
                         (username, password))
            user = cursor.fetchone()
            
            if user:
                messagebox.showinfo("Success", "Login successful!")
                self.destroy()  # Remove login frame
                self.parent.setup_main_window()  # Show main window
            else:
                messagebox.showerror("Error", "Invalid username or password")
                self.username_entry.delete(0, tk.END)
                self.password_entry.delete(0, tk.END)
                self.username_entry.focus()
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to login: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def register(self):
        """Handle registration"""
        try:
            username = simpledialog.askstring("Register", "Enter username:")
            if username:
                if len(username) < 3:
                    messagebox.showerror("Error", "Username must be at least 3 characters long")
                    return
                    
                password = simpledialog.askstring("Register", "Enter password:", show='*')
                if password:
                    if len(password) < 4:
                        messagebox.showerror("Error", "Password must be at least 4 characters long")
                        return
                        
                    try:
                        cursor = self.parent.conn.cursor()
                        cursor.execute("INSERT INTO emp (username, password) VALUES (?, ?)",
                                     (username, password))
                        self.parent.conn.commit()
                        messagebox.showinfo("Success", "Registration successful! You can now login.")
                    except sqlite3.IntegrityError:
                        messagebox.showerror("Error", "Username already exists")
                    except sqlite3.Error as e:
                        messagebox.showerror("Error", f"Failed to register: {str(e)}")
                        self.parent.conn.rollback()
                        
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

class HotelManagementApp(tk.Frame):  
    def __init__(self, master):  
        super().__init__(master)
        self.root = master
        self.root.title("Hotel Management System")  
        
        # Configure self frame
        self.configure(bg='white')
        self.pack(fill=tk.BOTH, expand=True)
        
        # Define theme colors
        self.colors = {
            'primary': '#2c3e50',      # Dark blue
            'secondary': '#3498db',    # Light blue
            'accent1': '#e74c3c',      # Red
            'accent2': '#2ecc71',      # Green
            'accent3': '#f1c40f',      # Yellow
            'accent4': '#9b59b6',      # Purple
            'bg': '#ecf0f1',          # Light gray
            'text': '#2c3e50'         # Dark blue
        }
        
        # Database initialization
        self.db_file = "hotel_management.db"
        self.initialize_database()
        
        # Show login window
        self.show_login_window()

    def show_login_window(self):
        """Show the login window"""
        try:
            # Clear any existing widgets
            for widget in self.winfo_children():
                widget.destroy()
            
            # Create and show login frame
            self.login_frame = LoginWindow(self)
            self.login_frame.pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to show login window: {str(e)}")
            if hasattr(self, 'conn'):
                try:
                    self.conn.close()
                except:
                    pass
            self.root.destroy()

    def setup_main_window(self):
        """Setup the main window after successful login"""
        # Clear any existing widgets
        for widget in self.winfo_children():
            widget.destroy()
        
        # Resize window for dashboard
        self.root.geometry("1200x800")
        
        # Create main container
        self.main_container = tk.Frame(self, bg=self.colors['bg'])
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=40)
        
        # Create header
        self.create_header()
        
        # Create dashboard
        self.create_dashboard()

    def create_header(self):
        """Create header with title and subtitle"""
        header_frame = tk.Frame(self.main_container, bg=self.colors['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 40))
        
        # Title
        title = tk.Label(header_frame, 
                        text="Hotel Management System",
                        font=('Helvetica', 36, 'bold'),
                        bg=self.colors['bg'],
                        fg=self.colors['primary'])
        title.pack()
        
        # Subtitle
        subtitle = tk.Label(header_frame,
                          text="Welcome to the future of hotel management",
                          font=('Helvetica', 14),
                          bg=self.colors['bg'],
                          fg=self.colors['text'])
        subtitle.pack()

    def create_dashboard(self):
        """Create main dashboard with 4 buttons"""
        # Create grid container with padding
        button_container = tk.Frame(self.main_container, bg=self.colors['bg'])
        button_container.pack(expand=True, fill='both', padx=20, pady=20)
        
        # Configure grid weights for centering
        button_container.grid_columnconfigure(0, weight=1)
        button_container.grid_columnconfigure(1, weight=1)
        button_container.grid_rowconfigure(0, weight=1)
        button_container.grid_rowconfigure(1, weight=1)
        
        # Calculate button dimensions
        button_width = 400  # Fixed width for all buttons
        button_height = 250  # Fixed height for all buttons
        
        # Create buttons with consistent size
        add_room_btn = DashboardButton(
            button_container,
            "Add Room",
            "Add new rooms to the hotel inventory",
            "🏨",
            self.open_add_room_window,
            self.colors['secondary']
        )
        add_room_btn.configure(width=button_width, height=button_height)
        add_room_btn.grid(row=0, column=0, padx=20, pady=20, sticky='nsew')
        
        book_room_btn = DashboardButton(
            button_container,
            "Book Room",
            "Make new room reservations",
            "📅",
            self.open_book_room_window,
            self.colors['accent2']
        )
        book_room_btn.configure(width=button_width, height=button_height)
        book_room_btn.grid(row=0, column=1, padx=20, pady=20, sticky='nsew')
        
        view_bookings_btn = DashboardButton(
            button_container,
            "View Bookings",
            "Manage existing bookings",
            "📋",
            self.open_view_bookings_window,
            self.colors['accent1']
        )
        view_bookings_btn.configure(width=button_width, height=button_height)
        view_bookings_btn.grid(row=1, column=0, padx=20, pady=20, sticky='nsew')
        
        customer_info_btn = DashboardButton(
            button_container,
            "Customer Info",
            "View and manage customer information",
            "👥",
            self.open_customer_info_window,
            self.colors['accent4']
        )
        customer_info_btn.configure(width=button_width, height=button_height)
        customer_info_btn.grid(row=1, column=1, padx=20, pady=20, sticky='nsew')

    def initialize_database(self):
        """Initialize database connection and create backup"""
        try:
            # Create database directory if it doesn't exist
            db_dir = os.path.dirname(self.db_file)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir)

            # Create a new connection
            self.conn = sqlite3.connect(self.db_file)
            
            # Enable foreign key support
            self.conn.execute("PRAGMA foreign_keys = ON")
            
            # Create tables
            self.create_tables()
            
            # Create default admin user if not exists
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM emp WHERE username = 'admin'")
            if not cursor.fetchone():
                cursor.execute("INSERT INTO emp (username, password) VALUES (?, ?)", 
                             ('admin', 'admin123'))
                self.conn.commit()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to initialize database: {str(e)}")
            raise  # Re-raise to be caught by main error handler

    def create_tables(self):
        """Create the necessary database tables"""
        try:
            cursor = self.conn.cursor()
            
            # Create tables with proper constraints
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
                status TEXT DEFAULT 'available' 
                CHECK (status IN ('available', 'booked', 'maintenance'))
            )
            """)
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_name TEXT NOT NULL,
                room_number INTEGER NOT NULL,
                check_in_date DATE NOT NULL,
                check_out_date DATE NOT NULL,
                num_persons INTEGER NOT NULL CHECK (num_persons > 0),
                children TEXT NOT NULL,
                status TEXT DEFAULT 'active' 
                CHECK (status IN ('active', 'completed', 'cancelled')),
                booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_number) REFERENCES rooms(room_number)
                ON DELETE RESTRICT
                ON UPDATE CASCADE
            )
            """)
            
            self.conn.commit()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to create tables: {str(e)}")
            raise

    def open_add_room_window(self):
        """Open window for adding rooms"""
        try:
            window = ModernWindow(self.root, "Add New Room")
            window.conn = self.conn  # Share database connection
            
            # Create form
            form = tk.Frame(window.container, bg='white')
            form.pack(fill=tk.BOTH, expand=True)
            
            # Room Type
            tk.Label(form, text="Room Type:", bg='white',
                    font=('Helvetica', 12)).grid(row=0, column=0, padx=20, pady=10)
            room_type_var = tk.StringVar(value="Normal")  # Set default value
            ttk.Combobox(form, textvariable=room_type_var,
                        values=["Normal", "Deluxe", "Premium", "Suite"],
                        width=30).grid(row=0, column=1)
            
            # AC Type
            tk.Label(form, text="AC/Non-AC:", bg='white',
                    font=('Helvetica', 12)).grid(row=1, column=0, padx=20, pady=10)
            ac_var = tk.StringVar(value="AC")  # Set default value
            ttk.Combobox(form, textvariable=ac_var,
                        values=["AC", "Non-AC"],
                        width=30).grid(row=1, column=1)
            
            # Room Number
            tk.Label(form, text="Room Number:", bg='white',
                    font=('Helvetica', 12)).grid(row=2, column=0, padx=20, pady=10)
            room_number = ttk.Entry(form, width=30)
            room_number.grid(row=2, column=1)

            # Price
            tk.Label(form, text="Price per Night:", bg='white',
                    font=('Helvetica', 12)).grid(row=3, column=0, padx=20, pady=10)
            price_entry = ttk.Entry(form, width=30)
            price_entry.grid(row=3, column=1)

            # Capacity
            tk.Label(form, text="Capacity:", bg='white',
                    font=('Helvetica', 12)).grid(row=4, column=0, padx=20, pady=10)
            capacity_var = tk.StringVar(value="2")  # Set default value
            ttk.Combobox(form, textvariable=capacity_var,
                        values=["1", "2", "3", "4"],
                        width=30).grid(row=4, column=1)

            # WiFi
            tk.Label(form, text="WiFi Available:", bg='white',
                    font=('Helvetica', 12)).grid(row=5, column=0, padx=20, pady=10)
            wifi_var = tk.BooleanVar(value=True)  # Set default value
            ttk.Checkbutton(form, variable=wifi_var).grid(row=5, column=1, sticky='w')
            
            def add_room_action():
                try:
                    if not all([room_type_var.get(), ac_var.get(), room_number.get(), 
                               price_entry.get(), capacity_var.get()]):
                        raise ValueError("All fields must be filled")

                    room_num = int(room_number.get())
                    price = float(price_entry.get())
                    capacity = int(capacity_var.get())

                    if price <= 0:
                        raise ValueError("Price must be greater than 0")
                    if capacity < 1 or capacity > 4:
                        raise ValueError("Capacity must be between 1 and 4")

                    cursor = self.conn.cursor()
                    cursor.execute("""
                        INSERT INTO rooms (room_number, room_type, ac_type, price, wifi, capacity, status)
                        VALUES (?, ?, ?, ?, ?, ?, 'available')
                    """, (room_num, room_type_var.get(), ac_var.get(), price, wifi_var.get(), capacity))
                    
                    self.conn.commit()
                    messagebox.showinfo("Success", "Room added successfully!")
                    window.destroy()
                    
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                except sqlite3.IntegrityError:
                    messagebox.showerror("Error", "Room number already exists")
                except sqlite3.Error as e:
                    messagebox.showerror("Database Error", f"Failed to add room: {str(e)}")
                    self.conn.rollback()

            # Add Button
            tk.Button(form, text="Add Room",
                     bg=self.colors['accent2'],
                     fg='white',
                     font=('Helvetica', 12, 'bold'),
                     padx=20, pady=10,
                     command=add_room_action).grid(row=6, column=0, columnspan=2, pady=30)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Add Room window: {str(e)}")

    def open_book_room_window(self):
        """Open window for booking rooms"""
        try:
            window = ModernWindow(self.root, "Book a Room", "1200x800")
            window.conn = self.conn  # Share database connection
            
            # Create main container
            main_container = tk.Frame(window.container, bg='white')
            main_container.pack(fill=tk.BOTH, expand=True)
            
            # Create left frame for form
            left_frame = tk.Frame(main_container, bg='white')
            left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
            
            # Create right frame for available rooms
            right_frame = tk.Frame(main_container, bg='white')
            right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
            
            # Form elements in left frame
            form = tk.Frame(left_frame, bg='white')
            form.pack(fill=tk.BOTH, expand=True)
            
            # Customer Name
            tk.Label(form, text="Customer Name:", bg='white',
                    font=('Helvetica', 12)).grid(row=0, column=0, padx=20, pady=10, sticky='w')
            name_entry = ttk.Entry(form, width=30)
            name_entry.grid(row=0, column=1, padx=20, pady=10, sticky='w')

            # Room Type
            tk.Label(form, text="Room Type:", bg='white',
                    font=('Helvetica', 12)).grid(row=1, column=0, padx=20, pady=10, sticky='w')
            room_type_var = tk.StringVar(value="Normal")
            ttk.Combobox(form, textvariable=room_type_var,
                        values=["Normal", "Deluxe", "Premium", "Suite"],
                        width=30).grid(row=1, column=1, padx=20, pady=10, sticky='w')

            # Number of Persons
            tk.Label(form, text="Number of Persons:", bg='white',
                    font=('Helvetica', 12)).grid(row=2, column=0, padx=20, pady=10, sticky='w')
            persons_var = tk.StringVar(value="2")
            persons_entry = ttk.Combobox(form, textvariable=persons_var,
                                       values=["1", "2", "3", "4"],
                                       width=30, state="readonly")
            persons_entry.grid(row=2, column=1, padx=20, pady=10, sticky='w')

            # Children
            tk.Label(form, text="Children:", bg='white',
                    font=('Helvetica', 12)).grid(row=3, column=0, padx=20, pady=10, sticky='w')
            children_var = tk.StringVar(value="No")
            ttk.Combobox(form, textvariable=children_var,
                        values=["Yes", "No"],
                        width=30).grid(row=3, column=1, padx=20, pady=10, sticky='w')

            # Check-in Date
            tk.Label(form, text="Check-in Date:", bg='white',
                    font=('Helvetica', 12)).grid(row=4, column=0, padx=20, pady=10, sticky='w')
            check_in_date = DateEntry(form, width=27, background=self.colors['secondary'],
                                    foreground='white', borderwidth=2)
            check_in_date.grid(row=4, column=1, padx=20, pady=10, sticky='w')

            # Check-out Date
            tk.Label(form, text="Check-out Date:", bg='white',
                    font=('Helvetica', 12)).grid(row=5, column=0, padx=20, pady=10, sticky='w')
            check_out_date = DateEntry(form, width=27, background=self.colors['secondary'],
                                     foreground='white', borderwidth=2)
            check_out_date.grid(row=5, column=1, padx=20, pady=10, sticky='w')

            # Available Rooms List (in right frame)
            tk.Label(right_frame, text="Available Rooms", bg='white',
                    font=('Helvetica', 14, 'bold')).pack(pady=(0, 10))
            
            # Create a frame for the treeview
            tree_frame = tk.Frame(right_frame, bg='white')
            tree_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create and configure the treeview
            room_list = ttk.Treeview(tree_frame, columns=("Room", "Type", "Price"),
                                    show="headings", height=15)
            
            # Configure column widths and alignments
            room_list.column("Room", width=100, anchor="center")
            room_list.column("Type", width=150, anchor="center")
            room_list.column("Price", width=100, anchor="center")
            
            # Configure column headings
            room_list.heading("Room", text="Room Number")
            room_list.heading("Type", text="Room Type")
            room_list.heading("Price", text="Price (₹)")
            
            # Add vertical scrollbar
            tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=room_list.yview)
            room_list.configure(yscrollcommand=tree_scrollbar.set)
            
            # Add horizontal scrollbar
            tree_scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=room_list.xview)
            room_list.configure(xscrollcommand=tree_scrollbar_x.set)
            
            # Grid layout for treeview and scrollbars
            room_list.grid(row=0, column=0, sticky='nsew')
            tree_scrollbar.grid(row=0, column=1, sticky='ns')
            tree_scrollbar_x.grid(row=1, column=0, sticky='ew')
            
            # Configure grid weights
            tree_frame.grid_columnconfigure(0, weight=1)
            tree_frame.grid_rowconfigure(0, weight=1)

            # Style configuration for treeview
            style = ttk.Style()
            style.configure("Treeview", font=('Helvetica', 10), rowheight=25)
            style.configure("Treeview.Heading", font=('Helvetica', 10, 'bold'))
            
            # Alternating row colors
            room_list.tag_configure('oddrow', background='#f5f5f5')
            room_list.tag_configure('evenrow', background='white')

            def check_availability():
                try:
                    cursor = self.conn.cursor()
                    cursor.execute("""
                        SELECT room_number, room_type, price FROM rooms 
                        WHERE room_type = ? AND status = 'available'
                        AND room_number NOT IN (
                            SELECT room_number FROM bookings 
                            WHERE (check_in_date <= ? AND check_out_date >= ?)
                            AND status = 'active'
                        )
                    """, (room_type_var.get(), check_out_date.get(), check_in_date.get()))
                    
                    # Clear existing items
                    for item in room_list.get_children():
                        room_list.delete(item)
                    
                    # Insert available rooms with alternating colors
                    rooms = cursor.fetchall()
                    if not rooms:
                        messagebox.showinfo("Info", "No rooms available for selected criteria")
                    
                    for i, room in enumerate(rooms):
                        tag = 'evenrow' if i % 2 == 0 else 'oddrow'
                        # Format price with 2 decimal places
                        formatted_room = (room[0], room[1], f"₹{room[2]:.2f}")
                        room_list.insert("", "end", values=formatted_room, tags=(tag,))
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Failed to check availability: {str(e)}")

            def book_room():
                try:
                    if not name_entry.get().strip():
                        raise ValueError("Please enter customer name")
                    if not room_list.selection():
                        raise ValueError("Please select a room to book")
                    
                    # Validate number of persons
                    try:
                        num_persons = int(persons_var.get())
                        if num_persons < 1 or num_persons > 4:
                            raise ValueError("Number of persons must be between 1 and 4")
                    except ValueError:
                        raise ValueError("Please enter a valid number of persons (1-4)")
                    
                    selected_room = room_list.item(room_list.selection()[0])['values'][0]
                    
                    # Check room capacity
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT capacity FROM rooms WHERE room_number = ?", (selected_room,))
                    room_capacity = cursor.fetchone()[0]
                    
                    if num_persons > room_capacity:
                        raise ValueError(f"Selected room has a capacity of {room_capacity} persons only")
                    
                    cursor.execute("""
                        INSERT INTO bookings 
                        (person_name, room_number, check_in_date, check_out_date, 
                         num_persons, children, status)
                        VALUES (?, ?, ?, ?, ?, ?, 'active')
                    """, (name_entry.get(), selected_room, check_in_date.get(),
                         check_out_date.get(), num_persons, children_var.get()))
                    
                    self.conn.commit()
                    messagebox.showinfo("Success", "Room booked successfully!")
                    window.destroy()
                    
                except ValueError as e:
                    messagebox.showerror("Error", str(e))
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Failed to book room: {str(e)}")
                    self.conn.rollback()

            # Add Book Now button in the form section
            book_now_btn = tk.Button(form, 
                     text="Book Now",
                     bg=self.colors['accent2'],
                     fg='white',
                     font=('Helvetica', 14, 'bold'),
                     padx=30,
                     pady=15,
                     command=book_room)
            book_now_btn.grid(row=6, column=0, columnspan=2, pady=30)

            # Create a separator between form and buttons
            ttk.Separator(window.container, orient='horizontal').pack(fill=tk.X, pady=10)

            # Create a button frame at the bottom
            button_frame = tk.Frame(window.container, bg='white')
            button_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=20)

            # Create a container for bottom buttons with center alignment
            bottom_buttons = tk.Frame(button_frame, bg='white')
            bottom_buttons.pack(expand=True)

            # Add Check Availability button
            check_availability_btn = tk.Button(bottom_buttons, 
                     text="Check Availability",
                     bg=self.colors['secondary'],
                     fg='white',
                     font=('Helvetica', 12),
                     padx=20,
                     pady=10,
                     command=check_availability)
            check_availability_btn.pack(side=tk.LEFT, padx=10)

            # Add Book Selected Room button
            book_selected_btn = tk.Button(bottom_buttons, 
                     text="Book Selected Room",
                     bg=self.colors['accent2'],
                     fg='white',
                     font=('Helvetica', 12, 'bold'),
                     padx=20,
                     pady=10,
                     command=book_room)
            book_selected_btn.pack(side=tk.LEFT, padx=10)

            # Bind room type change to automatically check availability
            def on_room_type_change(*args):
                check_availability()
            room_type_var.trace('w', on_room_type_change)

            # Check availability initially
            check_availability()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Book Room window: {str(e)}")

    def open_view_bookings_window(self):
        """Open window for viewing bookings"""
        try:
            window = ModernWindow(self.root, "View Bookings")
            window.conn = self.conn  # Share database connection
            
            # Create treeview
            tree = ttk.Treeview(window.container, 
                               columns=("ID", "Room", "Customer", "Check In", "Check Out", "Status"),
                               show="headings")
            
            # Configure columns
            tree.heading("ID", text="Booking ID")
            tree.heading("Room", text="Room Number")
            tree.heading("Customer", text="Customer Name")
            tree.heading("Check In", text="Check In")
            tree.heading("Check Out", text="Check Out")
            tree.heading("Status", text="Status")
            
            for col in tree["columns"]:
                tree.column(col, width=120)
            
            tree.pack(fill=tk.BOTH, expand=True, pady=20)

            def load_bookings():
                try:
                    # Clear existing items
                    for item in tree.get_children():
                        tree.delete(item)
                    
                    cursor = self.conn.cursor()
                    cursor.execute("""
                        SELECT booking_id, room_number, person_name, 
                               check_in_date, check_out_date, status
                        FROM bookings
                        ORDER BY check_in_date DESC
                    """)
                    
                    bookings = cursor.fetchall()
                    if not bookings:
                        messagebox.showinfo("Info", "No bookings found")
                    
                    for booking in bookings:
                        tree.insert("", "end", values=booking)
                        
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Failed to load bookings: {str(e)}")

            def cancel_booking():
                if not tree.selection():
                    messagebox.showwarning("Warning", "Please select a booking to cancel")
                    return
                
                booking_id = tree.item(tree.selection()[0])['values'][0]
                
                if messagebox.askyesno("Confirm", "Are you sure you want to cancel this booking?"):
                    try:
                        cursor = self.conn.cursor()
                        cursor.execute("""
                            UPDATE bookings SET status = 'cancelled'
                            WHERE booking_id = ?
                        """, (booking_id,))
                        
                        self.conn.commit()
                        messagebox.showinfo("Success", "Booking cancelled successfully!")
                        load_bookings()  # Refresh the list
                        
                    except sqlite3.Error as e:
                        messagebox.showerror("Error", f"Failed to cancel booking: {str(e)}")
                        self.conn.rollback()

            # Buttons Frame
            button_frame = tk.Frame(window.container, bg='white')
            button_frame.pack(fill=tk.X, pady=20)
            
            tk.Button(button_frame, text="Cancel Booking",
                     bg=self.colors['accent1'],
                     fg='white',
                     font=('Helvetica', 12),
                     command=cancel_booking).pack(side=tk.LEFT, padx=5)
            
            tk.Button(button_frame, text="Refresh",
                     bg=self.colors['secondary'],
                     fg='white',
                     font=('Helvetica', 12),
                     command=load_bookings).pack(side=tk.LEFT, padx=5)

            # Load bookings initially
            load_bookings()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open View Bookings window: {str(e)}")

    def open_customer_info_window(self):
        """Open window for customer information"""
        try:
            window = ModernWindow(self.root, "Customer Information")
            window.conn = self.conn  # Share database connection
            
            # Create treeview
            tree = ttk.Treeview(window.container, 
                               columns=("Name", "Room", "Check In", "Check Out", "Status"),
                               show="headings")
            
            # Configure columns
            tree.heading("Name", text="Customer Name")
            tree.heading("Room", text="Room Number")
            tree.heading("Check In", text="Check In")
            tree.heading("Check Out", text="Check Out")
            tree.heading("Status", text="Status")
            
            for col in tree["columns"]:
                tree.column(col, width=120)
            
            tree.pack(fill=tk.BOTH, expand=True, pady=20)

            def load_customer_info():
                try:
                    # Clear existing items
                    for item in tree.get_children():
                        tree.delete(item)
                    
                    cursor = self.conn.cursor()
                    cursor.execute("""
                        SELECT person_name, room_number, check_in_date, 
                               check_out_date, status
                        FROM bookings
                        WHERE status = 'active'
                        ORDER BY check_in_date DESC
                    """)
                    
                    customers = cursor.fetchall()
                    if not customers:
                        messagebox.showinfo("Info", "No active customers found")
                    
                    for customer in customers:
                        tree.insert("", "end", values=customer)
                        
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Failed to load customer information: {str(e)}")

            # Search frame
            search_frame = tk.Frame(window.container, bg='white')
            search_frame.pack(fill=tk.X, pady=(0, 20))

            tk.Label(search_frame, text="Search:", bg='white',
                    font=('Helvetica', 12)).pack(side=tk.LEFT, padx=5)
            
            search_entry = ttk.Entry(search_frame, width=30)
            search_entry.pack(side=tk.LEFT, padx=5)

            def search_customers():
                query = search_entry.get().strip()
                if not query:
                    load_customer_info()
                    return

                try:
                    cursor = self.conn.cursor()
                    cursor.execute("""
                        SELECT person_name, room_number, check_in_date, 
                               check_out_date, status
                        FROM bookings
                        WHERE person_name LIKE ? AND status = 'active'
                        ORDER BY check_in_date DESC
                    """, (f"%{query}%",))
                    
                    # Clear existing items
                    for item in tree.get_children():
                        tree.delete(item)
                    
                    customers = cursor.fetchall()
                    if not customers:
                        messagebox.showinfo("Info", "No matching customers found")
                    
                    for customer in customers:
                        tree.insert("", "end", values=customer)
                        
                except sqlite3.Error as e:
                    messagebox.showerror("Error", f"Failed to search customers: {str(e)}")

            tk.Button(search_frame, text="Search",
                     bg=self.colors['secondary'],
                     fg='white',
                     font=('Helvetica', 12),
                     command=search_customers).pack(side=tk.LEFT, padx=5)

            # Refresh button
            tk.Button(window.container, text="Refresh",
                     bg=self.colors['secondary'],
                     fg='white',
                     font=('Helvetica', 12),
                     command=load_customer_info).pack(pady=20)

            # Load customer info initially
            load_customer_info()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Customer Info window: {str(e)}")

    def on_closing(self):
        """Handle application closing"""
        try:
            if hasattr(self, 'conn'):
                try:
                    self.conn.commit()
                    self.conn.close()
                except:
                    pass
            self.root.destroy()
        except Exception as e:
            print(f"Error during cleanup: {str(e)}")
            import os
            os._exit(1)

    def create_user(self, username, password):  
        """Create a new user in the database."""  
        cursor = self.conn.cursor()  
        cursor.execute("INSERT INTO emp (username, password) VALUES (?, ?)", (username, password))  
        self.conn.commit()

    def register_user(self):  
        """Register a new user."""  
        username = simpledialog.askstring("Register", "Enter username:")  
        password = simpledialog.askstring("Register", "Enter password:", show='*')  

        if username and password:  
            try:  
                self.create_user(username, password)  
                messagebox.showinfo("Success", "User registered successfully!")  
            except sqlite3.Error as e:  
                messagebox.showerror("Error", f"Failed to register user: {str(e)}")  
        else:  
            messagebox.showerror("Error", "Username and password cannot be empty.")

if __name__ == "__main__":
    root = None
    app = None
    try:
        # Initialize the root window
        root = tk.Tk()
        root.title("Hotel Management System")
        
        # Set window icon (optional)
        try:
            root.iconbitmap('hotel.ico')
        except:
            pass
        
        # Center the window on screen
        window_width = 400
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configure root window
        root.configure(bg='white')
        root.resizable(True, True)  # Allow window resizing
        root.minsize(400, 600)  # Set minimum window size
        
        # Create the application instance
        app = HotelManagementApp(root)
        
        # Set up the closing protocol
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Start the main event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Fatal Error: {str(e)}")  # Print to console for debugging
        
        # Clean up database connection if it exists
        if app and hasattr(app, 'conn'):
            try:
                app.conn.close()
            except:
                pass
        
        # Exit without trying to destroy root
        import os
        os._exit(1)  # Force exit without cleanup
        
    except KeyboardInterrupt:
        print("Application terminated by user")
        if app and hasattr(app, 'conn'):
            try:
                app.conn.close()
            except:
                pass
        os._exit(0)
        