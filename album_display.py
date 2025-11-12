import tkinter as tk
from PIL import Image, ImageTk
import requests


class AlbumDisplay:
    def __init__(self, root, albums):
        """
        Initialize the AlbumDisplay component.
        Args:
            root (tk.Tk or tk.Frame): The parent widget for the display.
            albums (list): List of albums to display initially.
        """
        # Main frame for scrollable content
        self.main_frame = tk.Frame(root, bg="white")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Add Canvas for scrolling
        self.canvas = tk.Canvas(self.main_frame, bg="white")
        self.scrollbar = tk.Scrollbar(self.main_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")

        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack canvas and scrollbar
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Display the initial list of albums
        self.update_albums(albums)

    def update_albums(self, albums):
        """
        Update the album display.
        Args:
            albums (list): List of albums to display.
        """
        # Clear existing widgets in the album list frame
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # If no albums, show a default message
        if not albums:
            tk.Label(
                self.scrollable_frame,
                text="No albums added yet. Start by adding your first album!",
                font=("Helvetica", 12),
                fg="grey",
                bg="white"
            ).pack(expand=True)
        else:
            for album in albums:
                self.create_album_widget(album)

    def create_album_widget(self, album):
        """
        Create a widget to display an album's details.
        Args:
            album (dict): Album data to display.
        """
        album_frame = tk.Frame(self.scrollable_frame, bg="white", relief="groove", bd=2, padx=10, pady=10)
        album_frame.pack(anchor="e", padx=(10, 200), pady=10, fill=tk.X)  # Adjust padx to move further right

        # Display album cover
        try:
            cover_image = Image.open(requests.get(album["url"], stream=True).raw)
            cover_image = cover_image.resize((80, 80))
            cover_photo = ImageTk.PhotoImage(cover_image)
            cover_label = tk.Label(album_frame, image=cover_photo, bg="white")
            cover_label.image = cover_photo  # Prevent garbage collection
            cover_label.pack(side=tk.LEFT, padx=10)
        except Exception as e:
            print(f"Error loading cover image: {e}")
            cover_label = tk.Label(album_frame, text="[No Image]", font=("Helvetica", 10), bg="white")
            cover_label.pack(side=tk.LEFT, padx=10)

        # Display album information
        info_frame = tk.Frame(album_frame, bg="white")
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(info_frame, text=album["album"], font=("Helvetica", 14, "bold"), fg="#FF5B63", bg="white").pack(anchor="w")
        tk.Label(info_frame, text=f"Artist: {album['artist']}", font=("Helvetica", 12), bg="white").pack(anchor="w")
        tk.Label(info_frame, text=f"Genre: {album['genre']}", font=("Helvetica", 12), bg="white").pack(anchor="w")
        tk.Label(info_frame, text=f"Rating: {'★' * album['rating']}{'☆' * (5 - album['rating'])}", font=("Helvetica", 12), fg="#FF5B63", bg="white").pack(anchor="w")
        tk.Label(info_frame, text=f"Review: {album['review']}", font=("Helvetica", 10), fg="grey", bg="white", wraplength=400).pack(anchor="w")

    def clear_albums(self):
        """Clear the album display."""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
