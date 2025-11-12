# 🎶 Groovn

**Groovn** is a social music tracking app inspired by **Letterboxd** and **Goodreads** — but for music lovers.
It lets users **rate**, **review**, and **organize** their favorite albums, discover new ones, and explore the listening habits of others.

---

## 🚀 Features

* 🎧 **Add Albums** — Submit albums with details like title, artist, genre, release date, and album cover.
* ⭐ **Rating & Reviews** — Rate albums with a star system and write personal reviews.
* 🖼️ **Album Art Display** — Automatically shows cover images from URLs.
* 🔍 **Search & Filter** — Browse your collection by:

  * Artist (alphabetical order)
  * Genre (custom selection)
  * Rating (best to worst or vice versa)
  * Release date
* 👤 **User Accounts** — Sign up and log in to manage your own album list.
* 💾 **Database Integration** — Connects to both AWS RDS (MySQL) and local SQLite for testing.

---

## 🧱 Tech Stack

* **Python** (backend logic)
* **Tkinter** (user interface)
* **SQLite / AWS RDS (MySQL)** (database)
* **PyCharm** (IDE)
* **macOS** (development environment)

---

## 🗂️ Project Structure

```
groovn/
├── main_page.py            # Main app UI
├── add_album.py            # Album submission form
├── login.py                # Login page
├── signup.py               # Signup page
├── database.py             # Database connection and queries
├── icons/
│   └── logo.png            # App logo
└── README.md               # Project documentation
```

---

## ⚙️ Setup Instructions

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/groovn.git
   cd groovn
   ```

2. **(Optional) Create a virtual environment**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**

   ```bash
   python main_page.py
   ```

---

## 🧠 Future Plans

* Add user profiles with listening statistics
* Integrate APIs (Spotify, Last.fm) for automatic album imports
* Add friend system and activity feed
* Create a web version with Flask or React frontend

---

## 🧑‍💻 Author

**Lucas Ávila**

* 🎓 Philosophy, Politics, Law & Economics student at IE University
* 🌍 Passionate about music, data, and design
* 💡 Connect on [GitHub](https://github.com/<your-username>)

---

## 📄 License

This project is open-source under the [MIT License](LICENSE).
