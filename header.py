import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

class Header:
    def __init__(self, root, add_album_callback, login_callback, logout_callback):
        header_frame = tk.Frame(root, bg="white", padx=20, pady=10)
        header_frame.pack(fill=tk.X, anchor="n")

        # Load and display the logo image
        logo_image_path = "/Users/lucasavila/PycharmProjects/groovn/icons/logo.png"
        if os.path.exists(logo_image_path):
            try:
                logo_image = Image.open(logo_image_path)
                logo_image = logo_image.resize((60, 40))  # Resize to make the logo slightly wider
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                self.logo_label_img = tk.Label(header_frame, image=self.logo_photo, bg="white")
                self.logo_label_img.pack(side=tk.LEFT, padx=2)  # Reduced padding to bring it closer to text
                print("Logo image loaded and displayed successfully.")
            except Exception as e:
                print(f"Error loading logo image: {e}")
        else:
            print(f"Error: Logo file not found at path: {logo_image_path}")

        # Logo Label (Text)
        self.logo_label = tk.Label(header_frame, text="Groovn", font=("Helvetica", 24, "bold"), fg="#FF5B63", bg="white")
        self.logo_label.pack(side=tk.LEFT, padx=5)

        # Buttons Section - Add Album and Login/Logout buttons on the same line, aligned right
        button_frame = tk.Frame(header_frame, bg="white")
        button_frame.pack(side=tk.RIGHT, padx=10)

        # Custom Logout Button
        self.logout_button_frame = tk.Frame(button_frame, bg="#FF5B63", relief="raised", bd=2, cursor="hand2")
        self.logout_button_frame.pack(side=tk.RIGHT, padx=(5, 10))
        self.logout_button_label = tk.Label(self.logout_button_frame, text="Logout", font=("Helvetica", 10, "bold"), fg="white", bg="#FF5B63", padx=10, pady=5)
        self.logout_button_label.pack()
        self.logout_button_label.bind("<Button-1>", lambda event: logout_callback())

        # Custom Login/Signup Button
        self.login_button_frame = tk.Frame(button_frame, bg="#FF5B63", relief="raised", bd=2, cursor="hand2")
        self.login_button_frame.pack(side=tk.RIGHT, padx=(5, 10))
        self.login_button_label = tk.Label(self.login_button_frame, text="Login / Signup", font=("Helvetica", 10, "bold"), fg="white", bg="#FF5B63", padx=10, pady=5)
        self.login_button_label.pack()
        self.login_button_label.bind("<Button-1>", lambda event: login_callback())

        # Custom Add Album Button
        add_album_button_frame = tk.Frame(button_frame, bg="#FF5B63", relief="raised", bd=2, cursor="hand2")
        add_album_button_frame.pack(side=tk.RIGHT, padx=(5, 10))
        add_album_button_label = tk.Label(add_album_button_frame, text="Add Album", font=("Helvetica", 10, "bold"), fg="white", bg="#FF5B63", padx=15, pady=5)
        add_album_button_label.pack()
        add_album_button_label.bind("<Button-1>", lambda event: add_album_callback())
