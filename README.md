English | [Español](README.es.md)

# Groovn

A desktop app to rate, review and browse music albums, in the style of Letterboxd for music.

## Context

Personal project (autumn 2025).

## Features

- Sign up and log in with a username, email and password.
- Add an album with title, artist, genre, release date, a 1–5 rating, a written review and a cover image URL.
- Browse albums as cards with their cover art.
- Search as you type, filter by genre, and sort by artist (A–Z or Z–A), rating or release date.

## How it works

A Tkinter interface talks to a local MySQL database called `groovnapp` with two tables: `users` and `reviews`. Each review belongs to a user. Cover images are downloaded from their URL with `requests` and shown with Pillow.

This is a learning project. Passwords are stored in plain text and the database credentials are hard-coded for a local MySQL server, so do not use it with real accounts.

## Run it

Needs a local MySQL server with user `root` and password `root`, or edit the connection settings in `main.py` and `test-connection.py`.

```bash
git clone https://github.com/lucasavila23/groovn.git
cd groovn
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test-connection.py   # creates the database and tables
python main.py
```

## Stack

Python, Tkinter, MySQL (mysql-connector-python), Pillow, requests.

## License

MIT. See [LICENSE](LICENSE).

## Author

Lucas Avila Manotas · [LinkedIn](https://www.linkedin.com/in/lucas-avila23)
