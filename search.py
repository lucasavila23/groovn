import tkinter as tk
from tkinter import StringVar, ttk

class SearchBar:
    def __init__(self, root, update_callback):
        search_frame = tk.Frame(root, bg="white", padx=20, pady=10)
        search_frame.pack(fill=tk.X, anchor="w")

        # Search Entry
        self.search_var = StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, font=("Helvetica", 14), bg="white",fg="black", relief="flat", width=60)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 10), pady=5)
        self.search_entry.bind("<KeyRelease>", update_callback)

        # Placeholder behavior
        self.search_entry.insert(0, "Search albums...")
        self.search_entry.bind("<FocusIn>", self.clear_placeholder)
        self.search_entry.bind("<FocusOut>", self.add_placeholder)

        # Filter Section
        self.genre_var = StringVar(value="All Genres")
        self.artist_order_var = StringVar(value="A-Z")
        self.rating_order_var = StringVar(value="Best to Worst")
        self.date_order_var = StringVar(value="Newest First")

        # Create Comboboxes for filters
        self.create_filters(search_frame, update_callback)

    def create_filters(self, parent_frame, update_callback):
        # Genre Filter
        genre_combobox = ttk.Combobox(parent_frame, textvariable=self.genre_var, font=("Helvetica", 12), width=15)
        genre_combobox['values'] = ["All Genres", "Pop", "Rock", "Jazz", "Classical", "Hip-Hop/Rap", "Country", "Electronic", "Other"]
        genre_combobox.pack(side=tk.LEFT, padx=(0, 15))
        genre_combobox.bind("<<ComboboxSelected>>", update_callback)

        # Artist Order
        artist_order_combobox = ttk.Combobox(parent_frame, textvariable=self.artist_order_var, font=("Helvetica", 12), width=5)
        artist_order_combobox['values'] = ["A-Z", "Z-A"]
        artist_order_combobox.pack(side=tk.LEFT, padx=(0, 15))
        artist_order_combobox.bind("<<ComboboxSelected>>", update_callback)

        # Rating Order
        rating_order_combobox = ttk.Combobox(parent_frame, textvariable=self.rating_order_var, font=("Helvetica", 12), width=12)
        rating_order_combobox['values'] = ["Best to Worst", "Worst to Best"]
        rating_order_combobox.pack(side=tk.LEFT, padx=(0, 15))
        rating_order_combobox.bind("<<ComboboxSelected>>", update_callback)

        # Date Order
        date_order_combobox = ttk.Combobox(parent_frame, textvariable=self.date_order_var, font=("Helvetica", 12), width=12)
        date_order_combobox['values'] = ["Newest First", "Oldest First"]
        date_order_combobox.pack(side=tk.LEFT, padx=(0, 15))
        date_order_combobox.bind("<<ComboboxSelected>>", update_callback)

    def clear_placeholder(self, event):
        """Clear the placeholder text when the search bar is focused"""
        if self.search_entry.get() == "Search albums...":
            self.search_entry.delete(0, tk.END)

    def add_placeholder(self, event):
        """Add placeholder text if the search bar is empty after focus out"""
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Search albums...")

    def get_search_query(self):
        return self.search_var.get()

    def get_genre_filter(self):
        return self.genre_var.get()

    def get_artist_order(self):
        return self.artist_order_var.get()

    def get_rating_order(self):
        return self.rating_order_var.get()

    def get_date_order(self):
        return self.date_order_var.get()
