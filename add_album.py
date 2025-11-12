import tkinter as tk
from tkinter import messagebox, StringVar, Text
from tkinter import ttk
import datetime

class AddAlbumForm:
    def __init__(self, root, on_submit_callback):
        print("Initializing Add Album Form...")
        self.root = root
        self.root.title("Add New Album")
        self.root.geometry("500x750")
        self.root.configure(bg="white")
        self.on_submit_callback = on_submit_callback  # Store the callback function

        # Header Label
        self.header_label = tk.Label(self.root, text="Add New Album", font=("Helvetica", 18, "bold"), fg="#FF5B63", bg="white")
        self.header_label.pack(pady=(20, 10))

        # Album Title Entry
        self.album_title_label = tk.Label(self.root, text="Album Title:", font=("Helvetica", 12), bg="white", fg="black")
        self.album_title_label.pack(anchor="w", padx=20, pady=(10, 0))
        self.album_title_var = StringVar()
        self.album_title_entry = tk.Entry(self.root, textvariable=self.album_title_var, font=("Helvetica", 12), width=40, bg="white", fg="black")
        self.album_title_entry.pack(padx=20, pady=(0, 10))

        # Artist Entry
        self.artist_label = tk.Label(self.root, text="Artist:", font=("Helvetica", 12), bg="white", fg="black")
        self.artist_label.pack(anchor="w", padx=20, pady=(10, 0))
        self.artist_var = StringVar()
        self.artist_entry = tk.Entry(self.root, textvariable=self.artist_var, font=("Helvetica", 12), width=40, bg="white", fg="black")
        self.artist_entry.pack(padx=20, pady=(0, 10))

        # Genre Dropdown
        self.genre_label = tk.Label(self.root, text="Genre:", font=("Helvetica", 12), bg="white", fg="black")
        self.genre_label.pack(anchor="w", padx=20, pady=(10, 0))
        self.genre_var = StringVar()
        self.genre_combobox = ttk.Combobox(self.root, textvariable=self.genre_var, font=("Helvetica", 12), width=38, state="readonly")
        self.genre_combobox['values'] = [
    "Pop",
    "Rock",
    "Hip-Hop/Rap",
    "Electronic Dance Music (EDM)",
    "R&B",
    "Jazz",
    "Country",
    "Blues",
    "Folk",
    "Classical",
    "Metal",
    "Punk",
    "Indie Rock",
    "Soul",
    "Funk",
    "Disco",
    "Alternative",
    "Grunge",
    "Britpop",
    "Emo",
    "New Wave",
    "Synth-Pop",
    "Psychedelic Rock",
    "Progressive Rock",
    "Hardcore Punk",
    "Metalcore",
    "Nu Metal",
    "Death Metal",
    "Black Metal",
    "Thrash Metal",
    "Doom Metal",
    "Indian Classical Music",
    "Chinese Opera",
    "Japanese Enka",
    "K-Pop",
    "J-Pop",
    "Reggaeton",
    "Salsa",
    "Cumbia",
    "Samba",
    "Bossa Nova",
    "Afrobeat",
    "Highlife",
    "Mbalax",
    "Raï",
    "Chaabi",
    "Gnawa",
    "Mariachi",
    "Norteño",
    "Bachata",
    "Merengue",
    "Flamenco",
    "Rumba Catalana",
    "Rock en Español",
    "Latin Trap",
    "Reggaeton Romantico",
    "Banda",
    "Duranguense",
    "Norteño-Banda"
]
        self.genre_combobox.set("Select genre")
        self.genre_combobox.pack(padx=20, pady=(0, 10))

        # Release Date Dropdowns
        self.release_date_label = tk.Label(self.root, text="Release Date:", font=("Helvetica", 12), bg="white", fg="black")
        self.release_date_label.pack(anchor="w", padx=20, pady=(10, 0))

        # Date Selection Frame
        self.date_frame = tk.Frame(self.root, bg="white")
        self.date_frame.pack(anchor="w", padx=20, pady=(0, 10))

        # Day Dropdown (1-31)
        self.day_var = StringVar()
        self.day_combobox = ttk.Combobox(self.date_frame, textvariable=self.day_var, font=("Helvetica", 12), width=5, state="readonly")
        self.day_combobox['values'] = [str(i) for i in range(1, 32)]
        self.day_combobox.set("Day")
        self.day_combobox.pack(side=tk.LEFT, padx=(0, 5))

        # Month Dropdown (January - December)
        self.month_var = StringVar()
        self.month_combobox = ttk.Combobox(self.date_frame, textvariable=self.month_var, font=("Helvetica", 12), width=10, state="readonly")
        self.month_combobox['values'] = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        self.month_combobox.set("Month")
        self.month_combobox.pack(side=tk.LEFT, padx=(0, 5))

        # Year Dropdown (1950 - current year)
        current_year = datetime.datetime.now().year
        self.year_var = StringVar()
        self.year_combobox = ttk.Combobox(self.date_frame, textvariable=self.year_var, font=("Helvetica", 12), width=7, state="readonly")
        self.year_combobox['values'] = [str(i) for i in range(1950, current_year + 1)]
        self.year_combobox.set("Year")
        self.year_combobox.pack(side=tk.LEFT, padx=(0, 5))

        # Album Cover URL Entry
        self.cover_url_label = tk.Label(self.root, text="Album Cover URL:", font=("Helvetica", 12), bg="white", fg="black")
        self.cover_url_label.pack(anchor="w", padx=20, pady=(10, 0))
        self.cover_url_var = StringVar()
        self.cover_url_entry = tk.Entry(self.root, textvariable=self.cover_url_var, font=("Helvetica", 12), width=40, bg="white", fg="black")
        self.cover_url_entry.pack(padx=20, pady=(0, 20))

        # Rating Section
        self.rating_label = tk.Label(self.root, text="Rating:", font=("Helvetica", 12), bg="white", fg="black")
        self.rating_label.pack(anchor="w", padx=20, pady=(10, 0))

        self.rating_frame = tk.Frame(self.root, bg="white")
        self.rating_frame.pack(anchor="w", padx=20, pady=(0, 10))

        # Stars to represent rating
        self.stars = []
        self.rating_value = tk.IntVar(value=0)

        for i in range(5):
            star_label = tk.Label(self.rating_frame, text="☆", font=("Helvetica", 20), fg="#FF5B63", bg="white", cursor="hand2")
            star_label.pack(side=tk.LEFT, padx=2)
            star_label.bind("<Button-1>", lambda e, idx=i: self.set_rating(idx + 1))
            self.stars.append(star_label)

        # Review Section
        self.review_label = tk.Label(self.root, text="Review:", font=("Helvetica", 12), bg="white", fg="black")
        self.review_label.pack(anchor="w", padx=20, pady=(10, 0))
        self.review_text = Text(self.root, font=("Helvetica", 12), width=40, height=5, wrap="word", bg="white", fg="black")
        self.review_text.pack(padx=20, pady=(0, 20))

        # Submit Button - Explicit style set during creation
        self.submit_button = tk.Button(self.root, text="Add Album", font=("Helvetica", 12, "bold"),
                                       fg="white", bg="#FF5B63", activebackground="#FF5B63", activeforeground="white",
                                       padx=10, pady=5, command=self.submit_album)
        self.submit_button.pack(pady=(10, 20))

    def set_rating(self, rating):
        """Set the rating based on the clicked star"""
        self.rating_value.set(rating)
        for idx, star in enumerate(self.stars):
            if idx < rating:
                star.config(text="★")  # Filled star
            else:
                star.config(text="☆")  # Empty star

    def submit_album(self):
        """Handle adding the new album"""
        # Get all input values
        title = self.album_title_var.get().strip()
        artist = self.artist_var.get().strip()
        genre = self.genre_var.get().strip()
        day = self.day_var.get()
        month = self.month_var.get()
        year = self.year_var.get()
        cover_url = self.cover_url_var.get().strip()
        rating = self.rating_value.get()
        review = self.review_text.get("1.0", tk.END).strip()

        # Basic validation
        if not title or not artist or not genre or day == "Day" or month == "Month" or year == "Year":
            messagebox.showerror("Input Error", "Please fill in all fields.")
            return

        # Map month names to their numeric values
        month_mapping = {
            "January": "01", "February": "02", "March": "03", "April": "04", "May": "05", "June": "06",
            "July": "07", "August": "08", "September": "09", "October": "10", "November": "11", "December": "12"
        }

        if month not in month_mapping:
            messagebox.showerror("Input Error", "Invalid month selected.")
            return

        # Combine day, month, and year into a release date
        release_date = f"{year}-{month_mapping[month]}-{day.zfill(2)}"

        try:
            # Validate the constructed date
            datetime.datetime.strptime(release_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date format.")
            return

        # Call the callback function and close the window
        self.on_submit_callback({
            "title": title,
            "artist": artist,
            "genre": genre,
            "release_date": release_date,
            "cover_url": cover_url,
            "rating": rating,
            "review": review
        })
        self.root.destroy()  # Close the add-album window
