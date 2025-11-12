import tkinter as tk
from header import Header
from album_display import AlbumDisplay
from search import SearchBar
from add_album import AddAlbumForm
from mysql.connector import connect, Error


class GroovnApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Groovn - Music Album Manager")
        self.root.geometry("1000x600")
        self.root.configure(bg="white")

        # Connect to MySQL database
        self.connection = self.connect_to_db()
        self.current_user_id = None  # Logged-in user's ID

        # Initialize Header
        self.header = Header(
            self.root,
            self.show_add_album_form,  # Callback for "Add Album"
            self.show_login_form,  # Callback for "Login / Signup"
            self.logout_user  # Callback for "Logout"
        )

        # Initialize Search Bar and Album Display
        self.search_bar = SearchBar(self.root, self.update_display)
        self.album_display = AlbumDisplay(self.root, [])  # Pass empty list initially

        # Load albums on startup
        self.load_albums()

    def connect_to_db(self):
        """Establish a connection to the MySQL database"""
        try:
            connection = connect(
                host="localhost",
                port=8889,
                user="root",
                password="root",
                database="groovnapp"
            )
            print("Connected to the database successfully.")
            return connection
        except Error as e:
            print(f"Error connecting to database: {e}")
            tk.messagebox.showerror("Database Error", f"Could not connect to the database: {e}")
            return None

    def show_add_album_form(self):
        """Show the form to add a new album"""
        if not self.current_user_id:
            tk.messagebox.showerror("Access Denied", "You must be logged in to add an album.")
            return

        def submit_callback(album_data):
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    """
                    INSERT INTO reviews (user_id, album, artist, genre, rating, review, url, date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        self.current_user_id,
                        album_data["title"],
                        album_data["artist"],
                        album_data["genre"],
                        album_data["rating"],
                        album_data["review"],
                        album_data["cover_url"],
                        album_data["release_date"],
                    )
                )
                self.connection.commit()
                cursor.close()
                self.load_albums()
                tk.messagebox.showinfo("Success", "Album added successfully!")
            except Error as e:
                print(f"Error inserting album: {e}")
                tk.messagebox.showerror("Database Error", f"Failed to add album: {e}")

        AddAlbumForm(tk.Toplevel(self.root), submit_callback)

    def show_login_form(self):
        """Display the login form for user authentication."""
        login_window = tk.Toplevel(self.root)
        login_window.title("Login / Signup")
        login_window.geometry("300x300")

        # Username Input
        tk.Label(login_window, text="Username:").pack()
        username_var = tk.StringVar()
        tk.Entry(login_window, textvariable=username_var).pack()

        # Password Input
        tk.Label(login_window, text="Password:").pack()
        password_var = tk.StringVar()
        tk.Entry(login_window, textvariable=password_var, show="*").pack()

        def login():
            """Handle user login."""
            cursor = self.connection.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username=%s AND password=%s",
                (username_var.get(), password_var.get())
            )
            result = cursor.fetchone()
            if result:
                self.current_user_id = result[0]
                tk.messagebox.showinfo("Login Success", "You are logged in!")
                login_window.destroy()
                self.load_albums()
            else:
                tk.messagebox.showerror("Login Failed", "Invalid username or password.")
            cursor.close()

        tk.Button(login_window, text="Login", command=login).pack(pady=10)

        # Signup Button
        def show_signup_form():
            """Open the signup form."""
            signup_window = tk.Toplevel(self.root)
            signup_window.title("Signup")
            signup_window.geometry("300x350")

            # Username Input
            tk.Label(signup_window, text="Username:").pack()
            new_username_var = tk.StringVar()
            tk.Entry(signup_window, textvariable=new_username_var).pack()

            # Email Input
            tk.Label(signup_window, text="Email:").pack()
            new_email_var = tk.StringVar()
            tk.Entry(signup_window, textvariable=new_email_var).pack()

            # Password Input
            tk.Label(signup_window, text="Password:").pack()
            new_password_var = tk.StringVar()
            tk.Entry(signup_window, textvariable=new_password_var, show="*").pack()

            # Signup Button
            def signup():
                """Handle user signup."""
                new_username = new_username_var.get().strip()
                new_email = new_email_var.get().strip()
                new_password = new_password_var.get().strip()

                if not new_username or not new_email or not new_password:
                    tk.messagebox.showerror("Input Error", "All fields are required.")
                    return

                try:
                    cursor = self.connection.cursor()
                    cursor.execute(
                        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                        (new_username, new_email, new_password)
                    )
                    self.connection.commit()
                    cursor.close()
                    tk.messagebox.showinfo("Signup Success", "Account created successfully! You can now log in.")
                    signup_window.destroy()
                except Error as e:
                    tk.messagebox.showerror("Signup Error", f"Error creating account: {e}")

            tk.Button(signup_window, text="Signup", command=signup).pack(pady=10)

        tk.Button(login_window, text="Signup", command=show_signup_form).pack(pady=10)

    def logout_user(self):
        """Log out the current user"""
        self.current_user_id = None
        self.album_display.clear_albums()
        tk.messagebox.showinfo("Logout", "You have been logged out.")

    def load_albums(self):
        """Load albums for the logged-in user from the database"""
        if not self.current_user_id:
            self.album_display.clear_albums()
            return

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reviews WHERE user_id=%s", (self.current_user_id,))
        albums = cursor.fetchall()
        cursor.close()

        self.album_display.update_albums(albums)

    def update_display(self, event=None):
        """Update the display based on search and filter criteria"""
        query = self.search_bar.get_search_query().lower()
        genre_filter = self.search_bar.get_genre_filter()
        artist_order = self.search_bar.get_artist_order()
        rating_order = self.search_bar.get_rating_order()
        date_order = self.search_bar.get_date_order()

        cursor = self.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM reviews WHERE user_id=%s", (self.current_user_id,))
        albums = cursor.fetchall()

        if query:
            albums = [album for album in albums if query in album["album"].lower() or query in album["artist"].lower()]
        if genre_filter != "All Genres":
            albums = [album for album in albums if album["genre"] == genre_filter]
        if artist_order == "A-Z":
            albums.sort(key=lambda x: x["artist"])
        elif artist_order == "Z-A":
            albums.sort(key=lambda x: x["artist"], reverse=True)
        if rating_order == "Best to Worst":
            albums.sort(key=lambda x: x["rating"], reverse=True)
        elif rating_order == "Worst to Best":
            albums.sort(key=lambda x: x["rating"])
        if date_order == "Newest First":
            albums.sort(key=lambda x: x["date"], reverse=True)
        elif date_order == "Oldest First":
            albums.sort(key=lambda x: x["date"])

        self.album_display.update_albums(albums)


if __name__ == "__main__":
    root = tk.Tk()
    app = GroovnApp(root)
    root.mainloop()
